# 🚀 **INSTRUÇÕES RÁPIDAS - DOCKER**

## ❌ **PROBLEMAS RESOLVIDOS:**
1. ✅ Erro `"Could not read package.json"` foi corrigido!
2. ✅ Frontend não respondendo - CORRIGIDO!
3. ✅ Backend não respondendo - CORRIGIDO!

## ✅ **SOLUÇÃO:**

### **1. Para usuários Windows:**
```bash
# Execute este comando na pasta do projeto:
test-docker.bat
```

### **2. Para usuários Linux/Mac:**
```bash
# Execute este comando na pasta do projeto:
chmod +x test-docker.sh
./test-docker.sh
```

### **3. Comando manual (qualquer sistema):**
```bash
# Limpar cache
docker-compose down
docker system prune -f

# Reconstruir
docker-compose up --build --force-recreate
```

---

## 🎯 **O QUE FOI CORRIGIDO:**

1. **Dockerfile do Frontend:** Agora copia corretamente o `package.json` da raiz
2. **Docker Compose:** Configurado para usar o contexto correto
3. **Dockerfile do MCP:** Corrigidos caracteres especiais
4. **Arquivo .dockerignore:** Criado para otimizar o build

---

## 📋 **ARQUIVOS CRIADOS/MODIFICADOS:**

- ✅ `docker-compose.yml` - Corrigido contexto do frontend
- ✅ `src/Dockerfile` - Corrigidos caminhos de arquivos
- ✅ `mcp-server-pdf/Dockerfile` - Corrigidos caracteres especiais
- ✅ `.dockerignore` - Otimização do build
- ✅ `test-docker.bat` - Script de teste para Windows
- ✅ `test-docker.sh` - Script de teste para Linux/Mac
- ✅ `README-Docker-CORRIGIDO.md` - Documentação atualizada

---

## 🚀 **PRÓXIMOS PASSOS:**

1. **Execute o script de teste:**
   - Windows: `test-docker.bat`
   - Linux/Mac: `./test-docker.sh`

2. **Aguarde a construção dos containers** (5-10 minutos na primeira vez)

3. **Acesse a aplicação:**
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000

---

## 🆘 **SE AINDA DER ERRO:**

### **Limpar tudo e começar do zero:**
```bash
docker-compose down
docker system prune -af
docker volume prune -f
docker-compose up --build
```

### **Verificar portas ocupadas:**
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Linux/Mac
lsof -i :8000
lsof -i :5173
```

---

## ✅ **RESULTADO ESPERADO:**

Após executar o script, você deve ver:
- ✅ Containers construídos com sucesso
- ✅ Banco PostgreSQL rodando
- ✅ Backend FastAPI rodando na porta 8000
- ✅ Frontend React rodando na porta 5173
- ✅ MCP server para PDFs configurado

**🎉 A aplicação estará funcionando perfeitamente!**
