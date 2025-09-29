from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Numeric, ForeignKey, DateTime
from app.models.base import Base

class Unidade(Base):
    __tablename__ = "unidades"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True, index=True, nullable=False)
    descricao: Mapped[str] = mapped_column(nullable=False)
    fator_para_menor: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    menor_unidade_id: Mapped[int | None] = mapped_column(ForeignKey("unidades.id"), nullable=True)
    is_base: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    menor_unidade: Mapped["Unidade"] = relationship("Unidade", remote_side=[id], foreign_keys=[menor_unidade_id])
    materias_primas: Mapped[list["MateriaPrima"]] = relationship("MateriaPrima", foreign_keys="MateriaPrima.unidade_codigo", back_populates="unidade")
    materia_prima_menor: Mapped[list["MateriaPrima"]] = relationship("MateriaPrima", foreign_keys="MateriaPrima.menor_unidade_codigo", back_populates="menor_unidade")
    nota_itens: Mapped[list["NotaItem"]] = relationship("NotaItem", back_populates="unidade")
    produto_componentes: Mapped[list["ProdutoComponente"]] = relationship("ProdutoComponente", back_populates="unidade") 