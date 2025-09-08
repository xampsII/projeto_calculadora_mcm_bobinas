from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import require_admin, get_current_active_user
from app.auth.jwt import get_password_hash
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User
from app.utils.audit import log_audit, AuditAction

router = APIRouter(prefix="/users", tags=["usuários"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Lista todos os usuários (apenas admin)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Cria novo usuário (apenas admin)"""
    # Verifica se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado"
        )
    
    # Cria hash da senha
    hashed_password = get_password_hash(user_data.password)
    
    # Cria usuário
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Registra auditoria
    log_audit(
        db=db,
        user=current_user,
        entity="users",
        entity_id=db_user.id,
        action=AuditAction.create,
        changes={"after": {"name": user_data.name, "email": user_data.email, "role": user_data.role}}
    )
    
    return db_user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Obtém informações do usuário atual"""
    return current_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Atualiza usuário (apenas admin)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Captura valores antes da mudança para auditoria
    before_changes = {
        "name": db_user.name,
        "email": db_user.email,
        "is_active": db_user.is_active
    }
    
    # Atualiza campos
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    # Registra auditoria
    after_changes = {
        "name": db_user.name,
        "email": db_user.email,
        "is_active": db_user.is_active
    }
    
    log_audit(
        db=db,
        user=current_user,
        entity="users",
        entity_id=user_id,
        action=AuditAction.update,
        changes={"before": before_changes, "after": after_changes}
    )
    
    return db_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Desativa usuário (soft delete, apenas admin)"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível desativar o próprio usuário"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Soft delete
    db_user.is_active = False
    db.commit()
    
    # Registra auditoria
    log_audit(
        db=db,
        user=current_user,
        entity="users",
        entity_id=user_id,
        action=AuditAction.delete,
        changes={"before": {"is_active": True}, "after": {"is_active": False}}
    )
    
    return {"message": "Usuário desativado com sucesso"} 