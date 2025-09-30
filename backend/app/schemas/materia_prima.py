from pydantic import BaseModel, validator
from typing import Optional, List
from decimal import Decimal


class MateriaPrimaCreate(BaseModel):
    nome: str
    unidade_codigo: str
    menor_unidade_codigo: Optional[str] = None


class MateriaPrimaUpdate(BaseModel):
    nome: Optional[str] = None
    unidade_codigo: Optional[str] = None
    menor_unidade_codigo: Optional[str] = None


class MateriaPrimaPrecoCreate(BaseModel):
    valor_unitario: Decimal
    fornecedor_id: Optional[int] = None
    nota_id: Optional[int] = None

    @validator('valor_unitario')
    def validate_valor_unitario(cls, v):
        if v <= 0:
            raise ValueError('Valor unitário deve ser maior que zero')
        return v


class MateriaPrimaPrecoResponse(BaseModel):
    id: int
    valor_unitario: Decimal
    moeda: str
    vigente_desde: str
    vigente_ate: Optional[str] = None
    fornecedor_id: Optional[int] = None
    nota_id: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True


class MateriaPrimaResponse(BaseModel):
    id: int
    nome: str
    unidade_codigo: str
    menor_unidade_codigo: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    
    # Preços e variações
    preco_atual: Optional[Decimal] = None
    preco_anterior: Optional[Decimal] = None
    variacao_abs: Optional[Decimal] = None
    variacao_pct: Optional[Decimal] = None
    vigente_desde: Optional[str] = None
    
    # Histórico completo
    precos: Optional[List[MateriaPrimaPrecoResponse]] = []

    class Config:
        from_attributes = True 