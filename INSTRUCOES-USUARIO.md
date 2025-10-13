# 🚀 Instruções para o Usuário Final

## Como usar o Sistema NFE via Docker

### 1. 📥 Clone o Repositório
```bash
git clone <URL_DO_REPOSITORIO>
cd project
```

### 2. 🐳 Execute o Setup Automático

**Windows:**
```bash
setup-docker.bat
```

**Linux/Mac:**
```bash
chmod +x setup-docker.sh
./setup-docker.sh
```

### 3. ⏳ Aguarde a Inicialização
O script irá:
- ✅ Verificar pré-requisitos (Docker)
- ✅ Criar diretórios necessários
- ✅ Baixar e construir imagens Docker
- ✅ Iniciar todos os serviços
- ✅ Executar migrações do banco
- ✅ Popular com dados iniciais

**Tempo estimado: 3-5 minutos na primeira vez**

### 4. 🎉 Acesse o Sistema

Após o setup, acesse:
- **Sistema Web**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

### 5. 👤 Faça Login

Use um dos usuários padrão:
- **Admin**: `admin@nfe.com` / `admin123`
- **Editor**: `editor@nfe.com` / `editor123`
- **Viewer**: `viewer@nfe.com` / `viewer123`

---

## 🔧 Comandos Úteis

### Ver Status
```bash
docker-compose ps
```

### Ver Logs
```bash
docker-compose logs -f
```

### Parar Sistema
```bash
docker-compose down
```

### Reiniciar Sistema
```bash
docker-compose restart
```

---

## ❓ Problemas Comuns

### Porta já está em uso
- Pare outros serviços que usam as portas 5173, 8000, 5432, 6379
- Ou altere as portas no arquivo `docker-compose.yml`

### Docker não está rodando
- Inicie o Docker Desktop
- Aguarde o Docker ficar pronto

### Erro de permissão (Linux/Mac)
```bash
sudo chown -R $USER:$USER .
```

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs`
2. Consulte o `README-DOCKER.md` para mais detalhes
3. Entre em contato com o suporte técnico

---

**🎯 Objetivo**: Sistema NFE completo rodando em poucos minutos!
