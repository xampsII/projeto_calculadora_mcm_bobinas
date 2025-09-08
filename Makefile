# Makefile para o Sistema NFE
# Comandos para desenvolvimento local

.PHONY: help install run test migrate seed clean logs

# Comando padrão
help:
	@echo "Comandos disponíveis:"
	@echo "  install     - Instala as dependências Python"
	@echo "  run         - Executa a API FastAPI"
	@echo "  worker      - Executa o worker do Celery"
	@echo "  beat        - Executa o scheduler do Celery"
	@echo "  test        - Executa os testes"
	@echo "  migrate     - Executa as migrações do banco"
	@echo "  seed        - Popula o banco com dados iniciais"
	@echo "  clean       - Remove arquivos temporários"
	@echo "  logs        - Mostra os logs da aplicação"

# Instalação
install:
	@echo "Instalando dependências..."
	pip install -r requirements.txt
	@echo "Dependências instaladas!"

# Execução da API
run:
	@echo "Iniciando a API FastAPI..."
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Worker do Celery
worker:
	@echo "Iniciando worker do Celery..."
	cd backend && celery -A app.celery_app worker --loglevel=info

# Scheduler do Celery
beat:
	@echo "Iniciando scheduler do Celery..."
	cd backend && celery -A app.celery_app beat --loglevel=info

# Testes
test:
	@echo "Executando testes..."
	cd backend && python -m pytest tests/ -v

# Migrações
migrate:
	@echo "Executando migrações..."
	cd backend && alembic upgrade head

# Seeds
seed:
	@echo "Populando banco com dados iniciais..."
	cd backend && python -c "from app.seeds import executar_seeds; executar_seeds()"

# Limpeza
clean:
	@echo "Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	@echo "Limpeza concluída!"

# Logs
logs:
	@echo "Mostrando logs da aplicação..."
	tail -f logs/app.log

# Setup inicial do projeto
setup: install
	@echo "Configurando banco de dados..."
	cd backend && alembic upgrade head
	@echo "Populando com dados iniciais..."
	cd backend && python -c "from app.seeds import executar_seeds; executar_seeds()"
	@echo "Setup concluído! Execute 'make run' para iniciar a API."

# Verificação de saúde
health:
	@echo "Verificando serviços..."
	@echo "PostgreSQL: $(shell pg_isready -h localhost -p 5432 > /dev/null 2>&1 && echo "OK" || echo "FALHOU")"
	@echo "Redis: $(shell redis-cli ping > /dev/null 2>&1 && echo "OK" || echo "FALHOU")"
	@echo "API: $(shell curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "OK" || echo "FALHOU")"

# Desenvolvimento (API + Worker + Beat)
dev:
	@echo "Iniciando ambiente de desenvolvimento..."
	@echo "Execute em terminais separados:"
	@echo "  Terminal 1: make run"
	@echo "  Terminal 2: make worker"
	@echo "  Terminal 3: make beat" 