#!/usr/bin/env python3
"""
Script de Setup Local para o Sistema NFE
Configura o ambiente de desenvolvimento sem Docker
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python_version():
    """Verifica a versão do Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11+ é necessário")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_postgresql():
    """Verifica se o PostgreSQL está disponível"""
    success, stdout, stderr = run_command("psql --version")
    if success:
        print("✅ PostgreSQL encontrado")
        return True
    else:
        print("❌ PostgreSQL não encontrado")
        print("   Instale o PostgreSQL: https://www.postgresql.org/download/")
        return False

def check_redis():
    """Verifica se o Redis está disponível"""
    success, stdout, stderr = run_command("redis-cli ping")
    if success and "PONG" in stdout:
        print("✅ Redis está rodando")
        return True
    else:
        print("⚠️  Redis não está rodando")
        print("   Inicie o Redis: redis-server")
        return False

def create_directories():
    """Cria diretórios necessários"""
    directories = [
        "data/uploads",
        "logs",
        "backend/logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")

def setup_environment():
    """Configura o arquivo .env"""
    env_file = Path(".env")
    config_file = Path("config.local.env")
    
    if env_file.exists():
        print("⚠️  Arquivo .env já existe")
        return True
    
    if config_file.exists():
        shutil.copy(config_file, env_file)
        print("✅ Arquivo .env criado a partir de config.local.env")
        print("   Edite o arquivo .env com suas configurações")
        return True
    else:
        print("❌ Arquivo config.local.env não encontrado")
        return False

def install_dependencies():
    """Instala as dependências Python"""
    print("📦 Instalando dependências...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    
    if success:
        print("✅ Dependências instaladas")
        return True
    else:
        print("❌ Erro ao instalar dependências:")
        print(stderr)
        return False

def setup_database():
    """Configura o banco de dados"""
    print("🗄️  Configurando banco de dados...")
    
    # Verifica se o banco existe
    success, stdout, stderr = run_command(
        "psql -h localhost -U postgres -lqt | cut -d \\| -f 1 | grep -qw nfe_system"
    )
    
    if not success:
        print("⚠️  Banco 'nfe_system' não encontrado")
        print("   Crie o banco: createdb -U postgres nfe_system")
        return False
    
    # Executa migrações
    success, stdout, stderr = run_command(
        "alembic upgrade head", 
        cwd="backend"
    )
    
    if success:
        print("✅ Migrações aplicadas")
        return True
    else:
        print("❌ Erro ao aplicar migrações:")
        print(stderr)
        return False

def run_seeds():
    """Executa os seeds iniciais"""
    print("🌱 Executando seeds...")
    success, stdout, stderr = run_command(
        "python -c \"from app.seeds import executar_seeds; executar_seeds()\"",
        cwd="backend"
    )
    
    if success:
        print("✅ Seeds executados")
        return True
    else:
        print("❌ Erro ao executar seeds:")
        print(stderr)
        return False

def main():
    """Função principal"""
    print("🚀 Setup Local do Sistema NFE")
    print("=" * 40)
    
    # Verificações básicas
    if not check_python_version():
        sys.exit(1)
    
    if not check_postgresql():
        print("\n⚠️  Continue apenas se tiver certeza que o PostgreSQL está disponível")
    
    # Cria diretórios
    create_directories()
    
    # Configura ambiente
    if not setup_environment():
        sys.exit(1)
    
    # Instala dependências
    if not install_dependencies():
        sys.exit(1)
    
    # Configura banco
    if not setup_database():
        print("\n⚠️  Configure o banco manualmente e execute:")
        print("   make migrate")
        print("   make seed")
    else:
        # Executa seeds
        if not run_seeds():
            print("\n⚠️  Execute manualmente: make seed")
    
    print("\n🎉 Setup concluído!")
    print("\n📋 Próximos passos:")
    print("1. Configure o arquivo .env com suas credenciais")
    print("2. Inicie o Redis: redis-server")
    print("3. Execute: make run")
    print("4. Em outro terminal: make worker")
    print("5. Em outro terminal: make beat")

if __name__ == "__main__":
    main() 