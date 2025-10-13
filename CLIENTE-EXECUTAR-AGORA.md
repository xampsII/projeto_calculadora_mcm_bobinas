# 🚀 EXECUTAR AGORA - Sistema NFE

## ⚡ **COMANDO ÚNICO PARA EXECUTAR:**

```bash
docker-compose up -d
```

## 📋 **O QUE ACONTECERÁ AUTOMATICAMENTE:**

1. ✅ **PostgreSQL** será criado e configurado
2. ✅ **Banco nfedb** será criado automaticamente
3. ✅ **Migrações** serão executadas (criação de tabelas)
4. ✅ **Dados iniciais** serão inseridos:
   - 3 usuários (admin, editor, viewer)
   - 14 unidades de medida
   - Matérias-primas de exemplo
5. ✅ **Backend FastAPI** iniciará na porta 8000
6. ✅ **Frontend React** iniciará na porta 5173

## 🎯 **APÓS EXECUTAR O COMANDO:**

### **1. Aguarde 3-5 minutos** para inicialização completa

### **2. Verifique se está funcionando:**
```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver status dos containers
docker-compose ps
```

### **3. Acesse o sistema:**
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

### **4. Faça login:**
- **Admin**: `admin@nfe.com` / `admin123`
- **Editor**: `editor@nfe.com` / `editor123`
- **Viewer**: `viewer@nfe.com` / `viewer123`

## 🔧 **COMANDOS ÚTEIS:**

```bash
# Parar tudo
docker-compose down

# Reiniciar
docker-compose restart

# Ver logs
docker-compose logs -f backend
docker-compose logs -f db
```

## ❓ **SE DER PROBLEMA:**

### **Erro de porta ocupada:**
```bash
# Verificar o que está usando as portas
netstat -ano | findstr :5432
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

### **Banco vazio:**
```bash
# Executar seeds manualmente
docker-compose exec backend python -m app.seeds
```

### **Reiniciar do zero:**
```bash
docker-compose down -v
docker-compose up -d
```

---

## 🎉 **RESULTADO ESPERADO:**

Após executar `docker-compose up -d` e aguardar alguns minutos, você terá:

- ✅ **Sistema NFE completo funcionando**
- ✅ **Banco PostgreSQL populado com dados**
- ✅ **3 usuários prontos para login**
- ✅ **Interface web acessível**
- ✅ **API REST funcionando**

**🚀 Execute agora: `docker-compose up -d`**
