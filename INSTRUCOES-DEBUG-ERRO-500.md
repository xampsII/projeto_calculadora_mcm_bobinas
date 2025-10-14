# 🔧 DEBUG - ERRO 500 AO IMPORTAR NOTA

## ❌ Erro que você está vendo:

```
Failed to load resource: the server responded with a status of 500 (Internal Server Error)
```

---

## 🔍 PASSO 1: Ver logs do backend

Execute este comando para ver o erro completo:

```bash
docker-compose logs backend --tail=100
```

**OU se não estiver usando Docker:**

```bash
# Ver logs do terminal onde o backend está rodando
```

---

## 🎯 POSSÍVEIS CAUSAS:

### **Causa 1: Erro no algoritmo de matching**

O novo algoritmo pode estar causando erro. Procure no log por:
- `TypeError`
- `AttributeError`
- `KeyError`

### **Causa 2: Problema com vírgula vs ponto**

Se o erro mencionar `float` ou `Decimal`, pode ser:
- Valor com vírgula não convertido: "73,00" → erro

### **Causa 3: Campo faltando**

Se o erro mencionar `None` ou `NoneType`, pode ser:
- `fornecedor_id` é NULL
- `emissao_date` está vazio

---

## 🛠️ SOLUÇÕES RÁPIDAS:

### **Solução 1: Reverter para versão anterior**

```bash
# Voltar para versão antes do matching melhorado
git checkout dc6423b backend/app/api/notas.py

# Reiniciar
docker-compose restart backend
```

### **Solução 2: Adicionar try-catch no matching**

Se você souber programar Python, edite `backend/app/api/notas.py` linha 236:

```python
try:
    nome_nota = normalizar_nome(item_data.nome_no_documento)
    # ... resto do código
except Exception as e:
    print(f"ERRO no matching: {e}")
    materia_prima_id = None
```

---

## 📋 ENVIE PARA MIM:

Para eu corrigir, preciso ver:

```bash
# 1. Logs completos do erro
docker-compose logs backend --tail=100 > erro-backend.txt

# 2. Última nota que tentou importar
# (envie o arquivo XML ou tire print da tela)

# 3. Versão do código
git log --oneline -1
```

---

## 🚨 SOLUÇÃO TEMPORÁRIA:

Enquanto não corrigimos, você pode:

1. **Cadastrar notas manualmente** (sem XML)
2. **Cadastrar preços manualmente** em "Matérias-Primas"
3. **Usar versão anterior** do código

---

## ⚡ CORREÇÃO RÁPIDA (Se souber o erro):

Se o erro for relacionado a `normalizar_nome`, adicione esta linha no início da função:

```python
def normalizar_nome(nome: str) -> str:
    if not nome or not isinstance(nome, str):
        return ""
    # ... resto do código
```

---

**IMPORTANTE:** Envie os logs do backend para eu ver o erro exato! 🔍

