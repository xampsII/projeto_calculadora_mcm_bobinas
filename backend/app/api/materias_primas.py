from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database import get_db
from app.models.user import User
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.fornecedor import Fornecedor
from app.models.nota import Nota
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
import logging

logger = logging.getLogger(__name__)

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
        db.flush()  # Para obter o ID
        
        # Se foi fornecido um preço inicial, registrar no histórico
        preco_atual = None
        if hasattr(materia_prima_data, 'preco_inicial') and materia_prima_data.preco_inicial and materia_prima_data.preco_inicial > 0:
            from datetime import datetime
            preco_inicial = MateriaPrimaPreco(
                materia_prima_id=materia_prima.id,
                valor_unitario=materia_prima_data.preco_inicial,
                moeda="BRL",
                vigente_desde=datetime.now(),
                vigente_ate=None,  # Preço atual
                fornecedor_id=None,  # Preço manual
                nota_id=None
            )
            db.add(preco_inicial)
            preco_atual = materia_prima_data.preco_inicial
        
        db.commit()
        db.refresh(materia_prima)
        
        return {
            "success": True,
            "message": "Matéria-prima criada com sucesso!" + (" Preço inicial registrado." if preco_atual else ""),
            "data": {
                "id": materia_prima.id,
                "nome": materia_prima.nome,
                "unidade_codigo": materia_prima.unidade_codigo,
                "menor_unidade_codigo": materia_prima.menor_unidade_codigo,
                "is_active": materia_prima.is_active,
                "created_at": str(materia_prima.created_at),
                "updated_at": str(materia_prima.updated_at) if materia_prima.updated_at else None,
                "preco_atual": preco_atual,
                "preco_anterior": None,
                "variacao_abs": None,
                "variacao_pct": None,
                "vigente_desde": str(datetime.now()) if preco_atual else None
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
        log_audit(
            db=db,
            user=None,  # sem controle de usuário no momento
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

@router.delete("/{materia_prima_id}")
async def delete_materia_prima(
    materia_prima_id: int,
    db: Session = Depends(get_db),
):
    """
    Exclui (soft delete) uma matéria-prima, verificando se não está sendo usada
    em produtos, produtos finais ou notas fiscais.
    """
    try:
        # Verifica se a MP existe
        materia_prima = (
            db.query(MateriaPrima)
            .filter(MateriaPrima.id == materia_prima_id, MateriaPrima.is_active == True)
            .first()
        )
        if not materia_prima:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Matéria-prima não encontrada."
            )

        # Verifica se há vínculos em produtos tradicionais
        from app.models.produto import ProdutoComponente
        produtos_using_mp = (
            db.query(ProdutoComponente)
            .filter(ProdutoComponente.materia_prima_id == materia_prima_id)
            .first()
        )
        if produtos_using_mp:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não é possível excluir:materia prima vinculada a produtos."
            )

        # Verifica se há vínculos em notas fiscais
        from app.models.nota import NotaItem
        notas_using_mp = (
            db.query(NotaItem)
            .filter(NotaItem.materia_prima_id == materia_prima_id)
            .first()
        )
        if notas_using_mp:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não é possível excluir: matéria-prima referenciada em notas fiscais."
            )

        # Verifica se está em uso no JSON de produtos finais
        from app.models.produto_final import ProdutoFinal
        produtos_finais = db.query(ProdutoFinal).filter(ProdutoFinal.ativo == True).all()

        usados_em = []
        for produto in produtos_finais:
            if not produto.componentes:
                continue
            try:
                for comp in produto.componentes:
                    # comp é um dicionário JSON: {"id": <materia_prima_id>, "quantidade": ..., ...}
                    if isinstance(comp, dict) and comp.get("id") == materia_prima_id:
                        usados_em.append(produto.nome)
                        break
            except Exception:
                continue

        if usados_em:
            nomes = ", ".join(usados_em)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Não é possível excluir: esta matéria-prima é utilizada nos produtos finais ({nomes})."
            )
        from datetime import datetime
        materia_prima.is_active = False
        materia_prima.updated_at = datetime.now()
        db.commit()

        # Log de auditoria
        log_audit(
            db=db,
            user=None,  # sem controle de usuário no momento
            entity="materia_prima",
            entity_id=materia_prima.id,
            action="delete",
            changes={"is_active": {"before": True, "after": False}}
        )

        return {
            "success": True,
            "message": "Matéria-prima excluída com sucesso."
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir matéria-prima: {str(e)}"
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
                Fornecedor.id_fornecedor == preco_data.fornecedor_id,
                Fornecedor.ativo == True
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
    log_audit(
        db=db,
        user=None,  # sem controle de usuário no momento
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


@router.get("/historico-precos/todos")
async def get_historico_precos_todas_materias(
    db: Session = Depends(get_db)
):
    """Retorna o histórico completo de preços de todas as matérias-primas"""
    try:
        # Buscar todas as matérias-primas ativas
        materias_primas = db.query(MateriaPrima).filter(
            MateriaPrima.is_active == True
        ).order_by(MateriaPrima.nome).all()
        
        resultado = []
        
        for mp in materias_primas:
            # Buscar histórico de preços ordenado por data (mais recente primeiro)
            precos = db.query(MateriaPrimaPreco).filter(
                MateriaPrimaPreco.materia_prima_id == mp.id
            ).order_by(MateriaPrimaPreco.vigente_desde.desc()).all()
            
            if precos:  # Só adiciona se tiver histórico
                historico = []
                preco_anterior = None
                
                for i, preco in enumerate(precos):
                    # Calcular variação percentual
                    variacao_percentual = None
                    if preco_anterior:
                        if preco_anterior.valor_unitario > 0:
                            variacao = ((preco.valor_unitario - preco_anterior.valor_unitario) / preco_anterior.valor_unitario) * 100
                            variacao_percentual = round(variacao, 2)
                    
                    # Buscar fornecedor e nota relacionados
                    fornecedor_nome = "N/A"
                    if preco.fornecedor_id:
                        fornecedor = db.query(Fornecedor).filter(Fornecedor.id_fornecedor == preco.fornecedor_id).first()
                        if fornecedor:
                            fornecedor_nome = fornecedor.nome
                    
                    nota_numero = "N/A"
                    nota_serie = "N/A"
                    if preco.nota_id:
                        nota = db.query(Nota).filter(Nota.id == preco.nota_id).first()
                        if nota:
                            nota_numero = nota.numero or f"NF-{nota.id}"
                            nota_serie = nota.serie or "1"
                    
                    historico.append({
                        "id": preco.id,
                        "valor_unitario": float(preco.valor_unitario),
                        "vigente_desde": preco.vigente_desde.isoformat() if preco.vigente_desde else None,
                        "vigente_ate": preco.vigente_ate.isoformat() if preco.vigente_ate else None,
                        "variacao_percentual": variacao_percentual,
                        "origem": "nota_fiscal",
                        "fornecedor": {
                            "id": preco.fornecedor_id or 0,
                            "nome": fornecedor_nome
                        },
                        "nota": {
                            "id": preco.nota_id or 0,
                            "numero": nota_numero,
                            "serie": nota_serie
                        },
                        "created_at": preco.created_at.isoformat() if preco.created_at else None
                    })
                    
                    preco_anterior = preco
                
                resultado.append({
                    "materia_prima": {
                        "id": mp.id,
                        "nome": mp.nome,
                        "unidade": mp.unidade_codigo
                    },
                    "historico": historico,
                    "total_precos": len(historico)
                })
        
        return {
            "materias_primas": resultado,
            "total_materias_com_historico": len(resultado)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de preços: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar histórico de preços: {str(e)}"
        )


@router.get("/{materia_prima_id}/historico-precos")
async def get_historico_precos_materia_prima(
    materia_prima_id: int,
    db: Session = Depends(get_db)
):
    """Retorna o histórico completo de preços de uma matéria-prima"""
    try:
        # Verificar se a matéria-prima existe
        materia_prima = db.query(MateriaPrima).filter(
            MateriaPrima.id == materia_prima_id
        ).first()
        
        if not materia_prima:
            return {
                "materia_prima": {
                    "id": materia_prima_id,
                    "nome": "Matéria-prima não encontrada",
                    "unidade": "N/A"
                },
                "historico": [],
                "total_precos": 0
            }
        
        # Buscar histórico de preços ordenado por data (mais recente primeiro)
        precos = db.query(MateriaPrimaPreco).filter(
            MateriaPrimaPreco.materia_prima_id == materia_prima_id
        ).order_by(MateriaPrimaPreco.vigente_desde.desc()).all()
        
        historico = []
        preco_anterior = None
        
        for i, preco in enumerate(precos):
            # Calcular variação percentual
            variacao_percentual = None
            if preco_anterior:
                if preco_anterior.valor_unitario > 0:
                    variacao = ((preco.valor_unitario - preco_anterior.valor_unitario) / preco_anterior.valor_unitario) * 100
                    variacao_percentual = round(variacao, 2)
            
            historico.append({
                "id": preco.id,
                "valor_unitario": float(preco.valor_unitario),
                "vigente_desde": preco.vigente_desde.isoformat() if preco.vigente_desde else None,
                "vigente_ate": preco.vigente_ate.isoformat() if preco.vigente_ate else None,
                "variacao_percentual": variacao_percentual,
                "origem": "nota_fiscal",  # Simplificado para o frontend
                "fornecedor": {
                    "id": preco.fornecedor_id or 0,
                    "nome": "Fornecedor Padrão"  # Simplificado
                },
                "nota": {
                    "id": preco.nota_id or 0,
                    "numero": f"NF-{preco.nota_id}" if preco.nota_id else "N/A",
                    "serie": "1"
                },
                "created_at": preco.created_at.isoformat() if preco.created_at else None
            })
            
            preco_anterior = preco
        
        return {
            "materia_prima": {
                "id": materia_prima.id,
                "nome": materia_prima.nome,
                "unidade": materia_prima.unidade_codigo
            },
            "historico": historico,
            "total_precos": len(historico)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico de preços: {e}")
        return {
            "materia_prima": {
                "id": materia_prima_id,
                "nome": "Erro ao carregar",
                "unidade": "N/A"
            },
            "historico": [],
            "total_precos": 0
        } 