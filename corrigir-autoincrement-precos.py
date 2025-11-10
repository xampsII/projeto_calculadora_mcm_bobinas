"""
Corrige a tabela materia_prima_precos para ter AUTOINCREMENT
"""
import sqlite3
import os

SQLITE_PATH = 'backend/nfe_system.db'

print("\n" + "="*80)
print("🔧 CORRIGINDO TABELA materia_prima_precos")
print("="*80 + "\n")

if not os.path.exists(SQLITE_PATH):
    print(f"❌ Banco não encontrado: {SQLITE_PATH}")
    exit(1)

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()

try:
    # Verificar estrutura atual
    cursor.execute("PRAGMA table_info(materia_prima_precos)")
    colunas_info = cursor.fetchall()
    colunas = [col[1] for col in colunas_info]
    
    print(f"📋 Estrutura atual:")
    for col in colunas_info:
        print(f"  {col[1]:20s} {col[2]:15s} {'PK' if col[5] else ''}")
    
    # Backup dos dados
    cursor.execute("SELECT * FROM materia_prima_precos")
    dados = cursor.fetchall()
    
    print(f"\n📦 Fazendo backup de {len(dados)} registros...")
    
    # Recriar tabela com AUTOINCREMENT
    print(f"🔨 Recriando tabela com AUTOINCREMENT...")
    
    cursor.execute("DROP TABLE IF EXISTS materia_prima_precos_backup")
    cursor.execute("ALTER TABLE materia_prima_precos RENAME TO materia_prima_precos_backup")
    
    cursor.execute("""
    CREATE TABLE materia_prima_precos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_prima_id INTEGER NOT NULL,
        valor_unitario REAL NOT NULL,
        moeda TEXT NOT NULL,
        vigente_desde TIMESTAMP NOT NULL,
        vigente_ate TIMESTAMP,
        fornecedor_id INTEGER,
        nota_id REAL,
        created_at TIMESTAMP,
        id_fornecedor TEXT
    )
    """)
    
    print(f"✅ Tabela recriada com AUTOINCREMENT")
    
    # Restaurar dados (sem o campo id para que seja auto-gerado)
    if dados:
        print(f"📥 Restaurando {len(dados)} registros...")
        
        # Inserir dados SEM o campo id (será auto-gerado)
        colunas_sem_id = [col for col in colunas if col != 'id']
        placeholders = ','.join(['?' for _ in colunas_sem_id])
        
        dados_sem_id = []
        for row in dados:
            # Remover o primeiro campo (id)
            row_sem_id = row[1:]
            dados_sem_id.append(row_sem_id)
        
        cursor.executemany(
            f"INSERT INTO materia_prima_precos ({','.join(colunas_sem_id)}) VALUES ({placeholders})",
            dados_sem_id
        )
        
        print(f"✅ {len(dados)} registros restaurados")
    
    # Remover backup
    cursor.execute("DROP TABLE IF EXISTS materia_prima_precos_backup")
    
    conn.commit()
    
    # Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM materia_prima_precos")
    total = cursor.fetchone()[0]
    
    cursor.execute("PRAGMA table_info(materia_prima_precos)")
    nova_estrutura = cursor.fetchall()
    
    print(f"\n📊 Resultado:")
    print(f"  Total de registros: {total}")
    print(f"\n📋 Nova estrutura:")
    for col in nova_estrutura:
        pk_info = "PRIMARY KEY AUTOINCREMENT" if col[5] and col[1] == 'id' else ""
        print(f"  {col[1]:20s} {col[2]:15s} {pk_info}")
    
    print("\n" + "="*80)
    print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
    
finally:
    conn.close()





