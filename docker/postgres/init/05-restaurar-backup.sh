#!/bin/bash
# Script para restaurar backup dos dados reais

echo "📥 Restaurando backup dos dados reais..."

# Verificar se arquivo de backup existe
if [ ! -f "/docker-entrypoint-initdb.d/04-meus-dados.backup" ]; then
    echo "⚠️  Arquivo de backup não encontrado, pulando restauração..."
    exit 0
fi

echo "✅ Backup encontrado, aguardando banco estar pronto..."

# Aguardar banco estar completamente pronto
sleep 3

echo "🔄 Restaurando dados..."

# Tentar restaurar (ignorando erros de objetos que não existem)
PGPASSWORD=nfepass pg_restore \
    -h localhost \
    -U nfeuser \
    -d nfedb \
    --data-only \
    --disable-triggers \
    --no-owner \
    --no-acl \
    /docker-entrypoint-initdb.d/04-meus-dados.backup 2>&1 | grep -v "ERROR.*does not exist" | grep -v "WARNING" || true

echo "✅ Restauração do backup concluída!"

