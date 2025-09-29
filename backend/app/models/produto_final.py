from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.models.base import Base

class ProdutoFinal(Base):
    __tablename__ = "produtos_finais"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    id_unico = Column(String(100), unique=True, index=True, nullable=False)
    componentes = Column(JSON, nullable=False)  # Lista de componentes
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
