from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Fornecedor, User
from app.schemas import FornecedorCreate, FornecedorUpdate, FornecedorResponse
from app.auth.dependencies import require_editor

fornecedores_router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

@fornecedores_router.post("/", response_model=FornecedorResponse, status_code=status.HTTP_201_CREATED)
async def criar_fornecedor(
    fornecedor: FornecedorCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Criar novo fornecedor"""
    try:
        # Verificar se CNPJ já existe
        if fornecedor.cnpj:
            db_fornecedor = db.query(Fornecedor).filter(Fornecedor.cnpj == fornecedor.cnpj).first()
            if db_fornecedor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CNPJ já cadastrado"
                )
        
        # Criar fornecedor
        db_fornecedor = Fornecedor(
            nome=fornecedor.nome,
            cnpj=fornecedor.cnpj,
            email=fornecedor.email,
            telefone=fornecedor.telefone,
            endereco=fornecedor.endereco,
            cidade=fornecedor.cidade,
            estado=fornecedor.estado,
            cep=fornecedor.cep,
            ativo=True
        )
        
        db.add(db_fornecedor)
        db.commit()
        db.refresh(db_fornecedor)
        
        return db_fornecedor
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar fornecedor: {str(e)}"
        )

@fornecedores_router.get("/", response_model=List[FornecedorResponse])
async def listar_fornecedores(
    skip: int = 0, 
    limit: int = 100, 
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    """Listar fornecedores"""
    query = db.query(Fornecedor)
    if ativo is not None:
        query = query.filter(Fornecedor.ativo == ativo)
    
    fornecedores = query.offset(skip).limit(limit).all()
    return fornecedores

@fornecedores_router.get("/{fornecedor_id}", response_model=FornecedorResponse)
async def buscar_fornecedor(
    fornecedor_id: int, 
    db: Session = Depends(get_db)
):
    """Buscar fornecedor por ID"""
    fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    return fornecedor

@fornecedores_router.put("/{fornecedor_id}", response_model=FornecedorResponse)
async def atualizar_fornecedor(
    fornecedor_id: int,
    fornecedor: FornecedorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Atualizar fornecedor"""
    db_fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not db_fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    try:
        # Atualizar campos
        if fornecedor.nome:
            db_fornecedor.nome = fornecedor.nome
        if fornecedor.cnpj:
            db_fornecedor.cnpj = fornecedor.cnpj
        if fornecedor.email:
            db_fornecedor.email = fornecedor.email
        if fornecedor.telefone:
            db_fornecedor.telefone = fornecedor.telefone
        if fornecedor.endereco:
            db_fornecedor.endereco = fornecedor.endereco
        if fornecedor.cidade:
            db_fornecedor.cidade = fornecedor.cidade
        if fornecedor.estado:
            db_fornecedor.estado = fornecedor.estado
        if fornecedor.cep:
            db_fornecedor.cep = fornecedor.cep
        if fornecedor.ativo is not None:
            db_fornecedor.ativo = fornecedor.ativo
        
        db.commit()
        db.refresh(db_fornecedor)
        return db_fornecedor
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar fornecedor: {str(e)}"
        )

@fornecedores_router.delete("/{fornecedor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Deletar fornecedor (soft delete)"""
    db_fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
    if not db_fornecedor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado"
        )
    
    try:
        # Soft delete
        db_fornecedor.ativo = False
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar fornecedor: {str(e)}"
        ) 