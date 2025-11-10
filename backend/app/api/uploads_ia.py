# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
from unidecode import unidecode

from app.config import settings
from app.services.docai_client import process_invoice_pdf
from app.services.nfe_parser import parse_invoice_document

router = APIRouter(prefix="/uploads-ia", tags=["uploads-ia"])

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = BASE_DIR / settings.UPLOAD_DIR
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

pdf_text_cache: Dict[str, str] = {}
pdf_bytes_cache: Dict[str, bytes] = {}


def _generate_session_id(filename: str) -> str:
    stem = Path(filename).stem.replace(" ", "_")
    return f"{stem}_{uuid.uuid4().hex}"


def _persist_pdf(session_id: str, pdf_bytes: bytes) -> Path:
    file_path = UPLOADS_DIR / f"{session_id}.pdf"
    file_path.write_bytes(pdf_bytes)
    print(f"DEBUG: PDF salvo em disco: {file_path}")
    return file_path


def _load_pdf_from_session(session_id: str) -> Optional[bytes]:
    if session_id in pdf_bytes_cache:
        return pdf_bytes_cache[session_id]
    file_path = UPLOADS_DIR / f"{session_id}.pdf"
    if file_path.exists():
        data = file_path.read_bytes()
        pdf_bytes_cache[session_id] = data
        return data
    return None


def _merge_document_ai_data(base: dict, parsed: dict) -> None:
    if not parsed:
        return
    for key in ["fornecedor", "cnpj_fornecedor", "numero_nota", "valor_total", "data_emissao", "endereco"]:
        if parsed.get(key):
            base[key] = parsed[key]
    if parsed.get("itens"):
        base["itens"] = parsed["itens"]


def estruturar_dados_com_regex(texto: str) -> dict:
    """Extrai dados básicos quando Document AI não estiver disponível."""
    dados = {
        "numero_nota": "",
        "serie": "",
        "chave_acesso": "",
        "valor_total": 0.0,
        "fornecedor": "",
        "cnpj_fornecedor": "",
        "data_emissao": "",
        "endereco": "",
        "itens": [],
    }

    cnpj_match = re.search(r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})", texto)
    if cnpj_match:
        dados["cnpj_fornecedor"] = cnpj_match.group(1).replace(".", "").replace("/", "").replace("-", "")

    valor_match = re.search(r"valor total\s*[:\-]?\s*([\d.,]+)", texto, re.IGNORECASE)
    if valor_match:
        try:
            dados["valor_total"] = float(valor_match.group(1).replace(".", "").replace(",", "."))
        except ValueError:
            pass

    numero_match = re.search(r"nota\s*fiscal\s*(?:n[oº])?\s*[:\-]?\s*(\d+)", texto, re.IGNORECASE)
    if numero_match:
        dados["numero_nota"] = numero_match.group(1)

    data_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    if data_match:
        dados["data_emissao"] = data_match.group(1)

    fornecedor_match = re.search(r"fornecedor\s*[:\-]?\s*([A-Z0-9\s\.\-&]+)", texto, re.IGNORECASE)
    if fornecedor_match:
        dados["fornecedor"] = fornecedor_match.group(1).strip()

    return dados


async def processar_pdf_com_ia(content: bytes, filename: str) -> dict:
    """Processa PDF usando Document AI (Invoice Parser) com fallback em regex."""
    print("\n=== INÍCIO DO PROCESSAMENTO IA ===")
    print(f"Recebido arquivo: {filename}")

    session_id = _generate_session_id(filename)
    pdf_bytes_cache[session_id] = content
    pdf_path = _persist_pdf(session_id, content)

    texto_extraido = ""
    dados_estruturados = {
        "numero_nota": "000000",
        "serie": "",
        "chave_acesso": "",
        "valor_total": 0.0,
        "fornecedor": "",
        "cnpj_fornecedor": "",
        "data_emissao": "",
        "endereco": "",
        "itens": [],
    }

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name

        current_dir = Path(__file__).resolve().parent
        mcp_path = BASE_DIR / "mcp-server-pdf" / "index.js"
        if mcp_path.exists():
            print(f"DEBUG: Executando MCP: node {mcp_path} {tmp_path}")
            result = subprocess.run(
                ["node", str(mcp_path), tmp_path],
                capture_output=True,
                universal_newlines=False,
                check=False,
                cwd=BASE_DIR,
            )

            stdout_text = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
            stderr_text = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
            print(f"Código de retorno MCP: {result.returncode}")
            print(f"MCP stdout (primeiros 200 chars): {stdout_text[:200]}...")
            if result.returncode == 0 and stdout_text:
                try:
                    mcp_data = json.loads(stdout_text)
                    texto_extraido = mcp_data.get("text", "")
                    texto_extraido = unidecode(texto_extraido)
                    texto_extraido = re.sub(r"[^\x00-\x7F]+", "", texto_extraido)
                    texto_extraido = re.sub(r"\s+", " ", texto_extraido).strip()
                    dados_estruturados = estruturar_dados_com_regex(texto_extraido)
                    print(f"DEBUG: Dados estruturados por regex: {dados_estruturados}")
                except json.JSONDecodeError as e:
                    print(f"AVISO: Erro ao parsear JSON do MCP: {e}")
            else:
                print(f"AVISO: MCP retornou erro: {stderr_text}")
        else:
            print(f"AVISO: Script MCP não encontrado em {mcp_path}")
    finally:
        if "tmp_path" in locals() and Path(tmp_path).exists():
            Path(tmp_path).unlink()
            print(f"Arquivo temporário removido: {tmp_path}")

    pdf_text_cache[session_id] = texto_extraido

    method = "regex_fallback"
    docai_error: Optional[str] = None
    if settings.USE_DOCUMENT_AI:
        try:
            document = process_invoice_pdf(content)
            parsed = parse_invoice_document(document)
            _merge_document_ai_data(dados_estruturados, parsed)
            method = "document_ai"
        except Exception as exc:
            docai_error = str(exc)
            print(f"AVISO: Document AI falhou: {docai_error}")

    message = (
        "PDF processado com Document AI!"
        if method == "document_ai"
        else "PDF processado com regex! Dados limitados."
    )

    resultado_final = {
        "success": True,
        "method": method,
        "session_id": session_id,
        "dados_extraidos": dados_estruturados,
        "message": message,
    }

    if docai_error:
        resultado_final["docai_error"] = docai_error

    print(f"DEBUG: Retorno final do backend: {resultado_final}")
    return resultado_final


@router.post("/processar-pdf")
async def processar_pdf_com_ia_endpoint(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")
    content = await file.read()
    resultado = await processar_pdf_com_ia(content, file.filename)
    return resultado


class ReextrairCampoRequest(BaseModel):
    session_id: str
    campo: str


@router.post("/reextrair-campo")
async def reextrair_campo_endpoint(payload: ReextrairCampoRequest):
    campo = payload.campo.lower()
    pdf_bytes = _load_pdf_from_session(payload.session_id)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado: {payload.session_id}")

    try:
        document = process_invoice_pdf(pdf_bytes)
        parsed = parse_invoice_document(document)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro no Document AI: {exc}") from exc

    if campo == "itens":
        itens = parsed.get("itens", [])
        if not itens:
            raise HTTPException(status_code=422, detail="Nenhum item encontrado pelo Document AI.")
        return {"ok": True, "campo": "itens", "itens": itens, "method": "document_ai"}

    if campo not in parsed:
        raise HTTPException(status_code=404, detail=f"Campo '{campo}' não disponível.")

    return {"ok": True, "campo": campo, "valor": parsed.get(campo), "method": "document_ai"}
