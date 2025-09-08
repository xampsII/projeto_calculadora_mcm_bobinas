from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.nota import Nota, NotaItem
from app.models.enums import StatusNota
from app.models.fornecedor import Fornecedor
from app.models.materia_prima import MateriaPrima, MateriaPrimaPreco
from app.models.enums import OrigemPreco
from app.models.unidade import Unidade
from app.config import get_settings
from lxml import etree
import logging
import re
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, name="app.tasks.parsing_tasks.parse_xml_nfe")
def parse_xml_nfe(self, nota_id: int, file_path: str):
    """Tarefa para fazer parsing de XML de NF-e"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando parsing XML..."}
        )
        
        db = SessionLocal()
        
        try:
            # Buscar a nota
            nota = db.query(Nota).filter(Nota.id == nota_id).first()
            if not nota:
                raise Exception("Nota não encontrada")
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Lendo arquivo XML..."}
            )
            
            # Ler e parsear XML
            with open(file_path, 'rb') as f:
                xml_content = f.read()
            
            # Parsear XML
            root = etree.fromstring(xml_content)
            
            # Definir namespaces comuns de NF-e
            namespaces = {
                'nfe': 'http://www.portalfiscal.inf.br/nfe',
                'ns2': 'http://www.w3.org/2000/09/xmldsig#'
            }
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Extraindo dados da NF-e..."}
            )
            
            # Extrair dados básicos da nota
            try:
                # Chave de acesso
                chave_acesso = root.find('.//nfe:chNFe', namespaces)
                if chave_acesso is not None and chave_acesso.text:
                    nota.chave_acesso = chave_acesso.text
                
                # Número da nota
                numero = root.find('.//nfe:nNF', namespaces)
                if numero is not None and numero.text:
                    nota.numero = numero.text
                
                # Série
                serie = root.find('.//nfe:serie', namespaces)
                if serie is not None and serie.text:
                    nota.serie = serie.text
                
                # Data de emissão
                dh_emi = root.find('.//nfe:dhEmi', namespaces)
                if dh_emi is not None and dh_emi.text:
                    try:
                        # Converter formato de data da NF-e
                        data_str = dh_emi.text.split('T')[0]  # Pegar apenas a data
                        nota.emissao_date = datetime.strptime(data_str, '%Y-%m-%d').date()
                    except:
                        pass
                
            except Exception as e:
                logger.warning(f"Erro ao extrair dados básicos: {e}")
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Processando fornecedor..."}
            )
            
            # Extrair dados do fornecedor (emitente)
            try:
                emit_cnpj = root.find('.//nfe:emit/nfe:CNPJ', namespaces)
                emit_nome = root.find('.//nfe:emit/nfe:xNome', namespaces)
                
                if emit_cnpj is not None and emit_cnpj.text:
                    # Buscar ou criar fornecedor
                    fornecedor = db.query(Fornecedor).filter(
                        Fornecedor.cnpj == emit_cnpj.text
                    ).first()
                    
                    if not fornecedor:
                        fornecedor = Fornecedor(
                            cnpj=emit_cnpj.text,
                            nome=emit_nome.text if emit_nome is not None else "Fornecedor não identificado",
                            endereco="Endereço não disponível"
                        )
                        db.add(fornecedor)
                        db.commit()
                        db.refresh(fornecedor)
                    
                    nota.fornecedor_id = fornecedor.id
                
            except Exception as e:
                logger.warning(f"Erro ao processar fornecedor: {e}")
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Processando itens..."}
            )
            
            # Extrair itens da nota
            itens = root.findall('.//nfe:det', namespaces)
            valor_total = Decimal('0')
            
            for i, item in enumerate(itens):
                try:
                    # Dados do produto
                    prod = item.find('.//nfe:prod', namespaces)
                    if prod is None:
                        continue
                    
                    # Nome do produto
                    nome_prod = prod.find('.//nfe:xProd', namespaces)
                    nome_produto = nome_prod.text if nome_prod is not None else f"Item {i+1}"
                    
                    # Unidade
                    unidade = prod.find('.//nfe:uCom', namespaces)
                    unidade_codigo = unidade.text if unidade is not None else "un"
                    
                    # Quantidade
                    quantidade = prod.find('.//nfe:qCom', namespaces)
                    qtd = Decimal(quantidade.text) if quantidade is not None else Decimal('1')
                    
                    # Valor unitário
                    valor_unit = prod.find('.//nfe:vUnCom', namespaces)
                    valor_unitario = Decimal(valor_unit.text) if valor_unit is not None else Decimal('0')
                    
                    # Valor total do item
                    valor_item = prod.find('.//nfe:vProd', namespaces)
                    valor_total_item = Decimal(valor_item.text) if valor_item is not None else (qtd * valor_unitario)
                    
                    valor_total += valor_total_item
                    
                    # Buscar ou criar matéria-prima
                    materia_prima = db.query(MateriaPrima).filter(
                        MateriaPrima.nome == nome_produto
                    ).first()
                    
                    if not materia_prima:
                        # Verificar se a unidade existe
                        unidade_obj = db.query(Unidade).filter(
                            Unidade.codigo == unidade_codigo
                        ).first()
                        
                        if not unidade_obj:
                            # Criar unidade se não existir
                            unidade_obj = Unidade(
                                codigo=unidade_codigo,
                                descricao=f"Unidade {unidade_codigo}",
                                is_base=True
                            )
                            db.add(unidade_obj)
                            db.commit()
                            db.refresh(unidade_obj)
                        
                        materia_prima = MateriaPrima(
                            nome=nome_produto,
                            unidade_codigo=unidade_codigo
                        )
                        db.add(materia_prima)
                        db.commit()
                        db.refresh(materia_prima)
                    
                    # Criar item da nota
                    nota_item = NotaItem(
                        nota_id=nota.id,
                        materia_prima_id=materia_prima.id,
                        nome_no_documento=nome_produto,
                        unidade_codigo=unidade_codigo,
                        quantidade=qtd,
                        valor_unitario=valor_unitario,
                        valor_total=valor_total_item
                    )
                    db.add(nota_item)
                    
                    # Criar/atualizar preço da matéria-prima
                    preco_existente = db.query(MateriaPrimaPreco).filter(
                        MateriaPrimaPreco.materia_prima_id == materia_prima.id,
                        MateriaPrimaPreco.vigente_ate.is_(None)
                    ).first()
                    
                    if preco_existente:
                        # Fechar preço anterior
                        preco_existente.vigente_ate = nota.emissao_date or datetime.now().date()
                        db.add(preco_existente)
                    
                    novo_preco = MateriaPrimaPreco(
                        materia_prima_id=materia_prima.id,
                        valor_unitario=valor_unitario,
                        vigente_desde=nota.emissao_date or datetime.now().date(),
                        origem=OrigemPreco.nota_xml,
                        fornecedor_id=nota.fornecedor_id,
                        nota_id=nota.id
                    )
                    db.add(novo_preco)
                    
                except Exception as e:
                    logger.warning(f"Erro ao processar item {i}: {e}")
                    continue
            
            # Atualizar valor total da nota
            if valor_total > 0:
                nota.valor_total = valor_total
            
            # Marcar nota como processada
            nota.status = StatusNota.processada
            
            db.commit()
            
            current_task.update_state(
                state="SUCCESS",
                meta={"status": "XML processado com sucesso"}
            )
            
            return {
                "status": "sucesso",
                "message": "XML processado com sucesso",
                "itens_processados": len(itens),
                "valor_total": float(valor_total)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro ao processar XML: {str(e)}"
        logger.error(error_msg)
        
        # Marcar nota como falha
        try:
            db = SessionLocal()
            nota = db.query(Nota).filter(Nota.id == nota_id).first()
            if nota:
                nota.status = StatusNota.falha
                db.commit()
        except:
            pass
        finally:
            db.close()
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.parsing_tasks.parse_pdf_nfe")
def parse_pdf_nfe(self, nota_id: int, file_path: str):
    """Tarefa para fazer parsing de PDF de NF-e (best-effort)"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Iniciando parsing PDF..."}
        )
        
        db = SessionLocal()
        
        try:
            # Buscar a nota
            nota = db.query(Nota).filter(Nota.id == nota_id).first()
            if not nota:
                raise Exception("Nota não encontrada")
            
            current_task.update_state(
                state="PROGRESS",
                meta={"status": "Lendo arquivo PDF..."}
            )
            
            # TODO: Implementar parsing de PDF usando pdfminer.six
            # Por enquanto, marcar como falha
            nota.status = StatusNota.falha
            
            db.commit()
            
            current_task.update_state(
                state="SUCCESS",
                meta={"status": "PDF marcado como falha (parsing não implementado)"}
            )
            
            return {
                "status": "falha",
                "message": "Parsing de PDF não implementado",
                "nota_id": nota_id
            }
            
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro ao processar PDF: {str(e)}"
        logger.error(error_msg)
        
        # Marcar nota como falha
        try:
            db = SessionLocal()
            nota = db.query(Nota).filter(Nota.id == nota_id).first()
            if nota:
                nota.status = StatusNota.falha
                db.commit()
        except:
            pass
        finally:
            db.close()
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.parsing_tasks.reprocessar_nota")
def reprocessar_nota(self, nota_id: int):
    """Tarefa para reprocessar uma nota que falhou"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Reprocessando nota..."}
        )
        
        db = SessionLocal()
        
        try:
            # Buscar a nota
            nota = db.query(Nota).filter(Nota.id == nota_id).first()
            if not nota:
                raise Exception("Nota não encontrada")
            
            # Verificar se tem arquivo XML ou PDF
            if nota.arquivo_xml_path and os.path.exists(nota.arquivo_xml_path):
                # Reprocessar XML
                return parse_xml_nfe.delay(nota_id, nota.arquivo_xml_path)
            elif nota.arquivo_pdf_path and os.path.exists(nota.arquivo_pdf_path):
                # Reprocessar PDF
                return parse_pdf_nfe.delay(nota_id, nota.arquivo_pdf_path)
            else:
                raise Exception("Nenhum arquivo encontrado para reprocessamento")
                
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Erro ao reprocessar nota: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise


@celery_app.task(bind=True, name="app.tasks.parsing_tasks.validar_xml")
def validar_xml(self, file_path: str):
    """Tarefa para validar estrutura de XML de NF-e"""
    try:
        current_task.update_state(
            state="PROGRESS",
            meta={"status": "Validando XML..."}
        )
        
        # Ler arquivo
        with open(file_path, 'rb') as f:
            xml_content = f.read()
        
        # Tentar parsear XML
        try:
            root = etree.fromstring(xml_content)
        except etree.XMLSyntaxError as e:
            return {
                "status": "erro",
                "message": "XML malformado",
                "erro": str(e)
            }
        
        # Verificar se é uma NF-e válida
        namespaces = {
            'nfe': 'http://www.portalfiscal.inf.br/nfe'
        }
        
        # Verificar elementos obrigatórios
        elementos_obrigatorios = [
            './/nfe:chNFe',
            './/nfe:nNF',
            './/nfe:serie',
            './/nfe:emit',
            './/nfe:det'
        ]
        
        elementos_faltantes = []
        for elemento in elementos_obrigatorios:
            if root.find(elemento, namespaces) is None:
                elementos_faltantes.append(elemento)
        
        if elementos_faltantes:
            return {
                "status": "erro",
                "message": "Elementos obrigatórios não encontrados",
                "elementos_faltantes": elementos_faltantes
            }
        
        # Contar itens
        itens = root.findall('.//nfe:det', namespaces)
        
        current_task.update_state(
            state="SUCCESS",
            meta={"status": "XML validado com sucesso"}
        )
        
        return {
            "status": "sucesso",
            "message": "XML válido",
            "total_itens": len(itens),
            "estrutura_valida": True
        }
        
    except Exception as e:
        error_msg = f"Erro ao validar XML: {str(e)}"
        logger.error(error_msg)
        
        current_task.update_state(
            state="FAILURE",
            meta={"status": "erro", "message": error_msg}
        )
        
        raise 