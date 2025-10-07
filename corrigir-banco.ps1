# Script para corrigir banco de dados
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CORRIGIR BANCO DE DADOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/6] Parando containers..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "[2/6] Iniciando containers..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "[3/6] Aguardando 15 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host ""
Write-Host "[4/6] Executando migrações..." -ForegroundColor Yellow
docker exec -it projeto_calculadora_mcm_bobinas-backend-1 alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Falha ao executar migrações!" -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "[5/6] Executando seeds..." -ForegroundColor Yellow
docker exec -it projeto_calculadora_mcm_bobinas-backend-1 python -m app.seeds

Write-Host ""
Write-Host "[6/6] Reiniciando backend..." -ForegroundColor Yellow
docker-compose restart backend

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Acesse: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

pause

