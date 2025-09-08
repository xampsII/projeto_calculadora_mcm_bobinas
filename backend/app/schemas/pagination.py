from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico para respostas paginadas"""
    items: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int

    class Config:
        from_attributes = True

