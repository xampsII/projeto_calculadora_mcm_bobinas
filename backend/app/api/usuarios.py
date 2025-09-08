from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.auth.dependencies import require_admin

usuarios_router = APIRouter(prefix="/usuarios", tags=["Usuários"])

@usuarios_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def criar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    """Criar novo usuário"""
    try:
        # Verificar se email já existe
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado"
            )
        
        # Criar usuário
        db_user = User(
            nome=user.nome,
            email=user.email,
            role=user.role,
            ativo=True
        )
        db_user.set_password(user.senha)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

@usuarios_router.get("/", response_model=List[UserResponse])
async def listar_usuarios(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Listar todos os usuários (apenas admin)"""
    usuarios = db.query(User).offset(skip).limit(limit).all()
    return usuarios

@usuarios_router.get("/{usuario_id}", response_model=UserResponse)
async def buscar_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Buscar usuário por ID (apenas admin)"""
    usuario = db.query(User).filter(User.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    return usuario

@usuarios_router.put("/{usuario_id}", response_model=UserResponse)
async def atualizar_usuario(
    usuario_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Atualizar usuário (apenas admin)"""
    db_user = db.query(User).filter(User.id == usuario_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    try:
        # Atualizar campos
        if user.nome:
            db_user.nome = user.nome
        if user.email:
            db_user.email = user.email
        if user.role:
            db_user.role = user.role
        if user.ativo is not None:
            db_user.ativo = user.ativo
        
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )

@usuarios_router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Deletar usuário (soft delete, apenas admin)"""
    db_user = db.query(User).filter(User.id == usuario_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    try:
        # Soft delete
        db_user.ativo = False
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar usuário: {str(e)}"
        ) 