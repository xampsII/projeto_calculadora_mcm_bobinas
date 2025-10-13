#!/bin/bash

echo "Iniciando backend NFE..."

# Aguardar banco estar pronto
echo "Aguardando banco de dados..."
max_attempts=30
attempt=0
while ! pg_isready -h db -p 5432 -U nfeuser; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "Timeout aguardando PostgreSQL"
    exit 1
  fi
  echo "Tentativa $attempt/$max_attempts..."
  sleep 2
done
echo "Banco de dados pronto!"

# Aguardar PostgreSQL inicializar completamente
echo "Aguardando inicializacao completa..."
sleep 10

# Executar migraÃ§Ãµes
echo "Criando tabelas..."
alembic upgrade head || echo "Erro nas migracoes, mas continuando..."

# Aguardar backup ser restaurado
echo "Aguardando restauracao de backup..."
sleep 5

# Executar seeds
echo "Tentando inserir dados iniciais..."
python -m app.seeds || echo "Seeds falharam (normal se backup ja populou dados)"

echo "Sistema pronto para iniciar!"

# Iniciar aplicaÃ§Ã£o
echo "Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
