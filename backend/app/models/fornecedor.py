from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime
from app.models.base import Base

class Fornecedor(Base):
    __tablename__ = "fornecedor"

    id_fornecedor: Mapped[int] = mapped_column(primary_key=True, index=True)
    cnpj: Mapped[str] = mapped_column(String(18), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(nullable=False)
    endereco: Mapped[str] = mapped_column(nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default="now()")
    atualizado_em: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=None)

    notas: Mapped[list["Nota"]] = relationship("Nota", back_populates="fornecedor")
    materia_prima_precos: Mapped[list["MateriaPrimaPreco"]] = relationship("MateriaPrimaPreco", back_populates="fornecedor") 
