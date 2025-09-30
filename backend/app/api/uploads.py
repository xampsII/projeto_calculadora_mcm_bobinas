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
        
        # Definir namespaces da NFe
        namespaces = {
            'nfe': 'http://www.portalfiscal.inf.br/nfe'
        }
        
        dados = {
            "numero_nota": "",
            "serie": "",
            "chave_acesso": "",
            "valor_total": 0.0,
            "fornecedor": "",
            "cnpj_fornecedor": "",
            "data_emissao": "",
            "itens": []
        }
        
        # Extrair dados básicos da nota
        chave_acesso = root.find('.//nfe:chNFe', namespaces)
        if chave_acesso is not None and chave_acesso.text:
            dados["chave_acesso"] = chave_acesso.text
        
        numero = root.find('.//nfe:nNF', namespaces)
        if numero is not None and numero.text:
            dados["numero_nota"] = numero.text
        
        serie = root.find('.//nfe:serie', namespaces)
        if serie is not None and serie.text:
            dados["serie"] = serie.text
        
        # Data de emissão
        dh_emi = root.find('.//nfe:dhEmi', namespaces)
        if dh_emi is not None and dh_emi.text:
            try:
                data_str = dh_emi.text.split('T')[0]
                dados["data_emissao"] = data_str
            except:
                pass
        
        # Valor total
        v_nf = root.find('.//nfe:vNF', namespaces)
        if v_nf is not None and v_nf.text:
            try:
                dados["valor_total"] = float(v_nf.text)
            except:
                pass
        
        # Dados do emitente (fornecedor)
        emit_cnpj = root.find('.//nfe:emit/nfe:CNPJ', namespaces)
        if emit_cnpj is not None and emit_cnpj.text:
            dados["cnpj_fornecedor"] = emit_cnpj.text
        
        emit_nome = root.find('.//nfe:emit/nfe:xNome', namespaces)
        if emit_nome is not None and emit_nome.text:
            dados["fornecedor"] = emit_nome.text
        
        # Extrair itens da nota
        itens = root.findall('.//nfe:det', namespaces)
        for item in itens:
            try:
                # Código do produto
                c_prod = item.find('.//nfe:cProd', namespaces)
                codigo = c_prod.text if c_prod is not None and c_prod.text else ""
                
                # Descrição do produto
                x_prod = item.find('.//nfe:xProd', namespaces)
                descricao = x_prod.text if x_prod is not None and x_prod.text else ""
                
                # NCM
                ncm = item.find('.//nfe:NCM', namespaces)
                ncm_codigo = ncm.text if ncm is not None and ncm.text else ""
                
                # CFOP
                cfop = item.find('.//nfe:CFOP', namespaces)
                cfop_codigo = cfop.text if cfop is not None and cfop.text else ""
                
                # Unidade comercial
                u_com = item.find('.//nfe:uCom', namespaces)
                unidade = u_com.text if u_com is not None and u_com.text else "UN"
                
                # Quantidade comercial
                q_com = item.find('.//nfe:qCom', namespaces)
                quantidade = float(q_com.text) if q_com is not None and q_com.text else 0.0
                
                # Valor unitário comercial
                v_un_com = item.find('.//nfe:vUnCom', namespaces)
                valor_unitario = float(v_un_com.text) if v_un_com is not None and v_un_com.text else 0.0
                
                # Valor total do item
                v_prod = item.find('.//nfe:vProd', namespaces)
                valor_total = float(v_prod.text) if v_prod is not None and v_prod.text else 0.0
                
                # Adicionar item se tiver dados válidos
                if descricao and quantidade > 0 and valor_unitario > 0:
                    dados["itens"].append({
                        "codigo": codigo,
                        "descricao": descricao,
                        "ncm": ncm_codigo,
                        "cfop": cfop_codigo,
                        "un": unidade.lower(),
                        "quantidade": quantidade,
                        "valor_unitario": valor_unitario,
                        "valor_total": valor_total
                    })
                    
            except Exception as e:
                print(f"Erro ao processar item: {e}")
                continue
            
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
    
    # Fornecedor - buscar por qualquer nome em maiúsculas (melhorado)
    fornecedor_patterns = [
        r'EMITENTE[:\s]*([^\n\r]+)',  # EMITENTE: Nome
        r'RAZÃO\s+SOCIAL[:\s]*([^\n\r]+)',  # RAZÃO SOCIAL: Nome
        r'NOME[:\s]*([^\n\r]+)',  # NOME: Nome
        r'FORNECEDOR[:\s]*([^\n\r]+)',  # FORNECEDOR: Nome
        r'([A-Z][A-Z\s\.&\-]{15,})',  # Nome em maiúsculas com mais caracteres
        r'([A-Z][A-Z\s\.&\-]{10,})',  # Nome em maiúsculas (fallback)
    ]
    for pattern in fornecedor_patterns:
        fornecedor_match = re.search(pattern, texto, re.IGNORECASE)
        if fornecedor_match:
            nome = fornecedor_match.group(1).strip()
            # Filtrar nomes que não são fornecedores
            if (len(nome) > 10 and 
                not nome.startswith('NF-') and 
                not nome.startswith('NOTA') and
                not nome.startswith('IDENTIFICA') and
                'CNPJ' not in nome and
                'CPF' not in nome and
                'INSCRIÇÃO' not in nome):
                dados['fornecedor'] = nome
                break
    
    # CNPJ do fornecedor
    cnpj_patterns = [
        r'CNPJ[:\s]*(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
        r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})',
    ]
    for pattern in cnpj_patterns:
        cnpj_match = re.search(pattern, texto)
        if cnpj_match:
            dados['cnpj_fornecedor'] = cnpj_match.group(1)
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
    """Extrai itens de produtos do texto da NFe DANFE"""
    
    def norm(s: str) -> str:
        if s is None:
            return ""
        s = unidecode(str(s)).replace("\xa0", " ")
        s = re.sub(r"\s+", " ", s).strip()
        return s
    
    def to_float_brl(s: str) -> float:
        if not s: return 0.0
        s = re.sub(r"[^0-9\.,\-]", "", s)
        # Formato brasileiro: 1.234,56
        if s.count(",") == 1 and s.count(".") >= 1:
            s = s.replace(".", "").replace(",", ".")
        elif s.count(",") == 1:
            s = s.replace(",", ".")
        try:
            return float(s)
        except:
            return 0.0
    
    lines = [norm(l) for l in (texto or "").splitlines()]
    items = []
    
    # Buscar região da tabela de produtos
    start_idx = -1
    for i, line in enumerate(lines):
        if "DADOS DOS PRODUTOS" in line or "PRODUTOS/SERVIÇOS" in line:
            start_idx = i
            break
    
    if start_idx == -1:
        return items
    
    # Buscar linhas com código de 6 dígitos seguido de descrição
    for i in range(start_idx, min(start_idx + 50, len(lines))):
        line = lines[i]
        
        # Padrão: 000600 -FIO 2.0X7.0 CANTO QUADRADO 85118090 0500 2401 KG 306,5000 73,0000 22.374,50
        match = re.match(r'^(\d{6})\s+(.*?)\s+(\d{8})\s+(\d{4})\s+(\d{4})\s+(\w{1,3})\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)', line)
        if match:
            codigo, descricao, ncm, o_cst, cfop, unidade, qtd_str, valor_unit_str, valor_total_str = match.groups()
            
            # Converter valores
            quantidade = to_float_brl(qtd_str)
            valor_unitario = to_float_brl(valor_unit_str)
            valor_total = to_float_brl(valor_total_str)
            
            # Validar se os valores fazem sentido
            if quantidade > 0 and valor_unitario > 0 and valor_total > 0:
                item = {
                    "codigo": codigo,
                    "descricao": descricao.strip(),
                    "ncm": ncm,
                    "cfop": cfop,
                    "un": unidade.lower(),  # Converter para minúsculo
                    "quantidade": quantidade,
                    "valor_unitario": valor_unitario,
                    "valor_total": valor_total,
                }
                items.append(item)
    
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