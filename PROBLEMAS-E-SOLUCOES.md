# ðŸš¨ PROBLEMAS IDENTIFICADOS E SOLUÃ‡Ã•ES

## âŒ PROBLEMA 1: Banco de Dados Zerado

### **Causa:**
Quando o Docker Ã© reconstruÃ­do com docker-compose up --build --force-recreate, ele cria um **NOVO volume** se o anterior foi deletado.

### **Por que aconteceu:**
- Cliente executou docker volume prune -f ou docker volume rm project_postgres_data
- Isso APAGOU todos os dados do banco

### **âœ… SOLUÃ‡ÃƒO IMEDIATA:**

#### **OpÃ§Ã£o 1: Restaurar Backup (se tiver)**
```bash
# Se tiver um backup SQL
cat backup.sql | docker exec -i project_db_1 psql -U postgres -d mcm_bobinas
```

#### **OpÃ§Ã£o 2: Popular dados novamente**
O cliente precisa re-cadastrar os produtos manualmente OU vocÃª pode criar um script de seed.

### **âœ… PREVENÃ‡ÃƒO:**

#### **NUNCA execute estes comandos em produÃ§Ã£o:**
```bash
âŒ docker volume prune -f
âŒ docker volume rm project_postgres_data
âŒ docker-compose down -v
```

#### **Para limpar cache SEM perder dados:**
```bash
âœ… docker-compose down
âœ… docker system prune -f     # Limpa imagens e cache, MAS nÃ£o volumes
âœ… docker-compose up --build
```

---

## âŒ PROBLEMA 2: Erro ao Processar PDF com IA

### **Causa:**
No arquivo uploads_ia.py linha 32, o caminho mcp_path estava incompleto:
```python
mcp_path  # â† VariÃ¡vel sem valor!
```

### **âœ… SOLUÃ‡ÃƒO APLICADA:**
Corrigido o caminho para calcular dinamicamente:
```python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
mcp_path = os.path.join(project_root, 'mcp-server-pdf', 'index.js')
```

Agora funciona tanto:
- âœ… No desenvolvimento local
- âœ… Dentro do Docker

---

## ðŸ“‹ ARQUIVOS MODIFICADOS:

1. âœ… ackend/app/api/uploads_ia.py - Corrigido cÃ¡lculo do mcp_path

---

## ðŸš€ INSTRUÃ‡Ã•ES PARA O CLIENTE:

### **1. Parar Docker:**
```bash
docker-compose down
```

### **2. Reconstruir (SEM apagar volumes):**
```bash
docker-compose up --build
```

### **3. Re-cadastrar produtos:**
O cliente precisa cadastrar os produtos novamente atravÃ©s da interface.

---

## ðŸ” COMO FAZER BACKUP PREVENTIVO:

### **Backup AutomÃ¡tico DiÃ¡rio:**
Criar script ackup-diario.bat:
```bat
@echo off
set DATA=%date:~-4,4%%date:~-7,2%%date:~-10,2%
docker exec -t project_db_1 pg_dump -U postgres mcm_bobinas > backup_%DATA%.sql
echo Backup criado: backup_%DATA%.sql
```

### **Backup Manual:**
```bash
docker exec -t project_db_1 pg_dump -U postgres mcm_bobinas > backup.sql
```

### **Restaurar Backup:**
```bash
cat backup.sql | docker exec -i project_db_1 psql -U postgres -d mcm_bobinas
```

---

## ðŸ“Š VERIFICAR SE OS DADOS EXISTEM:

### **Ver tabelas:**
```bash
docker exec -it project_db_1 psql -U postgres -d mcm_bobinas -c "\dt"
```

### **Ver produtos:**
```bash
docker exec -it project_db_1 psql -U postgres -d mcm_bobinas -c "SELECT * FROM produtos LIMIT 10;"
```

### **Ver matÃ©rias-primas:**
```bash
docker exec -it project_db_1 psql -U postgres -d mcm_bobinas -c "SELECT * FROM materias_primas LIMIT 10;"
```

---

## ðŸŽ¯ RESUMO:

### **Problema 1 - Banco Zerado:**
- âŒ Causa: Volume deletado
- âœ… SoluÃ§Ã£o: Re-cadastrar ou restaurar backup
- âœ… PrevenÃ§Ã£o: NUNCA usar olume prune -f

### **Problema 2 - Erro PDF/IA:**
- âŒ Causa: mcp_path incompleto
- âœ… SoluÃ§Ã£o: CÃ³digo corrigido
- âœ… Funciona: Sim, apÃ³s rebuild

---

**Data:** 2025-10-07 18:21:41
