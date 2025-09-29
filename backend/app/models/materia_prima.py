from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Float, DateTime, ForeignKey, Numeric
from app.models.base import Base
from typing import Optional


class MateriaPrima(Base):
    __tablename__ = "materias_primas"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    unidade_codigo: Mapped[str] = mapped_column(String(10), ForeignKey("unidades.codigo"), nullable=False)
    menor_unidade_codigo: Mapped[Optional[str]] = mapped_column(String(10), ForeignKey("unidades.codigo"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), onupdate=None, nullable=True)
    
    # Relationships
    unidade: Mapped["Unidade"] = relationship("Unidade", foreign_keys=[unidade_codigo], back_populates="materias_primas")
    menor_unidade: Mapped[Optional["Unidade"]] = relationship("Unidade", foreign_keys=[menor_unidade_codigo], back_populates="materia_prima_menor")
    precos: Mapped[list["MateriaPrimaPreco"]] = relationship("MateriaPrimaPreco", back_populates="materia_prima", order_by="MateriaPrimaPreco.vigente_desde.desc()")
    nota_itens: Mapped[list["NotaItem"]] = relationship("NotaItem", back_populates="materia_prima")
    produto_componentes: Mapped[list["ProdutoComponente"]] = relationship("ProdutoComponente", back_populates="materia_prima")


class MateriaPrimaPreco(Base):
    __tablename__ = "materia_prima_precos"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    materia_prima_id: Mapped[int] = mapped_column(ForeignKey("materias_primas.id"), nullable=False)
    valor_unitario: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    moeda: Mapped[str] = mapped_column(String(3), default="BRL", nullable=False)
    vigente_desde: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    vigente_ate: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # null = preço atual
    # origem = Column(
    #     ENUM(OrigemPreco, name='origempreco', create_type=False),
    #     nullable=False,
    #     server_default=OrigemPreco.manual.value
    # )
    fornecedor_id: Mapped[int | None] = mapped_column(ForeignKey("fornecedor.id_fornecedor"), nullable=True)
    nota_id: Mapped[int | None] = mapped_column(ForeignKey("notas.id"), nullable=True)
    # observacao: Mapped[str | None] = mapped_column(String(500), nullable=True)  # Coluna não existe no banco
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")
    
    # Relationships
    materia_prima: Mapped["MateriaPrima"] = relationship("MateriaPrima", back_populates="precos")
    fornecedor: Mapped["Fornecedor"] = relationship("Fornecedor", back_populates="materia_prima_precos")
    nota: Mapped["Nota"] = relationship("Nota", back_populates="materia_prima_precos") 