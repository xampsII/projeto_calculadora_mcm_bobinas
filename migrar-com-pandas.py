# -*- coding: utf-8 -*-
"""
Migração usando pandas - contorna problemas de encoding
"""
import sys
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*60)
print("🔄 MIGRAÇÃO COM PANDAS")
print("="*60 + "\n")

# Verificar dependências
try:
    import pandas as pd
    import sqlalchemy
    from sqlalchemy import create_engine
    print("✅ Pandas e SQLAlchemy disponíveis\n")
except ImportError as e:
    print(f"❌ Erro de import: {e}")
    print("\nInstale as dependências:")
    print("  pip install pandas sqlalchemy psycopg2-binary")
    sys.exit(1)

# Configurações
PG_URL = "postgresql://postgres:postgres@localhost:5433/nfe_system"
SQLITE_PATH = "backend/nfe_system.db"
SQLITE_URL = f"sqlite:///{SQLITE_PATH}"

# Tabelas a migrar (em ordem de dependência)
TABELAS = [
    'alembic_version',
    'usuarios',
    'unidades',
    'fornecedor',
    'materias_primas',
    'materia_prima_precos',
    'notas',
    'nota_itens',
    'produtos_finais',
    'produto_componentes'
]

def migrar():
    """Executa a migração"""
    try:
        # Conectar aos bancos
        print("📡 Conectando ao PostgreSQL...")
        pg_engine = create_engine(PG_URL, client_encoding='utf8')
        
        print("📡 Conectando ao SQLite...")
        sqlite_engine = create_engine(SQLITE_URL)
        
        print("\n" + "="*60)
        print("MIGRANDO TABELAS\n")
        
        total_registros = 0
        
        for tabela in TABELAS:
            try:
                print(f"📊 {tabela}...", end=" ")
                
                # Ler do PostgreSQL
                df = pd.read_sql_table(tabela, pg_engine)
                
                if df.empty:
                    print("⚠️  vazia")
                    continue
                
                # Tratar tipos de dados
                for col in df.columns:
                    # Converter datetime para string ISO
                    if pd.api.types.is_datetime64_any_dtype(df[col]):
                        df[col] = df[col].astype(str)
                    # Converter objetos JSON/dict para string
                    elif df[col].dtype == 'object':
                        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else None)
                
                # Salvar no SQLite (substituir dados existentes)
                df.to_sql(tabela, sqlite_engine, if_exists='replace', index=False)
                
                registros = len(df)
                total_registros += registros
                print(f"✅ {registros} registros")
                
            except Exception as e:
                print(f"❌ Erro: {e}")
        
        print("\n" + "="*60)
        print(f"✅ CONCLUÍDO! Total: {total_registros} registros migrados")
        print("="*60 + "\n")
        
        # Verificação
        print("📊 VERIFICAÇÃO:\n")
        with sqlite_engine.connect() as conn:
            for tabela in TABELAS:
                try:
                    result = conn.execute(sqlalchemy.text(f"SELECT COUNT(*) FROM {tabela}"))
                    count = result.scalar()
                    print(f"   • {tabela}: {count}")
                except:
                    print(f"   • {tabela}: tabela não existe")
        
        print("\n✅ Banco SQLite atualizado: " + SQLITE_PATH)
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrar()

