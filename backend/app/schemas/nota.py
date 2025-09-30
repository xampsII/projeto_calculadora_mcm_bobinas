from pydantic import BaseModel, validator
from typing import Optional, List
from decimal import Decimal
from datetime import date
from app.models.enums import StatusNota


class NotaItemCreate(BaseModel):
    materia_prima_id: Optional[int] = None
    nome_no_documento: str
    unidade_codigo: str
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal

    @validator('quantidade')
    def validate_quantidade(cls, v):
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        return v

    @validator('valor_unitario')
    def validate_valor_unitario(cls, v):
        if v < 0:
            raise ValueError('Valor unitário não pode ser negativo')
        return v


class NotaItemResponse(BaseModel):
    id: int
    materia_prima_id: Optional[int] = None
    nome_no_documento: str
    unidade_codigo: str
    quantidade: Decimal
    valor_unitario: Decimal
    valor_total: Decimal

    class Config:
        from_attributes = True


class NotaCreate(BaseModel):
    numero: str  # Mudando de int para str para alinhar com o modelo
    serie: str
    chave_acesso: Optional[str] = None
    fornecedor_id: int
    emissao_date: date
    valor_total: Decimal
    itens: List[NotaItemCreate]

    @validator('chave_acesso')
    def validate_chave_acesso(cls, v):
        if v and len(v) != 44:
            raise ValueError('Chave de acesso deve ter 44 dígitos')
        return v

    @validator('valor_total')
    def validate_valor_total(cls, v):
        if v <= 0:
            raise ValueError('Valor total deve ser maior que zero')
        return v


class NotaUpdate(BaseModel):
    numero: Optional[str] = None  # Mudando de int para str
    serie: Optional[str] = None
    chave_acesso: Optional[str] = None
    fornecedor_id: Optional[int] = None
    emissao_date: Optional[date] = None
    valor_total: Optional[Decimal] = None
    status: Optional[StatusNota] = None


class NotaResponse(BaseModel):
    id: int
    numero: str  # Mudando para str para compatibilidade
    serie: Optional[str] = None
    chave_acesso: Optional[str] = None
    fornecedor_id: Optional[int] = None
    emissao_date: date
    valor_total: Decimal
    arquivo_xml_path: Optional[str] = None
    arquivo_pdf_path: Optional[str] = None
    file_hash: Optional[str] = None
    status: StatusNota
    is_active: bool
    is_pinned: bool = False
    created_at: str
    updated_at: Optional[str] = None
    
    # Relacionamentos
    fornecedor: Optional[dict] = None
    itens: List[NotaItemResponse] = []

    class Config:
        from_attributes = True


class NotaFilters(BaseModel):
    page: int = 1
    page_size: int = 25
    fornecedor_id: Optional[int] = None
    numero: Optional[str] = None
    cnpj: Optional[str] = None
    status: Optional[StatusNota] = None
    emissao_date_from: Optional[date] = None
    emissao_date_to: Optional[date] = None
    q: Optional[str] = None  # Busca textual

    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Página deve ser maior ou igual a 1')
        return v

    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Tamanho da página deve estar entre 1 e 100')
        return v 