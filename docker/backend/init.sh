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
    echo "❌ Timeout aguardando PostgreSQL. Verificando logs..."
    exit 1
  fi
  echo "   Aguardando PostgreSQL... (tentativa $attempt/$max_attempts)"
  sleep 2
done
echo "✅ Banco de dados pronto!"

# Aguardar um pouco mais para garantir que o PostgreSQL esteja totalmente inicializado
echo "⏳ Aguardando inicialização completa do PostgreSQL..."
sleep 5

# Verificar se o banco existe
echo "🔍 Verificando se o banco nfedb existe..."
if ! psql -h db -p 5432 -U nfeuser -d nfedb -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ Banco nfedb não existe! Criando..."
    psql -h db -p 5432 -U nfeuser -d postgres -c "CREATE DATABASE nfedb;"
    echo "✅ Banco nfedb criado!"
fi

# Executar migrações
echo "📊 Executando migrações do Alembic..."
alembic upgrade head

# Executar seeds
echo "🌱 Populando banco com dados iniciais..."
python -m app.seeds

# Verificar se seeds funcionaram
echo "🔍 Verificando se dados foram inseridos..."
python -c "
from app.database import SessionLocal
from app.models import *
db = SessionLocal()
try:
    users_count = db.query(User).count()
    unidades_count = db.query(Unidade).count()
    print(f'✅ Usuários criados: {users_count}')
    print(f'✅ Unidades criadas: {unidades_count}')
    if users_count == 0 or unidades_count == 0:
        print('⚠️  Alguns dados podem não ter sido inseridos')
    else:
        print('🎉 Banco populado com sucesso!')
finally:
    db.close()
"

# Verificar se há dados para importar do SQLite
echo "🔍 Verificando se há dados do SQLite para importar..."
if [ -f "/app/nfe_system.db" ]; then
    echo "📥 Encontrado arquivo SQLite, importando dados..."
    python /app/scripts/export_sqlite_to_postgres.py || echo "⚠️  Importação SQLite falhou, continuando..."
fi

# Iniciar aplicação
echo "🎯 Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
