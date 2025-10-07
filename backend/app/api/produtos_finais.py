from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
import logging

from app.database import get_db
from app.models.produto_final import ProdutoFinal
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.schemas.produto_final import ProdutoFinalCreate, ProdutoFinalResponse

logger = logging.getLogger(__name__)

produtos_finais_router = APIRouter(prefix="/produtos-finais", tags=["produtos-finais"])

@produtos_finais_router.post("/", status_code=status.HTTP_201_CREATED)
async def criar_produto_final(
    produto: ProdutoFinalCreate, 
    db: Session = Depends(get_db)
):
    """Criar produto final"""
    try:
        # Criar produto
        novo_produto = ProdutoFinal(
            nome=produto.nome,
            descricao=produto.descricao,
            componentes=produto.componentes,
            ativo=True
        )
        
        db.add(novo_produto)
        db.commit()
        db.refresh(novo_produto)
        
        return {
            "success": True,
            "message": "Produto final criado com sucesso!",
            "data": novo_produto
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar produto final: {str(e)}")
        return {
            "success": False,
            "message": f"Erro ao criar produto final: {str(e)}"
        }

@produtos_finais_router.get("/materias-primas-disponiveis")
async def listar_materias_primas_disponiveis(
    db: Session = Depends(get_db)
):
    """Lista matÃ©rias-primas disponÃ­veis para uso em produtos"""
    try:
        print("DEBUG: Iniciando busca de matÃ©rias-primas disponÃ­veis")
        
        # Buscar todas as matÃ©rias-primas ativas
        materias_primas = db.query(MateriaPrima).filter(MateriaPrima.is_active == True).all()
        print(f"DEBUG: Encontradas {len(materias_primas)} matÃ©rias-primas ativas")
        
        materias_formatadas = []
        
        for mp in materias_primas:
            print(f"DEBUG: Processando matÃ©ria-prima: {mp.nome}")
            
            # Buscar preÃ§o atual usando ORM (sem SQL raw)
            preco_atual = 0.0
            try:
                preco_obj = db.query(MateriaPrimaPreco).filter(
                    MateriaPrimaPreco.materia_prima_id == mp.id,
                    MateriaPrimaPreco.vigente_ate.is_(None)  # PreÃ§o atual
                ).order_by(MateriaPrimaPreco.vigente_desde.desc()).first()
                
                if preco_obj:
                    preco_atual = float(preco_obj.valor_unitario)
                    print(f"DEBUG: PreÃ§o encontrado: R$ {preco_atual}")
                else:
                    print(f"DEBUG: Nenhum preÃ§o encontrado para {mp.nome}")
            except Exception as e:
                print(f"DEBUG: Erro ao buscar preÃ§o: {e}")
                preco_atual = 0.0
            
            # Extrair quantidade do nome se existir
            quantidade_original = 1
            nome_limpo = mp.nome
            unidade_original = mp.unidade_codigo or "un"
            
            # Procurar por padrÃµes como "18L", "5KG", "10PC", etc.
            import re
            match = re.search(r'(\d+(?:\.\d+)?)\s*(L|KG|PC|UN|MT|M)$', mp.nome.upper())
            if match:
                quantidade_original = float(match.group(1))
                unidade_original = match.group(2)
                # Remover quantidade do nome
                nome_limpo = re.sub(r'\s*\d+(?:\.\d+)?\s*(L|KG|PC|UN|MT|M)$', '', mp.nome).strip()
            
            # Converter preÃ§o para unidade base
            if quantidade_original and quantidade_original > 0:
                preco_por_unidade = preco_atual / quantidade_original
            else:
                preco_por_unidade = preco_atual
            
            materias_formatadas.append({
                "id": mp.id,
                "nome": nome_limpo,
                "unidade": unidade_original,
                "valorUnitario": preco_por_unidade
            })
        
        # Ordenar por nome
        materias_formatadas.sort(key=lambda x: x['nome'])
        print(f"DEBUG: Retornando {len(materias_formatadas)} matÃ©rias-primas formatadas")
        
        return materias_formatadas
        
    except Exception as e:
        print(f"ERROR: Erro ao listar matÃ©rias-primas: {str(e)}")
        logger.error(f"Erro ao listar matÃ©rias-primas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar matÃ©rias-primas: {str(e)}"
        )

@produtos_finais_router.get("/")
async def listar_produtos_finais(
    skip: int = 0, 
    limit: int = 100, 
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    """Listar produtos finais"""
    try:
        print("DEBUG: Listando produtos finais")
        
        query = db.query(ProdutoFinal)
        if ativo is not None:
            query = query.filter(ProdutoFinal.ativo == ativo)
        
        produtos = query.offset(skip).limit(limit).all()
        print(f"DEBUG: Encontrados {len(produtos)} produtos finais")
        
        # Converter para formato simples
        produtos_formatados = []
        for produto in produtos:
            produtos_formatados.append({
                "id": produto.id,
                "nome": produto.nome,
                "descricao": produto.descricao,
                "componentes": produto.componentes,
                "ativo": produto.ativo,
                "created_at": produto.created_at.isoformat() if produto.created_at else None,
                "updated_at": produto.updated_at.isoformat() if produto.updated_at else None
            })
        
        return produtos_formatados
        
    except Exception as e:
        print(f"ERROR: Erro ao listar produtos finais: {str(e)}")
        logger.error(f"Erro ao listar produtos finais: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar produtos finais: {str(e)}"
        )

@produtos_finais_router.get("/{produto_id}")
async def obter_produto_final(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Obter produto final por ID"""
    try:
        produto = db.query(ProdutoFinal).filter(ProdutoFinal.id == produto_id).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto final nÃ£o encontrado"
            )
        
        return {
            "id": produto.id,
            "nome": produto.nome,
            "descricao": produto.descricao,
            "componentes": produto.componentes,
            "ativo": produto.ativo,
            "created_at": produto.created_at.isoformat() if produto.created_at else None,
            "updated_at": produto.updated_at.isoformat() if produto.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter produto final: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter produto final: {str(e)}"
        )

@produtos_finais_router.put("/{produto_id}")
async def atualizar_produto_final(
    produto_id: int,
    produto: ProdutoFinalCreate,
    db: Session = Depends(get_db)
):
    """Atualizar produto final"""
    try:
        produto_existente = db.query(ProdutoFinal).filter(ProdutoFinal.id == produto_id).first()
        
        if not produto_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto final nÃ£o encontrado"
            )
        
        # Atualizar campos
        produto_existente.nome = produto.nome
        produto_existente.descricao = produto.descricao
        produto_existente.componentes = produto.componentes
        
        db.commit()
        db.refresh(produto_existente)
        
        return {
            "success": True,
            "message": "Produto final atualizado com sucesso!",
            "data": produto_existente
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar produto final: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar produto final: {str(e)}"
        )

@produtos_finais_router.delete("/{produto_id}")
async def deletar_produto_final(
    produto_id: int,
    db: Session = Depends(get_db)
):
    """Deletar produto final (soft delete)"""
    try:
        produto = db.query(ProdutoFinal).filter(ProdutoFinal.id == produto_id).first()
        
        if not produto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto final nÃ£o encontrado"
            )
        
        # Soft delete
        produto.ativo = False
        db.commit()
        
        return {
            "success": True,
            "message": "Produto final deletado com sucesso!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar produto final: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar produto final: {str(e)}"
        )
