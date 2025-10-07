# ðŸ“Š DIAGRAMA - ONDE FICAM OS DADOS?

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    MÃQUINA DO CLIENTE                           â”‚
â”‚                                                                 â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚                     DOCKER DESKTOP                        â”‚  â”‚
â”‚  â”‚                                                           â”‚  â”‚
â”‚  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”‚  â”‚
â”‚  â”‚  â”‚  Frontend   â”‚  â”‚  Backend    â”‚  â”‚  PostgreSQL â”‚      â”‚  â”‚
â”‚  â”‚  â”‚  (React)    â”‚  â”‚  (FastAPI)  â”‚  â”‚    (DB)     â”‚      â”‚  â”‚
â”‚  â”‚  â”‚  Port 5173  â”‚  â”‚  Port 8000  â”‚  â”‚  Port 5432  â”‚      â”‚  â”‚
â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜      â”‚  â”‚
â”‚  â”‚         â”‚                â”‚                â”‚              â”‚  â”‚
â”‚  â”‚         â”‚                â”‚                â”‚              â”‚  â”‚
â”‚  â”‚         â”‚                â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â”‚  â”‚
â”‚  â”‚         â”‚                  Conecta automaticamente       â”‚  â”‚
â”‚  â”‚         â”‚                                                â”‚  â”‚
â”‚  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”‚  â”‚
â”‚  â”‚  â”‚           VOLUMES PERSISTENTES                   â”‚   â”‚  â”‚
â”‚  â”‚  â”‚                                                  â”‚   â”‚  â”‚
â”‚  â”‚  â”‚  ðŸ“ postgres_data/                              â”‚   â”‚  â”‚
â”‚  â”‚  â”‚     â””â”€â”€ Todos os dados do banco aqui           â”‚   â”‚  â”‚
â”‚  â”‚  â”‚                                                  â”‚   â”‚  â”‚
â”‚  â”‚  â”‚  ðŸ“ backend/uploads/                            â”‚   â”‚  â”‚
â”‚  â”‚  â”‚     â””â”€â”€ Arquivos enviados pelos usuÃ¡rios       â”‚   â”‚  â”‚
â”‚  â”‚  â”‚                                                  â”‚   â”‚  â”‚
â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”‚  â”‚
â”‚  â”‚                                                           â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

âœ… DADOS FICAM NO DISCO DA MÃQUINA
âœ… PERSISTENTES (nÃ£o somem ao reiniciar)
âœ… ISOLADOS (nÃ£o interferem no sistema)
âœ… PORTÃVEIS (podem ser copiados/movidos)
```

---

## ðŸ”„ FLUXO DE DADOS

```
1. Cliente usa o Frontend (navegador)
         â†“
2. Frontend envia requisiÃ§Ã£o para Backend
         â†“
3. Backend processa e consulta Banco
         â†“
4. Banco retorna dados (salvos no volume)
         â†“
5. Backend retorna para Frontend
         â†“
6. Frontend mostra para o Cliente
```

---

## ðŸ’¾ LOCALIZAÃ‡ÃƒO FÃSICA DOS DADOS

### **Windows:**
```
C:\ProgramData\Docker\volumes\
  â””â”€â”€ project_postgres_data\
      â””â”€â”€ _data\
          â””â”€â”€ (arquivos do PostgreSQL)
```

### **Linux:**
```
/var/lib/docker/volumes/
  â””â”€â”€ project_postgres_data/
      â””â”€â”€ _data/
          â””â”€â”€ (arquivos do PostgreSQL)
```

### **Mac:**
```
~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker/volumes/
  â””â”€â”€ project_postgres_data/
      â””â”€â”€ _data/
          â””â”€â”€ (arquivos do PostgreSQL)
```

---

## ðŸŽ¯ RESUMO SIMPLES

**Pergunta:** Onde ficam salvos os dados?
**Resposta:** Em um "volume" do Docker na mÃ¡quina do cliente

**Pergunta:** Precisa instalar PostgreSQL?
**Resposta:** NÃƒO! Docker faz tudo automaticamente

**Pergunta:** Os dados somem se reiniciar?
**Resposta:** NÃƒO! Dados ficam salvos permanentemente

**Pergunta:** Como fazer backup?
**Resposta:** Copiar a pasta do volume ou usar comandos de backup

**Pergunta:** Ã‰ seguro?
**Resposta:** SIM! Isolado do sistema e com credenciais configurÃ¡veis

---

**Data:** 2025-10-07 18:18:23
