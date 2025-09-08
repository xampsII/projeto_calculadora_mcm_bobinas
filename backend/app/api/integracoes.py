from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import imaplib
import email
import os
from email.header import decode_header
import hashlib
import asyncio

from app.database import get_db
from app.models.user import User
from app.models.nota import Nota
from app.models.enums import StatusNota
from app.models.fornecedor import Fornecedor
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.enums import OrigemPreco
from app.models.unidade import Unidade
from app.auth.dependencies import get_current_active_user, require_admin
from app.config import settings

router = APIRouter(prefix="/integracoes", tags=["Integrações"])

@router.get("/ping")
def ping_integracoes():
    return {"ok": True}


@router.post("/email/processar")
async def processar_emails(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Inicia o processamento de emails em background"""
    background_tasks.add_task(processar_emails_background, db)
    
    return {
        "message": "Processamento de emails iniciado em background",
        "status": "iniciado",
        "timestamp": datetime.now()
    }


@router.get("/email/status")
async def get_email_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém status do processamento de emails"""
    # Contar notas por status
    total_notas = db.query(Nota).count()
    notas_processando = db.query(Nota).filter(Nota.status == StatusNota.processando).count()
    notas_processadas = db.query(Nota).filter(Nota.status == StatusNota.processada).count()
    notas_falha = db.query(Nota).filter(Nota.status == StatusNota.falha).count()
    
    # Última execução (simulado - em produção seria armazenado em cache/DB)
    ultima_execucao = datetime.now() - timedelta(hours=1)  # Simulado
    
    return {
        "status": "ativo",
        "ultima_execucao": ultima_execucao,
        "proxima_execucao": ultima_execucao + timedelta(minutes=5),
        "estatisticas": {
            "total_notas": total_notas,
            "processando": notas_processando,
            "processadas": notas_processadas,
            "falha": notas_falha
        }
    }


@router.post("/email/testar-conexao")
async def testar_conexao_email(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Testa a conexão com o servidor IMAP"""
    try:
        # Conectar ao servidor IMAP
        imap_server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
        imap_server.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)
        
        # Listar pastas
        status, folders = imap_server.list()
        
        # Verificar se existe a pasta "NFe"
        nfe_folder_exists = any(b'NFe' in folder for folder in folders)
        
        imap_server.logout()
        
        return {
            "status": "sucesso",
            "message": "Conexão IMAP estabelecida com sucesso",
            "pasta_nfe_existe": nfe_folder_exists,
            "pastas_disponiveis": [folder.decode() for folder in folders[:5]]  # Primeiras 5 pastas
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na conexão IMAP: {str(e)}"
        )


@router.get("/email/contadores")
async def get_email_counters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém contadores de emails processados"""
    # Contar notas por origem
    notas_por_origem = db.query(
        Nota.arquivo_xml_path,
        Nota.arquivo_pdf_path
    ).filter(Nota.status.in_([StatusNota.processada, StatusNota.falha])).all()
    
    xml_count = sum(1 for nota in notas_por_origem if nota.arquivo_xml_path)
    pdf_count = sum(1 for nota in notas_por_origem if nota.arquivo_pdf_path)
    
    # Contar por período (últimos 30 dias)
    data_limite = datetime.now() - timedelta(days=30)
    notas_recentes = db.query(Nota).filter(
        Nota.created_at >= data_limite
    ).count()
    
    return {
        "total_notas": len(notas_por_origem),
        "xml_processados": xml_count,
        "pdf_processados": pdf_count,
        "notas_ultimos_30_dias": notas_recentes,
        "periodo_analise": {
            "inicio": data_limite,
            "fim": datetime.now()
        }
    }


@router.post("/api-externa/simular")
async def simular_api_externa(
    chave_acesso: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Simula resposta de API externa para testes"""
    # Validar formato da chave de acesso
    if len(chave_acesso) != 44:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chave de acesso deve ter 44 dígitos"
        )
    
    if not chave_acesso.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chave de acesso deve conter apenas números"
        )
    
    # Simular resposta de API externa
    nota_simulada = {
        "chave_acesso": chave_acesso,
        "numero": "12345",
        "serie": "1",
        "emissao": datetime.now().isoformat(),
        "fornecedor": {
            "cnpj": "12345678000195",
            "nome": "Fornecedor Simulado LTDA",
            "endereco": "Rua Simulada, 123 - São Paulo/SP"
        },
        "itens": [
            {
                "nome": "Matéria-prima Simulada 1",
                "unidade": "kg",
                "quantidade": 10.5,
                "valor_unitario": 15.75,
                "valor_total": 165.38
            },
            {
                "nome": "Matéria-prima Simulada 2",
                "unidade": "m",
                "quantidade": 25.0,
                "valor_unitario": 8.50,
                "valor_total": 212.50
            }
        ],
        "valor_total": 377.88
    }
    
    return {
        "message": "Simulação de API externa",
        "nota": nota_simulada,
        "timestamp": datetime.now(),
        "api_version": "1.0"
    }


@router.get("/api-externa/status")
async def get_api_externa_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém status das integrações com APIs externas"""
    return {
        "status": "simulado",
        "message": "Integração com API externa em modo simulado",
        "endpoints_disponiveis": [
            "POST /integracoes/api-externa/simular",
            "GET /integracoes/api-externa/status"
        ],
        "configuracoes": {
            "modo": "simulado",
            "timeout": "30s",
            "retry_attempts": 3
        }
    }


async def processar_emails_background(db: Session):
    """Processa emails em background (será executado pelo Celery)"""
    try:
        # Conectar ao servidor IMAP
        imap_server = imaplib.IMAP4_SSL(settings.IMAP_HOST)
        imap_server.login(settings.IMAP_USERNAME, settings.IMAP_PASSWORD)
        
        # Selecionar pasta "NFe" (criar se não existir)
        try:
            imap_server.select('NFe')
        except:
            # Pasta não existe, criar
            imap_server.create('NFe')
            imap_server.select('NFe')
        
        # Buscar emails não lidos
        status, messages = imap_server.search(None, 'UNSEEN')
        
        if status != 'OK':
            return
        
        email_ids = messages[0].split()
        
        for email_id in email_ids:
            try:
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
                
                # Marcar email como lido
                imap_server.store(email_id, '+FLAGS', '\\Seen')
                
            except Exception as e:
                # Log do erro
                print(f"Erro ao processar email {email_id}: {str(e)}")
                continue
        
        imap_server.logout()
        
    except Exception as e:
        # Log do erro geral
        print(f"Erro no processamento de emails: {str(e)}")


@router.post("/sincronizar")
async def sincronizar_dados(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Inicia sincronização de dados em background"""
    background_tasks.add_task(sincronizar_dados_background, db)
    
    return {
        "message": "Sincronização de dados iniciada em background",
        "status": "iniciado",
        "timestamp": datetime.now()
    }


async def sincronizar_dados_background(db: Session):
    """Sincroniza dados em background (será executado pelo Celery)"""
    try:
        # TODO: Implementar sincronização com sistemas externos
        # Por exemplo: ERP, CRM, sistemas de fornecedores
        
        # Simular sincronização
        await asyncio.sleep(5)
        
        print("Sincronização de dados concluída")
        
    except Exception as e:
        print(f"Erro na sincronização: {str(e)}")


@router.get("/logs")
async def get_integration_logs(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém logs de integração (simulado)"""
    # Em produção, isso viria de uma tabela de logs
    logs_simulados = [
        {
            "id": 1,
            "timestamp": datetime.now() - timedelta(minutes=5),
            "level": "INFO",
            "message": "Processamento de emails iniciado",
            "details": "5 emails processados com sucesso"
        },
        {
            "id": 2,
            "timestamp": datetime.now() - timedelta(minutes=10),
            "level": "WARNING",
            "message": "Timeout na API externa",
            "details": "Tentativa de reconexão em 30s"
        },
        {
            "id": 3,
            "timestamp": datetime.now() - timedelta(minutes=15),
            "level": "ERROR",
            "message": "Falha na conexão IMAP",
            "details": "Credenciais inválidas"
        }
    ]
    
    total = len(logs_simulados)
    offset = (page - 1) * page_size
    logs_paginados = logs_simulados[offset:offset + page_size]
    
    return {
        "logs": logs_paginados,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    } 