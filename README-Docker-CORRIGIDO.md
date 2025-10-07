# 🐳 **GUIA COMPLETO - DOCKER**

## 📋 **PRÉ-REQUISITOS**

### **1. Instalar Docker Desktop:**
- **Windows:** https://www.docker.com/products/docker-desktop/
- **Mac:** https://www.docker.com/products/docker-desktop/
- **Linux:** https://docs.docker.com/engine/install/

### **2. Verificar instalação:**
```bash
docker --version
docker-compose --version
```

---

## 🚀 **EXECUÇÃO SIMPLES**

### **1. Navegar para o projeto:**
```bash
cd project
```

### **2. Execute com Docker Compose:**
```bash
docker-compose up --build
```

### **3. Aguarde a inicialização:**
O comando acima irá:
- ✅ Baixar as imagens necessárias
- ✅ Construir os containers
- ✅ Inicializar o banco PostgreSQL
- ✅ Executar o backend FastAPI
- ✅ Executar o frontend React
- ✅ Configurar o MCP server para PDFs

### **4. Acesse a aplicação:**
- **🌐 Frontend:** http://localhost:5173
- **🔧 Backend API:** http://localhost:8000
- **🗄️ Banco de dados:** localhost:5432

---

## ⚠️ **SOLUÇÃO DE PROBLEMAS**

### **Erro: "Could not read package.json"**
Se aparecer este erro durante o build:

```bash
# 1. Limpar cache do Docker
docker-compose down
docker system prune -f

# 2. Reconstruir tudo
docker-compose up --build --force-recreate
```

### **Erro: "Port already in use"**
Se alguma porta estiver ocupada:

```bash
# Windows - Verificar o que está usando a porta
netstat -ano | findstr :8000
netstat -ano | findstr :5173
netstat -ano | findstr :5432

# Windows - Parar processo se necessário
taskkill /PID <numero_do_processo> /F

# Linux/Mac - Verificar portas
lsof -i :8000
lsof -i :5173
lsof -i :5432

# Linux/Mac - Parar processo
kill -9 <PID>
```

### **Erro de permissão no Windows:**
```bash
# Executar PowerShell como Administrador
# Ou usar WSL2 se disponível
```

---

## 🔧 **COMANDOS ÚTEIS**

### **Parar todos os serviços:**
```bash
docker-compose down
```

### **Ver logs em tempo real:**
```bash
docker-compose logs -f
```

### **Ver logs de um serviço específico:**
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### **Reiniciar um serviço específico:**
```bash
docker-compose restart backend
docker-compose restart frontend
```

### **Limpar tudo e começar do zero:**
```bash
docker-compose down
docker system prune -f
docker volume prune -f
docker-compose up --build
```

---

## 📊 **ESTRUTURA DOS SERVIÇOS**

### **🗄️ Banco de dados (PostgreSQL):**
- **Porta:** 5432
- **Banco:** mcm_bobinas
- **Usuário:** postgres
- **Senha:** postgres123
- **Dados persistentes:** Sim (volume postgres_data)

### **🔧 Backend (FastAPI):**
- **Porta:** 8000
- **Framework:** Python FastAPI
- **Banco:** Conecta automaticamente ao PostgreSQL
- **Uploads:** Pasta compartilhada

### **🌐 Frontend (React):**
- **Porta:** 5173
- **Framework:** React + Vite + TypeScript
- **API:** Conecta ao backend automaticamente

### **📄 MCP Server (PDF):**
- **Função:** Processamento de PDFs com IA
- **Tipo:** Node.js
- **Integração:** Usado pelo backend quando necessário

---

## 💾 **VOLUMES PERSISTENTES**

### **Dados que ficam salvos:**
- ✅ **Banco PostgreSQL:** Todos os dados da aplicação
- ✅ **Uploads:** Arquivos enviados pelos usuários
- ✅ **Configurações:** Configurações do sistema

### **Localização dos volumes:**
```bash
# Ver volumes do Docker
docker volume ls

# Ver detalhes de um volume
docker volume inspect project_postgres_data
```

---

## 🆘 **SUPORTE**

### **Se algo não funcionar:**

1. **Verificar se Docker está rodando:**
   ```bash
   docker ps
   ```

2. **Verificar logs de erro:**
   ```bash
   docker-compose logs
   ```

3. **Limpar cache e tentar novamente:**
   ```bash
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```

4. **Verificar se as portas estão livres:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

### **Contato:**
- 📧 Email: suporte@empresa.com
- 💬 WhatsApp: (11) 99999-9999

---

## 🎯 **RESUMO RÁPIDO**

```bash
# 1. Instalar Docker Desktop
# 2. Navegar para a pasta do projeto
cd project

# 3. Executar
docker-compose up --build

# 4. Acessar
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```

**🎉 Pronto! A aplicação estará rodando localmente!**
