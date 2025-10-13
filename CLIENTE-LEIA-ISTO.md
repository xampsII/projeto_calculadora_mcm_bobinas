# 🚀 SISTEMA NFE - INSTRUÇÕES DE INSTALAÇÃO

## **COMANDO PARA INICIAR:**

```bash
docker-compose up -d
```

## **⏱️ AGUARDE 3-5 MINUTOS**

O sistema vai:
1. ✅ Criar banco PostgreSQL
2. ✅ Criar todas as tabelas
3. ✅ Inserir usuários e dados iniciais
4. ✅ **Restaurar todos os dados reais do backup**
5. ✅ Iniciar backend e frontend

## **🌐 ACESSAR O SISTEMA:**

- **URL**: http://localhost:5173
- **Login**: `admin@nfe.com`
- **Senha**: `admin123`

## **📊 DADOS INCLUÍDOS:**

✅ Todos os dados do banco de produção foram restaurados:
- Matérias-primas
- Fornecedores
- Notas fiscais
- Produtos
- Usuários
- Histórico de preços

---

## **🔧 COMANDOS ÚTEIS:**

```bash
# Ver logs em tempo real
docker-compose logs -f

# Ver apenas logs do backend
docker-compose logs -f backend

# Ver apenas logs do banco
docker-compose logs -f db

# Reiniciar tudo
docker-compose restart

# Parar tudo
docker-compose down

# Parar e limpar volumes (recomeçar do zero)
docker-compose down -v
```

---

## **❓ PROBLEMAS COMUNS:**

### **Backend não sobe:**
```bash
# 1. Ver logs do backend
docker-compose logs backend

# 2. Ver logs em tempo real
docker-compose logs -f backend

# 3. Verificar status dos containers
docker-compose ps

# 4. Se backend está "Exit" ou "Restarting", reiniciar:
docker-compose restart backend
```

### **Porta já em uso:**
```bash
# Verificar o que está usando as portas
netstat -ano | findstr :5432
netstat -ano | findstr :8000
netstat -ano | findstr :5173
```

### **Banco vazio (sem dados):**
```bash
# Verificar se backup existe
dir docker\postgres\init\04-meus-dados.backup

# Ver logs do banco
docker-compose logs db
```

### **Erro de conexão:**
Aguarde 5-10 minutos. O PostgreSQL pode demorar para:
- Criar o banco
- Restaurar o backup (pode ter muitos dados)
- Executar migrações

---

## **✅ RESULTADO ESPERADO:**

Após executar `docker-compose up -d`:
- ✅ Sistema funcionando em http://localhost:5173
- ✅ API em http://localhost:8000
- ✅ Documentação em http://localhost:8000/docs
- ✅ Todos os dados restaurados e funcionando

**Bom uso! 🎉**
