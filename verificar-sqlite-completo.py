import sqlite3

SQLITE_PATH = 'backend/nfe_system.db'

print("\n" + "="*60)
print("🔍 VERIFICAÇÃO COMPLETA DO SQLite")
print("="*60 + "\n")

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tabelas = [row[0] for row in cursor.fetchall()]

print(f"📋 Tabelas encontradas: {len(tabelas)}\n")

for tabela in tabelas:
    cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
    count = cursor.fetchone()[0]
    
    # Cor baseada na quantidade
    if count == 0:
        status = "⚠️  VAZIA"
    elif count < 10:
        status = f"✅ {count} registros"
    else:
        status = f"✅ {count} registros"
    
    print(f"  {tabela:30s} {status}")

print("\n" + "="*60)

# Detalhes de materia_prima_precos
print("\n📊 DETALHES: materia_prima_precos\n")

cursor.execute("""
    SELECT 
        COUNT(*) as total,
        MIN(vigente_desde) as primeira_data,
        MAX(vigente_desde) as ultima_data
    FROM materia_prima_precos
""")
total, primeira, ultima = cursor.fetchone()

print(f"  Total de preços: {total}")
print(f"  Primeira data: {primeira}")
print(f"  Última data: {ultima}\n")

# Últimos 5 preços
cursor.execute("""
    SELECT mp.nome, mpp.valor_unitario, mpp.vigente_desde
    FROM materia_prima_precos mpp
    JOIN materias_primas mp ON mp.id = mpp.materia_prima_id
    ORDER BY mpp.vigente_desde DESC
    LIMIT 5
""")

print("  Últimos 5 preços registrados:")
for nome, valor, data in cursor.fetchall():
    print(f"    • {nome[:40]:40s} R$ {valor:8.4f}  ({data[:10]})")

conn.close()

print("\n" + "="*60)
print("✅ Verificação concluída!")
print("="*60 + "\n")

