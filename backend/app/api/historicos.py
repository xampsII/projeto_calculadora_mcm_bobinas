from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, date

from app.database import get_db
from app.models.user import User
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.produto import Produto, ProdutoPreco
from app.models.fornecedor import Fornecedor
from app.schemas.common import PaginatedResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/historicos", tags=["historicos"])


@router.get("/materias-primas")
async def get_historico_materias_primas(
    nome: Optional[str] = Query(None, description="Filtrar por nome da matéria-prima"),
    fornecedor: Optional[str] = Query(None, description="Filtrar por fornecedor"),
    periodo_ini: Optional[date] = Query(None, description="Data inicial"),
    periodo_fim: Optional[date] = Query(None, description="Data final"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém histórico de preços de matérias-primas"""
    query = db.query(MateriaPrimaPreco).join(MateriaPrima)
    
    if nome:
        query = query.filter(MateriaPrima.nome.ilike(f"%{nome}%"))
    
    if fornecedor:
        query = query.join(Fornecedor).filter(
            or_(
                Fornecedor.nome.ilike(f"%{fornecedor}%"),
                Fornecedor.cnpj.ilike(f"%{fornecedor}%")
            )
        )
    
    if periodo_ini:
        query = query.filter(MateriaPrimaPreco.vigente_desde >= periodo_ini)
    
    if periodo_fim:
        query = query.filter(MateriaPrimaPreco.vigente_desde <= periodo_fim)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    precos = query.order_by(desc(MateriaPrimaPreco.vigente_desde)).offset(offset).limit(page_size).all()
    
    # Agrupar por matéria-prima para criar timeline
    timeline = {}
    for preco in precos:
        mp_id = preco.materia_prima_id
        if mp_id not in timeline:
            timeline[mp_id] = {
                "materia_prima": {
                    "id": preco.materia_prima.id,
                    "nome": preco.materia_prima.nome,
                    "unidade_codigo": preco.materia_prima.unidade_codigo
                },
                "precos": []
            }
        
        # Buscar informações do fornecedor
        fornecedor_info = None
        if preco.fornecedor_id:
            fornecedor_obj = db.query(Fornecedor).filter(Fornecedor.id == preco.fornecedor_id).first()
            if fornecedor_obj:
                fornecedor_info = {
                    "id": fornecedor_obj.id,
                    "nome": fornecedor_obj.nome,
                    "cnpj": fornecedor_obj.cnpj
                }
        
        timeline[mp_id]["precos"].append({
            "id": preco.id,
            "valor_unitario": float(preco.valor_unitario),
            "moeda": preco.moeda,
            "vigente_desde": preco.vigente_desde,
            "vigente_ate": preco.vigente_ate,
            "origem": preco.origem.value,
            "fornecedor": fornecedor_info,
            "nota_id": preco.nota_id,
            "created_at": preco.created_at
        })
    
    # Calcular variações para cada matéria-prima
    for mp_data in timeline.values():
        precos_ordenados = sorted(mp_data["precos"], key=lambda x: x["vigente_desde"], reverse=True)
        
        for i, preco in enumerate(precos_ordenados):
            if i < len(precos_ordenados) - 1:
                preco_anterior = precos_ordenados[i + 1]
                variacao_abs = preco["valor_unitario"] - preco_anterior["valor_unitario"]
                variacao_pct = (variacao_abs / preco_anterior["valor_unitario"]) * 100 if preco_anterior["valor_unitario"] > 0 else 0
                
                preco["variacao_abs"] = variacao_abs
                preco["variacao_pct"] = variacao_pct
            else:
                preco["variacao_abs"] = None
                preco["variacao_pct"] = None
    
    items = list(timeline.values())
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/materias-primas/{materia_prima_id}")
async def get_historico_materia_prima(
    materia_prima_id: int,
    periodo_ini: Optional[date] = Query(None, description="Data inicial"),
    periodo_fim: Optional[date] = Query(None, description="Data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém histórico detalhado de uma matéria-prima específica"""
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
    
    query = db.query(MateriaPrimaPreco).filter(
        MateriaPrimaPreco.materia_prima_id == materia_prima_id
    )
    
    if periodo_ini:
        query = query.filter(MateriaPrimaPreco.vigente_desde >= periodo_ini)
    
    if periodo_fim:
        query = query.filter(MateriaPrimaPreco.vigente_desde <= periodo_fim)
    
    precos = query.order_by(desc(MateriaPrimaPreco.vigente_desde)).all()
    
    # Buscar informações do fornecedor para cada preço
    historico = []
    for preco in precos:
        fornecedor_info = None
        if preco.fornecedor_id:
            fornecedor = db.query(Fornecedor).filter(Fornecedor.id == preco.fornecedor_id).first()
            if fornecedor:
                fornecedor_info = {
                    "id": fornecedor.id,
                    "nome": fornecedor.nome,
                    "cnpj": fornecedor.cnpj
                }
        
        historico.append({
            "id": preco.id,
            "valor_unitario": float(preco.valor_unitario),
            "moeda": preco.moeda,
            "vigente_desde": preco.vigente_desde,
            "vigente_ate": preco.vigente_ate,
            "origem": preco.origem.value,
            "fornecedor": fornecedor_info,
            "nota_id": preco.nota_id,
            "created_at": preco.created_at
        })
    
    # Calcular variações
    for i, preco in enumerate(historico):
        if i < len(historico) - 1:
            preco_anterior = historico[i + 1]
            variacao_abs = preco["valor_unitario"] - preco_anterior["valor_unitario"]
            variacao_pct = (variacao_abs / preco_anterior["valor_unitario"]) * 100 if preco_anterior["valor_unitario"] > 0 else 0
            
            preco["variacao_abs"] = variacao_abs
            preco["variacao_pct"] = variacao_pct
        else:
            preco["variacao_abs"] = None
            preco["variacao_pct"] = None
    
    return {
        "materia_prima": {
            "id": materia_prima.id,
            "nome": materia_prima.nome,
            "unidade_codigo": materia_prima.unidade_codigo,
            "menor_unidade_codigo": materia_prima.menor_unidade_codigo
        },
        "historico": historico,
        "total_registros": len(historico)
    }


@router.get("/produtos")
async def get_historico_produtos(
    nome: Optional[str] = Query(None, description="Filtrar por nome do produto"),
    periodo_ini: Optional[date] = Query(None, description="Data inicial"),
    periodo_fim: Optional[date] = Query(None, description="Data final"),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém histórico de custos de produtos"""
    query = db.query(ProdutoPreco).join(Produto)
    
    if nome:
        query = query.filter(Produto.nome.ilike(f"%{nome}%"))
    
    if periodo_ini:
        query = query.filter(ProdutoPreco.vigente_desde >= periodo_ini)
    
    if periodo_fim:
        query = query.filter(ProdutoPreco.vigente_desde <= periodo_fim)
    
    total = query.count()
    offset = (page - 1) * page_size
    
    precos = query.order_by(desc(ProdutoPreco.vigente_desde)).offset(offset).limit(page_size).all()
    
    # Agrupar por produto para criar timeline
    timeline = {}
    for preco in precos:
        produto_id = preco.produto_id
        if produto_id not in timeline:
            timeline[produto_id] = {
                "produto": {
                    "id": preco.produto.id,
                    "nome": preco.produto.nome
                },
                "custos": []
            }
        
        timeline[produto_id]["custos"].append({
            "id": preco.id,
            "custo_total": float(preco.custo_total),
            "vigente_desde": preco.vigente_desde,
            "vigente_ate": preco.vigente_ate,
            "created_at": preco.created_at
        })
    
    # Calcular variações para cada produto
    for produto_data in timeline.values():
        custos_ordenados = sorted(produto_data["custos"], key=lambda x: x["vigente_desde"], reverse=True)
        
        for i, custo in enumerate(custos_ordenados):
            if i < len(custos_ordenados) - 1:
                custo_anterior = custos_ordenados[i + 1]
                variacao_abs = custo["custo_total"] - custo_anterior["custo_total"]
                variacao_pct = (variacao_abs / custo_anterior["custo_total"]) * 100 if custo_anterior["custo_total"] > 0 else 0
                
                custo["variacao_abs"] = variacao_abs
                custo["variacao_pct"] = variacao_pct
            else:
                custo["variacao_abs"] = None
                custo["variacao_pct"] = None
    
    items = list(timeline.values())
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/produtos/{produto_id}")
async def get_historico_produto(
    produto_id: int,
    periodo_ini: Optional[date] = Query(None, description="Data inicial"),
    periodo_fim: Optional[date] = Query(None, description="Data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém histórico detalhado de um produto específico"""
    produto = db.query(Produto).filter(
        and_(
            Produto.id == produto_id,
            Produto.is_active == True
        )
    ).first()
    
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    query = db.query(ProdutoPreco).filter(ProdutoPreco.produto_id == produto_id)
    
    if periodo_ini:
        query = query.filter(ProdutoPreco.vigente_desde >= periodo_ini)
    
    if periodo_fim:
        query = query.filter(ProdutoPreco.vigente_desde <= periodo_fim)
    
    precos = query.order_by(desc(ProdutoPreco.vigente_desde)).all()
    
    historico = []
    for preco in precos:
        historico.append({
            "id": preco.id,
            "custo_total": float(preco.custo_total),
            "vigente_desde": preco.vigente_desde,
            "vigente_ate": preco.vigente_ate,
            "created_at": preco.created_at
        })
    
    # Calcular variações
    for i, preco in enumerate(historico):
        if i < len(historico) - 1:
            preco_anterior = historico[i + 1]
            variacao_abs = preco["custo_total"] - preco_anterior["custo_total"]
            variacao_pct = (variacao_abs / preco_anterior["custo_total"]) * 100 if preco_anterior["custo_total"] > 0 else 0
            
            preco["variacao_abs"] = variacao_abs
            preco["variacao_pct"] = variacao_pct
        else:
            preco["variacao_abs"] = None
            preco["variacao_pct"] = None
    
    return {
        "produto": {
            "id": produto.id,
            "nome": produto.nome
        },
        "historico": historico,
        "total_registros": len(historico)
    }


@router.get("/resumo")
async def get_resumo_historicos(
    periodo_ini: Optional[date] = Query(None, description="Data inicial"),
    periodo_fim: Optional[date] = Query(None, description="Data final"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém resumo dos históricos de preços e custos"""
    # Estatísticas de matérias-primas
    query_mp = db.query(MateriaPrimaPreco)
    if periodo_ini:
        query_mp = query_mp.filter(MateriaPrimaPreco.vigente_desde >= periodo_ini)
    if periodo_fim:
        query_mp = query_mp.filter(MateriaPrimaPreco.vigente_desde <= periodo_fim)
    
    total_precos_mp = query_mp.count()
    variacao_media_mp = db.query(
        func.avg(
            func.abs(
                func.coalesce(
                    func.lag(MateriaPrimaPreco.valor_unitario).over(
                        partition_by=MateriaPrimaPreco.materia_prima_id,
                        order_by=MateriaPrimaPreco.vigente_desde
                    ) - MateriaPrimaPreco.valor_unitario,
                    0
                )
            )
        )
    ).scalar()
    
    # Estatísticas de produtos
    query_prod = db.query(ProdutoPreco)
    if periodo_ini:
        query_prod = query_prod.filter(ProdutoPreco.vigente_desde >= periodo_ini)
    if periodo_fim:
        query_prod = query_prod.filter(ProdutoPreco.vigente_desde <= periodo_fim)
    
    total_custos_prod = query_prod.count()
    variacao_media_prod = db.query(
        func.avg(
            func.abs(
                func.coalesce(
                    func.lag(ProdutoPreco.custo_total).over(
                        partition_by=ProdutoPreco.produto_id,
                        order_by=ProdutoPreco.vigente_desde
                    ) - ProdutoPreco.custo_total,
                    0
                )
            )
        )
    ).scalar()
    
    # Top 5 matérias-primas com mais variações
    top_mp_variacoes = db.query(
        MateriaPrima.nome,
        func.count(MateriaPrimaPreco.id).label('total_precos')
    ).join(MateriaPrimaPreco).group_by(MateriaPrima.id, MateriaPrima.nome).order_by(
        func.count(MateriaPrimaPreco.id).desc()
    ).limit(5).all()
    
    # Top 5 produtos com mais variações
    top_prod_variacoes = db.query(
        Produto.nome,
        func.count(ProdutoPreco.id).label('total_custos')
    ).join(ProdutoPreco).group_by(Produto.id, Produto.nome).order_by(
        func.count(ProdutoPreco.id).desc()
    ).limit(5).all()
    
    return {
        "periodo": {
            "inicio": periodo_ini,
            "fim": periodo_fim
        },
        "materias_primas": {
            "total_precos": total_precos_mp,
            "variacao_media_absoluta": float(variacao_media_mp) if variacao_media_mp else 0,
            "top_variacoes": [
                {"nome": mp.nome, "total_precos": mp.total_precos}
                for mp in top_mp_variacoes
            ]
        },
        "produtos": {
            "total_custos": total_custos_prod,
            "variacao_media_absoluta": float(variacao_media_prod) if variacao_media_prod else 0,
            "top_variacoes": [
                {"nome": prod.nome, "total_custos": prod.total_custos}
                for prod in top_prod_variacoes
            ]
        }
    } 