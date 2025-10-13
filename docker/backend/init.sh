#!/bin/bash
set -e

echo "🚀 Iniciando backend NFE..."

# Aguardar banco estar pronto
echo "⏳ Aguardando banco de dados..."
max_attempts=30
attempt=0
while ! pg_isready -h db -p 5432 -U nfeuser; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "❌ Timeout aguardando PostgreSQL"
    exit 1
  fi
  echo "   Tentativa $attempt/$max_attempts..."
  sleep 2
done
echo "✅ Banco de dados pronto!"

# Aguardar PostgreSQL inicializar completamente
sleep 5

# Executar migrações
echo "📊 Criando tabelas..."
alembic upgrade head

# Executar seeds
echo "🌱 Inserindo dados iniciais..."
python -m app.seeds

echo "✅ Sistema pronto!"

# Iniciar aplicação
echo "🎯 Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
