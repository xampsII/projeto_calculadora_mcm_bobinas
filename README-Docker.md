# ðŸ³ MCM Bobinas - Setup com Docker

## ðŸ“‹ PrÃ©-requisitos

Antes de comeÃ§ar, certifique-se de ter instalado:

- **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux)
- **Docker Compose** (vem junto com Docker Desktop)

### Como instalar Docker:
- **Windows:** [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **Mac:** [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Linux:** [Docker Engine](https://docs.docker.com/engine/install/)

## ðŸš€ Como executar o projeto

### 1. Clone o repositÃ³rio
```bash
git clone <URL_DO_REPOSITORIO>
cd project
```

### 2. Execute com Docker Compose
```bash
docker-compose up --build
```

### 3. Aguarde a inicializaÃ§Ã£o
O comando acima irÃ¡:
- âœ… Baixar as imagens necessÃ¡rias
- âœ… Construir os containers
- âœ… Inicializar o banco PostgreSQL
- âœ… Executar o backend FastAPI
- âœ… Executar o frontend React
- âœ… Configurar o MCP server para PDFs

### 4. Acesse a aplicaÃ§Ã£o
- **ðŸŒ Frontend:** http://localhost:5173
- **ðŸ”§ Backend API:** http://localhost:8000
- **ðŸ“Š Banco de dados:** localhost:5432

## ðŸ› ï¸ Comandos Ãºteis

### Parar todos os serviÃ§os
```bash
docker-compose down
```

### Ver logs em tempo real
```bash
docker-compose logs -f
```

### Ver logs de um serviÃ§o especÃ­fico
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Rebuild apenas um serviÃ§o
```bash
docker-compose up --build backend
docker-compose up --build frontend
```

### Acessar container para debug
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Banco de dados
docker-compose exec db psql -U postgres -d mcm_bobinas
```

### Limpar tudo (containers, volumes, imagens)
```bash
docker-compose down -v --rmi all
```

## ðŸ“ Estrutura dos serviÃ§os

| ServiÃ§o | Porta | DescriÃ§Ã£o |
|---------|-------|-----------|
| **db** | 5432 | PostgreSQL - Banco de dados |
| **backend** | 8000 | FastAPI - API REST |
| **frontend** | 5173 | React/Vite - Interface web |
| **mcp-pdf** | - | Servidor MCP para processamento de PDFs |

## ðŸ’¾ Volumes persistentes

- **postgres_data:** Dados do PostgreSQL sÃ£o mantidos mesmo apÃ³s parar os containers
- **uploads:** Arquivos PDFs enviados sÃ£o mantidos no sistema

## ðŸ”§ ConfiguraÃ§Ãµes

### VariÃ¡veis de ambiente importantes:
- `DATABASE_URL`: ConexÃ£o com PostgreSQL
- `SECRET_KEY`: Chave secreta para autenticaÃ§Ã£o
- `VITE_API_URL`: URL da API para o frontend

### Portas utilizadas:
- **5432:** PostgreSQL
- **8000:** Backend API
- **5173:** Frontend

## â— Troubleshooting

### Porta jÃ¡ estÃ¡ em uso
```bash
# Verificar o que estÃ¡ usando a porta
netstat -ano | findstr :8000
netstat -ano | findstr :5173
netstat -ano | findstr :5432

# Parar processos se necessÃ¡rio
docker-compose down
```

### Problemas de permissÃ£o (Linux/Mac)
```bash
sudo docker-compose up --build
```

### Limpar cache do Docker
```bash
docker system prune -a
```

### Rebuild completo
```bash
docker-compose down
docker-compose up --build --force-recreate
```

## ðŸ“ž Suporte

Se encontrar problemas:
1. Verifique os logs: `docker-compose logs -f`
2. Certifique-se que o Docker estÃ¡ rodando
3. Verifique se as portas nÃ£o estÃ£o ocupadas
4. Tente rebuild completo: `docker-compose up --build --force-recreate`

---
**ðŸŽ¯ Com esse setup, qualquer pessoa pode rodar o projeto com apenas 2 comandos!**
