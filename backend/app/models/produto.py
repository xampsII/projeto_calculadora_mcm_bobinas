from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Float, DateTime, ForeignKey
from app.models.base import Base

class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String, unique=True, index=True)
    nome: Mapped[str] = mapped_column(nullable=False)
    descricao: Mapped[str] = mapped_column(nullable=True)
    categoria: Mapped[str] = mapped_column(nullable=True)
    unidade_medida: Mapped[str] = mapped_column(nullable=True)
    preco_custo: Mapped[float] = mapped_column(Float, nullable=True)
    preco_venda: Mapped[float] = mapped_column(Float, nullable=True)
    estoque_minimo: Mapped[float] = mapped_column(Float, nullable=True)
    estoque_atual: Mapped[float] = mapped_column(Float, nullable=True)
    fornecedor_id: Mapped[int | None] = mapped_column(ForeignKey("fornecedor.id_fornecedor"), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=None)

    componentes: Mapped[list["ProdutoComponente"]] = relationship("ProdutoComponente", back_populates="produto", cascade="all, delete-orphan")
    precos: Mapped[list["ProdutoPreco"]] = relationship("ProdutoPreco", back_populates="produto", order_by="ProdutoPreco.vigente_desde.desc()")

class ProdutoComponente(Base):
    __tablename__ = "produto_componentes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    materia_prima_id: Mapped[int] = mapped_column(ForeignKey("materias_primas.id"), nullable=False)
    quantidade: Mapped[float] = mapped_column(Float, nullable=False)
    unidade_codigo: Mapped[str] = mapped_column(String(10), ForeignKey("unidades.codigo"), nullable=False)

    produto: Mapped["Produto"] = relationship("Produto", back_populates="componentes")
    materia_prima: Mapped["MateriaPrima"] = relationship("MateriaPrima", back_populates="produto_componentes")
    unidade: Mapped["Unidade"] = relationship("Unidade", back_populates="produto_componentes")

class ProdutoPreco(Base):
    __tablename__ = "produto_precos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)
    custo_total: Mapped[float] = mapped_column(Float, nullable=False)
    vigente_desde: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    vigente_ate: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    observacao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")

    produto: Mapped["Produto"] = relationship("Produto", back_populates="precos") 