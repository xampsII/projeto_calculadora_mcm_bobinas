# -*- coding: utf-8 -*-
from fastapi import APIRouter, UploadFile, File, HTTPException
import subprocess
import json
import tempfile
import os
import re
from typing import Dict, List
from unidecode import unidecode

router = APIRouter(prefix="/uploads-ia", tags=["uploads-ia"])

async def processar_pdf_com_ia(content: bytes, filename: str) -> dict:
    """Processa PDF usando MCP + IA quando o parser normal falha"""
    print("\n=== INÃCIO DO PROCESSAMENTO IA ===")
    print(f"Recebido arquivo: {filename}")
    try:
        # Salvar arquivo temporÃ¡rio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        print(f"Arquivo temporÃ¡rio salvo em: {tmp_file_path}")
        
        try:
            # Caminho do MCP (dentro do Docker)
            # No Docker, o backend estÃ¡ em /app, entÃ£o o MCP estÃ¡ em ../mcp-server-pdf
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
            mcp_path = os.path.join(project_root, 'mcp-server-pdf', 'index.js')
            
            print(f"DEBUG: Current dir: {current_dir}")
            print(f"DEBUG: Project root: {project_root}")
            print(f"DEBUG: Caminho MCP: {mcp_path}")
            print(f"DEBUG: Arquivo existe? {os.path.exists(mcp_path)}")

            if not os.path.exists(mcp_path):
                raise Exception(f"Arquivo MCP nÃ£o encontrado: {mcp_path}")

            # Chamar MCP
            print(f"Executando MCP: node {mcp_path} {tmp_file_path}")
            result = subprocess.run(
                ['node', mcp_path, tmp_file_path],
                capture_output=True,
                universal_newlines=False,
                check=False,
                cwd=project_root
            )

            # Decodificar stdout e stderr manualmente
            try:
                stdout_text = result.stdout.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                stdout_text = result.stdout.decode('latin-1', errors='replace')

            try:
                stderr_text = result.stderr.decode('utf-8', errors='replace')
            except UnicodeDecodeError:
                stderr_text = result.stderr.decode('latin-1', errors='replace')

            print(f"CÃ³digo de retorno: {result.returncode}")
            print(f"Stdout (primeiros 200 chars): {stdout_text[:200]}...")
            print(f"Stderr: {stderr_text}")

            if result.returncode != 0:
                raise Exception(f"Erro no script MCP: {stderr_text}")
            
            if not stdout_text or stdout_text.strip() == "":
                raise Exception("MCP nÃ£o retornou nenhum texto.")

            # Parse do resultado JSON do MCP
            mcp_data = None
            try:
                mcp_data = json.loads(stdout_text)
                print(f"DEBUG: mcp_data parseado: {mcp_data}")
            except json.JSONDecodeError as e:
                print(f"DEBUG: Erro ao parsear JSON: {e}")
                print(f"DEBUG: Raw stdout: {stdout_text}")
                raise Exception(f"Erro ao parsear JSON do MCP: {e}. SaÃ­da: {stdout_text[:200]}")
            
            if mcp_data is None:
                raise Exception("MCP retornou None apÃ³s parse.")
                
            texto_extraido = mcp_data.get('text', '')
            
            # Limpar texto extraÃ­do para remover caracteres problemÃ¡ticos
            texto_extraido = unidecode(texto_extraido)
            texto_extraido = re.sub(r'[^\x00-\x7F]+', '', texto_extraido)
            texto_extraido = re.sub(r'\s+', ' ', texto_extraido).strip()

            print(f"DEBUG: Texto extraÃ­do (primeiros 100 chars): {texto_extraido[:100]}...")
            
            # Usar IA para estruturar os dados
            dados_estruturados = estruturar_dados_com_ia(texto_extraido)
            print(f"DEBUG: Dados estruturados: {dados_estruturados}")
            
            resultado_final = {
                "success": True,
                "method": "ai_fallback",
                "dados_extraidos": dados_estruturados,
                "message": f"PDF processado com IA! {len(dados_estruturados.get('itens', []))} itens encontrados."
            }
            print(f"DEBUG: Retorno final do backend: {resultado_final}")
            return resultado_final
            
        finally:
            # Limpar arquivo temporÃ¡rio
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            print(f"Arquivo temporÃ¡rio removido: {tmp_file_path}")
            
    except Exception as e:
        print(f"ERROR: Erro completo no processamento IA: {str(e)}")
        return {
            "success": False,
            "method": "ai_fallback",
            "message": f"Erro ao processar com IA: {str(e)}"
        }

def estruturar_dados_com_ia(texto: str) -> dict:
    """Extrai dados usando regex inteligente"""
    print(f"DEBUG: Estruturando dados com IA (regex) do texto: {texto[:100]}...")
    
    dados = {
        "numero_nota": "000000",
        "serie": "1",
        "chave_acesso": "",
        "valor_total": 0.0,
        "fornecedor": "Fornecedor nÃ£o identificado",
        "cnpj_fornecedor": "00000000000000",
        "data_emissao": "",
        "endereco": "",
        "itens": []
    }
    
    # CNPJ
    cnpj_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
    if cnpj_match:
        dados["cnpj_fornecedor"] = cnpj_match.group(1).replace('.', '').replace('/', '').replace('-', '')
    
    # Valor total
    valor_match = re.search(r'Total.*?R\$\s*([\d.,]+)', texto, re.IGNORECASE)
    if valor_match:
        try:
            valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
            dados["valor_total"] = float(valor_str)
        except:
            pass
    
    # NÃºmero da nota
    numero_match = re.search(r'Nota.*?(\d+)', texto, re.IGNORECASE)
    if numero_match:
        dados["numero_nota"] = numero_match.group(1)
    
    # Data
    data_match = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
    if data_match:
        dados["data_emissao"] = data_match.group(1)
    
    print(f"DEBUG: Dados extraÃ­dos por regex: {dados}")
    return dados

@router.post("/processar-pdf")
async def processar_pdf_com_ia_endpoint(file: UploadFile = File(...)):
    """Endpoint para processar PDF com IA"""
    print(f"Recebida requisiÃ§Ã£o para /uploads-ia/processar-pdf para {file.filename}")
    
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF sÃ£o aceitos")
    
    content = await file.read()
    resultado = await processar_pdf_com_ia(content, file.filename)
    
    print(f"DEBUG: Retornando resultado do endpoint: {resultado['success']}")
    return resultado
