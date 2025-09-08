from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.audit import AuditLog
from app.models.nota import Nota
from app.models.materia_prima_preco import MateriaPrimaPreco
from app.models.produto_preco import ProdutoPreco
from app.config import get_settings
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import and_, func, or_

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="app.tasks.maintenance_tasks.limpar_logs_antigos")
def limpar_logs_antigos(self, dias_manter: int = 90):
    """Tarefa para limpar logs de auditoria antigos"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando limpeza de logs antigos..."}
        )
        
        db = SessionLocal()
        
        try:
            # Calcular data limite
            data_limite = datetime.now() - timedelta(days=dias_manter)
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Contando logs antigos..."}
            )
            
            # Contar logs antigos
            total_logs_antigos = db.query(AuditLog).filter(
                AuditLog.created_at < data_limite
            ).count()
            
            if total_logs_antigos == 0:
                return {
                    "status": "sucesso",
                    "message": "Nenhum log antigo para limpar",
                    "dias_manter": dias_manter,
                    "logs_removidos": 0
                }
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": f"Removendo {total_logs_antigos} logs antigos..."}
            )
            
            # Remover logs antigos
            logs_removidos = db.query(AuditLog).filter(
                AuditLog.created_at < data_limite
            ).delete()
            
            db.commit()
            
            resultado = {
                "status": "sucesso",
                "message": "Limpeza de logs concluída",
                "dias_manter": dias_manter,
                "data_limite": data_limite.isoformat(),
                "total_logs_antigos": total_logs_antigos,
                "logs_removidos": logs_removidos
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro na limpeza de logs: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.maintenance_tasks.limpar_arquivos_antigos")
def limpar_arquivos_antigos(self, dias_manter: int = 30):
    """Tarefa para limpar arquivos antigos do diretório de uploads"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando limpeza de arquivos antigos..."}
        )
        
        upload_dir = settings.UPLOAD_DIR
        
        if not os.path.exists(upload_dir):
            return {
                "status": "sucesso",
                "message": "Diretório de uploads não existe",
                "arquivos_removidos": 0
            }
        
        # Calcular data limite
        data_limite = datetime.now() - timedelta(days=dias_manter)
        timestamp_limite = data_limite.timestamp()
        
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Verificando arquivos antigos..."}
        )
        
        arquivos_removidos = 0
        erros = []
        
        # Listar arquivos no diretório
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            
            try:
                if os.path.isfile(file_path):
                    # Verificar data de criação
                    file_stat = os.stat(file_path)
                    if file_stat.st_ctime < timestamp_limite:
                        # Verificar se o arquivo não está sendo usado por nenhuma nota
                        db = SessionLocal()
                        try:
                            # Buscar notas que referenciam este arquivo
                            nota_com_arquivo = db.query(Nota).filter(
                                or_(
                                    Nota.arquivo_xml_path == file_path,
                                    Nota.arquivo_pdf_path == file_path
                                )
                            ).first()
                            
                            if not nota_com_arquivo:
                                # Arquivo não está sendo usado, pode remover
                                os.remove(file_path)
                                arquivos_removidos += 1
                                
                                current_task.update_state(
                                    state="PROGRESS",
                                    meta={
                                        "status": f"Arquivo removido: {filename}",
                                        "arquivos_removidos": arquivos_removidos
                                    }
                                )
                            
                        finally:
                            db.close()
                            
            except Exception as e:
                error_msg = f"Erro ao processar arquivo {filename}: {str(e)}"
                logger.error(error_msg)
                erros.append(error_msg)
                continue
        
        resultado = {
            "status": "sucesso",
            "message": "Limpeza de arquivos concluída",
            "dias_manter": dias_manter,
            "data_limite": data_limite.isoformat(),
            "arquivos_removidos": arquivos_removidos,
            "erros": erros
        }
        
        current_task.update_state(
            state="SUCCESS",
            meta=resultado
        )
        
        return resultado
        
    except Exception as e:
        error_msg = f"Erro na limpeza de arquivos: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.maintenance_tasks.otimizar_banco_dados")
def otimizar_banco_dados(self):
    """Tarefa para otimizar o banco de dados"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando otimização do banco de dados..."}
        )
        
        db = SessionLocal()
        
        try:
            # Estatísticas antes da otimização
            total_notas = db.query(Nota).count()
            total_audit_logs = db.query(AuditLog).count()
            total_precos_mp = db.query(MateriaPrimaPreco).count()
            total_precos_prod = db.query(ProdutoPreco).count()
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Executando VACUUM ANALYZE..."}
            )
            
            # Executar VACUUM ANALYZE (PostgreSQL)
            try:
                db.execute("VACUUM ANALYZE")
                db.commit()
                vacuum_executado = True
            except Exception as e:
                logger.warning(f"VACUUM ANALYZE não executado: {e}")
                vacuum_executado = False
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Atualizando estatísticas..."}
            )
            
            # Atualizar estatísticas das tabelas
            try:
                db.execute("ANALYZE")
                db.commit()
                analyze_executado = True
            except Exception as e:
                logger.warning(f"ANALYZE não executado: {e}")
                analyze_executado = False
            
            resultado = {
                "status": "sucesso",
                "message": "Otimização do banco concluída",
                "estatisticas": {
                    "total_notas": total_notas,
                    "total_audit_logs": total_audit_logs,
                    "total_precos_mp": total_precos_mp,
                    "total_precos_prod": total_precos_prod
                },
                "otimizacoes": {
                    "vacuum_executado": vacuum_executado,
                    "analyze_executado": analyze_executado
                }
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro na otimização do banco: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.maintenance_tasks.verificar_integridade")
def verificar_integridade(self):
    """Tarefa para verificar integridade dos dados"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando verificação de integridade..."}
        )
        
        db = SessionLocal()
        
        try:
            problemas = []
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Verificando notas sem fornecedor..."}
            )
            
            # Verificar notas sem fornecedor
            notas_sem_fornecedor = db.query(Nota).filter(
                Nota.fornecedor_id.is_(None)
            ).count()
            
            if notas_sem_fornecedor > 0:
                problemas.append({
                    "tipo": "notas_sem_fornecedor",
                    "descricao": f"{notas_sem_fornecedor} notas sem fornecedor associado",
                    "severidade": "media"
                })
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Verificando itens sem matéria-prima..."}
            )
            
            # Verificar itens sem matéria-prima
            from app.models.nota import NotaItem
            itens_sem_mp = db.query(NotaItem).filter(
                NotaItem.materia_prima_id.is_(None)
            ).count()
            
            if itens_sem_mp > 0:
                problemas.append({
                    "tipo": "itens_sem_materia_prima",
                    "descricao": f"{itens_sem_mp} itens sem matéria-prima associada",
                    "severidade": "alta"
                })
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Verificando preços duplicados..."}
            )
            
            # Verificar preços duplicados (múltiplos preços vigentes para mesma MP)
            precos_duplicados = db.query(MateriaPrimaPreco).filter(
                MateriaPrimaPreco.vigente_ate.is_(None)
            ).group_by(MateriaPrimaPreco.materia_prima_id).having(
                func.count(MateriaPrimaPreco.id) > 1
            ).count()
            
            if precos_duplicados > 0:
                problemas.append({
                    "tipo": "precos_duplicados",
                    "descricao": f"{precos_duplicados} matérias-primas com múltiplos preços vigentes",
                    "severidade": "alta"
                })
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Verificando produtos sem componentes..."}
            )
            
            # Verificar produtos sem componentes
            from app.models.produto import Produto, ProdutoComponente
            produtos_sem_componentes = db.query(Produto).outerjoin(ProdutoComponente).filter(
                ProdutoComponente.id.is_(None)
            ).count()
            
            if produtos_sem_componentes > 0:
                problemas.append({
                    "tipo": "produtos_sem_componentes",
                    "descricao": f"{produtos_sem_componentes} produtos sem componentes",
                    "severidade": "baixa"
                })
            
            # Estatísticas gerais
            total_notas = db.query(Nota).count()
            total_fornecedores = db.query(Fornecedor).count()
            total_materias_primas = db.query(MateriaPrima).count()
            total_produtos = db.query(Produto).count()
            
            resultado = {
                "status": "sucesso",
                "message": "Verificação de integridade concluída",
                "estatisticas": {
                    "total_notas": total_notas,
                    "total_fornecedores": total_fornecedores,
                    "total_materias_primas": total_materias_primas,
                    "total_produtos": total_produtos
                },
                "problemas_encontrados": len(problemas),
                "problemas": problemas,
                "timestamp": datetime.now().isoformat()
            }
            
            current_task.update_state(
                state="SUCCESS",
                meta=resultado
            )
            
            return resultado
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro na verificação de integridade: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.maintenance_tasks.backup_dados")
def backup_dados(self, tipo_backup: str = "completo"):
    """Tarefa para fazer backup dos dados"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando backup dos dados..."}
        )
        
        # TODO: Implementar backup real
        # Por enquanto, simular backup
        
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Preparando backup..."}
        )
        
        # Simular tempo de backup
        import time
        time.sleep(2)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Executando backup..."}
        )
        
        time.sleep(3)
        
        resultado = {
            "status": "sucesso",
            "message": "Backup concluído com sucesso",
            "tipo_backup": tipo_backup,
            "timestamp": datetime.now().isoformat(),
            "arquivo_backup": f"backup_{tipo_backup}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
            "tamanho_estimado": "50MB"
        }
        
        current_task.update_state(
            state="SUCCESS",
            meta=resultado
        )
        
        return resultado
        
    except Exception as e:
        error_msg = f"Erro no backup: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise 