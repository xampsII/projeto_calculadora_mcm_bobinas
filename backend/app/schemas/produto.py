from pydantic import BaseModel, validator
from typing import Optional, List
from decimal import Decimal


class ProdutoComponenteCreate(BaseModel):
    materia_prima_id: Optional[int] = None
    nome: Optional[str] = None  # Para criar MP automaticamente
    quantidade: Decimal
    unidade_codigo: str

    @validator('quantidade')
    def validate_quantidade(cls, v):
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        return v

    @validator('materia_prima_id', 'nome')
    def validate_materia_prima(cls, v, values):
        if not values.get('materia_prima_id') and not values.get('nome'):
            raise ValueError('Deve fornecer materia_prima_id ou nome')
        return v


class ProdutoComponenteResponse(BaseModel):
    id: int
    materia_prima_id: int
    nome: str
    quantidade: Decimal
    unidade_codigo: str
    preco_unitario_atual: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ProdutoPrecoResponse(BaseModel):
    id: int
    custo_total: Decimal
    vigente_desde: str
    vigente_ate: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class ProdutoCreate(BaseModel):
    nome: str
    componentes: List[ProdutoComponenteCreate]


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None


class ProdutoResponse(BaseModel):
    id: int
    nome: str
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None
    
    # Componentes e custos
    componentes: List[ProdutoComponenteResponse] = []
    custo_atual: Optional[Decimal] = None
    historico_precos: List[ProdutoPrecoResponse] = []

    class Config:
        from_attributes = True 