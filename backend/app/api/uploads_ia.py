from fastapi import APIRouter, UploadFile, File, HTTPException
import subprocess
import json
import tempfile
import os
import re
import sys
from typing import Dict, List

# Forçar encoding UTF-8
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

router = APIRouter(prefix="/uploads-ia", tags=["uploads-ia"])

async def processar_pdf_com_ia(content: bytes, filename: str) -> dict:
    """Processa PDF usando MCP + IA quando o parser normal falha"""
    try:
        print("=== INÍCIO DO PROCESSAMENTO IA ===")
        
        # Salvar arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        print(f"Arquivo temporário criado: {tmp_file_path}")
        
        try:
            # Caminho absoluto fixo
            mcp_path = r"C:\Users\pplima\Downloads\project\mcp-server-pdf\index.js"
            project_dir = r"C:\Users\pplima\Downloads\project"
            
            print(f"Caminho MCP: {mcp_path}")
            print(f"Arquivo MCP existe? {os.path.exists(mcp_path)}")
            
            if not os.path.exists(mcp_path):
                raise Exception(f"Arquivo MCP não encontrado: {mcp_path}")
            
            # Chamar MCP
            print("Executando MCP...")
            # Usar subprocess.run com bytes para evitar problemas de encoding
            result = subprocess.run([
                'node', 
                mcp_path, 
                tmp_file_path
            ], capture_output=True, cwd=project_dir)
            
            # Converter bytes para string de forma segura
            stdout_bytes = result.stdout
            stderr_bytes = result.stderr
            
            # Decodificar usando UTF-8 com tratamento de erros
            try:
                stdout_text = stdout_bytes.decode('utf-8', errors='ignore')
                stderr_text = stderr_bytes.decode('utf-8', errors='ignore') if stderr_bytes else ""
            except Exception as e:
                stdout_text = stdout_bytes.decode('latin-1', errors='ignore')
                stderr_text = stderr_bytes.decode('latin-1', errors='ignore') if stderr_bytes else ""
                print(f"Usando latin-1 como fallback: {e}")
            
            print(f"Código de retorno: {result.returncode}")
            print(f"STDOUT length: {len(stdout_text)}")
            print(f"STDERR: {stderr_text}")
            
            if result.returncode != 0:
                raise Exception(f"MCP falhou: {result.stderr}")
            
            if not stdout_text or stdout_text.strip() == '':
                raise Exception("MCP não retornou nenhum output")
            
            # Parse JSON
            print("Parseando JSON...")
            try:
                # Remover espaços em branco e quebras de linha
                clean_stdout = stdout_text.strip()
                print(f"STDOUT limpo (primeiros 200 chars): {clean_stdout[:200]}")
                mcp_data = json.loads(clean_stdout)
                print(f"Dados parseados com sucesso!")
            except json.JSONDecodeError as e:
                print(f"Erro ao parsear JSON: {e}")
                print(f"Raw stdout completo: {stdout_text}")
                raise Exception(f"Erro ao parsear JSON: {e}")
            
            if mcp_data is None:
                raise Exception("MCP retornou None")
            
            texto_extraido = mcp_data.get('text', '')
            # Limpar caracteres especiais que podem causar problemas
            if texto_extraido:
                texto_extraido = texto_extraido.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"Texto extraído: {len(texto_extraido)} caracteres")
            print(f"Primeiros 100 chars: {texto_extraido[:100]}")
            
            # Estruturar dados
            dados_estruturados = estruturar_dados_com_ia(texto_extraido)
            print(f"Dados estruturados: {dados_estruturados}")
            print(f"=== DADOS FINAIS PARA O FRONTEND ===")
            print(f"Número da Nota: {dados_estruturados.get('numero_nota', 'N/A')}")
            print(f"Fornecedor: {dados_estruturados.get('fornecedor', 'N/A')}")
            print(f"CNPJ: {dados_estruturados.get('cnpj_fornecedor', 'N/A')}")
            print(f"Valor Total: {dados_estruturados.get('valor_total', 'N/A')}")
            print(f"Data: {dados_estruturados.get('data_emissao', 'N/A')}")
            print(f"=== FIM DOS DADOS ===")
            
            resultado_final = {
                "success": True,
                "method": "ai_fallback",
                "dados_extraidos": dados_estruturados,
                "message": f"PDF processado com IA! {len(dados_estruturados.get('itens', []))} itens encontrados."
            }
            
            print(f"=== RESULTADO FINAL PARA O FRONTEND ===")
            print(f"Success: {resultado_final['success']}")
            print(f"Message: {resultado_final['message']}")
            print(f"Dados extraídos: {resultado_final['dados_extraidos']}")
            print(f"=== FIM RESULTADO ===")
            
            return resultado_final
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
                print(f"Arquivo temporário removido: {tmp_file_path}")
            
    except Exception as e:
        print(f"ERRO GERAL: {str(e)}")
        return {
            "success": False,
            "method": "ai_fallback",
            "message": f"Erro ao processar com IA: {str(e)}"
        }

def estruturar_dados_com_ia(texto: str) -> dict:
    """Extrai dados usando regex inteligente"""
    
    dados = {
        "numero_nota": "000000",
        "serie": "1",
        "chave_acesso": "",
        "valor_total": 0.0,
        "fornecedor": "Fornecedor não identificado",
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
    
    # Número da nota
    numero_match = re.search(r'Nota.*?(\d+)', texto, re.IGNORECASE)
    if numero_match:
        dados["numero_nota"] = numero_match.group(1)
    
    # Data
    data_match = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
    if data_match:
        dados["data_emissao"] = data_match.group(1)
    
    return dados

@router.post("/processar-pdf")
async def processar_pdf_com_ia_endpoint(file: UploadFile = File(...)):
    """Endpoint para processar PDF com IA"""
    
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")
    
    content = await file.read()
    resultado = await processar_pdf_com_ia(content, file.filename)
    
    return resultado
