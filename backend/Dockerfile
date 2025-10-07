# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependÃªncias do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar cÃ³digo da aplicaÃ§Ã£o
COPY . .

# Criar diretÃ³rio para uploads
RUN mkdir -p uploads

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
