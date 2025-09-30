#!/usr/bin/env python3
"""
Script para gerar build do frontend
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_dependencies():
    """Instala dependências do frontend"""
    print("📦 Instalando dependências do frontend...")
    
    try:
        subprocess.run(["npm", "install"], check=True, cwd="src")
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False
    except FileNotFoundError:
        print("❌ Node.js/npm não encontrado. Instale o Node.js primeiro.")
        return False

def build_frontend():
    """Gera build de produção do frontend"""
    print("🔨 Gerando build de produção...")
    
    try:
        subprocess.run(["npm", "run", "build"], check=True, cwd="src")
        print("✅ Build do frontend gerado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar build: {e}")
        return False

def create_serve_script():
    """Cria script para servir o frontend"""
    serve_script = '''@echo off
echo Servindo frontend NFE...
echo.
echo Frontend disponível em: http://localhost:8080
echo Para parar o servidor, pressione Ctrl+C
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python não encontrado. Instalando servidor HTTP simples...
    echo.
    echo Abra o arquivo index.html no navegador ou use um servidor HTTP.
    pause
    exit /b 1
)

REM Servir arquivos estáticos
python -m http.server 8080
pause
'''
    
    # Criar diretório dist se não existir
    os.makedirs("dist", exist_ok=True)
    
    with open('dist/serve_frontend.bat', 'w', encoding='utf-8') as f:
        f.write(serve_script)
    
    print("✅ Script de servidor criado: serve_frontend.bat")

def copy_build_files():
    """Copia arquivos de build para dist"""
    print("📁 Copiando arquivos de build...")
    
    # Criar diretório dist
    os.makedirs("dist", exist_ok=True)
    
    # Copiar arquivos de build
    if os.path.exists("src/dist"):
        shutil.copytree("src/dist", "dist/frontend", dirs_exist_ok=True)
        print("✅ Arquivos do frontend copiados para dist/frontend/")
    else:
        print("❌ Pasta src/dist não encontrada. Execute o build primeiro.")

def main():
    """Função principal"""
    print("🚀 Gerando build do frontend NFE...")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("src/package.json"):
        print("❌ Execute este script na raiz do projeto (onde está a pasta src/)")
        return
    
    try:
        # Instalar dependências
        if not install_dependencies():
            return
        
        # Gerar build
        if not build_frontend():
            return
        
        # Copiar arquivos
        copy_build_files()
        
        # Criar script de servidor
        create_serve_script()
        
        print("\n" + "=" * 50)
        print("🎉 BUILD DO FRONTEND CONCLUÍDO!")
        print("=" * 50)
        print("📁 Arquivos gerados:")
        print("   - dist/frontend/ (arquivos estáticos)")
        print("   - dist/serve_frontend.bat (script de servidor)")
        print("\n📋 Para usar:")
        print("   1. Copie a pasta 'dist' completa")
        print("   2. Execute 'serve_frontend.bat'")
        print("   3. Acesse http://localhost:8080")
        
    except Exception as e:
        print(f"❌ Erro durante o build: {e}")

if __name__ == "__main__":
    main()
