# 🔍 CLIENTE - DIAGNÓSTICO DE PROBLEMAS

## ❌ ERRO: Backend não está respondendo

O erro `net::ERR_EMPTY_RESPONSE` significa que o backend não está rodando na porta 8000.

## 📋 COMANDOS PARA DIAGNOSTICAR:

### **1. Verificar containers:**
```bash
docker-compose ps
```

### **2. Ver logs do backend:**
```bash
docker-compose logs backend
```

### **3. Verificar se o backend está rodando:**
```bash
curl http://localhost:8000/health
```

### **4. Verificar se o arquivo SQLite existe:**
```bash
ls -la backend/nfe_system.db
```

## 🚨 POSSÍVEIS PROBLEMAS:

### **Problema 1: Arquivo SQLite não existe**
```bash
# Verificar se o arquivo existe
ls -la backend/nfe_system.db

# Se não existir, o desenvolvedor precisa enviar o arquivo
```

### **Problema 2: Backend não consegue acessar SQLite**
```bash
# Ver logs detalhados
docker-compose logs backend --follow
```

### **Problema 3: Porta 8000 ocupada**
```bash
# Verificar se algo está usando a porta 8000
netstat -tulpn | grep 8000
# ou
lsof -i :8000
```

## 🔧 SOLUÇÕES:

### **Solução 1: Reconstruir containers**
```bash
docker-compose down -v
docker-compose up -d --build
```

### **Solução 2: Verificar se o arquivo SQLite está sendo montado**
```bash
# Entrar no container backend
docker-compose exec backend bash

# Dentro do container, verificar se o arquivo existe
ls -la /app/nfe_system.db

# Sair do container
exit
```

### **Solução 3: Testar backend diretamente**
```bash
# Entrar no container backend
docker-compose exec backend bash

# Dentro do container, testar se o SQLite funciona
python -c "import sqlite3; conn = sqlite3.connect('nfe_system.db'); print('SQLite OK')"

# Testar se o FastAPI inicia
python -c "from app.main import app; print('FastAPI OK')"

# Sair do container
exit
```

## 📱 TESTE SIMPLES:

### **1. Testar se o backend responde:**
```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{"status": "healthy"}
```

### **2. Se não responder, verificar logs:**
```bash
docker-compose logs backend
```

## 🎯 RESULTADO ESPERADO:

- ✅ `docker-compose ps` mostra backend como "Up"
- ✅ `curl http://localhost:8000/health` retorna JSON
- ✅ Frontend consegue carregar dados

---

**Execute esses comandos e me envie o resultado dos logs!**
