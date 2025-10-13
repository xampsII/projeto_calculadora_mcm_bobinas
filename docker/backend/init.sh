#!/bin/bash
# NÃO usar set -e para continuar mesmo com erros não críticos

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
echo "⏳ Aguardando inicialização completa..."
sleep 10

# Executar migrações
echo "📊 Criando tabelas..."
if alembic upgrade head; then
    echo "✅ Migrações executadas com sucesso!"
else
    echo "⚠️  Erro nas migrações, mas continuando..."
fi

# Aguardar backup ser restaurado (se existir)
echo "⏳ Aguardando restauração de backup..."
sleep 5

# Executar seeds (opcional - pode falhar se dados já existem)
echo "🌱 Tentando inserir dados iniciais..."
if python -m app.seeds; then
    echo "✅ Seeds executados com sucesso!"
else
    echo "⚠️  Seeds falharam (pode ser normal se backup já populou dados)"
fi

echo "✅ Sistema pronto para iniciar!"

# Iniciar aplicação
echo "🎯 Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
