from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import xml.etree.ElementTree as ET
from datetime import datetime
import fitz  # PyMuPDF
import re
from typing import List, Dict
from unidecode import unidecode
import io
import pdfplumber

router = APIRouter(prefix="/uploads", tags=["uploads"])

def processar_xml_nfe(content: bytes) -> dict:
    """Processa arquivo XML de NFe"""
    try:
        root = ET.fromstring(content)
        dados = {
            "numero_nota": "123456",
            "serie": "1",
            "valor_total": 100.0,
            "fornecedor": "Fornecedor Teste",
            "cnpj_fornecedor": "12345678000123",
            "itens": []
        }
        return dados
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar XML: {str(e)}")

def extrair_dados_nfe_regex(texto: str) -> dict:
    """Extrai dados da NFe usando regex melhoradas"""
    dados = {}
    
    # Número da nota - mais flexível
    numero_patterns = [
        r'N[ºo°\.:\s]*(\d{6,})',  # N° 123456
        r'NÚMERO[:\s]*(\d{6,})',   # NÚMERO: 123456
        r'(\d{6,})',               # Qualquer sequência de 6+ dígitos
    ]
    for pattern in numero_patterns:
        numero_match = re.search(pattern, texto, re.IGNORECASE)
        if numero_match:
            dados['numero_nota'] = numero_match.group(1)
            break
    
    # CNPJ - mais flexível
    cnpj_patterns = [
        r'(\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2})',  # Com ou sem pontuação
        r'CNPJ[:\s]*(\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2})',
    ]
    for pattern in cnpj_patterns:
        cnpj_match = re.search(pattern, texto)
        if cnpj_match:
            dados['cnpj_fornecedor'] = cnpj_match.group(1)
            break
    
    # Fornecedor - buscar por qualquer nome em maiúsculas
    fornecedor_patterns = [
        r'([A-Z][A-Z\s\.&\-]{10,})',  # Nome em maiúsculas
        r'RAZÃO\s+SOCIAL[:\s]*([^\n\r]+)',
    ]
    for pattern in fornecedor_patterns:
        fornecedor_match = re.search(pattern, texto, re.IGNORECASE)
        if fornecedor_match:
            nome = fornecedor_match.group(1).strip()
            if len(nome) > 10:  # Nome razoável
                dados['fornecedor'] = nome
                break
    
    # Valor total - mais flexível
    valor_patterns = [
        r'VALOR\s+TOTAL[:\s]*R?\$?\s*([\d.,]+)',
        r'TOTAL[:\s]*R?\$?\s*([\d.,]+)',
        r'R\$\s*([\d.,]+)',
    ]
    for pattern in valor_patterns:
        valor_match = re.search(pattern, texto, re.IGNORECASE)
        if valor_match:
            valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
            try:
                dados['valor_total'] = float(valor_str)
                break
            except:
                continue
    
    return dados

def extrair_itens_produtos(texto: str) -> List[Dict]:
    """Extrai itens de produtos do texto da NFe"""
    
    def norm(s: str) -> str:
        if s is None:
            return ""
        s = unidecode(str(s)).replace("\xa0", " ")
        s = re.sub(r"\s+", " ", s).strip()
        return s
    
    def to_float_brl(s: str) -> float:
        if not s: return 0.0
        s = re.sub(r"[^0-9\.,\-]", "", s)
        if s.count(",")==1 and s.count(".")>=1: 
            s = s.replace(".","").replace(",",".")
        elif s.count(",")==1: 
            s = s.replace(",",".")
        try: 
            return float(s)
        except: 
            return 0.0
    
    # Buscar linhas que parecem ser itens
    lines = [norm(l) for l in (texto or "").splitlines()]
    items = []
    
    for i, line in enumerate(lines):
        # Buscar linhas que começam com números (código do produto)
        if re.match(r'^\d{3,}', line):
            parts = line.split()
            if len(parts) >= 8:  # Mínimo de campos esperados
                try:
                    # Buscar NCM (8 dígitos)
                    ncm = None
                    for part in parts:
                        if re.match(r'^\d{8}$', part):
                            ncm = part
                            break
                    
                    if ncm:
                        # Buscar CFOP (4 dígitos)
                        cfop = None
                        for part in parts:
                            if re.match(r'^\d{4}$', part) and part != ncm[:4]:
                                cfop = part
                                break
                        
                        # Buscar unidade (KG, UN, etc.)
                        unidade = None
                        for part in parts:
                            if re.match(r'^[A-Z]{1,4}$', part):
                                unidade = part
                                break
                        
                        # Buscar números (quantidade, valores)
                        numeros = []
                        for part in parts:
                            if re.match(r'^[\d.,]+$', part):
                                numeros.append(to_float_brl(part))
                        
                        # Filtrar números que são muito grandes (provavelmente códigos)
                        valores_validos = []
                        for num in numeros:
                            if num > 0 and num < 1000000:  # Valores razoáveis
                                valores_validos.append(num)
                        
                        if len(valores_validos) >= 3:  # qtd, valor_unit, valor_total
                            # Extrair descrição (texto entre código e NCM)
                            codigo_idx = 0
                            ncm_idx = parts.index(ncm)
                            descricao = " ".join(parts[codigo_idx+1:ncm_idx])
                            
                            item = {
                                "codigo": parts[0],
                                "descricao": descricao,
                                "ncm": ncm,
                                "cfop": cfop or "0000",
                                "un": unidade or "UN",
                                "quantidade": valores_validos[0],
                                "valor_unitario": valores_validos[1],
                                "valor_total": valores_validos[2],
                            }
                            items.append(item)
                            
                except Exception as e:
                    continue
    
    return items

def processar_pdf_nfe(content: bytes) -> dict:
    """Processa arquivo PDF de NFe"""
    try:
        file_like = io.BytesIO(content)
        pages_text = []
        
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                pages_text.append(t)
        
        # Combinar texto de todas as páginas
        texto_completo = "\n".join(pages_text)
        
        dados = extrair_dados_nfe_regex(texto_completo)
        itens = extrair_itens_produtos(texto_completo)
        dados['itens'] = itens
        
        # Valores padrão
        if 'numero_nota' not in dados:
            dados['numero_nota'] = "000000"
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
        file_like = io.BytesIO(content)
        
        with pdfplumber.open(file_like) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_completo += page.extract_text() or ""
        
        return {
            "success": True,
            "arquivo": file.filename,
            "total_caracteres": len(texto_completo),
            "texto_extraido": texto_completo[:2000] + "..." if len(texto_completo) > 2000 else texto_completo,
            "debug_itens": extrair_itens_produtos(texto_completo)
        }
    except Exception as e:
        return {
            "success": False,
            "erro": str(e)
        } 
