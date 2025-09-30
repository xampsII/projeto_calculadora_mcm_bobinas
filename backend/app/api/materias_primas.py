from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models.user import User
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.fornecedor import Fornecedor
from app.models.unidade import Unidade
from app.schemas.materia_prima import (
    MateriaPrimaCreate,
    MateriaPrimaUpdate,
    MateriaPrimaPrecoCreate,
    MateriaPrimaResponse,
    MateriaPrimaPrecoResponse
)
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import get_current_active_user, require_editor
from app.utils.audit import log_audit

router = APIRouter(prefix="/materias-primas", tags=["materias-primas"])


@router.get("/public", response_model=List[MateriaPrimaResponse])
async def list_materias_primas_public(
    db: Session = Depends(get_db)
):
    """Lista todas as matérias-primas ativas (endpoint público para frontend)"""
    materias_primas = db.query(MateriaPrima).filter(MateriaPrima.is_active == True).all()
    
    items = []
    for mp in materias_primas:
        # Buscar preço atual diretamente da tabela
        preco_atual = db.query(MateriaPrimaPreco).filter(
            and_(
                MateriaPrimaPreco.materia_prima_id == mp.id,
                MateriaPrimaPreco.vigente_ate.is_(None)
            )
        ).first()
        
        items.append(MateriaPrimaResponse(
            id=mp.id,
            nome=mp.nome,
            unidade_codigo=mp.unidade_codigo,
            menor_unidade_codigo=mp.menor_unidade_codigo,
            is_active=mp.is_active,
            created_at=str(mp.created_at),
            updated_at=str(mp.updated_at) if mp.updated_at else None,
            preco_atual=preco_atual.valor_unitario if preco_atual else None,
            preco_anterior=None,
            variacao_abs=None,
            variacao_pct=None,
            vigente_desde=str(preco_atual.vigente_desde) if preco_atual and preco_atual.vigente_desde else None
        ))
    
    return items


@router.get("/", response_model=PaginatedResponse[MateriaPrimaResponse])
async def list_materias_primas(
    nome: Optional[str] = Query(None, description="Filtrar por nome"),
    unidade_codigo: Optional[str] = Query(None, description="Filtrar por unidade"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db)
):
    """Lista matérias-primas com paginação e filtros"""
    query = db.query(MateriaPrima).filter(MateriaPrima.is_active == True)
    
    if nome:
        query = query.filter(MateriaPrima.nome.ilike(f"%{nome}%"))
    
    if unidade_codigo:
        query = query.filter(MateriaPrima.unidade_codigo == unidade_codigo)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    materias_primas = query.offset(offset).limit(page_size).all()
    
    # Buscar preços atuais e anteriores para cada MP
    items = []
    for mp in materias_primas:
        preco_atual = db.query(MateriaPrimaPreco).filter(
            and_(
                MateriaPrimaPreco.materia_prima_id == mp.id,
                MateriaPrimaPreco.vigente_ate.is_(None)
            )
        ).first()
        
        preco_anterior = None
        variacao_abs = None
        variacao_pct = None
        
        if preco_atual:
            preco_anterior = db.query(MateriaPrimaPreco).filter(
                and_(
                    MateriaPrimaPreco.materia_prima_id == mp.id,
                    MateriaPrimaPreco.vigente_ate.isnot(None)
                )
            ).order_by(MateriaPrimaPreco.vigente_ate.desc()).first()
            
            if preco_anterior:
                variacao_abs = preco_atual.valor_unitario - preco_anterior.valor_unitario
                if preco_anterior.valor_unitario > 0:
                    variacao_pct = (variacao_abs / preco_anterior.valor_unitario) * 100
        
        items.append(MateriaPrimaResponse(
            id=mp.id,
            nome=mp.nome,
            unidade_codigo=mp.unidade_codigo,
            menor_unidade_codigo=mp.menor_unidade_codigo,
            is_active=mp.is_active,
            created_at=str(mp.created_at),
            updated_at=str(mp.updated_at) if mp.updated_at else None,
            preco_atual=preco_atual.valor_unitario if preco_atual else None,
            preco_anterior=preco_anterior.valor_unitario if preco_anterior else None,
            variacao_abs=variacao_abs,
            variacao_pct=variacao_pct,
            vigente_desde=str(preco_atual.vigente_desde) if preco_atual and preco_atual.vigente_desde else None
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{materia_prima_id}", response_model=MateriaPrimaResponse)
async def get_materia_prima(
    materia_prima_id: int,
    db: Session = Depends(get_db)
):
    """Obtém detalhes de uma matéria-prima específica"""
    materia_prima = db.query(MateriaPrima).filter(
        and_(
            MateriaPrima.id == materia_prima_id,
            MateriaPrima.is_active == True
        )
    ).first()
    
    if not materia_prima:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matéria-prima não encontrada"
        )
    
    # Buscar preço atual
    preco_atual = db.query(MateriaPrimaPreco).filter(
        and_(
            MateriaPrimaPreco.materia_prima_id == materia_prima_id,
            MateriaPrimaPreco.vigente_ate.is_(None)
        )
    ).first()
    
    return MateriaPrimaResponse(
        id=materia_prima.id,
        nome=materia_prima.nome,
        unidade_codigo=materia_prima.unidade_codigo,
        menor_unidade_codigo=materia_prima.menor_unidade_codigo,
        is_active=materia_prima.is_active,
            created_at=str(materia_prima.created_at),
            updated_at=str(materia_prima.updated_at) if materia_prima.updated_at else None,
        preco_atual=preco_atual.valor_unitario if preco_atual else None,
        preco_anterior=None,
        variacao_abs=None,
        variacao_pct=None,
            vigente_desde=str(preco_atual.vigente_desde) if preco_atual and preco_atual.vigente_desde else None
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_materia_prima(
    materia_prima_data: MateriaPrimaCreate,
    db: Session = Depends(get_db)
):
    """Cria uma nova matéria-prima"""
    try:
        # Verificar se já existe MP com o mesmo nome
        existing_mp = db.query(MateriaPrima).filter(
            and_(
                MateriaPrima.nome == materia_prima_data.nome,
                MateriaPrima.is_active == True
            )
        ).first()
        
        if existing_mp:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma matéria-prima com este nome"
            )
        
        # Verificar se a unidade existe, se não, criar automaticamente
        unidade = db.query(Unidade).filter(
            Unidade.codigo == materia_prima_data.unidade_codigo
        ).first()
        
        if not unidade:
            # Criar unidade automaticamente
            unidade = Unidade(
                codigo=materia_prima_data.unidade_codigo,
                descricao=materia_prima_data.unidade_codigo.upper(),
                fator_para_menor=1.0,
                menor_unidade_id=None,
                is_base=True
            )
            db.add(unidade)
            db.flush()
        
        # Criar a matéria-prima
        materia_prima = MateriaPrima(
            nome=materia_prima_data.nome,
            unidade_codigo=materia_prima_data.unidade_codigo,
            menor_unidade_codigo=materia_prima_data.menor_unidade_codigo or materia_prima_data.unidade_codigo,
            is_active=True
        )
        
        db.add(materia_prima)
        db.commit()
        db.refresh(materia_prima)
        
        return {
            "success": True,
            "message": "Matéria-prima criada com sucesso!",
            "data": {
                "id": materia_prima.id,
                "nome": materia_prima.nome,
                "unidade_codigo": materia_prima.unidade_codigo,
                "menor_unidade_codigo": materia_prima.menor_unidade_codigo,
                "is_active": materia_prima.is_active,
                "created_at": str(materia_prima.created_at),
                "updated_at": str(materia_prima.updated_at) if materia_prima.updated_at else None,
                "preco_atual": None,
                "preco_anterior": None,
                "variacao_abs": None,
                "variacao_pct": None,
                "vigente_desde": None
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar matéria-prima: {str(e)}"
        )


@router.put("/{materia_prima_id}", response_model=MateriaPrimaResponse)
async def update_materia_prima(
    materia_prima_id: int,
    materia_prima_data: MateriaPrimaUpdate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_editor)  # Removido para simplificar
):
    """Atualiza uma matéria-prima existente"""
    materia_prima = db.query(MateriaPrima).filter(
        and_(
            MateriaPrima.id == materia_prima_id,
            MateriaPrima.is_active == True
        )
    ).first()
    
    if not materia_prima:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matéria-prima não encontrada"
        )
    
    # Verificar se o novo nome já existe em outra MP
    if materia_prima_data.nome and materia_prima_data.nome != materia_prima.nome:
        existing_mp = db.query(MateriaPrima).filter(
            and_(
                MateriaPrima.nome == materia_prima_data.nome,
                MateriaPrima.id != materia_prima_id,
                MateriaPrima.is_active == True
            )
        ).first()
        
        if existing_mp:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe uma matéria-prima com este nome"
            )
    
    # Verificar unidades se especificadas
    if materia_prima_data.unidade_codigo:
        unidade = db.query(Unidade).filter(
            Unidade.codigo == materia_prima_data.unidade_codigo
        ).first()
        
        if not unidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unidade não encontrada"
            )
    
    if materia_prima_data.menor_unidade_codigo:
        menor_unidade = db.query(Unidade).filter(
            Unidade.codigo == materia_prima_data.menor_unidade_codigo
        ).first()
        
        if not menor_unidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Menor unidade não encontrada"
            )
    
    # Capturar mudanças para auditoria
    changes = {}
    if materia_prima_data.nome and materia_prima_data.nome != materia_prima.nome:
        changes["nome"] = {"before": materia_prima.nome, "after": materia_prima_data.nome}
        materia_prima.nome = materia_prima_data.nome
    
    if materia_prima_data.unidade_codigo and materia_prima_data.unidade_codigo != materia_prima.unidade_codigo:
        changes["unidade_codigo"] = {"before": materia_prima.unidade_codigo, "after": materia_prima_data.unidade_codigo}
        materia_prima.unidade_codigo = materia_prima_data.unidade_codigo
    
    if materia_prima_data.menor_unidade_codigo != materia_prima.menor_unidade_codigo:
        changes["menor_unidade_codigo"] = {"before": materia_prima.menor_unidade_codigo, "after": materia_prima_data.menor_unidade_codigo}
        materia_prima.menor_unidade_codigo = materia_prima_data.menor_unidade_codigo
    
    if changes:
        db.commit()
        db.refresh(materia_prima)
        
        # Log de auditoria
        await log_audit(
            db=db,
            user_id=current_user.id,
            entity="materia_prima",
            entity_id=materia_prima.id,
            action="update",
            changes=changes
        )
    
    # Buscar preço atual para resposta
    preco_atual = db.query(MateriaPrimaPreco).filter(
        and_(
            MateriaPrimaPreco.materia_prima_id == materia_prima_id,
            MateriaPrimaPreco.vigente_ate.is_(None)
        )
    ).first()
    
    return MateriaPrimaResponse(
        id=materia_prima.id,
        nome=materia_prima.nome,
        unidade_codigo=materia_prima.unidade_codigo,
        menor_unidade_codigo=materia_prima.menor_unidade_codigo,
        is_active=materia_prima.is_active,
            created_at=str(materia_prima.created_at),
            updated_at=str(materia_prima.updated_at) if materia_prima.updated_at else None,
        preco_atual=preco_atual.valor_unitario if preco_atual else None,
        preco_anterior=None,
        variacao_abs=None,
        variacao_pct=None,
            vigente_desde=str(preco_atual.vigente_desde) if preco_atual and preco_atual.vigente_desde else None
    )


@router.delete("/{materia_prima_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia_prima(
    materia_prima_id: int,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_editor)  # Removido para simplificar
):
    """Soft delete de uma matéria-prima"""
    materia_prima = db.query(MateriaPrima).filter(
        and_(
            MateriaPrima.id == materia_prima_id,
            MateriaPrima.is_active == True
        )
    ).first()
    
    if not materia_prima:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matéria-prima não encontrada"
        )
    
    # Verificar se há produtos que usam esta MP
    from app.models.produto import ProdutoComponente
    produtos_using_mp = db.query(ProdutoComponente).filter(
        ProdutoComponente.materia_prima_id == materia_prima_id
    ).first()
    
    if produtos_using_mp:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir matéria-prima que está sendo usada por produtos"
        )
    
    # Verificar se há notas que referenciam esta MP
    from app.models.nota import NotaItem
    notas_using_mp = db.query(NotaItem).filter(
        NotaItem.materia_prima_id == materia_prima_id
    ).first()
    
    if notas_using_mp:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir matéria-prima que está sendo referenciada por notas"
        )
    
    materia_prima.is_active = False
    db.commit()
    
    # Log de auditoria
    await log_audit(
        db=db,
        user_id=current_user.id,
        entity="materia_prima",
        entity_id=materia_prima.id,
        action="delete",
        changes={"is_active": {"before": True, "after": False}}
    )


@router.post("/{materia_prima_id}/precos", response_model=MateriaPrimaPrecoResponse, status_code=status.HTTP_201_CREATED)
async def create_materia_prima_preco(
    materia_prima_id: int,
    preco_data: MateriaPrimaPrecoCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(require_editor)  # Removido para simplificar
):
    """Cria um novo preço para uma matéria-prima"""
    materia_prima = db.query(MateriaPrima).filter(
        and_(
            MateriaPrima.id == materia_prima_id,
            MateriaPrima.is_active == True
        )
    ).first()
    
    if not materia_prima:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matéria-prima não encontrada"
        )
    
    # Verificar fornecedor se especificado
    fornecedor = None
    if preco_data.fornecedor_id:
        fornecedor = db.query(Fornecedor).filter(
            and_(
                Fornecedor.id == preco_data.fornecedor_id,
                Fornecedor.is_active == True
            )
        ).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fornecedor não encontrado"
            )
    
    # Fechar preço anterior se existir
    preco_anterior = db.query(MateriaPrimaPreco).filter(
        and_(
            MateriaPrimaPreco.materia_prima_id == materia_prima_id,
            MateriaPrimaPreco.vigente_ate.is_(None)
        )
    ).first()
    
    if preco_anterior:
        preco_anterior.vigente_ate = preco_data.vigente_desde
        db.add(preco_anterior)
    
    # Criar novo preço
    novo_preco = MateriaPrimaPreco(
        materia_prima_id=materia_prima_id,
        valor_unitario=preco_data.valor_unitario,
        moeda=preco_data.moeda,
        vigente_desde=preco_data.vigente_desde,
        origem=preco_data.origem,
        fornecedor_id=preco_data.fornecedor_id,
        nota_id=preco_data.nota_id
    )
    
    db.add(novo_preco)
    db.commit()
    db.refresh(novo_preco)
    
    # Log de auditoria
    await log_audit(
        db=db,
        user_id=current_user.id,
        entity="materia_prima_preco",
        entity_id=novo_preco.id,
        action="create",
        changes={
            "valor_unitario": novo_preco.valor_unitario,
            "origem": novo_preco.origem.value,
            "fornecedor_id": novo_preco.fornecedor_id
        }
    )
    
    return MateriaPrimaPrecoResponse(
        id=novo_preco.id,
        materia_prima_id=novo_preco.materia_prima_id,
        valor_unitario=novo_preco.valor_unitario,
        moeda=novo_preco.moeda,
        vigente_desde=novo_preco.vigente_desde,
        vigente_ate=novo_preco.vigente_ate,
        origem=novo_preco.origem,
        fornecedor_id=novo_preco.fornecedor_id,
        nota_id=novo_preco.nota_id,
        created_at=novo_preco.created_at
    ) 