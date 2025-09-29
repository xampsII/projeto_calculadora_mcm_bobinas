from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

class ProdutoComponente(BaseModel):
    id: str
    materiaPrimaNome: str
    quantidade: float
    unidadeMedida: str
    valorUnitario: float

class ProdutoFinalBase(BaseModel):
    nome: str
    idUnico: str
    componentes: List[ProdutoComponente]
    ativo: bool = True

class ProdutoFinalCreate(ProdutoFinalBase):
    pass

class ProdutoFinalUpdate(BaseModel):
    nome: Optional[str] = None
    idUnico: Optional[str] = None
    componentes: Optional[List[ProdutoComponente]] = None
    ativo: Optional[bool] = None

class ProdutoFinalResponse(BaseModel):
    id: int
    nome: str
    idUnico: str = Field(alias="id_unico")
    componentes: List[ProdutoComponente]
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class ProdutoFinalCreateResponse(BaseModel):
    success: bool
    message: str
    data: ProdutoFinalResponse



