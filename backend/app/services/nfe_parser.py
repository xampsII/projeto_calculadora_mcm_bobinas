"""
Parser para converter o retorno do Document AI (Invoice Parser)
em estrutura de DANFE utilizada pelo sistema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:  # type-check friendly
    from google.cloud.documentai_v1 import Document
except Exception:  # pragma: no cover - em testes sem lib instalada
    Document = Any  # type: ignore


def _clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return value.strip()


def _to_float(value: Optional[str]) -> float:
    if value is None:
        return 0.0
    cleaned = value.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def _to_number(prop) -> float:
    normalized = getattr(prop, "normalized_value", None)
    if normalized:
        number_value = getattr(normalized, "number_value", None)
        if number_value is not None:
            return float(number_value)
        text_value = getattr(normalized, "text", None)
        if text_value:
            return _to_float(text_value)
    return _to_float(getattr(prop, "mention_text", None))


@dataclass
class LineItem:
    codigo: str = ""
    descricao: str = ""
    unidade: str = "UN"
    quantidade: float = 0.0
    valor_unitario: float = 0.0
    valor_total: float = 0.0
    extras: Dict[str, Any] = field(default_factory=dict)

    def update_from_property(self, key: str, prop) -> None:
        key_lower = key.lower()
        mention = _clean_text(getattr(prop, "mention_text", ""))

        if "description" in key_lower:
            self.descricao = mention or self.descricao
        elif key_lower.endswith("product_code") or "item_code" in key_lower or "code" in key_lower:
            self.codigo = mention or self.codigo
        elif key_lower.endswith("unit") or key_lower in {"unit", "uom"}:
            self.unidade = mention.upper() if mention else self.unidade
        elif "quantity" in key_lower:
            self.quantidade = _to_number(prop) or self.quantidade
        elif "unit_price" in key_lower or "unit_cost" in key_lower or "price" in key_lower:
            self.valor_unitario = _to_number(prop) or self.valor_unitario
        elif (
            "amount" in key_lower
            or "total" in key_lower
            or "net_amount" in key_lower
            or "net_price" in key_lower
        ):
            self.valor_total = _to_number(prop) or self.valor_total
        elif "ncm" in key_lower:
            self.extras["ncm"] = mention
        elif "cfop" in key_lower:
            self.extras["cfop"] = mention

    def as_dict(self) -> Dict[str, Any]:
        base = {
            "codigo": self.codigo,
            "descricao": self.descricao,
            "unidade": self.unidade or "UN",
            "quantidade": float(self.quantidade or 0.0),
            "valor_unitario": float(self.valor_unitario or 0.0),
            "valor_total": float(self.valor_total or 0.0),
        }
        base.update(self.extras)
        return base


def parse_invoice_document(doc: Document) -> Dict[str, Any]:
    """
    Reconstrói os itens da DANFE a partir das entidades do Document AI.
    """
    result: Dict[str, Any] = {
        "itens": [],
        "fornecedor": "",
        "cnpj_fornecedor": "",
        "numero_nota": "",
        "valor_total": 0.0,
        "data_emissao": "",
        "endereco": "",
    }

    entities = getattr(doc, "entities", None) or []
    print(f"DEBUG: Parseando {len(entities)} entidades do Document AI...")

    line_items: Dict[str, LineItem] = {}
    order: list[str] = []
    current_key: Optional[str] = None
    seq_counter = 0

    for entity in entities:
        entity_type = (entity.type_ or "").lower()
        mention = entity.mention_text or ""
        entity_id = getattr(entity, "id", None)
        parent_id = getattr(entity, "parent_id", None)

        if entity_type == "line_item":
            prop_types = [prop.type_ or "" for prop in entity.properties]
            has_description = any("description" in p.lower() for p in prop_types)

            key = parent_id or entity_id
            if has_description:
                if not key:
                    key = f"seq-{seq_counter}"
                    seq_counter += 1
                current_key = key
                if key not in line_items:
                    line_items[key] = LineItem()
                    order.append(key)
                print("DEBUG: ---- LINE ITEM ----")
                print(f"DEBUG: entity.id       : {entity_id}")
                print(f"DEBUG: entity.parent_id: {parent_id}")
                print(f"DEBUG: mention_text    : {mention}")
            else:
                if key and key in line_items:
                    current_key = key
                if current_key is None:
                    current_key = key or f"seq-{seq_counter}"
                    if current_key not in line_items:
                        line_items[current_key] = LineItem()
                        order.append(current_key)
                    seq_counter += 1

            item_key = current_key
            if item_key not in line_items:
                line_items[item_key] = LineItem()
                order.append(item_key)
            item = line_items[item_key]

            for prop in entity.properties:
                key_name = prop.type_ or ""
                print(f"   PROP type      : {prop.type_}")
                print(f"   PROP mention   : {prop.mention_text}")
                normalized = getattr(prop, "normalized_value", None)
                if normalized:
                    print(f"   PROP normalized: {normalized}")
                item.update_from_property(key_name, prop)

        else:
            if "supplier_tax_id" in entity_type or "vendor_tax_id" in entity_type:
                cnpj = mention.replace(".", "").replace("/", "").replace("-", "").strip()
                if len(cnpj) == 14:
                    result["cnpj_fornecedor"] = cnpj
                    print(f"  ✓ CNPJ: {result['cnpj_fornecedor']}")
            elif "supplier" in entity_type or "vendor" in entity_type:
                if "name" in entity_type:
                    result["fornecedor"] = mention.strip()
                    print(f"  ✓ Fornecedor: {result['fornecedor']}")
            elif "invoice_id" in entity_type or "invoice_number" in entity_type:
                result["numero_nota"] = mention.strip()
                print(f"  ✓ Número NF: {result['numero_nota']}")
            elif (
                "total_amount" in entity_type
                or "net_amount" in entity_type
                or "amount_due" in entity_type
            ):
                result["valor_total"] = _to_float(mention)
                print(f"  ✓ Valor Total: R$ {result['valor_total']:.2f}")
            elif "invoice_date" in entity_type or "issue_date" in entity_type:
                result["data_emissao"] = mention.strip()
                print(f"  ✓ Data Emissão: {result['data_emissao']}")
            elif "supplier_address" in entity_type or "vendor_address" in entity_type:
                result["endereco"] = mention.strip()
                print(f"  ✓ Endereço: {result['endereco'][:50]}...")

    for key in order:
        item = line_items[key]
        item_dict = item.as_dict()
        if item_dict["descricao"] or item_dict["codigo"]:
            result["itens"].append(item_dict)
            print(f"DEBUG: ✓ Item final ({key}): {item_dict}")

    print(f"DEBUG: ✓ Parser extraiu {len(result['itens'])} itens")
    return result

