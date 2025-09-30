#!/usr/bin/env python3
"""
Script completo para gerar build de todo o sistema NFE
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_deployment_package():
    """Cria pacote completo de deployment"""
    print("📦 Criando pacote de deployment...")
    
    # Criar diretório de deployment
    deployment_dir = "nfe_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    
    os.makedirs(deployment_dir, exist_ok=True)
    
    # Copiar executável do backend
    if os.path.exists("backend/dist/nfe_backend.exe"):
        shutil.copy2("backend/dist/nfe_backend.exe", deployment_dir)
        print("✅ Executável do backend copiado")
    else:
        print("❌ Executável do backend não encontrado")
        return False
    
    # Copiar script de inicialização
    if os.path.exists("backend/dist/start_server.bat"):
        shutil.copy2("backend/dist/start_server.bat", deployment_dir)
        print("✅ Script de inicialização copiado")
    
    # Copiar frontend
    if os.path.exists("dist/frontend"):
        shutil.copytree("dist/frontend", f"{deployment_dir}/frontend")
        print("✅ Frontend copiado")
    else:
        print("❌ Frontend não encontrado")
        return False
    
    # Copiar script do frontend
    if os.path.exists("dist/serve_frontend.bat"):
        shutil.copy2("dist/serve_frontend.bat", f"{deployment_dir}/serve_frontend.bat")
        print("✅ Script do frontend copiado")
    
    # Criar README
    readme_content = '''# Sistema NFE - Pacote de Deployment

## Como usar:

### 1. Backend (API)
- Execute `start_server.bat` ou `nfe_backend.exe`
- O servidor iniciará em http://127.0.0.1:8000
- Certifique-se de que o PostgreSQL está rodando

### 2. Frontend (Interface Web)
- Execute `serve_frontend.bat`
- Acesse http://localhost:8080 no navegador

## Requisitos:
- Windows 10/11
- PostgreSQL (para o banco de dados)
- Conexão com internet (para dependências)

## Configuração do Banco:
1. Instale o PostgreSQL
2. Crie um banco de dados
3. Configure as variáveis de ambiente se necessário

## Suporte:
Em caso de problemas, verifique:
- Se o PostgreSQL está rodando
- Se as portas 8000 e 8080 estão livres
- Se há conexão com internet
'''
    
    with open(f"{deployment_dir}/README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ README criado")
    
    return True

def create_installer_script():
    """Cria script de instalação automática"""
    installer_script = '''@echo off
echo ========================================
echo    INSTALADOR SISTEMA NFE
echo ========================================
echo.

echo Verificando requisitos...

REM Verificar PostgreSQL
psql --version >nul 2>&1
if errorlevel 1 (
    echo ❌ PostgreSQL não encontrado
    echo.
    echo Por favor, instale o PostgreSQL primeiro:
    echo https://www.postgresql.org/download/windows/
    echo.
    pause
    exit /b 1
) else (
    echo ✅ PostgreSQL encontrado
)

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado
    echo.
    echo Por favor, instale o Python primeiro:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python encontrado
)

echo.
echo ========================================
echo    INICIANDO SISTEMA
echo ========================================
echo.

echo Iniciando backend...
start "NFE Backend" start_server.bat

echo Aguardando backend inicializar...
timeout /t 5 /nobreak >nul

echo Iniciando frontend...
start "NFE Frontend" serve_frontend.bat

echo.
echo ========================================
echo    SISTEMA INICIADO COM SUCESSO!
echo ========================================
echo.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:8080
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
'''
    
    with open("nfe_deployment/install.bat", 'w', encoding='utf-8') as f:
        f.write(installer_script)
    
    print("✅ Script de instalação criado")

def main():
    """Função principal"""
    print("🚀 Gerando pacote completo de deployment...")
    print("=" * 60)
    
    # Verificar se os builds existem
    if not os.path.exists("backend/dist/nfe_backend.exe"):
        print("❌ Executável do backend não encontrado.")
        print("   Execute primeiro: python build_executable.py")
        return
    
    if not os.path.exists("dist/frontend"):
        print("❌ Build do frontend não encontrado.")
        print("   Execute primeiro: python build_frontend.py")
        return
    
    try:
        # Criar pacote de deployment
        if create_deployment_package():
            # Criar script de instalação
            create_installer_script()
            
            print("\n" + "=" * 60)
            print("🎉 PACOTE DE DEPLOYMENT CRIADO COM SUCESSO!")
            print("=" * 60)
            print("📁 Pacote criado em: nfe_deployment/")
            print("\n📋 Conteúdo do pacote:")
            print("   - nfe_backend.exe (executável do backend)")
            print("   - start_server.bat (inicializar backend)")
            print("   - frontend/ (arquivos do frontend)")
            print("   - serve_frontend.bat (servir frontend)")
            print("   - install.bat (instalador automático)")
            print("   - README.txt (instruções)")
            print("\n🚀 Para usar em outra máquina:")
            print("   1. Copie a pasta 'nfe_deployment' completa")
            print("   2. Execute 'install.bat' para instalação automática")
            print("   3. Ou execute os scripts individuais manualmente")
            print("\n⚠️  IMPORTANTE:")
            print("   - Certifique-se de que o PostgreSQL está instalado")
            print("   - Configure o banco de dados conforme necessário")
            print("   - O sistema precisa de acesso à internet")
        
    except Exception as e:
        print(f"❌ Erro durante a criação do pacote: {e}")

if __name__ == "__main__":
    main()
