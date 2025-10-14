"""
Script para corrigir preços duplicados no histórico
Fecha preços antigos que ainda estão com vigente_ate = NULL
"""
import sqlite3
from datetime import datetime

SQLITE_PATH = 'backend/nfe_system.db'

print("\n" + "="*60)
print("🔧 CORREÇÃO DE PREÇOS DUPLICADOS")
print("="*60 + "\n")

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()

# Buscar matérias-primas com múltiplos preços ativos
cursor.execute("""
    SELECT materia_prima_id, COUNT(*) as total
    FROM materia_prima_precos
    WHERE vigente_ate IS NULL
    GROUP BY materia_prima_id
    HAVING COUNT(*) > 1
    ORDER BY total DESC
""")

materias_com_duplicados = cursor.fetchall()

if not materias_com_duplicados:
    print("✅ Nenhum preço duplicado encontrado!")
    print("   Todos os preços estão corretos.\n")
    conn.close()
    exit(0)

print(f"⚠️  Encontradas {len(materias_com_duplicados)} matérias-primas com múltiplos preços ativos:\n")

total_corrigidos = 0

for mp_id, total_ativos in materias_com_duplicados:
    # Buscar nome da matéria-prima
    cursor.execute("SELECT nome FROM materias_primas WHERE id = ?", (mp_id,))
    nome = cursor.fetchone()[0]
    
    print(f"📦 {nome} (ID: {mp_id}) - {total_ativos} preços ativos")
    
    # Buscar todos os preços ativos, ordenados por data (mais recente primeiro)
    cursor.execute("""
        SELECT id, valor_unitario, vigente_desde
        FROM materia_prima_precos
        WHERE materia_prima_id = ? AND vigente_ate IS NULL
        ORDER BY vigente_desde DESC
    """, (mp_id,))
    
    precos = cursor.fetchall()
    
    # O primeiro é o mais recente (manter ativo)
    preco_atual = precos[0]
    print(f"   ✅ Mantendo: R$ {preco_atual[1]:.4f} (desde {preco_atual[2][:10]})")
    
    # Os demais devem ser fechados
    for i, preco_antigo in enumerate(precos[1:], 1):
        preco_id, valor, vigente_desde = preco_antigo
        
        # Fechar com a data do próximo preço (ou data atual se for o último)
        if i < len(precos) - 1:
            vigente_ate = precos[i][2]  # Data do próximo preço
        else:
            vigente_ate = preco_atual[2]  # Data do preço mais recente
        
        cursor.execute("""
            UPDATE materia_prima_precos
            SET vigente_ate = ?
            WHERE id = ?
        """, (vigente_ate, preco_id))
        
        print(f"   🔒 Fechando: R$ {valor:.4f} (até {vigente_ate[:10]})")
        total_corrigidos += 1
    
    print()

# Confirmar alterações
conn.commit()

print("="*60)
print(f"✅ CORREÇÃO CONCLUÍDA!")
print(f"   {total_corrigidos} preços antigos foram fechados")
print("="*60 + "\n")

# Verificação final
cursor.execute("""
    SELECT materia_prima_id, COUNT(*) as total
    FROM materia_prima_precos
    WHERE vigente_ate IS NULL
    GROUP BY materia_prima_id
    HAVING COUNT(*) > 1
""")

ainda_duplicados = cursor.fetchall()

if ainda_duplicados:
    print("⚠️  ATENÇÃO: Ainda existem preços duplicados!")
    for mp_id, total in ainda_duplicados:
        cursor.execute("SELECT nome FROM materias_primas WHERE id = ?", (mp_id,))
        nome = cursor.fetchone()[0]
        print(f"   • {nome}: {total} preços ativos")
else:
    print("✅ Verificação final: Todos os preços estão corretos!")

conn.close()
print()

