#!/bin/bash

echo "🔍 TESTANDO BACKEND SQLITE"
echo "=========================="

echo "1. Verificando containers..."
docker-compose ps

echo ""
echo "2. Verificando logs do backend..."
docker-compose logs backend --tail=20

echo ""
echo "3. Testando health check..."
curl -f http://localhost:8000/health || echo "❌ Backend não responde"

echo ""
echo "4. Verificando se arquivo SQLite existe..."
if [ -f "backend/nfe_system.db" ]; then
    echo "✅ Arquivo SQLite encontrado"
    ls -la backend/nfe_system.db
else
    echo "❌ Arquivo SQLite NÃO encontrado"
fi

echo ""
echo "5. Verificando se arquivo está montado no container..."
docker-compose exec backend ls -la /app/nfe_system.db 2>/dev/null || echo "❌ Arquivo não está no container"

echo ""
echo "6. Testando SQLite dentro do container..."
docker-compose exec backend python -c "
import sqlite3
try:
    conn = sqlite3.connect('/app/nfe_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM materias_primas')
    count = cursor.fetchone()[0]
    print(f'✅ SQLite OK - {count} matérias primas')
    conn.close()
except Exception as e:
    print(f'❌ Erro SQLite: {e}')
" 2>/dev/null || echo "❌ Erro ao testar SQLite"

echo ""
echo "=========================="
echo "🎯 Se tudo estiver ✅, o backend deve funcionar!"
echo "❌ Se houver erros, envie os logs acima"
