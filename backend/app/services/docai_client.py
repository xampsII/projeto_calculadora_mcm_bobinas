from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from google.cloud import documentai_v1 as documentai

from app.config import settings


@lru_cache()
def _credentials_path() -> Optional[str]:
    cred_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    if not cred_path:
        return None
    if os.path.isabs(cred_path):
        resolved = cred_path
    else:
        resolved = os.path.join(settings.PROJECT_ROOT, cred_path)
    return resolved


def configure_credentials() -> None:
    cred_path = _credentials_path()
    if cred_path and os.path.exists(cred_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        print(f"DEBUG: Document AI credentials loaded from: {cred_path}")
    elif cred_path:
        print(f"AVISO: Credenciais do Document AI não encontradas em: {cred_path}")


def process_invoice_pdf(pdf_bytes: bytes) -> documentai.Document:
    """
    Processa PDF de nota fiscal usando o Invoice Parser.
    """
    if not settings.GCP_PROJECT_ID or not settings.GCP_PROCESSOR_ID_INVOICE:
        raise ValueError("Document AI não configurado. Verifique o arquivo .env.")

    configure_credentials()

    client = documentai.DocumentProcessorServiceClient()
    name = client.processor_path(
        settings.GCP_PROJECT_ID,
        settings.GCP_LOCATION,
        settings.GCP_PROCESSOR_ID_INVOICE,
    )

    print(f"DEBUG: Processor path: {name}")

    request = documentai.ProcessRequest(
        name=name,
        raw_document=documentai.RawDocument(
            content=pdf_bytes,
            mime_type="application/pdf",
        ),
    )

    print("DEBUG: Enviando request para Document AI...")
    result = client.process_document(request=request)
    print("DEBUG: ✓ Document AI processou com sucesso!")
    print(f"  Páginas: {len(result.document.pages)}")
    print(f"  Entidades: {len(result.document.entities)}")
    return result.document

