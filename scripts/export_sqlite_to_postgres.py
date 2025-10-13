#!/usr/bin/env python3
"""
Script para exportar dados do SQLite para PostgreSQL
Executa migrações e popula o banco com dados existentes
"""
import sqlite3
import psycopg2
from datetime import datetime
import json
import sys
import os

def connect_sqlite():
    """Conecta ao SQLite"""
    sqlite_path = os.path.join('backend', 'nfe_system.db')
    if not os.path.exists(sqlite_path):
        print(f"❌ Arquivo SQLite não encontrado: {sqlite_path}")
        return None
    
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
    return conn

def connect_postgres():
    """Conecta ao PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="nfedb",
            user="nfeuser",
            password="nfepass"
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar PostgreSQL: {e}")
        print("💡 Certifique-se que o Docker está rodando: docker-compose up -d")
        return None

def export_table(sqlite_cursor, pg_cursor, table_name, sqlite_to_pg_mapping=None):
    """Exporta uma tabela do SQLite para PostgreSQL"""
    try:
        print(f"📊 Exportando tabela: {table_name}")
        
        # Buscar dados do SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ℹ️  Tabela {table_name} está vazia")
            return
        
        # Obter nomes das colunas
        columns = [description[0] for description in sqlite_cursor.description]
        
        # Se há mapeamento personalizado, usar ele
        if sqlite_to_pg_mapping:
            pg_columns = sqlite_to_pg_mapping.get('columns', columns)
            table_name_pg = sqlite_to_pg_mapping.get('table_name', table_name)
        else:
            pg_columns = columns
            table_name_pg = table_name
        
        # Limpar tabela PostgreSQL (se existir)
        try:
            pg_cursor.execute(f"TRUNCATE TABLE {table_name_pg} RESTART IDENTITY CASCADE")
        except:
            pass  # Tabela pode não existir ainda
        
        # Inserir dados
        for row in rows:
            row_dict = dict(row)
            values = []
            placeholders = []
            
            for col in pg_columns:
                if col in row_dict:
                    value = row_dict[col]
                    # Tratar valores None e converter tipos se necessário
                    if value is None:
                        values.append(None)
                    elif isinstance(value, str) and value.lower() in ['true', 'false']:
                        values.append(value.lower() == 'true')
                    else:
                        values.append(value)
                    placeholders.append('%s')
            
            if values:
                placeholders_str = ', '.join(placeholders)
                columns_str = ', '.join(pg_columns)
                query = f"INSERT INTO {table_name_pg} ({columns_str}) VALUES ({placeholders_str})"
                pg_cursor.execute(query, values)
        
        print(f"   ✅ {len(rows)} registros exportados")
        
    except Exception as e:
        print(f"   ❌ Erro ao exportar {table_name}: {e}")

def export_data():
    """Função principal de exportação"""
    print("🚀 Iniciando exportação SQLite → PostgreSQL")
    
    # Conectar aos bancos
    sqlite_conn = connect_sqlite()
    if not sqlite_conn:
        return False
    
    pg_conn = connect_postgres()
    if not pg_conn:
        sqlite_conn.close()
        return False
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        # Mapeamento especial para tabelas com nomes diferentes
        table_mappings = {
            'materias_primas': {
                'table_name': 'materias_primas',
                'columns': ['id', 'nome', 'unidade_codigo', 'menor_unidade_codigo', 'is_active', 'created_at', 'updated_at']
            },
            'fornecedor': {
                'table_name': 'fornecedor',
                'columns': ['id_fornecedor', 'nome', 'cnpj', 'email', 'telefone', 'endereco', 'is_active', 'created_at', 'updated_at']
            },
            'unidades': {
                'table_name': 'unidades',
                'columns': ['codigo', 'nome', 'descricao', 'menor_unidade_id', 'fator_conversao', 'created_at']
            },
            'users': {
                'table_name': 'users',
                'columns': ['id', 'name', 'email', 'password_hash', 'role', 'is_active', 'created_at', 'updated_at']
            },
            'materia_prima_precos': {
                'table_name': 'materia_prima_precos',
                'columns': ['id', 'materia_prima_id', 'valor_unitario', 'moeda', 'vigente_desde', 'vigente_ate', 'fornecedor_id', 'nota_id', 'created_at']
            }
        }
        
        # Exportar tabelas principais
        tables_to_export = ['unidades', 'users', 'fornecedor', 'materias_primas', 'materia_prima_precos']
        
        for table in tables_to_export:
            mapping = table_mappings.get(table)
            export_table(sqlite_cursor, pg_cursor, table, mapping)
        
        # Commit das alterações
        pg_conn.commit()
        print("✅ Exportação concluída com sucesso!")
        
        # Mostrar estatísticas
        print("\n📊 Estatísticas do banco PostgreSQL:")
        for table in tables_to_export:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = pg_cursor.fetchone()[0]
            print(f"   • {table}: {count} registros")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a exportação: {e}")
        pg_conn.rollback()
        return False
    finally:
        sqlite_conn.close()
        pg_conn.close()

def main():
    """Função principal"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
🐳 Exportador SQLite → PostgreSQL

Uso: python scripts/export_sqlite_to_postgres.py

Requisitos:
1. Docker rodando: docker-compose up -d
2. PostgreSQL acessível em localhost:5432
3. Arquivo SQLite em backend/nfe_system.db

Este script exporta dados do SQLite para PostgreSQL mantendo a estrutura.
        """)
        return
    
    print("🔍 Verificando pré-requisitos...")
    
    # Verificar se Docker está rodando
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if 'postgres' not in result.stdout:
            print("⚠️  PostgreSQL Docker não está rodando")
            print("💡 Execute: docker-compose up -d")
            return
    except:
        print("⚠️  Docker não encontrado")
        return
    
    # Executar exportação
    success = export_data()
    
    if success:
        print("\n🎉 Exportação concluída!")
        print("📱 Acesse: http://localhost:5173")
        print("📚 API: http://localhost:8000/docs")
    else:
        print("\n❌ Exportação falhou!")
        sys.exit(1)

if __name__ == "__main__":
    main()
