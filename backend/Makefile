# Makefile para o Sistema NFE
# Comandos úteis para desenvolvimento e produção

.PHONY: help install run test migrate seed clean docker-up docker-down docker-build

# Variáveis
PYTHON = python3
PIP = pip3
APP_NAME = nfe_system

# Comando padrão
help:
	@echo "Comandos disponíveis:"
	@echo "  install     - Instala dependências"
	@echo "  run         - Executa a aplicação"
	@echo "  test        - Executa testes"
	@echo "  migrate     - Executa migrações do banco"
	@echo "  seed        - Popula banco com dados iniciais"
	@echo "  clean       - Remove arquivos temporários"
	@echo "  docker-up   - Inicia serviços Docker"
	@echo "  docker-down - Para serviços Docker"
	@echo "  docker-build- Constrói imagens Docker"
	@echo "  celery      - Inicia worker Celery"
	@echo "  celery-beat - Inicia scheduler Celery"

# Instalar dependências
install:
	@echo "Instalando dependências..."
	$(PIP) install -r requirements.txt

# Executar aplicação
run:
	@echo "Executando aplicação..."
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Executar testes
test:
	@echo "Executando testes..."
	$(PYTHON) -m pytest tests/ -v

# Executar migrações
migrate:
	@echo "Executando migrações..."
	alembic upgrade head

# Executar seeds
seed:
	@echo "Executando seeds..."
	$(PYTHON) app/seeds.py

# Limpar arquivos temporários
clean:
	@echo "Limpando arquivos temporários..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

# Docker commands
docker-up:
	@echo "Iniciando serviços Docker..."
	docker-compose up -d

docker-down:
	@echo "Parando serviços Docker..."
	docker-compose down

docker-build:
	@echo "Construindo imagens Docker..."
	docker-compose build

# Celery commands
celery:
	@echo "Iniciando worker Celery..."
	celery -A app.celery_app worker --loglevel=info

celery-beat:
	@echo "Iniciando scheduler Celery..."
	celery -A app.celery_app beat --loglevel=info

# Desenvolvimento
dev-setup: install migrate seed
	@echo "Ambiente de desenvolvimento configurado!"

# Produção
prod-setup: install migrate
	@echo "Ambiente de produção configurado!"

# Verificar status
status:
	@echo "Verificando status dos serviços..."
	docker-compose ps
	@echo ""
	@echo "Logs da aplicação:"
	docker-compose logs api --tail=10

# Backup
backup:
	@echo "Fazendo backup do banco..."
	docker-compose exec db pg_dump -U postgres nfe_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

# Restore
restore:
	@echo "Restaurando backup..."
	@read -p "Digite o nome do arquivo de backup: " backup_file; \
	docker-compose exec -T db psql -U postgres nfe_db < $$backup_file

# Logs
logs:
	@echo "Exibindo logs..."
	docker-compose logs -f

# Shell do banco
db-shell:
	@echo "Conectando ao banco..."
	docker-compose exec db psql -U postgres nfe_db

# Shell da aplicação
app-shell:
	@echo "Conectando à aplicação..."
	docker-compose exec api python

# Reiniciar aplicação
restart:
	@echo "Reiniciando aplicação..."
	docker-compose restart api

# Verificar dependências
check-deps:
	@echo "Verificando dependências..."
	$(PIP) list --outdated

# Atualizar dependências
update-deps:
	@echo "Atualizando dependências..."
	$(PIP) install --upgrade -r requirements.txt

# Formatar código
format:
	@echo "Formatando código..."
	black app/
	isort app/

# Lint
lint:
	@echo "Executando lint..."
	flake8 app/
	black --check app/
	isort --check-only app/

# Coverage
coverage:
	@echo "Executando testes com coverage..."
	$(PYTHON) -m pytest tests/ --cov=app --cov-report=html
	@echo "Relatório de coverage gerado em htmlcov/"

# Performance
profile:
	@echo "Executando testes de performance..."
	$(PYTHON) -m pytest tests/ -m "performance" -v

# Segurança
security:
	@echo "Verificando vulnerabilidades..."
	safety check
	bandit -r app/

# Documentação
docs:
	@echo "Gerando documentação..."
	$(PYTHON) -m pdoc --html app/
	@echo "Documentação gerada em html/app/"

# OpenAPI
openapi:
	@echo "Gerando OpenAPI spec..."
	curl http://localhost:8000/openapi.json > openapi.json

# Health check
health:
	@echo "Verificando saúde da aplicação..."
	curl -f http://localhost:8000/health || echo "Aplicação não está respondendo"

# Monitoramento
monitor:
	@echo "Monitorando recursos..."
	@echo "CPU e Memória:"
	docker stats --no-stream
	@echo ""
	@echo "Espaço em disco:"
	df -h
	@echo ""
	@echo "Processos Python:"
	ps aux | grep python | grep -v grep

# Limpeza completa
clean-all: clean docker-down
	@echo "Limpando tudo..."
	docker system prune -f
	docker volume prune -f
	@echo "Limpeza completa concluída!"

# Ajuda detalhada
help-detailed:
	@echo "=== SISTEMA NFE - COMANDOS DETALHADOS ==="
	@echo ""
	@echo "DESENVOLVIMENTO:"
	@echo "  dev-setup     - Configura ambiente completo de desenvolvimento"
	@echo "  install       - Instala dependências Python"
	@echo "  run           - Executa aplicação localmente"
	@echo "  test          - Executa suite de testes"
	@echo "  migrate       - Aplica migrações do banco"
	@echo "  seed          - Popula banco com dados de exemplo"
	@echo ""
	@echo "DOCKER:"
	@echo "  docker-up     - Inicia todos os serviços"
	@echo "  docker-down   - Para todos os serviços"
	@echo "  docker-build  - Reconstrói imagens"
	@echo "  status        - Mostra status dos serviços"
	@echo ""
	@echo "CELERY:"
	@echo "  celery        - Inicia worker de tarefas"
	@echo "  celery-beat   - Inicia agendador de tarefas"
	@echo ""
	@echo "MANUTENÇÃO:"
	@echo "  backup        - Faz backup do banco"
	@echo "  restore       - Restaura backup"
	@echo "  logs          - Mostra logs em tempo real"
	@echo "  restart       - Reinicia aplicação"
	@echo ""
	@echo "QUALIDADE:"
	@echo "  format        - Formata código automaticamente"
	@echo "  lint          - Verifica qualidade do código"
	@echo "  coverage      - Gera relatório de cobertura"
	@echo "  security      - Verifica vulnerabilidades"
	@echo ""
	@echo "MONITORAMENTO:"
	@echo "  health        - Verifica saúde da aplicação"
	@echo "  monitor       - Mostra recursos do sistema"
	@echo ""
	@echo "LIMPEZA:"
	@echo "  clean         - Remove arquivos temporários"
	@echo "  clean-all     - Limpeza completa (Docker + arquivos)" 