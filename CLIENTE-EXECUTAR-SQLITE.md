# 🚀 CLIENTE - EXECUTAR COM SQLITE

## ✅ SOLUÇÃO SIMPLIFICADA

Agora o sistema usa **SQLite** em vez de PostgreSQL, garantindo que você tenha **TODAS** as matérias primas e dados do sistema!

## 📋 COMANDOS PARA EXECUTAR:

```bash
# 1. Parar containers existentes
docker-compose down -v

# 2. Remover containers antigos (opcional)
docker system prune -f

# 3. Subir com SQLite
docker-compose up -d

# 4. Verificar se está funcionando
docker-compose logs backend
docker-compose logs frontend
```

## 🔍 VERIFICAR SE FUNCIONOU:

### **1. Testar Backend:**
```bash
curl http://localhost:8000/health
```

### **2. Testar Matérias Primas:**
```bash
curl http://localhost:8000/produtos-finais/materias-primas-disponiveis
```

### **3. Acessar Frontend:**
- Abra: http://localhost:5173
- Vá para "Matérias-Primas"
- Deve aparecer **166 matérias primas** ✅

## 🎯 VANTAGENS DA SOLUÇÃO SQLITE:

✅ **Simples:** Sem configuração complexa  
✅ **Completo:** Todas as 166 matérias primas + dados  
✅ **Rápido:** Inicia em segundos  
✅ **Funcional:** Mesmos dados que o desenvolvedor vê  
✅ **Sem dependências:** Não precisa de PostgreSQL  

## 🚨 SE DER PROBLEMA:

### **Verificar logs:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

### **Reiniciar tudo:**
```bash
docker-compose down -v
docker-compose up -d --build
```

### **Verificar se o arquivo SQLite existe:**
```bash
ls -la backend/nfe_system.db
```

## 📱 ACESSO:

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

---

**🎉 Agora você deve ver TODAS as 166 matérias primas!**
