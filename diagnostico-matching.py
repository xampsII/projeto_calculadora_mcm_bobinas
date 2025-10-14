"""
Script de diagnóstico para verificar matching de matérias-primas
"""
import sqlite3

SQLITE_PATH = 'backend/nfe_system.db'

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO DE MATCHING DE MATÉRIAS-PRIMAS")
print("="*80 + "\n")

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()

# 1. Buscar matérias-primas com FIO
print("📦 MATÉRIAS-PRIMAS COM 'FIO' CADASTRADAS:\n")
cursor.execute("""
    SELECT id, nome 
    FROM materias_primas 
    WHERE nome LIKE '%FIO%' AND is_active = 1
    ORDER BY nome
    LIMIT 20
""")

materias_fio = cursor.fetchall()
if materias_fio:
    for mp_id, nome in materias_fio:
        print(f"  {mp_id:3d} | {nome}")
else:
    print("  ⚠️  Nenhuma matéria-prima com 'FIO' encontrada")

# 2. Buscar últimas notas importadas
print("\n" + "="*80)
print("📄 ÚLTIMAS 5 NOTAS IMPORTADAS:\n")

cursor.execute("""
    SELECT n.id, n.numero, n.emissao_date, COUNT(ni.id) as total_itens
    FROM notas n
    LEFT JOIN nota_itens ni ON ni.nota_id = n.id
    GROUP BY n.id
    ORDER BY n.created_at DESC
    LIMIT 5
""")

notas = cursor.fetchall()
if notas:
    for nota_id, numero, data, total in notas:
        print(f"  📋 Nota {nota_id} | {numero} | {data} | {total} itens")
        
        # Buscar itens dessa nota
        cursor.execute("""
            SELECT nome_no_documento, materia_prima_id, valor_unitario
            FROM nota_itens
            WHERE nota_id = ?
        """, (nota_id,))
        
        itens = cursor.fetchall()
        for nome_doc, mp_id, valor in itens:
            if mp_id:
                # Buscar nome da matéria-prima vinculada
                cursor.execute("SELECT nome FROM materias_primas WHERE id = ?", (mp_id,))
                mp_nome = cursor.fetchone()
                mp_nome = mp_nome[0] if mp_nome else "???"
                status = f"✅ Vinculado: {mp_nome}"
            else:
                status = "❌ NÃO VINCULADO"
            
            print(f"      • {nome_doc[:45]:45s} | {status}")
            print(f"        Valor: R$ {valor:.4f}")
        print()
else:
    print("  ⚠️  Nenhuma nota encontrada")

# 3. Verificar preços registrados recentemente
print("="*80)
print("💰 ÚLTIMOS 10 PREÇOS REGISTRADOS (ATIVOS):\n")

cursor.execute("""
    SELECT 
        mp.nome,
        mpp.valor_unitario,
        mpp.vigente_desde,
        mpp.nota_id
    FROM materia_prima_precos mpp
    JOIN materias_primas mp ON mp.id = mpp.materia_prima_id
    WHERE mpp.vigente_ate IS NULL
    ORDER BY mpp.vigente_desde DESC
    LIMIT 10
""")

precos = cursor.fetchall()
if precos:
    for nome, valor, data, nota_id in precos:
        print(f"  {nome[:45]:45s} | R$ {valor:8.4f} | {data[:10]} | Nota: {nota_id or 'Manual'}")
else:
    print("  ⚠️  Nenhum preço ativo encontrado")

# 4. Estatísticas gerais
print("\n" + "="*80)
print("📊 ESTATÍSTICAS GERAIS:\n")

cursor.execute("SELECT COUNT(*) FROM materias_primas WHERE is_active = 1")
total_mp = cursor.fetchone()[0]
print(f"  • Total de matérias-primas ativas: {total_mp}")

cursor.execute("SELECT COUNT(*) FROM notas")
total_notas = cursor.fetchone()[0]
print(f"  • Total de notas fiscais: {total_notas}")

cursor.execute("SELECT COUNT(*) FROM nota_itens WHERE materia_prima_id IS NOT NULL")
itens_vinculados = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM nota_itens")
total_itens = cursor.fetchone()[0]
percentual = (itens_vinculados / total_itens * 100) if total_itens > 0 else 0
print(f"  • Itens vinculados a matérias-primas: {itens_vinculados}/{total_itens} ({percentual:.1f}%)")

cursor.execute("SELECT COUNT(*) FROM materia_prima_precos WHERE vigente_ate IS NULL")
precos_ativos = cursor.fetchone()[0]
print(f"  • Preços ativos no histórico: {precos_ativos}")

cursor.execute("SELECT COUNT(DISTINCT materia_prima_id) FROM materia_prima_precos WHERE vigente_ate IS NULL")
mp_com_preco = cursor.fetchone()[0]
print(f"  • Matérias-primas com preço atual: {mp_com_preco}/{total_mp} ({mp_com_preco/total_mp*100 if total_mp > 0 else 0:.1f}%)")

# 5. Problemas identificados
print("\n" + "="*80)
print("⚠️  PROBLEMAS IDENTIFICADOS:\n")

problemas = []

# Itens não vinculados
cursor.execute("""
    SELECT COUNT(*) 
    FROM nota_itens 
    WHERE materia_prima_id IS NULL
""")
itens_nao_vinculados = cursor.fetchone()[0]
if itens_nao_vinculados > 0:
    problemas.append(f"  ❌ {itens_nao_vinculados} itens de notas NÃO estão vinculados a matérias-primas")
    print(problemas[-1])
    
    # Mostrar exemplos
    cursor.execute("""
        SELECT DISTINCT nome_no_documento
        FROM nota_itens
        WHERE materia_prima_id IS NULL
        LIMIT 5
    """)
    print("     Exemplos:")
    for (nome,) in cursor.fetchall():
        print(f"       • {nome}")

# Matérias-primas sem preço
mp_sem_preco = total_mp - mp_com_preco
if mp_sem_preco > 0:
    problemas.append(f"  ⚠️  {mp_sem_preco} matérias-primas NÃO têm preço registrado")
    print(problemas[-1])

if not problemas:
    print("  ✅ Nenhum problema identificado!")

# 6. Recomendações
print("\n" + "="*80)
print("💡 RECOMENDAÇÕES:\n")

if itens_nao_vinculados > 0:
    print("  1. Verificar logs do backend ao importar notas:")
    print("     docker-compose logs backend | grep 'DEBUG'")
    print()
    print("  2. Verificar se nomes das matérias-primas no banco correspondem aos da nota")
    print()

if mp_sem_preco > 0:
    print("  3. Cadastrar preço inicial para matérias-primas sem histórico:")
    print("     - Ir em 'Matérias-Primas' → Editar → Informar preço inicial")
    print()

print("  4. Após importar uma nota, verificar:")
print("     - Histórico de preços em 'Matérias-Primas'")
print("     - Clicar 'Recalcular Preços' em 'Produtos'")

conn.close()

print("\n" + "="*80)
print("✅ DIAGNÓSTICO CONCLUÍDO!")
print("="*80 + "\n")

