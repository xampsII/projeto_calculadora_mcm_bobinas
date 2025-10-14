"""
Testar algoritmo de matching melhorado
"""
import re

def normalizar_nome(nome: str) -> str:
    """Normaliza nome para matching mais flexível"""
    # Remover hífens e underscores do início/fim
    nome = nome.strip('-_').strip()
    # Remover sufixos comuns de notas fiscais
    nome = re.sub(r'\s*-\s*inf\s+\w+$', '', nome, flags=re.IGNORECASE)  # Remove "- inf KG"
    # Remover parênteses MAS manter o conteúdo (ex: (CANTO QUADRADO) -> CANTO QUADRADO)
    nome = nome.replace('(', ' ').replace(')', ' ')
    # Converter vírgulas em pontos (ex: 2,0 -> 2.0)
    nome = nome.replace(',', '.')
    # Remover espaços ao redor de 'X' (ex: 2.0 X 7.0 -> 2.0X7.0)
    nome = re.sub(r'\s*X\s*', 'X', nome, flags=re.IGNORECASE)
    # Remover caracteres especiais mantendo letras, números, pontos e espaços
    nome = re.sub(r'[^\w\s.]', ' ', nome)
    # Padronizar espaços múltiplos
    nome = re.sub(r'\s+', ' ', nome)
    # Uppercase e trim
    return nome.upper().strip()

# Casos de teste
testes = [
    ("-FIO 2.0X7.0 CANTO QUADRADO", "FIO 2.0X7.0 (CANTO QUADRADO)"),
    ("-FIO 1.5X7.0 CANTO QUADRADO", "FIO 1.5X7.0 (CANTO QUADRADO)"),
    ("-FIO 1.0X5.0 CANTO QUADRADO - inf KG", "FIO 1.0X5.0 (CANTO QUADRADO)"),
    ("-FIO 2.0X5,2 CANTO QUADRADO - inf KG", "FIO 2.0X5,2 (CANTO QUADRADO)"),
    ("FIO 2.0 X 7.0", "FIO 2.0X7.0 (CANTO QUADRADO)"),
    ("VERNIZ ASA-952 INCOLOR 18L", "VERNIZ ASA 952 INCOLOR - 18L"),
]

print("\n" + "="*80)
print("🧪 TESTE DE MATCHING")
print("="*80 + "\n")

for nome_nota, nome_banco in testes:
    nota_norm = normalizar_nome(nome_nota)
    banco_norm = normalizar_nome(nome_banco)
    
    match = nota_norm == banco_norm
    status = "✅ MATCH" if match else "❌ NO MATCH"
    
    print(f"{status}")
    print(f"  Nota:  '{nome_nota}'")
    print(f"    →    '{nota_norm}'")
    print(f"  Banco: '{nome_banco}'")
    print(f"    →    '{banco_norm}'")
    print()

print("="*80)

