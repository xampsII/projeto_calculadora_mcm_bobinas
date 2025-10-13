#!/usr/bin/env python3
"""
Script para testar conexão com PostgreSQL
"""
import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

def test_connection():
    """Testa a conexão com o banco"""
    try:
        print("Testando conexao com PostgreSQL...")
        print(f"Database URL: {engine.url}")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"PostgreSQL Version: {version}")
            
            # Verificar tabelas existentes
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\nTabelas encontradas: {len(tables)}")
            for table in tables:
                print(f"- {table}")
                
        print("\nConexao com PostgreSQL funcionando!")
        return True
        
    except Exception as e:
        print(f"Erro ao conectar com PostgreSQL: {e}")
        return False

if __name__ == "__main__":
    test_connection()

