@echo off
chcp 65001 >nul
color 0A
cls

echo ================================================
echo    🚀 INICIANDO PROJETO NFE - LOCAL
echo ================================================
echo.

echo [1/3] Verificando PostgreSQL...
timeout /t 2 /nobreak >nul
echo ✓ PostgreSQL: localhost:5433
echo.

echo [2/3] Iniciando Backend (FastAPI)...
start "NFE Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul
echo ✓ Backend rodando em: http://127.0.0.1:8000
echo.

echo [3/3] Iniciando Frontend (React)...
start "NFE Frontend" cmd /k "npm run dev"
timeout /t 3 /nobreak >nul
echo ✓ Frontend rodando em: http://localhost:5173
echo.

echo ================================================
echo    ✅ SISTEMA INICIADO COM SUCESSO!
echo ================================================
echo.
echo 📋 Serviços disponíveis:
echo    • Frontend:    http://localhost:5173
echo    • Backend:     http://127.0.0.1:8000
echo    • API Docs:    http://127.0.0.1:8000/docs
echo.
echo 🔑 Credenciais:
echo    • Email: admin@nfe.com
echo    • Senha: admin123
echo.
echo 💡 Dica: Mantenha este terminal aberto
echo    Pressione qualquer tecla para fechar...
echo.
pause >nul


