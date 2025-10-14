# 🚨 RESOLVER ERRO 500 - PASSO A PASSO

## ⚠️ IMPORTANTE: O erro persiste porque o Docker NÃO FOI ATUALIZADO!

Quando você faz `git pull`, o código é baixado, mas o **Docker ainda está rodando a versão antiga**.

---

## ✅ SOLUÇÃO COMPLETA (Execute TODOS os passos):

### **Passo 1: Parar TUDO**

```bash
# Parar e REMOVER containers antigos
docker-compose down -v
```

**⚠️ O `-v` é ESSENCIAL!** Ele remove volumes antigos.

---

### **Passo 2: Limpar cache do Docker**

```bash
# Remover imagens antigas (força rebuild completo)
docker-compose rm -f backend
docker rmi projeto_calculadora_mcm_bobinas-backend
```

**Se der erro "image not found", tudo bem, continue!**

---

### **Passo 3: Verificar se tem a versão correta do código**

```bash
git log --oneline -1
```

**Deve mostrar:**
```
1787f24 fix: corrigir erro 500 ao importar nota - mover função normalizar_nome para escopo global
```

**Se NÃO mostrar**, faça:

```bash
# Descartar alterações locais
git checkout -- backend/nfe_system.db

# Fazer pull novamente
git pull origin main

# Verificar novamente
git log --oneline -1
```

---

### **Passo 4: Rebuild COMPLETO do Docker**

```bash
# Rebuild SEM usar cache
docker-compose build --no-cache backend

# Aguarde... pode demorar 2-3 minutos
```

---

### **Passo 5: Subir os serviços**

```bash
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f backend
```

**Aguarde até ver:**
```
INFO: Application startup complete.
```

**Então pressione Ctrl+C** para parar de ver os logs.

---

### **Passo 6: Testar importação**

```
1. Acessar: http://localhost:5173
2. Ir em "Notas Fiscais"
3. Importar XML
4. Ver se funcionou!
```

---

## 🔍 SE AINDA DER ERRO 500:

### **Capturar logs detalhados:**

```bash
# Windows (PowerShell)
docker-compose logs backend --tail=200 > logs-erro.txt
notepad logs-erro.txt

# Linux/Mac
docker-compose logs backend --tail=200 > logs-erro.txt
cat logs-erro.txt
```

**Procure por:**
- `ERROR: Erro ao criar nota:`
- `Traceback`
- `Exception`

**Envie essas linhas para mim!**

---

## 🧪 TESTE RÁPIDO:

Verifique se o backend está com o código novo:

```bash
docker-compose exec backend python -c "
from app.api.notas import normalizar_nome_materia_prima
print('✅ Função existe!')
print('Teste:', normalizar_nome_materia_prima('-FIO 2.0X7.0 CANTO QUADRADO'))
"
```

**Deve mostrar:**
```
✅ Função existe!
Teste: FIO 2.0X7.0 CANTO QUADRADO
```

**Se der erro**, o Docker NÃO foi atualizado!

---

## 🎯 COMANDO ÚNICO (Copie e cole tudo):

```bash
docker-compose down -v && docker-compose build --no-cache backend && docker-compose up -d && echo "✅ Sistema atualizado! Aguarde 10 segundos e teste em http://localhost:5173"
```

---

## ⚡ SOLUÇÃO ALTERNATIVA (Se o Docker não funcionar):

### **Rodar SEM Docker:**

```bash
# 1. Ativar ambiente virtual
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 4. Em outro terminal, rodar frontend
cd ..
npm run dev
```

---

## 📋 CHECKLIST:

- [ ] `docker-compose down -v` executado
- [ ] `git pull origin main` sem erros
- [ ] `git log` mostra commit `1787f24`
- [ ] `docker-compose build --no-cache backend` concluído
- [ ] `docker-compose up -d` rodando
- [ ] `docker-compose logs backend` mostra "Application startup complete"
- [ ] Teste de importação funcionou

---

## 🆘 AINDA COM PROBLEMA?

Execute e envie:

```bash
# 1. Versão do código
git log --oneline -5

# 2. Status dos containers
docker-compose ps

# 3. Logs completos
docker-compose logs backend --tail=100

# 4. Teste da função
docker-compose exec backend python -c "from app.api.notas import normalizar_nome_materia_prima; print(normalizar_nome_materia_prima('-FIO 2.0X7.0'))"
```

---

**O problema é 99% certeza que o Docker não foi atualizado!** 🎯

