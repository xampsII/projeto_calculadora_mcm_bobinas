from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.nota import Nota
from app.models.enums import StatusNota
from app.models.fornecedor import Fornecedor
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.enums import OrigemPreco
from app.models.unidade import Unidade
from app.config import settings
import imaplib
import email
import os
import hashlib
from datetime import datetime
from email.header import decode_header
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="app.tasks.email_tasks.processar_emails_periodico")
def processar_emails_periodico(self):
    """Tarefa periódica para processar emails de NF-e"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 0, "status": "Conectando ao servidor IMAP..."}
        )
        
        # Conectar ao servidor IMAP
        imap_server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
        imap_server.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 1, "total": 10, "status": "Conectado ao servidor IMAP"}
        )
        
        # Selecionar pasta "NFe" (criar se não existir)
        try:
            imap_server.select('NFe')
        except:
            imap_server.create('NFe')
            imap_server.select('NFe')
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 2, "total": 10, "status": "Pasta NFe selecionada"}
        )
        
        # Buscar emails não lidos
        status, messages = imap_server.search(None, 'UNSEEN')
        
        if status != 'OK':
            imap_server.logout()
            return {"status": "erro", "message": "Falha ao buscar emails"}
        
        email_ids = messages[0].split()
        total_emails = len(email_ids)
        
        if total_emails == 0:
            imap_server.logout()
            return {"status": "sucesso", "message": "Nenhum email novo para processar"}
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 3, "total": 10, "status": f"Encontrados {total_emails} emails"}
        )
        
        # Processar cada email
        emails_processados = 0
        anexos_processados = 0
        erros = []
        
        for i, email_id in enumerate(email_ids):
            try:
                current_task.update_state(
                    state="PROGRESS",
                    meta={
                        "current": 3 + (i * 6 / total_emails),
                        "total": 10,
                        "status": f"Processando email {i+1}/{total_emails}"
                    }
                )
                
                # Buscar email
                status, msg_data = imap_server.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Processar anexos
                for part in email_message.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    
                    if part.get('Content-Disposition') is None:
                        continue
                    
                    filename = part.get_filename()
                    if filename:
                        # Decodificar nome do arquivo se necessário
                        if decode_header(filename)[0][1] is not None:
                            filename = decode_header(filename)[0][0].decode(decode_header(filename)[0][1])
                        
                        # Verificar extensão
                        if filename.lower().endswith(('.xml', '.pdf')):
                            # Salvar anexo
                            file_content = part.get_payload(decode=True)
                            file_hash = hashlib.md5(file_content).hexdigest()
                            
                            # Verificar se já foi processado
                            db = SessionLocal()
                            try:
                                nota_existente = db.query(Nota).filter(Nota.file_hash == file_hash).first()
                                if nota_existente:
                                    continue
                                
                                # Salvar arquivo
                                upload_dir = settings.UPLOAD_DIR
                                os.makedirs(upload_dir, exist_ok=True)
                                
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                safe_filename = f"{timestamp}_{file_hash[:8]}_{filename}"
                                file_path = os.path.join(upload_dir, safe_filename)
                                
                                with open(file_path, "wb") as f:
                                    f.write(file_content)
                                
                                # Criar nota com status "processando"
                                nota = Nota(
                                    numero=f"EMAIL_{timestamp}",
                                    serie="EMAIL",
                                    file_hash=file_hash,
                                    status=StatusNota.processando
                                )
                                
                                if filename.lower().endswith('.xml'):
                                    nota.arquivo_xml_path = file_path
                                else:
                                    nota.arquivo_pdf_path = file_path
                                
                                db.add(nota)
                                db.commit()
                                
                                anexos_processados += 1
                                
                                # Enfileirar tarefa de parsing
                                if filename.lower().endswith('.xml'):
                                    from app.tasks.parsing_tasks import parse_xml_nfe
                                    parse_xml_nfe.delay(nota.id, file_path)
                                else:
                                    from app.tasks.parsing_tasks import parse_pdf_nfe
                                    parse_pdf_nfe.delay(nota.id, file_path)
                                
                            finally:
                                db.close()
                
                # Marcar email como lido
                imap_server.store(email_id, '+FLAGS', '\\Seen')
                emails_processados += 1
                
            except Exception as e:
                error_msg = f"Erro ao processar email {email_id}: {str(e)}"
                logger.error(error_msg)
                erros.append(error_msg)
                continue
        
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 9, "total": 10, "status": "Finalizando processamento"}
        )
        
        imap_server.logout()
        
        resultado = {
            "status": "sucesso",
            "emails_processados": emails_processados,
            "anexos_processados": anexos_processados,
            "erros": erros,
            "total_emails": total_emails
        }
        
        current_task.update_state(
            state="SUCCESS",
            meta=resultado
        )
        
        return resultado
        
    except Exception as e:
        error_msg = f"Erro geral no processamento de emails: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.email_tasks.processar_email_especifico")
def processar_email_especifico(self, email_id: str):
    """Tarefa para processar um email específico"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Processando email específico..."}
        )
        
        # Conectar ao servidor IMAP
        imap_server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
        imap_server.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)
        
        # Selecionar pasta "NFe"
        try:
            imap_server.select('NFe')
        except:
            imap_server.create('NFe')
            imap_server.select('NFe')
        
        # Buscar email específico
        status, msg_data = imap_server.fetch(email_id, '(RFC822)')
        
        if status != 'OK':
            imap_server.logout()
            return {"status": "erro", "message": "Email não encontrado"}
        
        email_body = msg_data[0][1]
        email_message = email.message_from_bytes(email_body)
        
        anexos_processados = 0
        erros = []
        
        # Processar anexos
        for part in email_message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            
            if part.get('Content-Disposition') is None:
                continue
            
            filename = part.get_filename()
            if filename:
                try:
                    # Decodificar nome do arquivo se necessário
                    if decode_header(filename)[0][1] is not None:
                        filename = decode_header(filename)[0][0].decode(decode_header(filename)[0][1])
                    
                    # Verificar extensão
                    if filename.lower().endswith(('.xml', '.pdf')):
                        # Salvar anexo
                        file_content = part.get_payload(decode=True)
                        file_hash = hashlib.md5(file_content).hexdigest()
                        
                        # Verificar se já foi processado
                        db = SessionLocal()
                        try:
                            nota_existente = db.query(Nota).filter(Nota.file_hash == file_hash).first()
                            if nota_existente:
                                continue
                            
                            # Salvar arquivo
                            upload_dir = settings.UPLOAD_DIR
                            os.makedirs(upload_dir, exist_ok=True)
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            safe_filename = f"{timestamp}_{file_hash[:8]}_{filename}"
                            file_path = os.path.join(upload_dir, safe_filename)
                            
                            with open(file_path, "wb") as f:
                                f.write(file_content)
                            
                            # Criar nota com status "processando"
                            nota = Nota(
                                numero=f"EMAIL_{timestamp}",
                                serie="EMAIL",
                                file_hash=file_hash,
                                status=StatusNota.processando
                            )
                            
                            if filename.lower().endswith('.xml'):
                                nota.arquivo_xml_path = file_path
                            else:
                                nota.arquivo_pdf_path = file_path
                            
                            db.add(nota)
                            db.commit()
                            
                            anexos_processados += 1
                            
                            # Enfileirar tarefa de parsing
                            if filename.lower().endswith('.xml'):
                                from app.tasks.parsing_tasks import parse_xml_nfe
                                parse_xml_nfe.delay(nota.id, file_path)
                            else:
                                from app.tasks.parsing_tasks import parse_pdf_nfe
                                parse_pdf_nfe.delay(nota.id, file_path)
                            
                        finally:
                            db.close()
                            
                except Exception as e:
                    error_msg = f"Erro ao processar anexo {filename}: {str(e)}"
                    logger.error(error_msg)
                    erros.append(error_msg)
                    continue
        
        # Marcar email como lido
        imap_server.store(email_id, '+FLAGS', '\\Seen')
        imap_server.logout()
        
        resultado = {
            "status": "sucesso",
            "anexos_processados": anexos_processados,
            "erros": erros
        }
        
        current_task.update_state(
            state="SUCCESS",
            meta=resultado
        )
        
        return resultado
        
    except Exception as e:
        error_msg = f"Erro ao processar email específico: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.email_tasks.testar_conexao_imap")
def testar_conexao_imap(self):
    """Tarefa para testar conexão IMAP"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Testando conexão IMAP..."}
        )
        
        # Conectar ao servidor IMAP
        imap_server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
        imap_server.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)
        
        # Listar pastas
        status, folders = imap_server.list()
        
        # Verificar se existe a pasta "NFe"
        nfe_folder_exists = any(b'NFe' in folder for folder in folders)
        
        imap_server.logout()
        
        resultado = {
            "status": "sucesso",
            "message": "Conexão IMAP estabelecida com sucesso",
            "pasta_nfe_existe": nfe_folder_exists,
            "pastas_disponiveis": [folder.decode() for folder in folders[:5]]
        }
        
        current_task.update_state(
            state="SUCCESS",
            meta=resultado
        )
        
        return resultado
        
    except Exception as e:
        error_msg = f"Erro na conexão IMAP: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise 