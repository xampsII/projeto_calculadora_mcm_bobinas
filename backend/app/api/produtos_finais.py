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
        # Converter componentes para dicionários se necessário
        componentes_dict = []
        for componente in produto.componentes:
            if hasattr(componente, 'dict'):
                componentes_dict.append(componente.dict())
            elif hasattr(componente, 'model_dump'):
                componentes_dict.append(componente.model_dump())
            else:
                componentes_dict.append(componente)
        
        # Criar produto
        novo_produto = ProdutoFinal(
            nome=produto.nome,
            id_unico=produto.idUnico,
            componentes=componentes_dict,
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
    """Lista matérias-primas disponíveis para uso em produtos"""
    try:
        print("DEBUG: Iniciando busca de matérias-primas disponíveis")
        
        # Verificar se a tabela existe primeiro
        try:
            materias_primas = db.query(MateriaPrima).filter(MateriaPrima.is_active == True).all()
            print(f"DEBUG: Encontradas {len(materias_primas)} matérias-primas ativas")
        except Exception as e:
            print(f"DEBUG: Erro ao buscar matérias-primas: {e}")
            # Retornar lista vazia se tabela não existir
            return []
        
        materias_formatadas = []
        
        for mp in materias_primas:
            try:
                print(f"DEBUG: Processando matéria-prima: {mp.nome}")
                
                # Buscar preço atual usando ORM (sem SQL raw)
                preco_atual = 0.0
                try:
                    preco_obj = db.query(MateriaPrimaPreco).filter(
                        MateriaPrimaPreco.materia_prima_id == mp.id,
                        MateriaPrimaPreco.vigente_ate.is_(None)  # Preço atual
                    ).order_by(MateriaPrimaPreco.vigente_desde.desc()).first()
                    
                    if preco_obj:
                        preco_atual = float(preco_obj.valor_unitario)
                        print(f"DEBUG: Preço encontrado: R$ {preco_atual}")
                    else:
                        print(f"DEBUG: Nenhum preço encontrado para {mp.nome}")
                except Exception as e:
                    print(f"DEBUG: Erro ao buscar preço: {e}")
                    preco_atual = 0.0
                
                # Extrair quantidade do nome se existir
                quantidade_original = 1
                nome_limpo = mp.nome
                unidade_original = mp.unidade_codigo or "un"
                
                # Procurar por padrões como "18L", "5KG", "10PC", etc.
                import re
                match = re.search(r'(\d+(?:\.\d+)?)\s*(L|KG|PC|UN|MT|M)$', mp.nome.upper())
                if match:
                    quantidade_original = float(match.group(1))
                    unidade_original = match.group(2)
                    # Remover quantidade do nome
                    nome_limpo = re.sub(r'\s*\d+(?:\.\d+)?\s*(L|KG|PC|UN|MT|M)$', '', mp.nome).strip()
                
                # Converter preço para unidade base
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
                
            except Exception as e:
                print(f"DEBUG: Erro ao processar matéria-prima {mp.nome}: {e}")
                continue
        
        # Ordenar por nome
        materias_formatadas.sort(key=lambda x: x['nome'])
        print(f"DEBUG: Retornando {len(materias_formatadas)} matérias-primas formatadas")
        
        return materias_formatadas
        
    except Exception as e:
        print(f"ERROR: Erro ao listar matérias-primas: {str(e)}")
        logger.error(f"Erro ao listar matérias-primas: {str(e)}")
        # Retornar lista vazia em caso de erro
        return []

@produtos_finais_router.get("/")
async def listar_produtos_finais(
    skip: int = 0, 
    limit: int = 100, 
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    """Listar produtos finais com preços SEMPRE atualizados do histórico
    
    Args:
        skip: Offset para paginação
        limit: Limite de resultados
        ativo: Filtrar apenas produtos ativos
    """
    try:
        print(f"DEBUG: Listando produtos finais com preços atualizados automaticamente")
        
        # Verificar se a tabela existe primeiro
        try:
            query = db.query(ProdutoFinal)
            if ativo is not None:
                query = query.filter(ProdutoFinal.ativo == ativo)
            
            produtos = query.offset(skip).limit(limit).all()
            print(f"DEBUG: Encontrados {len(produtos)} produtos finais")
        except Exception as e:
            print(f"DEBUG: Erro ao buscar produtos finais: {e}")
            return []
        
        # Converter para formato simples
        produtos_formatados = []
        for produto in produtos:
            try:
                # Processar componentes
                componentes_atualizados = []
                custo_total = 0.0
                
                if produto.componentes:
                    for componente in produto.componentes:
                        try:
                            quantidade = float(componente.get('quantidade', 0))
                            valor_unitario_salvo = float(componente.get('valorUnitario', 0))
                            
                            # SEMPRE buscar preço mais recente do histórico (atualização automática)
                            nome_mp = componente.get('materiaPrimaNome', '')
                            
                            # Buscar matéria-prima pelo nome
                            mp = db.query(MateriaPrima).filter(
                                MateriaPrima.nome.ilike(f"%{nome_mp}%"),
                                MateriaPrima.is_active == True
                            ).first()
                            
                            valor_unitario_atual = valor_unitario_salvo  # Padrão: valor salvo
                            
                            if mp:
                                # Buscar preço mais recente do histórico
                                preco_obj = db.query(MateriaPrimaPreco).filter(
                                    MateriaPrimaPreco.materia_prima_id == mp.id,
                                    MateriaPrimaPreco.vigente_ate.is_(None)
                                ).order_by(MateriaPrimaPreco.vigente_desde.desc()).first()
                                
                                if preco_obj:
                                    valor_unitario_atual = float(preco_obj.valor_unitario)
                                    if valor_unitario_atual != valor_unitario_salvo:
                                        print(f"DEBUG: Preço atualizado automaticamente: {nome_mp}: {valor_unitario_salvo} → {valor_unitario_atual}")
                            
                            # Adicionar componente com preço atualizado
                            comp_atualizado = componente.copy()
                            comp_atualizado['valorUnitario'] = valor_unitario_atual
                            componentes_atualizados.append(comp_atualizado)
                            
                            custo_total += quantidade * valor_unitario_atual
                        except (ValueError, TypeError) as e:
                            print(f"DEBUG: Erro ao processar componente {componente}: {e}")
                            componentes_atualizados.append(componente)
                            continue
                
                produtos_formatados.append({
                    "id": produto.id,
                    "nome": produto.nome,
                    "idUnico": produto.id_unico,
                    "componentes": componentes_atualizados,  # SEMPRE com preços atualizados
                    "custo_total": round(custo_total, 2),
                    "ativo": produto.ativo,
                    "created_at": produto.created_at.isoformat() if produto.created_at else None,
                    "updated_at": produto.updated_at.isoformat() if produto.updated_at else None
                })
            except Exception as e:
                print(f"DEBUG: Erro ao formatar produto {produto.id}: {e}")
                continue
        
        return produtos_formatados
        
    except Exception as e:
        print(f"ERROR: Erro ao listar produtos finais: {str(e)}")
        logger.error(f"Erro ao listar produtos finais: {str(e)}")
        # Retornar lista vazia em caso de erro
        return []

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
                detail="Produto final não encontrado"
            )
        
        # Calcular custo total baseado nos componentes
        custo_total = 0.0
        if produto.componentes:
            for componente in produto.componentes:
                try:
                    quantidade = float(componente.get('quantidade', 0))
                    valor_unitario = float(componente.get('valorUnitario', 0))
                    custo_total += quantidade * valor_unitario
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Erro ao calcular custo do componente {componente}: {e}")
                    continue
        
        return {
            "id": produto.id,
            "nome": produto.nome,
            "idUnico": produto.id_unico,
            "componentes": produto.componentes,
            "custo_total": round(custo_total, 2),
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
                detail="Produto final não encontrado"
            )
        
        # Converter componentes para dicionários se necessário
        componentes_dict = []
        for componente in produto.componentes:
            if hasattr(componente, 'dict'):
                componentes_dict.append(componente.dict())
            elif hasattr(componente, 'model_dump'):
                componentes_dict.append(componente.model_dump())
            else:
                componentes_dict.append(componente)
        
        # Atualizar campos
        produto_existente.nome = produto.nome
        produto_existente.id_unico = produto.idUnico
        produto_existente.componentes = componentes_dict
        
        # IMPORTANTE: Marcar campo JSON como modificado
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(produto_existente, "componentes")
        
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
                detail="Produto final não encontrado"
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
