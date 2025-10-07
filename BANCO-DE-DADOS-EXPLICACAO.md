# ðŸ—„ï¸ BANCO DE DADOS NO DOCKER - EXPLICAÃ‡ÃƒO COMPLETA

## â“ O CLIENTE PRECISA INSTALAR POSTGRESQL?

### **âŒ NÃƒO! O CLIENTE NÃƒO PRECISA INSTALAR NADA!**

O Docker faz **TUDO automaticamente**:
- âœ… Baixa a imagem do PostgreSQL 15
- âœ… Cria o banco de dados
- âœ… Configura usuÃ¡rio e senha
- âœ… Inicia o PostgreSQL
- âœ… MantÃ©m os dados salvos

---

## ðŸ“¦ COMO FUNCIONA?

### **1. Docker Volume (Armazenamento Persistente)**

No docker-compose.yml:
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

**O que isso significa?**
- Docker cria um "volume" chamado postgres_data
- Todos os dados do banco ficam salvos nesse volume
- Mesmo parando ou reiniciando o Docker, os dados **NÃƒO SÃƒO PERDIDOS**

---

## ðŸ“ ONDE OS DADOS FICAM SALVOS?

### **Windows:**
```
C:\ProgramData\Docker\volumes\project_postgres_data\_data
```

### **Linux:**
```
/var/lib/docker/volumes/project_postgres_data/_data
```

### **Mac:**
```
~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker/volumes/project_postgres_data/_data
```

---

## ðŸ” COMO VERIFICAR OS VOLUMES?

### **Ver todos os volumes:**
```bash
docker volume ls
```

**SaÃ­da esperada:**
```
DRIVER    VOLUME NAME
local     project_postgres_data
```

### **Ver detalhes do volume:**
```bash
docker volume inspect project_postgres_data
```

**SaÃ­da exemplo:**
```json
[
    {
        "CreatedAt": "2025-10-07T20:00:00Z",
        "Driver": "local",
        "Mountpoint": "C:\\ProgramData\\Docker\\volumes\\project_postgres_data\\_data",
        "Name": "project_postgres_data"
    }
]
```

---

## ðŸ”„ CICLO DE VIDA DOS DADOS

### **CenÃ¡rio 1: Parar e Iniciar Docker**
```bash
docker-compose down
docker-compose up
```
âœ… **DADOS PRESERVADOS** - Tudo continua como estava

### **CenÃ¡rio 2: Reconstruir Containers**
```bash
docker-compose down
docker-compose up --build
```
âœ… **DADOS PRESERVADOS** - Volume nÃ£o Ã© afetado

### **CenÃ¡rio 3: Limpar Sistema (sem volumes)**
```bash
docker-compose down
docker system prune -f
```
âœ… **DADOS PRESERVADOS** - Volumes nÃ£o sÃ£o removidos

### **CenÃ¡rio 4: Remover TUDO (incluindo dados)**
```bash
docker-compose down
docker volume rm project_postgres_data
```
âŒ **DADOS PERDIDOS** - Volume foi deletado

---

## ðŸ” CREDENCIAIS DO BANCO

Configuradas no docker-compose.yml:

| Campo | Valor |
|-------|-------|
| **Host** | localhost (externo) ou db (interno) |
| **Porta** | 5432 |
| **Banco** | mcm_bobinas |
| **UsuÃ¡rio** | postgres |
| **Senha** | postgres123 |

---

## ðŸ”Œ COMO ACESSAR O BANCO?

### **Do Host (mÃ¡quina local):**
```bash
# Usando psql (se tiver instalado)
psql -h localhost -p 5432 -U postgres -d mcm_bobinas

# Usando DBeaver, pgAdmin, DataGrip, etc.
Host: localhost
Port: 5432
Database: mcm_bobinas
User: postgres
Password: postgres123
```

### **De dentro do Docker (backend):**
```python
# JÃ¡ configurado automaticamente via variÃ¡vel de ambiente
DATABASE_URL=postgresql://postgres:postgres123@db:5432/mcm_bobinas
```

---

## ðŸ“Š TAMANHO DOS DADOS

### **Ver tamanho do volume:**
```bash
docker system df -v
```

### **Ver espaÃ§o usado pelo banco:**
```bash
docker exec -it project_db_1 psql -U postgres -d mcm_bobinas -c "SELECT pg_size_pretty(pg_database_size('mcm_bobinas'));"
```

---

## ðŸ”„ BACKUP E RESTORE

### **Fazer Backup:**
```bash
# Backup do banco inteiro
docker exec -t project_db_1 pg_dumpall -U postgres > backup.sql

# Backup de um banco especÃ­fico
docker exec -t project_db_1 pg_dump -U postgres mcm_bobinas > backup_mcm.sql
```

### **Restaurar Backup:**
```bash
# Restaurar banco especÃ­fico
cat backup_mcm.sql | docker exec -i project_db_1 psql -U postgres -d mcm_bobinas

# Restaurar tudo
cat backup.sql | docker exec -i project_db_1 psql -U postgres
```

---

## ðŸš¨ PERGUNTAS FREQUENTES

### **1. Os dados sÃ£o perdidos se reiniciar o computador?**
âŒ **NÃƒO!** Os dados ficam no volume do Docker, que Ã© persistente.

### **2. Preciso instalar PostgreSQL na mÃ¡quina?**
âŒ **NÃƒO!** O Docker roda PostgreSQL isolado em container.

### **3. Posso acessar o banco com ferramentas visuais?**
âœ… **SIM!** Use DBeaver, pgAdmin, DataGrip, etc.
- Host: localhost
- Port: 5432
- User: postgres
- Password: postgres123

### **4. Como mudar a senha do banco?**
Editar no docker-compose.yml:
```yaml
environment:
  POSTGRES_PASSWORD: sua_senha_aqui
```

### **5. Onde ficam os uploads de arquivos?**
```
./backend/uploads/
```
TambÃ©m mapeado no Docker como volume.

### **6. Posso usar outro banco de dados?**
âœ… **SIM!** Substituir postgres:15 por:
- postgres:16 (versÃ£o mais nova)
- mysql:8 (MySQL)
- mariadb:10 (MariaDB)

### **7. Como limpar o banco mas manter a estrutura?**
```bash
docker exec -it project_db_1 psql -U postgres -d mcm_bobinas -c "TRUNCATE TABLE nome_tabela CASCADE;"
```

---

## ðŸ“‹ RESUMO PARA O CLIENTE

### **âœ… O QUE O CLIENTE PRECISA:**
1. Docker Desktop instalado
2. Executar docker-compose up --build
3. **PRONTO!** Banco criado e funcionando

### **âœ… O QUE ACONTECE AUTOMATICAMENTE:**
1. Docker baixa imagem PostgreSQL 15
2. Cria banco mcm_bobinas
3. Configura usuÃ¡rio e senha
4. Cria volume persistente
5. Inicia banco de dados
6. Backend conecta automaticamente

### **âœ… DADOS FICAM SALVOS EM:**
- Volume Docker: project_postgres_data
- Persistente mesmo reiniciando
- Backup automÃ¡tico via volume

### **âŒ O QUE NÃƒO PRECISA:**
- âŒ Instalar PostgreSQL
- âŒ Configurar banco manualmente
- âŒ Criar tabelas manualmente
- âŒ Gerenciar credenciais
- âŒ Se preocupar com backups (volume persistente)

---

## ðŸŽ¯ CONCLUSÃƒO

**O cliente NÃƒO precisa fazer NADA relacionado ao banco de dados!**

O Docker faz tudo:
- âœ… Instala
- âœ… Configura
- âœ… Inicia
- âœ… MantÃ©m dados salvos
- âœ… Conecta com backend

**Ã‰ literalmente "apertar um botÃ£o e funcionar"! ðŸš€**

---

**Data:** 2025-10-07 18:17:56
