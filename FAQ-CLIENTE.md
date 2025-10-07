# â“ FAQ - PERGUNTAS FREQUENTES DO CLIENTE

## ðŸ—„ï¸ BANCO DE DADOS

### **1. Preciso instalar PostgreSQL?**
**âŒ NÃƒO!** O Docker faz tudo automaticamente.

### **2. Onde os dados ficam salvos?**
**ðŸ“ Em um volume do Docker** na sua mÃ¡quina. Os dados NÃƒO somem ao reiniciar.

**LocalizaÃ§Ã£o:**
- Windows: C:\ProgramData\Docker\volumes\project_postgres_data\_data
- Linux: /var/lib/docker/volumes/project_postgres_data/_data
- Mac: ~/Library/Containers/com.docker.docker/.../project_postgres_data/_data

### **3. Os dados sÃ£o perdidos ao fechar o Docker?**
**âŒ NÃƒO!** Os dados ficam salvos permanentemente no volume.

### **4. Como fazer backup do banco?**
```bash
# Backup simples
docker exec -t project_db_1 pg_dump -U postgres mcm_bobinas > backup.sql

# Restaurar
cat backup.sql | docker exec -i project_db_1 psql -U postgres -d mcm_bobinas
```

### **5. Posso acessar o banco com programas visuais?**
**âœ… SIM!** Use DBeaver, pgAdmin, DataGrip, etc:
- Host: localhost
- Port: 5432
- User: postgres
- Password: postgres123
- Database: mcm_bobinas

---

## ðŸ³ DOCKER

### **6. Preciso instalar algo alÃ©m do Docker?**
**âŒ NÃƒO!** Apenas o Docker Desktop. Tudo mais Ã© automÃ¡tico.

### **7. Como iniciar o sistema?**
```bash
# OpÃ§Ã£o 1: Script automÃ¡tico
reiniciar-docker.bat

# OpÃ§Ã£o 2: Manual
docker-compose up --build
```

### **8. Como parar o sistema?**
```bash
# Ctrl+C no terminal (ou fechar o terminal)

# Ou comando:
docker-compose down
```

### **9. Os dados sÃ£o perdidos ao parar o Docker?**
**âŒ NÃƒO!** Volumes sÃ£o persistentes.

### **10. Quanto espaÃ§o em disco Ã© necessÃ¡rio?**
- **Docker Desktop:** ~500 MB
- **Imagens (PostgreSQL, Node, Python):** ~1-2 GB
- **Dados da aplicaÃ§Ã£o:** Depende do uso (comeÃ§a com ~100 MB)

**Total inicial:** ~2-3 GB

---

## ðŸŒ ACESSO

### **11. Como acessar a aplicaÃ§Ã£o?**
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/docs

### **12. Outros computadores podem acessar?**
**âœ… SIM!** Mas precisa configurar:
- Liberar portas no firewall
- Usar IP da mÃ¡quina ao invÃ©s de localhost
- Exemplo: http://192.168.1.100:5173

### **13. Funciona na internet (online)?**
**âŒ NÃƒO por padrÃ£o.** Ã‰ local. Para colocar online precisa:
- Servidor em nuvem (AWS, Azure, DigitalOcean)
- DomÃ­nio prÃ³prio
- ConfiguraÃ§Ãµes de seguranÃ§a

---

## ðŸ”’ SEGURANÃ‡A

### **14. Ã‰ seguro usar as senhas padrÃ£o?**
**âš ï¸ APENAS EM AMBIENTE LOCAL!** 

Para produÃ§Ã£o, mudar em docker-compose.yml:
```yaml
environment:
  POSTGRES_PASSWORD: senha_forte_aqui_123!@#
  SECRET_KEY: chave_secreta_unica_aqui
```

### **15. Meus dados sÃ£o privados?**
**âœ… SIM!** Tudo roda localmente na sua mÃ¡quina. Nada vai para internet.

---

## ðŸ› ï¸ MANUTENÃ‡ÃƒO

### **16. Como atualizar o sistema?**
```bash
# 1. Puxar atualizaÃ§Ãµes do repositÃ³rio
git pull

# 2. Reconstruir containers
docker-compose down
docker-compose up --build
```

### **17. Como limpar dados antigos (reset completo)?**
```bash
# âš ï¸ ATENÃ‡ÃƒO: Isso APAGA TODOS OS DADOS!
docker-compose down
docker volume rm project_postgres_data
docker-compose up --build
```

### **18. Como ver logs de erro?**
```bash
# Todos os logs
docker-compose logs

# Apenas backend
docker-compose logs backend

# Apenas frontend
docker-compose logs frontend

# Apenas banco
docker-compose logs db
```

---

## ðŸš¨ PROBLEMAS COMUNS

### **19. "Port already in use"**
**SoluÃ§Ã£o:** Outra aplicaÃ§Ã£o estÃ¡ usando a porta.
```bash
# Windows - Verificar
netstat -ano | findstr :8000
taskkill /PID <numero> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### **20. "Cannot connect to Docker daemon"**
**SoluÃ§Ã£o:** Docker Desktop nÃ£o estÃ¡ rodando. Abrir o Docker Desktop.

### **21. Frontend nÃ£o carrega (tela branca)**
**SoluÃ§Ã£o:**
```bash
# Ver logs
docker-compose logs frontend

# Se aparecer "vite: not found", reconstruir:
docker-compose down
docker system prune -f
docker-compose up --build
```

### **22. Backend retorna erro 500**
**SoluÃ§Ã£o:**
```bash
# Ver logs
docker-compose logs backend

# Verificar se banco estÃ¡ funcionando
docker-compose ps
```

---

## ðŸ’¡ DICAS

### **23. Como acelerar o Docker?**
- Alocar mais RAM no Docker Desktop (Settings â†’ Resources)
- Usar SSD ao invÃ©s de HD
- Fechar outras aplicaÃ§Ãµes pesadas

### **24. Posso rodar em vÃ¡rias mÃ¡quinas?**
**âœ… SIM!** Cada mÃ¡quina terÃ¡ seu prÃ³prio banco de dados local.

### **25. Como compartilhar o banco entre mÃ¡quinas?**
Usar um PostgreSQL externo (nÃ£o no Docker) ou:
- Servidor dedicado
- Banco em nuvem (AWS RDS, Supabase, etc.)

---

## ðŸ“ž SUPORTE

### **26. Onde pedir ajuda?**
1. Ver logs: docker-compose logs
2. Verificar documentaÃ§Ã£o: README-Docker-CORRIGIDO.md
3. Contatar suporte tÃ©cnico

### **27. Como reportar um bug?**
Enviar:
1. Resultado de docker ps
2. Logs completos: docker-compose logs > logs.txt
3. DescriÃ§Ã£o do problema
4. Screenshot (se houver erro visual)

---

**Data:** 2025-10-07 18:19:00
