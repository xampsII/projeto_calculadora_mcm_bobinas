from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.produto import Produto, ProdutoComponente, ProdutoPreco
from app.models.unidade import Unidade
from app.config import get_settings
import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, func

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="app.tasks.price_tasks.atualizar_preco_materia_prima")
def atualizar_preco_materia_prima(self, materia_prima_id: int, novo_preco: float, 
                                 fornecedor_id: Optional[int] = None, 
                                 nota_id: Optional[int] = None,
                                 origem: str = "manual"):
    """Tarefa para atualizar preço de matéria-prima e recalcular custos de produtos"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Atualizando preço de matéria-prima..."}
        )
        
        db = SessionLocal()
        
        try:
            # Buscar a matéria-prima
            materia_prima = db.query(MateriaPrima).filter(
                MateriaPrima.id == materia_prima_id
            ).first()
            
            if not materia_prima:
                raise Exception("Matéria-prima não encontrada")
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Fechando preço anterior..."}
            )
            
            # Fechar preço anterior se existir
            preco_anterior = db.query(MateriaPrimaPreco).filter(
                and_(
                    MateriaPrimaPreco.materia_prima_id == materia_prima_id,
                    MateriaPrimaPreco.vigente_ate.is_(None)
                )
            ).first()
            
            if preco_anterior:
                preco_anterior.vigente_ate = datetime.now()
                db.add(preco_anterior)
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Criando novo preço..."}
            )
            
            # Criar novo preço
            novo_preco_obj = MateriaPrimaPreco(
                materia_prima_id=materia_prima_id,
                valor_unitario=Decimal(str(novo_preco)),
                vigente_desde=datetime.now(),
                origem=origem,
                fornecedor_id=fornecedor_id,
                nota_id=nota_id
            )
            
            db.add(novo_preco_obj)
            db.commit()
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Recalculando custos de produtos..."}
            )
            
            # Enfileirar tarefa para recalcular custos de produtos que usam esta MP
            recalcular_custos_por_materia_prima.delay(materia_prima_id)
            
            resultado = {
                "status": "sucesso",
                "message": "Preço atualizado com sucesso",
                "materia_prima_id": materia_prima_id,
                "preco_anterior": float(preco_anterior.valor_unitario) if preco_anterior else None,
                "novo_preco": novo_preco,
                "variacao": float(novo_preco - preco_anterior.valor_unitario) if preco_anterior else None
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro ao atualizar preço: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.price_tasks.recalcular_custos_por_materia_prima")
def recalcular_custos_por_materia_prima(self, materia_prima_id: int):
    """Tarefa para recalcular custos de produtos que usam uma matéria-prima específica"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Recalculando custos de produtos..."}
        )
        
        db = SessionLocal()
        
        try:
            # Buscar produtos que usam esta matéria-prima
            produtos_afetados = db.query(Produto).join(ProdutoComponente).filter(
                ProdutoComponente.materia_prima_id == materia_prima_id
            ).distinct().all()
            
            if not produtos_afetados:
                return {
                    "status": "sucesso",
                    "message": "Nenhum produto afetado",
                    "produtos_recalculados": 0
                }
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": f"Recalculando {len(produtos_afetados)} produtos..."}
            )
            
            produtos_recalculados = 0
            
            for i, produto in enumerate(produtos_afetados):
                try:
                    current_task.update_state(
                        state="PROGRESS",
                        meta={
                            "status": f"Recalculando produto {i+1}/{len(produtos_afetados)}: {produto.nome}"
                        }
                    )
                    
                    # Calcular novo custo
                    novo_custo = calcular_custo_produto(produto.id, db)
                    
                    if novo_custo is None:
                        logger.warning(f"Não foi possível calcular custo para produto {produto.id}")
                        continue
                    
                    # Buscar preço atual
                    preco_atual = db.query(ProdutoPreco).filter(
                        and_(
                            ProdutoPreco.produto_id == produto.id,
                            ProdutoPreco.vigente_ate.is_(None)
                        )
                    ).first()
                    
                    # Verificar se o custo mudou
                    if preco_atual and preco_atual.custo_total == novo_custo:
                        continue
                    
                    # Fechar preço anterior se existir
                    if preco_atual:
                        preco_atual.vigente_ate = datetime.now()
                        db.add(preco_atual)
                    
                    # Criar novo preço
                    novo_preco = ProdutoPreco(
                        produto_id=produto.id,
                        custo_total=novo_custo,
                        vigente_desde=datetime.now()
                    )
                    
                    db.add(novo_preco)
                    produtos_recalculados += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao recalcular produto {produto.id}: {e}")
                    continue
            
            db.commit()
            
            resultado = {
                "status": "sucesso",
                "message": "Custos recalculados com sucesso",
                "produtos_afetados": len(produtos_afetados),
                "produtos_recalculados": produtos_recalculados
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro ao recalcular custos: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.price_tasks.recalcular_custos_periodico")
def recalcular_custos_periodico(self):
    """Tarefa periódica para recalcular todos os custos de produtos"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando recálculo periódico de custos..."}
        )
        
        db = SessionLocal()
        
        try:
            # Buscar todos os produtos ativos
            produtos = db.query(Produto).filter(Produto.is_active == True).all()
            
            if not produtos:
                return {
                    "status": "sucesso",
                    "message": "Nenhum produto para recalcular",
                    "produtos_recalculados": 0
                }
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": f"Recalculando {len(produtos)} produtos..."}
            )
            
            produtos_recalculados = 0
            erros = []
            
            for i, produto in enumerate(produtos):
                try:
                    current_task.update_state(
                        state="PROGRESS",
                        meta={
                            "status": f"Recalculando produto {i+1}/{len(produtos)}: {produto.nome}",
                            "progress": (i / len(produtos)) * 100
                        }
                    )
                    
                    # Calcular novo custo
                    novo_custo = calcular_custo_produto(produto.id, db)
                    
                    if novo_custo is None:
                        logger.warning(f"Não foi possível calcular custo para produto {produto.id}")
                        continue
                    
                    # Buscar preço atual
                    preco_atual = db.query(ProdutoPreco).filter(
                        and_(
                            ProdutoPreco.produto_id == produto.id,
                            ProdutoPreco.vigente_ate.is_(None)
                        )
                    ).first()
                    
                    # Verificar se o custo mudou
                    if preco_atual and preco_atual.custo_total == novo_custo:
                        continue
                    
                    # Fechar preço anterior se existir
                    if preco_atual:
                        preco_atual.vigente_ate = datetime.now()
                        db.add(preco_atual)
                    
                    # Criar novo preço
                    novo_preco = ProdutoPreco(
                        produto_id=produto.id,
                        custo_total=novo_custo,
                        vigente_desde=datetime.now()
                    )
                    
                    db.add(novo_preco)
                    produtos_recalculados += 1
                    
                except Exception as e:
                    error_msg = f"Erro ao recalcular produto {produto.id}: {e}"
                    logger.error(error_msg)
                    erros.append(error_msg)
                    continue
            
            db.commit()
            
            resultado = {
                "status": "sucesso",
                "message": "Recálculo periódico concluído",
                "total_produtos": len(produtos),
                "produtos_recalculados": produtos_recalculados,
                "erros": erros
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro no recálculo periódico: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.price_tasks.recalcular_produto_especifico")
def recalcular_produto_especifico(self, produto_id: int):
    """Tarefa para recalcular custo de um produto específico"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Recalculando produto específico..."}
        )
        
        db = SessionLocal()
        
        try:
            # Buscar o produto
            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            
            if not produto:
                raise Exception("Produto não encontrado")
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": f"Calculando custo de {produto.nome}..."}
            )
            
            # Calcular novo custo
            novo_custo = calcular_custo_produto(produto.id, db)
            
            if novo_custo is None:
                raise Exception("Não foi possível calcular o custo do produto")
            
            # Buscar preço atual
            preco_atual = db.query(ProdutoPreco).filter(
                and_(
                    ProdutoPreco.produto_id == produto_id,
                    ProdutoPreco.vigente_ate.is_(None)
                )
            ).first()
            
            # Verificar se o custo mudou
            if preco_atual and preco_atual.custo_total == novo_custo:
                return {
                    "status": "sucesso",
                    "message": "Custo não mudou",
                    "custo_atual": float(novo_custo)
                }
            
            # Fechar preço anterior se existir
            if preco_atual:
                preco_atual.vigente_ate = datetime.now()
                db.add(preco_atual)
            
            # Criar novo preço
            novo_preco = ProdutoPreco(
                produto_id=produto_id,
                custo_total=novo_custo,
                vigente_desde=datetime.now()
            )
            
            db.add(novo_preco)
            db.commit()
            
            resultado = {
                "status": "sucesso",
                "message": "Custo recalculado com sucesso",
                "produto_id": produto_id,
                "produto_nome": produto.nome,
                "custo_anterior": float(preco_atual.custo_total) if preco_atual else None,
                "custo_novo": float(novo_custo),
                "variacao": float(novo_custo - preco_atual.custo_total) if preco_atual else None
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro ao recalcular produto: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


def calcular_custo_produto(produto_id: int, db: SessionLocal) -> Optional[Decimal]:
    """Função auxiliar para calcular custo de um produto"""
    try:
        componentes = db.query(ProdutoComponente).filter(
            ProdutoComponente.produto_id == produto_id
        ).all()
        
        if not componentes:
            return None
        
        custo_total = Decimal('0')
        
        for componente in componentes:
            # Buscar preço atual da matéria-prima
            preco_mp = db.query(MateriaPrimaPreco).filter(
                and_(
                    MateriaPrimaPreco.materia_prima_id == componente.materia_prima_id,
                    MateriaPrimaPreco.vigente_ate.is_(None)
                )
            ).first()
            
            if not preco_mp:
                # Se não há preço para uma MP, não é possível calcular o custo
                return None
            
            # Calcular custo do componente
            custo_componente = componente.quantidade * preco_mp.valor_unitario
            
            # TODO: Implementar conversão de unidades se necessário
            # Por enquanto, assumir que as unidades são compatíveis
            
            custo_total += custo_componente
        
        return custo_total
        
    except Exception as e:
        logger.error(f"Erro ao calcular custo do produto {produto_id}: {e}")
        return None


@celery_app.task(bind=True, name="app.tasks.price_tasks.analisar_variacoes_precos")
def analisar_variacoes_precos(self, periodo_dias: int = 30):
    """Tarefa para analisar variações de preços no período"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Analisando variações de preços..."}
        )
        
        db = SessionLocal()
        
        try:
            from datetime import timedelta
            data_limite = datetime.now() - timedelta(days=periodo_dias)
            
            # Buscar preços criados no período
            precos_periodo = db.query(MateriaPrimaPreco).filter(
                MateriaPrimaPreco.created_at >= data_limite
            ).all()
            
            if not precos_periodo:
                return {
                    "status": "sucesso",
                    "message": "Nenhuma variação de preço no período",
                    "periodo_dias": periodo_dias,
                    "total_variacoes": 0
                }
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Calculando estatísticas de variação..."}
            )
            
            # Agrupar por matéria-prima
            variacoes_por_mp = {}
            
            for preco in precos_periodo:
                mp_id = preco.materia_prima_id
                if mp_id not in variacoes_por_mp:
                    variacoes_por_mp[mp_id] = []
                
                variacoes_por_mp[mp_id].append({
                    "valor": float(preco.valor_unitario),
                    "data": preco.vigente_desde,
                    "origem": preco.origem.value
                })
            
            # Calcular estatísticas
            estatisticas = []
            
            for mp_id, variacoes in variacoes_por_mp.items():
                if len(variacoes) < 2:
                    continue
                
                # Ordenar por data
                variacoes.sort(key=lambda x: x["data"])
                
                # Calcular variações
                variacoes_calculadas = []
                for i in range(1, len(variacoes)):
                    valor_anterior = variacoes[i-1]["valor"]
                    valor_atual = variacoes[i]["valor"]
                    
                    variacao_abs = valor_atual - valor_anterior
                    variacao_pct = (variacao_abs / valor_anterior) * 100 if valor_anterior > 0 else 0
                    
                    variacoes_calculadas.append({
                        "data": variacoes[i]["data"],
                        "valor_anterior": valor_anterior,
                        "valor_atual": valor_atual,
                        "variacao_abs": variacao_abs,
                        "variacao_pct": variacao_pct
                    })
                
                if variacoes_calculadas:
                    # Buscar nome da matéria-prima
                    materia_prima = db.query(MateriaPrima).filter(MateriaPrima.id == mp_id).first()
                    
                    estatisticas.append({
                        "materia_prima_id": mp_id,
                        "materia_prima_nome": materia_prima.nome if materia_prima else "Desconhecida",
                        "total_variacoes": len(variacoes_calculadas),
                        "variacoes": variacoes_calculadas,
                        "maior_variacao_abs": max(v["variacao_abs"] for v in variacoes_calculadas),
                        "maior_variacao_pct": max(v["variacao_pct"] for v in variacoes_calculadas)
                    })
            
            resultado = {
                "status": "sucesso",
                "message": "Análise de variações concluída",
                "periodo_dias": periodo_dias,
                "total_materias_primas": len(estatisticas),
                "estatisticas": estatisticas
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro na análise de variações: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise 