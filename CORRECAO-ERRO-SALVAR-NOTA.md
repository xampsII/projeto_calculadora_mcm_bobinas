# 🔧 CORREÇÃO - ERRO 500 AO SALVAR NOTA FISCAL

## ✅ O QUE FOI FEITO:

Adicionamos logs detalhados no endpoint `/notas/` para identificar onde o erro está acontecendo.

---

## 📝 ALTERAÇÃO APLICADA:

### **Arquivo: `backend/app/api/notas.py`**

**ANTES:**
```python
except Exception as e:
    print(f"ERROR: Erro ao criar nota: {str(e)}")
    db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Erro interno: {str(e)}"
    )
```

**DEPOIS:**
```python
except Exception as e:
    print(f"ERROR: Erro ao criar nota: {str(e)}")
    print(f"ERROR: Tipo de erro: {type(e).__name__}")
    import traceback
    print(f"ERROR: Traceback completo:")
    traceback.print_exc()
    db.rollback()
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Erro interno: {str(e)}"
    )
```

---

## 🚀 INSTRUÇÕES PARA O CLIENTE:

### **PASSO 1: Reiniciar Docker**
```bash
docker-compose down
docker-compose up --build
```

### **PASSO 2: Ver logs do backend**
```bash
docker logs -f project-backend-1
```

### **PASSO 3: Tentar salvar nota novamente**
1. Acessar http://localhost:5173
2. Fazer upload do PDF
3. Tentar salvar a nota
4. **Copiar os logs de erro** que aparecerem no console do Docker
5. **Me enviar os logs** para eu identificar o problema exato

---

## 🔍 O QUE VAMOS VER NOS LOGS:

Os logs vão mostrar:
- ✅ Tipo específico do erro
- ✅ Traceback completo
- ✅ Linha exata onde o erro acontece
- ✅ Detalhes dos dados que estavam sendo processados

---

## 📊 EXEMPLO DE LOGS ESPERADOS:

```
DEBUG: Criando nota - Numero: 69474, Itens: 8
DEBUG: Fornecedor ID: 1
DEBUG: Emissão: 2025-10-07
DEBUG: Valor total: 129242.35
DEBUG: Nota criada com ID: 1
DEBUG: Processando item 1: FIO 2.0X7.0 CANTO QUADRADO
ERROR: Erro ao criar nota: relation "materias_primas" does not exist
ERROR: Tipo de erro: ProgrammingError
ERROR: Traceback completo:
  File "/app/app/api/notas.py", line 237, in create_nota
    materia_prima = db.query(MateriaPrima).filter(...)
```

---

## 💡 NOTA:

Com esses logs detalhados, vou conseguir identificar:
- Se é problema de tabela não existir
- Se é problema de campo incorreto
- Se é problema de tipo de dado
- Se é problema de constraint do banco

---

## ✅ PRÓXIMO PASSO:

**Cliente:** Execute os passos acima e me envie os logs de erro!

---

**Data:** 2025-10-07
**Status:** ⏳ AGUARDANDO LOGS DO CLIENTE

