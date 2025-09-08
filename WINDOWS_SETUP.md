# Configuração no Windows

Este guia explica como configurar o Sistema NFE no Windows sem Docker.

## Pré-requisitos

### 1. Python 3.11+
- Baixe em: https://www.python.org/downloads/
- **IMPORTANTE**: Marque "Add Python to PATH" durante a instalação
- Verifique: `python --version`

### 2. PostgreSQL 14+
- Baixe em: https://www.postgresql.org/download/windows/
- Use o instalador oficial do PostgreSQL
- **IMPORTANTE**: Anote a senha do usuário `postgres`
- **IMPORTANTE**: Mantenha a porta padrão 5432

### 3. Redis
- **Opção 1**: Redis via WSL2 (recomendado)
  ```bash
  # Instale WSL2 primeiro
  wsl --install
  
  # No WSL2
  sudo apt update
  sudo apt install redis-server
  sudo systemctl start redis-server
  ```

- **Opção 2**: Redis via Windows
  - Baixe em: https://github.com/microsoftarchive/redis/releases
  - Execute `redis-server.exe`

### 4. Tesseract OCR
- Baixe em: https://github.com/UB-Mannheim/tesseract/wiki
- **IMPORTANTE**: Adicione ao PATH do sistema
- Verifique: `tesseract --version`

## Instalação

### 1. Clone o Repositório
```cmd
git clone <url-do-repositorio>
cd project
```

### 2. Ambiente Virtual
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Dependências
```cmd
pip install -r requirements.txt
```

### 4. Configuração do Banco
```cmd
# Conecte ao PostgreSQL
psql -U postgres -h localhost

# No psql, crie o banco
CREATE DATABASE nfe_system;
\q

# Execute as migrações
cd backend
alembic upgrade head
```

### 5. Configuração do Ambiente
```cmd
# Copie o arquivo de configuração
copy config.local.env .env

# Edite o arquivo .env com suas configurações
notepad .env
```

**Configurações importantes no .env:**
```env
DATABASE_DSN=postgresql://postgres:SUA_SENHA@localhost:5432/nfe_system
REDIS_URL=redis://localhost:6379/0
```

### 6. Seeds Iniciais
```cmd
cd backend
python -c "from app.seeds import executar_seeds; executar_seeds()"
```

## Execução

### Terminal 1 - API
```cmd
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 - Worker Celery
```cmd
cd backend
celery -A app.celery_app worker --loglevel=info
```

### Terminal 3 - Scheduler Celery
```cmd
cd backend
celery -A app.celery_app beat --loglevel=info
```

## Comandos Make (Windows)

Se você tiver o Make instalado no Windows:

```cmd
make help          # Lista comandos
make run           # Executa a API
make worker        # Executa o worker
make beat          # Executa o scheduler
make test          # Executa testes
make migrate       # Executa migrações
make seed          # Executa seeds
```

## Alternativa sem Make

Se não tiver o Make, use os comandos diretos:

```cmd
# Instalar dependências
pip install -r requirements.txt

# Executar migrações
cd backend && alembic upgrade head

# Executar seeds
cd backend && python -c "from app.seeds import executar_seeds; executar_seeds()"

# Executar API
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Executar worker
cd backend && celery -A app.celery_app worker --loglevel=info

# Executar scheduler
cd backend && celery -A app.celery_app beat --loglevel=info
```

## Troubleshooting

### Erro de Conexão com PostgreSQL
```cmd
# Verifique se o serviço está rodando
services.msc
# Procure por "PostgreSQL" e verifique se está "Running"

# Ou via linha de comando
sc query postgresql-x64-14
```

### Erro de Conexão com Redis
```cmd
# Se usando WSL2
wsl redis-cli ping

# Se usando Windows
redis-cli.exe ping
```

### Erro de PATH
- Verifique se Python, PostgreSQL e Tesseract estão no PATH
- Reinicie o terminal após adicionar ao PATH
- Use `where python`, `where psql`, `where tesseract` para verificar

### Erro de Permissão
- Execute o terminal como Administrador
- Verifique as permissões da pasta do projeto

## Verificação

### 1. Teste a API
```cmd
curl http://localhost:8000/health
```

### 2. Teste o Banco
```cmd
psql -U postgres -h localhost -d nfe_system -c "SELECT version();"
```

### 3. Teste o Redis
```cmd
redis-cli ping
```

## Próximos Passos

1. Acesse http://localhost:8000/docs para ver a documentação da API
2. Use o endpoint `/auth/login` para fazer login
3. Explore os outros endpoints da API
4. Configure o processamento de emails se necessário 