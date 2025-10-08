# 📋 INSTRUÇÕES FINAIS - DOCKER PARA CLIENTE

## ✅ **CORREÇÕES APLICADAS:**

### **1. Migração `0001_initial_migration.py`**
- ✅ `unidades.menor_unidade_codigo` → `menor_unidade_id` (INTEGER)
- ✅ Tabela `fornecedores` → `fornecedor`
- ✅ Coluna `id` → `id_fornecedor`
- ✅ `notas.numero` INTEGER → VARCHAR(50)
- ✅ Adicionadas colunas `is_active` e `is_pinned` em `notas`
- ✅ Tabela `produtos_finais` adicionada

### **2. Migração `0002_populate_unidades.py`**
- ✅ Corrigido para usar `menor_unidade_id` (INTEGER) ao invés de `menor_unidade_codigo` (STRING)
- ✅ Agora usa SQL puro com `op.execute()` ao invés de `op.bulk_insert()`
- ✅ Insere unidades base primeiro, depois atualiza para auto-referência, depois insere derivadas

---

## 🎯 **ESTRATÉGIA RECOMENDADA:**

### **VOCÊ (Desenvolvedor):**
- ✅ Continue desenvolvendo **localmente** (mais rápido)
- ✅ Não precisa usar Docker no dia-a-dia
- ✅ Apenas teste Docker antes de enviar para o cliente

### **CLIENTE:**
- ✅ Usa Docker (fácil, sem instalações complexas)
- ✅ Apenas roda `docker-compose up -d`
- ✅ Tudo funciona automaticamente

---

## 🧪 **TESTANDO O DOCKER (VOCÊ):**

### **Antes de testar:**
1. **Feche seu frontend local** (Ctrl+C no terminal do Vite)
2. Feche qualquer processo usando porta 5173

### **Execute:**
```batch
.\testar-docker-cliente.bat
```

### **O que o script faz:**
1. Limpa ambiente Docker anterior
2. Reconstrói imagens com código corrigido
3. Aplica migrações corrigidas
4. Popula banco de dados
5. Mostra logs

### **Resultado esperado:**
- ✅ Sem erros de `menor_unidade_codigo`
- ✅ Tabelas criadas corretamente
- ✅ Seeds executados com sucesso
- ✅ Frontend acessível em http://localhost:5173
- ✅ Backend acessível em http://localhost:8000/docs

---

## 📦 **PARA O CLIENTE:**

### **Arquivos importantes:**
- ✅ `docker-compose.yml` - Configuração dos serviços
- ✅ `backend/Dockerfile` - Imagem do backend
- ✅ `src/Dockerfile` - Imagem do frontend
- ✅ `.dockerignore` - Arquivos a ignorar

### **Instruções para o cliente:**

**Crie um arquivo `CLIENTE-LEIA-ME.txt`:**

```txt
========================================
  INSTRUÇÕES PARA EXECUTAR O SISTEMA
========================================

REQUISITOS:
- Docker Desktop instalado
- Porta 5173 (frontend) disponível
- Porta 8000 (backend) disponível
- Porta 5432 (banco) disponível

PASSOS:

1. Extrair o projeto em uma pasta

2. Abrir PowerShell ou CMD nessa pasta

3. Executar:
   docker-compose up -d

4. Aguardar 1-2 minutos (primeira vez demora mais)

5. Acessar:
   http://localhost:5173

COMANDOS ÚTEIS:

- Ver logs:
  docker-compose logs -f

- Parar sistema:
  docker-compose down

- Resetar banco de dados:
  docker-compose down -v
  docker-compose up -d

SUPORTE:
- Se der erro de porta ocupada, pare o serviço que está usando
- Se der erro no banco, execute: docker-compose down -v && docker-compose up -d
- Logs ficam em: docker-compose logs

========================================
```

---

## 🚀 **PRÓXIMOS PASSOS:**

### **1. Teste agora (você):**
```batch
.\testar-docker-cliente.bat
```

### **2. Se funcionar:**
- ✅ Faça commit das correções
- ✅ Crie o arquivo `CLIENTE-LEIA-ME.txt`
- ✅ Envie para o cliente

### **3. Commit sugerido:**
```bash
git add .
git commit -m "fix: corrige migrações para usar menor_unidade_id

- Corrige 0001_initial_migration.py com estrutura correta
- Corrige 0002_populate_unidades.py para usar INTEGER
- Adiciona scripts de teste Docker
- Adiciona instruções para cliente
"
git push
```

---

## ⚠️ **IMPORTANTE:**

### **Você não precisa usar Docker sempre!**
- Continue usando seu ambiente local para desenvolver
- Use Docker apenas para:
  1. Testar antes de enviar para o cliente
  2. Garantir que funciona igual para todos
  3. Deploy em produção (se for o caso)

### **Vantagens dessa abordagem:**
- ✅ Você trabalha rápido (ambiente local)
- ✅ Cliente não precisa configurar nada (Docker)
- ✅ Garante compatibilidade (testa Docker antes de enviar)

---

## 📝 **CHECKLIST FINAL:**

Antes de enviar para o cliente:

- [ ] Testou Docker localmente com `testar-docker-cliente.bat`
- [ ] Frontend abre sem erros
- [ ] Backend responde (http://localhost:8000/docs)
- [ ] Consegue criar nota fiscal
- [ ] Banco de dados está populado
- [ ] Criou `CLIENTE-LEIA-ME.txt`
- [ ] Fez commit com código corrigido
- [ ] Testou em máquina limpa (se possível)

---

**Data:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

**Status:** ✅ Correções aplicadas, pronto para testar!

