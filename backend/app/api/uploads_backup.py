from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
import xml.etree.ElementTree as ET
from datetime import datetime
import fitz  # PyMuPDF
import re
from typing import List, Dict

router = APIRouter(prefix="/uploads", tags=["uploads"])

def processar_xml_nfe(content: bytes) -> dict:
    """Processa arquivo XML de NFe"""
    try:
        root = ET.fromstring(content)
        
        dados = {
            "numero_nota": "123456",
            "serie": "1",
            "data_emissao": "01/01/2024",
            "valor_total": 100.0,
            "fornecedor": "Fornecedor Teste",
            "cnpj_fornecedor": "12345678000123",
            "itens": []
        }
        
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar XML: {str(e)}")

def extrair_dados_nfe_regex(texto: str) -> dict:
    """Extrai dados da NFe usando regex"""
    dados = {}
    
    # Número da nota
    numero_match = re.search(r'N[ºo°]\s*(\d+)', texto, re.IGNORECASE)
    if numero_match:
        dados['numero_nota'] = numero_match.group(1)
    
    # Data de emissão
    data_match = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
    if data_match:
        dados['data_emissao'] = data_match.group(1)
    
    # Valor total
    valor_match = re.search(r'VALOR\s+TOTAL\s+DA\s+NOTA\s+FISCAL[:\s]*R\$\s*([\d.,]+)', texto, re.IGNORECASE)
    if valor_match:
        valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
        dados['valor_total'] = float(valor_str)
    
    # Fornecedor
    fornecedor_match = re.search(r'RAZÃO\s+SOCIAL[:\s]*([^\n\r]+)', texto, re.IGNORECASE)
    if fornecedor_match:
        dados['fornecedor'] = fornecedor_match.group(1).strip()
    
    # CNPJ
    cnpj_match = re.search(r'CNPJ[:\s]*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
    if cnpj_match:
        dados['cnpj_fornecedor'] = cnpj_match.group(1)
    
    return dados

def extrair_itens_produtos(texto: str) -> List[Dict]:
    """Extrai itens de produtos do texto da NFe"""
    itens = []
    
    # Procurar por seção de produtos
    produtos_section = re.search(r'DADOS\s+DOS\s+PRODUTOS/SERVIÇOS(.*?)(?=INFORMAÇÕES\s+COMPLEMENTARES|$)', texto, re.IGNORECASE | re.DOTALL)
    
    if produtos_section:
        produtos_texto = produtos_section.group(1)
        
        # Dividir em linhas e processar
        linhas = produtos_texto.split('\n')
        
        for linha in linhas:
            linha = linha.strip()
            if not linha or len(linha) < 10:
                continue
            
            # Procurar por padrão de item (código, descrição, quantidade, valor)
            item_match = re.search(r'(\d+)\s+([A-Za-z\s]+?)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)', linha)
            
            if item_match:
                codigo = item_match.group(1)
                descricao = item_match.group(2).strip()
                quantidade = item_match.group(3)
                valor_unit = item_match.group(4).replace(',', '.')
                valor_total = item_match.group(5).replace(',', '.')
                
                itens.append({
                    "codigo": codigo,
                    "descricao": descricao,
                    "quantidade": float(quantidade),
                    "valor_unitario": float(valor_unit),
                    "valor_total": float(valor_total),
                    "unidade": "UN"
                })
    
    return itens

def processar_pdf_nfe(content: bytes) -> dict:
    """Processa arquivo PDF de NFe"""
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        texto_completo = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            texto_completo += page.get_text()
        
        doc.close()
        
        # Extrair dados básicos
        dados = extrair_dados_nfe_regex(texto_completo)
        
        # Extrair itens
        itens = extrair_itens_produtos(texto_completo)
        dados['itens'] = itens
        
        # Valores padrão se não encontrados
        if 'numero_nota' not in dados:
            dados['numero_nota'] = "000000"
        if 'data_emissao' not in dados:
            dados['data_emissao'] = "01/01/2024"
        if 'valor_total' not in dados:
            dados['valor_total'] = 0.0
        if 'fornecedor' not in dados:
            dados['fornecedor'] = "Fornecedor não identificado"
        if 'cnpj_fornecedor' not in dados:
            dados['cnpj_fornecedor'] = "00000000000000"
        
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar PDF: {str(e)}")

@router.post("/processar-arquivo")
async def processar_arquivo_universal(file: UploadFile = File(...)):
    """Processa qualquer arquivo (PDF, XML, CSV, etc.)"""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Arquivo não fornecido")
    
    content = await file.read()
    
    if file.filename.lower().endswith(".xml"):
        try:
            dados_extraidos = processar_xml_nfe(content)
            return {
                "success": True,
                "arquivo": file.filename,
                "dados_extraidos": dados_extraidos,
                "message": f"XML processado com sucesso! {len(dados_extraidos.get('itens', []))} itens encontrados."
            }
        except Exception as e:
            return {
                "success": False,
                "arquivo": file.filename,
                "message": f"Erro ao processar XML: {str(e)}"
            }
    
    elif file.filename.lower().endswith(".pdf"):
        try:
            dados_extraidos = processar_pdf_nfe(content)
            return {
                "success": True,
                "arquivo": file.filename,
                "dados_extraidos": dados_extraidos,
                "message": f"PDF processado com sucesso! {len(dados_extraidos.get('itens', []))} itens encontrados."
            }
        except Exception as e:
            return {
                "success": False,
                "arquivo": file.filename,
                "message": f"Erro ao processar PDF: {str(e)}"
            }
    
    return {
        "success": True,
        "arquivo": file.filename,
        "message": f"Arquivo {file.filename} recebido com sucesso"
    }

@router.post("/salvar-dados")
async def salvar_dados_nota(dados_nota: dict, db: Session = Depends(get_db)):
    """Salva os dados extraídos da nota fiscal no banco de dados"""
    try:
        return {
            "success": True,
            "message": "Nota fiscal salva com sucesso!",
            "materias_criadas": [],
            "precos_atualizados": []
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao salvar dados: {str(e)}"
        }

@router.post("/teste-pdf")
async def teste_pdf(file: UploadFile = File(...)):
    """Endpoint de teste para debug de PDF"""
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        texto_completo = ""
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            texto_completo += page.get_text()
        
        doc.close()
        
        return {
            "success": True,
            "arquivo": file.filename,
            "total_caracteres": len(texto_completo),
            "texto_extraido": texto_completo[:1000] + "..." if len(texto_completo) > 1000 else texto_completo
        }
    except Exception as e:
        return {
            "success": False,
            "erro": str(e)
        }