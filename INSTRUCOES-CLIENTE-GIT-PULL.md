# 🔧 RESOLVER CONFLITO NO GIT PULL

## ❌ Erro que você está vendo:

```
error: Your local changes to the following files would be overwritten by merge:
        backend/nfe_system.db
Please commit your changes or stash them before you merge.
```

---

## ✅ SOLUÇÃO RÁPIDA (Recomendada)

O arquivo `backend/nfe_system.db` foi atualizado no servidor com **67 correções de preços duplicados**.

### **Opção 1: Aceitar a versão do servidor (RECOMENDADO)**

```bash
# 1. Fazer backup do seu banco atual (opcional)
cp backend/nfe_system.db backend/nfe_system.db.backup

# 2. Descartar suas alterações locais e aceitar a versão do servidor
git checkout -- backend/nfe_system.db

# 3. Fazer pull novamente
git pull origin main

# 4. Reiniciar o Docker
docker-compose down -v
docker-compose up -d --build
```

**✅ Use esta opção se:**
- Você não fez alterações importantes no banco
- Quer usar o banco corrigido do servidor

---

### **Opção 2: Manter suas alterações locais**

```bash
# 1. Fazer backup do seu banco
cp backend/nfe_system.db backend/nfe_system.db.local

# 2. Guardar suas alterações temporariamente
git stash

# 3. Fazer pull
git pull origin main

# 4. Restaurar seu banco local
cp backend/nfe_system.db.local backend/nfe_system.db

# 5. Executar script de correção de preços duplicados
python corrigir-precos-duplicados.py

# 6. Reiniciar o Docker
docker-compose down -v
docker-compose up -d --build
```

**✅ Use esta opção se:**
- Você tem dados importantes no seu banco local
- Quer manter suas alterações

---

### **Opção 3: Forçar atualização (Limpar tudo)**

```bash
# ⚠️ ATENÇÃO: Isso apaga TODAS as suas alterações locais!

# 1. Fazer backup completo (opcional)
cp -r backend backend_backup

# 2. Resetar para o estado do servidor
git fetch origin
git reset --hard origin/main

# 3. Reiniciar o Docker
docker-compose down -v
docker-compose up -d --build
```

**⚠️ Use esta opção APENAS se:**
- Você quer começar do zero
- Não tem dados importantes localmente

---

## 🎯 QUAL OPÇÃO ESCOLHER?

### **Se você está testando o sistema:**
→ Use **Opção 1** (mais rápida e segura)

### **Se você já tem notas e produtos cadastrados:**
→ Use **Opção 2** (preserva seus dados)

### **Se está com muitos problemas:**
→ Use **Opção 3** (recomeça do zero)

---

## 📋 DEPOIS DO GIT PULL

### **1. Verificar se atualizou:**
```bash
git log --oneline -5
```

**Deve mostrar:**
```
f801a20 fix: corrigir 67 preços duplicados no histórico
40e1e37 fix: corrigir atualização de preços ao importar nota fiscal
2b36cc0 feat: adicionar sistema de atualização automática de preços
aaf7060 fix: corrigir salvamento de valores editados manualmente
```

### **2. Verificar banco corrigido:**
```bash
python verificar-sqlite-completo.py
```

### **3. Testar o sistema:**
1. Acessar: http://localhost:5173
2. Ir em "Matérias-Primas" → Ver histórico de preços
3. Importar uma nota fiscal XML
4. Ver preços atualizados
5. Ir em "Produtos" → Clicar "Recalcular Preços"
6. Confirmar valores atualizados

---

## ❓ PROBLEMAS COMUNS

### **Erro: "git: command not found"**
→ Você está no PowerShell, use:
```powershell
git checkout -- backend/nfe_system.db
git pull origin main
```

### **Erro: "Permission denied"**
→ Feche o Docker primeiro:
```bash
docker-compose down
# Depois faça o git pull
git pull origin main
# Depois suba novamente
docker-compose up -d --build
```

### **Banco continua com preços duplicados**
→ Execute o script de correção:
```bash
python corrigir-precos-duplicados.py
```

---

## 📞 PRECISA DE AJUDA?

Se nenhuma opção funcionar, envie:

```bash
# 1. Status do git
git status

# 2. Logs do erro completo
git pull origin main 2>&1

# 3. Versão atual
git log --oneline -1
```

---

## ✅ RESUMO RÁPIDO

**Comando mais rápido (Opção 1):**
```bash
git checkout -- backend/nfe_system.db && git pull origin main && docker-compose down -v && docker-compose up -d --build
```

**Pronto! Sistema atualizado com todas as correções!** 🚀

