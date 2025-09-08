from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Produto, User
from app.schemas import ProdutoCreate, ProdutoUpdate, ProdutoResponse
from app.auth.dependencies import require_editor

produtos_router = APIRouter(prefix="/produtos", tags=["Produtos"])

@produtos_router.post("/", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    produto: ProdutoCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Criar novo produto"""
    try:
        # Verificar se código já existe
        if produto.codigo:
            db_produto = db.query(Produto).filter(Produto.codigo == produto.codigo).first()
            if db_produto:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código já cadastrado"
                )
        
        # Criar produto
        db_produto = Produto(
            codigo=produto.codigo,
            nome=produto.nome,
            descricao=produto.descricao,
            categoria=produto.categoria,
            unidade_medida=produto.unidade_medida,
            preco_custo=produto.preco_custo,
            preco_venda=produto.preco_venda,
            estoque_minimo=produto.estoque_minimo,
            estoque_atual=produto.estoque_atual,
            fornecedor_id=produto.fornecedor_id,
            ativo=True
        )
        
        db.add(db_produto)
        db.commit()
        db.refresh(db_produto)
        
        return db_produto
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar produto: {str(e)}"
        )

@produtos_router.get("/", response_model=List[ProdutoResponse])
async def listar_produtos(
    skip: int = 0, 
    limit: int = 100, 
    ativo: bool = True,
    categoria: str = None,
    db: Session = Depends(get_db)
):
    """Listar produtos"""
    query = db.query(Produto)
    if ativo is not None:
        query = query.filter(Produto.ativo == ativo)
    if categoria:
        query = query.filter(Produto.categoria == categoria)
    
    produtos = query.offset(skip).limit(limit).all()
    return produtos

@produtos_router.get("/{produto_id}", response_model=ProdutoResponse)
async def buscar_produto(
    produto_id: int, 
    db: Session = Depends(get_db)
):
    """Buscar produto por ID"""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    return produto

@produtos_router.put("/{produto_id}", response_model=ProdutoResponse)
async def atualizar_produto(
    produto_id: int,
    produto: ProdutoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Atualizar produto"""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    try:
        # Atualizar campos
        if produto.codigo:
            db_produto.codigo = produto.codigo
        if produto.nome:
            db_produto.nome = produto.nome
        if produto.descricao:
            db_produto.descricao = produto.descricao
        if produto.categoria:
            db_produto.categoria = produto.categoria
        if produto.unidade_medida:
            db_produto.unidade_medida = produto.unidade_medida
        if produto.preco_custo:
            db_produto.preco_custo = produto.preco_custo
        if produto.preco_venda:
            db_produto.preco_venda = produto.preco_venda
        if produto.estoque_minimo:
            db_produto.estoque_minimo = produto.estoque_minimo
        if produto.estoque_atual:
            db_produto.estoque_atual = produto.estoque_atual
        if produto.fornecedor_id:
            db_produto.fornecedor_id = produto.fornecedor_id
        if produto.ativo is not None:
            db_produto.ativo = produto.ativo
        
        db.commit()
        db.refresh(db_produto)
        return db_produto
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar produto: {str(e)}"
        )

@produtos_router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_editor)
):
    """Deletar produto (soft delete)"""
    db_produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not db_produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado"
        )
    
    try:
        # Soft delete
        db_produto.ativo = False
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar produto: {str(e)}"
        ) 