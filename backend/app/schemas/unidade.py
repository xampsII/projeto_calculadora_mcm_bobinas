from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class UnidadeResponse(BaseModel):
    id: int
    codigo: str
    descricao: str
    fator_para_menor: Optional[Decimal] = None
    menor_unidade_codigo: Optional[str] = None
    is_base: bool

    class Config:
        from_attributes = True 