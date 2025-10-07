# 🔍 **DEBUG - DOCKER NÃO RESPONDE**

## ❌ **PROBLEMA:**
Os containers iniciam mas frontend e backend não respondem.

---

## ✅ **CORREÇÕES APLICADAS:**

### **1. Frontend (Vite):**
- ✅ Configurado `host: 0.0.0.0` no `vite.config.ts`
- ✅ Adicionado `watch: { usePolling: true }` para Docker
- ✅ Copiados todos os arquivos de configuração necessários
- ✅ Estrutura de pastas corrigida (`src/` dentro de `/app`)

### **2. Backend (FastAPI):**
- ✅ Removido `--reload` (pode causar problemas no Docker)
- ✅ Configurado `--host 0.0.0.0`
- ✅ Adicionadas variáveis de ambiente corretas
- ✅ Volumes montados para hot-reload

### **3. Docker Compose:**
- ✅ Variáveis de ambiente completas
- ✅ Volumes para desenvolvimento
- ✅ Dependências corretas entre serviços

---

## 🚀 **INSTRUÇÕES PARA O USUÁRIO:**

### **Passo 1: Parar tudo**
```bash
docker-compose down
```

### **Passo 2: Limpar cache**
```bash
docker system prune -f
docker volume prune -f
```

### **Passo 3: Reconstruir**
```bash
docker-compose up --build --force-recreate
```

### **Passo 4: Verificar logs**
```bash
# Em outro terminal, verificar cada serviço:

# Logs do backend
docker-compose logs -f backend

# Logs do frontend
docker-compose logs -f frontend

# Logs do banco
docker-compose logs -f db
```

---

## 🔧 **VERIFICAÇÕES IMPORTANTES:**

### **1. Verificar se os containers estão rodando:**
```bash
docker ps
```

**Resultado esperado:**
```
CONTAINER ID   IMAGE          COMMAND                  STATUS         PORTS
xxxxx          project_backend   "uvicorn app.main:app"  Up 2 minutes   0.0.0.0:8000->8000/tcp
xxxxx          project_frontend  "npm run dev"           Up 2 minutes   0.0.0.0:5173->5173/tcp
xxxxx          postgres:15       "docker-entrypoint.s…"  Up 2 minutes   0.0.0.0:5432->5432/tcp
```

### **2. Testar Backend diretamente:**
```bash
# Windows
curl http://localhost:8000/docs

# Linux/Mac
curl http://localhost:8000/docs

# Ou abrir no navegador:
http://localhost:8000/docs
```

**Resultado esperado:** Página da documentação FastAPI (Swagger)

### **3. Testar Frontend diretamente:**
```bash
# Abrir no navegador:
http://localhost:5173
```

**Resultado esperado:** Aplicação React carregada

### **4. Verificar logs do Frontend:**
```bash
docker-compose logs frontend
```

**Logs esperados:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: http://0.0.0.0:5173/
➜  Network: http://172.x.x.x:5173/
```

### **5. Verificar logs do Backend:**
```bash
docker-compose logs backend
```

**Logs esperados:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## ⚠️ **PROBLEMAS COMUNS:**

### **Problema 1: "Cannot connect to the Docker daemon"**
**Solução:**
```bash
# Windows: Abrir Docker Desktop
# Linux: 
sudo systemctl start docker
```

### **Problema 2: "Port already in use"**
**Solução:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <numero_do_processo> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### **Problema 3: Frontend não carrega (tela branca)**
**Verificar:**
1. Console do navegador (F12)
2. Logs do container: `docker-compose logs frontend`
3. Se Vite está rodando: deve aparecer "ready in XXX ms"

**Solução:**
```bash
# Entrar no container e verificar
docker exec -it project_frontend_1 sh
ls -la /app
cat vite.config.ts
```

### **Problema 4: Backend retorna 404**
**Verificar:**
1. Se uvicorn está rodando: `docker-compose logs backend`
2. Se banco está conectado: `docker-compose logs db`
3. Se migrações rodaram

**Solução:**
```bash
# Entrar no container e verificar
docker exec -it project_backend_1 bash
ls -la /app
python -c "from app.main import app; print(app.routes)"
```

### **Problema 5: Erro de banco de dados**
**Verificar:**
```bash
# Verificar se PostgreSQL está saudável
docker-compose ps

# Deve mostrar "healthy" no status do db
```

**Solução:**
```bash
# Recriar volume do banco
docker-compose down
docker volume rm project_postgres_data
docker-compose up --build
```

---

## 🎯 **TESTE COMPLETO:**

Execute este comando para testar tudo:
```bash
# Parar tudo
docker-compose down

# Limpar
docker system prune -f

# Reconstruir
docker-compose up --build --force-recreate
```

Aguarde ver estas mensagens:
1. ✅ `db_1 | database system is ready to accept connections`
2. ✅ `backend_1 | INFO: Uvicorn running on http://0.0.0.0:8000`
3. ✅ `frontend_1 | VITE ready in XXX ms`

Então teste:
1. ✅ http://localhost:8000/docs (deve abrir Swagger)
2. ✅ http://localhost:5173 (deve abrir aplicação)

---

## 📞 **SE AINDA NÃO FUNCIONAR:**

### **Envie estas informações:**

1. **Resultado de:** `docker ps`
2. **Logs completos:**
   ```bash
   docker-compose logs > logs.txt
   ```
3. **Teste de conectividade:**
   ```bash
   curl -v http://localhost:8000/docs
   curl -v http://localhost:5173
   ```
4. **Verificar portas:**
   ```bash
   # Windows
   netstat -ano | findstr ":8000 :5173 :5432"
   
   # Linux/Mac
   lsof -i :8000 -i :5173 -i :5432
   ```

---

## 🎉 **SUCESSO:**

Se tudo funcionar, você verá:
- ✅ **Backend:** http://localhost:8000/docs → Documentação Swagger
- ✅ **Frontend:** http://localhost:5173 → Aplicação React
- ✅ **Banco:** Conectado e funcionando
- ✅ **Logs:** Sem erros nos 3 containers
