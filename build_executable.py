#!/usr/bin/env python3
"""
Script para gerar executável do backend NFE
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller se não estiver instalado"""
    try:
        import PyInstaller
        print("✅ PyInstaller já está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller instalado com sucesso")

def create_spec_file():
    """Cria arquivo .spec para PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('alembic', 'alembic'),
        ('alembic.ini', '.'),
    ],
    hiddenimports=[
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.loops.uvloop',
        'uvicorn.logging',
        'sqlalchemy.dialects.postgresql',
        'psycopg2',
        'alembic',
        'alembic.runtime.migration',
        'alembic.script',
        'alembic.util',
        'fitz',
        'pdfplumber',
        'unidecode',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='nfe_backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('nfe_backend.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Arquivo .spec criado")

def build_executable():
    """Gera o executável"""
    print("🔨 Gerando executável...")
    
    # Comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",
        "--console",
        "--name", "nfe_backend",
        "--add-data", "app;app",
        "--add-data", "alembic;alembic", 
        "--add-data", "alembic.ini;.",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "uvicorn.lifespan.off",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.protocols.websockets.wsproto_impl",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.http.h11_impl",
        "--hidden-import", "uvicorn.protocols.http.httptools_impl",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.loops.asyncio",
        "--hidden-import", "uvicorn.loops.uvloop",
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "sqlalchemy.dialects.postgresql",
        "--hidden-import", "psycopg2",
        "--hidden-import", "alembic",
        "--hidden-import", "alembic.runtime.migration",
        "--hidden-import", "alembic.script",
        "--hidden-import", "alembic.util",
        "--hidden-import", "fitz",
        "--hidden-import", "pdfplumber",
        "--hidden-import", "unidecode",
        "app/main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True, cwd="backend")
        print("✅ Executável gerado com sucesso!")
        print("📁 Localização: backend/dist/nfe_backend.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar executável: {e}")
        return False
    
    return True

def create_startup_script():
    """Cria script de inicialização"""
    startup_script = '''@echo off
echo Iniciando servidor NFE...
echo.
echo Servidor rodando em: http://127.0.0.1:8000
echo Para parar o servidor, pressione Ctrl+C
echo.
nfe_backend.exe
pause
'''
    
    with open('backend/dist/start_server.bat', 'w', encoding='utf-8') as f:
        f.write(startup_script)
    
    print("✅ Script de inicialização criado: start_server.bat")

def main():
    """Função principal"""
    print("🚀 Gerando executável do backend NFE...")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("backend/app/main.py"):
        print("❌ Execute este script na raiz do projeto (onde está a pasta backend/)")
        return
    
    # Mudar para diretório backend
    os.chdir("backend")
    
    try:
        # Instalar PyInstaller
        install_pyinstaller()
        
        # Gerar executável
        if build_executable():
            # Criar script de inicialização
            create_startup_script()
            
            print("\n" + "=" * 50)
            print("🎉 BUILD CONCLUÍDO COM SUCESSO!")
            print("=" * 50)
            print("📁 Arquivos gerados:")
            print("   - dist/nfe_backend.exe (executável principal)")
            print("   - dist/start_server.bat (script de inicialização)")
            print("\n📋 Para usar em outra máquina:")
            print("   1. Copie a pasta 'dist' completa")
            print("   2. Execute 'start_server.bat' ou 'nfe_backend.exe'")
            print("   3. O servidor iniciará em http://127.0.0.1:8000")
            print("\n⚠️  IMPORTANTE:")
            print("   - Certifique-se de que o PostgreSQL está rodando")
            print("   - Configure as variáveis de ambiente se necessário")
            print("   - O executável precisa de acesso à internet para baixar dependências")
        
    except Exception as e:
        print(f"❌ Erro durante o build: {e}")
    
    finally:
        # Voltar ao diretório original
        os.chdir("..")

if __name__ == "__main__":
    main()
