from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean, Numeric, Date
from app.models.base import Base
from app.models.enums import StatusNota
from typing import Optional, List
from datetime import datetime
from sqlalchemy import func

class Nota(Base):
    __tablename__ = "notas"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    numero: Mapped[str] = mapped_column(String(50), nullable=False)
    serie: Mapped[str] = mapped_column(nullable=True)
    chave_acesso: Mapped[Optional[str]] = mapped_column(String(44), unique=True, nullable=True)
    fornecedor_id: Mapped[int | None] = mapped_column(ForeignKey("fornecedor.id_fornecedor"), nullable=True)
    emissao_date: Mapped[Date] = mapped_column(Date, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    arquivo_xml_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    arquivo_pdf_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String(32), unique=True, nullable=True)
    status: Mapped[StatusNota] = mapped_column(nullable=False, default=StatusNota.rascunho)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    fornecedor: Mapped["Fornecedor"] = relationship("Fornecedor", back_populates="notas")
    itens: Mapped[List["NotaItem"]] = relationship("NotaItem", back_populates="nota", cascade="all, delete-orphan")
    materia_prima_precos: Mapped[List["MateriaPrimaPreco"]] = relationship("MateriaPrimaPreco", back_populates="nota")


class NotaItem(Base):
    __tablename__ = "nota_itens"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nota_id: Mapped[int] = mapped_column(ForeignKey("notas.id"), nullable=False)
    materia_prima_id: Mapped[int | None] = mapped_column(ForeignKey("materias_primas.id"), nullable=True)
    nome_no_documento: Mapped[str] = mapped_column(nullable=False)
    unidade_codigo: Mapped[str] = mapped_column(String(10), ForeignKey("unidades.codigo"), nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    valor_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Relationships
    nota: Mapped["Nota"] = relationship("Nota", back_populates="itens")
    materia_prima: Mapped[Optional["MateriaPrima"]] = relationship("MateriaPrima", back_populates="nota_itens")
    unidade: Mapped["Unidade"] = relationship("Unidade", back_populates="nota_itens") 