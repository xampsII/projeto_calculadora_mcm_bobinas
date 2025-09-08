from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth.dependencies import get_current_active_user
from app.schemas.unidade import UnidadeResponse
from app.models.unidade import Unidade
from app.models.user import User

router = APIRouter(prefix="/unidades", tags=["unidades"])


@router.get("/", response_model=List[UnidadeResponse])
async def list_unidades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista todas as unidades disponíveis"""
    unidades = db.query(Unidade).all()
    return unidades


@router.get("/{unidade_codigo}", response_model=UnidadeResponse)
async def get_unidade(
    unidade_codigo: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém unidade por código"""
    unidade = db.query(Unidade).filter(Unidade.codigo == unidade_codigo).first()
    
    if not unidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada"
        )
    
    return unidade 