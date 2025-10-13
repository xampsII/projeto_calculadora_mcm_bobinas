# backend/app/config.py
from __future__ import annotations
from functools import lru_cache
from typing import Optional
from urllib.parse import quote
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# ===== Caminho absoluto para a raiz do repo (project/) =====
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

# Carrega o .env da raiz, independentemente do CWD
load_dotenv(ENV_PATH)

class Settings(BaseSettings):
    # Pydantic também lê o mesmo .env da raiz
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), extra="ignore")

    # URL pronta (opção preferida)
    DATABASE_URL: Optional[str] = "sqlite:///./backend/nfe_system.db"

    # Componentes para montar a URL (fallback)
    DB_HOST_POOLER: Optional[str] = None
    DB_USER: str = "postgres"
    DB_PASSWORD: Optional[str] = None
    DB_NAME: str = "postgres"
    DB_PORT_POOLER: int = 6543
    DB_SSLMODE: str = "require"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        assert self.DB_HOST_POOLER and self.DB_PASSWORD, (
            "Faltam variáveis para montar a URL: defina DATABASE_URL "
            "ou DB_HOST_POOLER e DB_PASSWORD no .env"
        )
        pwd = quote(self.DB_PASSWORD)
        return (
            f"postgresql+psycopg://{self.DB_USER}:{pwd}"
            f"@{self.DB_HOST_POOLER}:{self.DB_PORT_POOLER}/{self.DB_NAME}"
            f"?sslmode={self.DB_SSLMODE}"
        )

        # Debug / Docs da API
    DEBUG: bool = True  # pode ser sobrescrito por DEBUG=false no .env

    # ---- CORS ----
    # Pode ser lista via .env (ex.: "http://localhost:5173,http://localhost:3000")
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174"
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True  # será desativado se origins == ["*"]

    # ---- Hosts confiáveis ----
    ALLOWED_HOSTS: list[str] = ["*"]  # pode ser sobrescrito por ALLOWED_HOSTS no .env
    
    # ---- Upload ----
    UPLOAD_DIR: str = "uploads"  # diretório para uploads de arquivos
    
    # ---- API Server ----
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    @property
    def cors_origins_list(self) -> list[str]:
        """Converte CORS_ORIGINS string em lista"""
        if not self.CORS_ORIGINS:
            return []
        v = self.CORS_ORIGINS.strip()
        if not v:
            return []
        if v == "*":
            return ["*"]
        return [s.strip() for s in v.split(",") if s.strip()]

settings = Settings()

__all__ = ["Settings", "settings", "get_settings"]

@lru_cache()
def get_settings() -> Settings:
    return settings 