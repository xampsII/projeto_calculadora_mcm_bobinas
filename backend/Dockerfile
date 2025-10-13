# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    postgresql-client \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Copiar script de exportação se existir
COPY ../scripts/export_sqlite_to_postgres.py ./scripts/ 2>/dev/null || true

# Criar diretórios necessários
RUN mkdir -p uploads scripts

# Tornar scripts executáveis
RUN chmod +x scripts/*.py 2>/dev/null || true

# Verificar se arquivo SQLite existe e copiar
COPY nfe_system.db ./nfe_system.db 2>/dev/null || echo "SQLite file not found, will use seeds only"

# Expor porta
EXPOSE 8000

# Comando para iniciar (será sobrescrito pelo docker-compose)
CMD ["sh", "/app/init.sh"]
