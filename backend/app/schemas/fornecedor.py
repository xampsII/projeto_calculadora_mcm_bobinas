from pydantic import BaseModel, validator
from typing import Optional
import re


class FornecedorCreate(BaseModel):
    cnpj: str
    nome: str
    endereco: Optional[str] = None

    @validator('cnpj')
    def validate_cnpj(cls, v):
        # Remove caracteres não numéricos
        cnpj_clean = re.sub(r'[^\d]', '', v)
        if len(cnpj_clean) != 14:
            raise ValueError('CNPJ deve ter 14 dígitos')
        
        # Validação básica de dígitos verificadores
        if cnpj_clean == cnpj_clean[0] * 14:
            raise ValueError('CNPJ não pode ter todos os dígitos iguais')
        
        return cnpj_clean


class FornecedorUpdate(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None


class FornecedorResponse(BaseModel):
    id: int
    cnpj: str
    nome: str
    endereco: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True 