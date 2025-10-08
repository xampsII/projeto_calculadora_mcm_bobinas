@echo off
echo ========================================
echo   VERIFICANDO ESTRUTURA DAS TABELAS
echo ========================================
echo.

echo === TABELA UNIDADES ===
docker-compose exec db psql -U nfeuser -d nfedb -c "\d unidades"
echo.

echo === TABELA FORNECEDOR ===
docker-compose exec db psql -U nfeuser -d nfedb -c "\d fornecedor"
echo.

echo === TABELA NOTAS ===
docker-compose exec db psql -U nfeuser -d nfedb -c "\d notas"
echo.

echo === TABELA PRODUTOS_FINAIS ===
docker-compose exec db psql -U nfeuser -d nfedb -c "\d produtos_finais"
echo.

echo === MIGRAÇÕES APLICADAS ===
docker-compose exec db psql -U nfeuser -d nfedb -c "SELECT * FROM alembic_version;"
echo.

pause
