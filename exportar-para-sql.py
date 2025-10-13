#!/usr/bin/env python3
"""
Script para exportar dados do PostgreSQL local em formato SQL compatível
"""
import subprocess
import sys

print("Exportando dados do PostgreSQL local...")
print("-" * 50)

# Configurações
pg_dump_path = r"C:\Program Files\PostgreSQL\17\bin\pg_dump.exe"
output_file = r"docker\postgres\init\04-meus-dados.sql"
password = "Yasmin123"

# Comando pg_dump
cmd = [
    pg_dump_path,
    "-h", "localhost",
    "-p", "5432",
    "-U", "postgres",
    "-d", "nfedb",
    "--data-only",
    "--inserts",
    "--column-inserts",
    "--no-owner",
    "--no-acl",
    "-f", output_file
]

# Executar
try:
    env = {"PGPASSWORD": password}
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Dados exportados com sucesso para: {output_file}")
        print("\nAgora faça:")
        print("1. git add docker/postgres/init/04-meus-dados.sql")
        print("2. git commit -m 'feat: adiciona dados em formato SQL'")
        print("3. git push")
    else:
        print(f"❌ Erro ao exportar:")
        print(result.stderr)
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

