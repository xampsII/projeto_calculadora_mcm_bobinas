@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo 🐳 SISTEMA NFE - SETUP DOCKER
echo ==========================================
echo.

REM Verificar pré-requisitos
echo 🔍 Verificando pré-requisitos...

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está instalado!
    echo 📥 Instale Docker Desktop: https://docs.docker.com/desktop/windows/
    pause
    exit /b 1
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker Compose não está instalado!
        echo 📥 Instale Docker Compose: https://docs.docker.com/compose/install/
        pause
        exit /b 1
    )
)

REM Verificar se Docker está rodando
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker não está rodando!
    echo 🚀 Inicie o Docker Desktop
    pause
    exit /b 1
)

echo ✅ Pré-requisitos OK!
echo.

REM Criar diretórios necessários
echo 📁 Criando diretórios necessários...
if not exist "docker\postgres\init" mkdir "docker\postgres\init"
if not exist "docker\backend" mkdir "docker\backend"
if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "scripts" mkdir "scripts"
echo ✅ Diretórios criados!
echo.

REM Verificar dados SQLite
echo 🔍 Verificando dados existentes...
if exist "backend\nfe_system.db" (
    echo 📊 Encontrado banco SQLite com dados!
    echo • O sistema migrará automaticamente os dados para PostgreSQL
) else (
    echo 📝 Nenhum banco SQLite encontrado, iniciando com dados de exemplo
)
echo.

REM Parar containers existentes
echo 🛑 Parando containers existentes...
docker-compose down >nul 2>&1
echo ✅ Containers parados!
echo.

REM Perguntar sobre limpeza de cache
set /p clean_cache="🧹 Limpar cache Docker? (y/N): "
if /i "%clean_cache%"=="y" (
    echo 🧹 Limpando cache Docker...
    docker system prune -f
    echo ✅ Cache limpo!
)
echo.

REM Construir e iniciar containers
echo 🏗️ Construindo e iniciando containers...
echo ⏳ Isso pode demorar alguns minutos na primeira vez...
echo.

docker-compose up --build -d

if errorlevel 1 (
    echo ❌ Erro ao iniciar containers!
    echo Verifique os logs: docker-compose logs
    pause
    exit /b 1
)

echo ✅ Containers iniciados!
echo.

REM Aguardar serviços ficarem prontos
echo ⏳ Aguardando serviços ficarem prontos...

REM Aguardar PostgreSQL
echo Aguardando PostgreSQL...
:wait_postgres
docker-compose exec -T db pg_isready -U nfeuser >nul 2>&1
if errorlevel 1 (
    timeout /t 2 >nul
    goto wait_postgres
)
echo ✅ PostgreSQL pronto!

REM Aguardar Backend
echo Aguardando Backend...
:wait_backend
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 3 >nul
    goto wait_backend
)
echo ✅ Backend pronto!

REM Aguardar Frontend
echo Aguardando Frontend...
:wait_frontend
curl -s http://localhost:5173 >nul 2>&1
if errorlevel 1 (
    timeout /t 3 >nul
    goto wait_frontend
)
echo ✅ Frontend pronto!

echo 🎉 Todos os serviços estão prontos!
echo.

REM Verificar saúde dos serviços
echo 🏥 Verificando saúde dos serviços...

REM Backend
curl -s http://localhost:8000/health | findstr "ok" >nul
if errorlevel 1 (
    echo ❌ Backend: ERRO
) else (
    echo ✅ Backend: OK
)

REM Frontend
curl -s http://localhost:5173 | findstr "html" >nul
if errorlevel 1 (
    echo ❌ Frontend: ERRO
) else (
    echo ✅ Frontend: OK
)

REM PostgreSQL
docker-compose exec -T db pg_isready -U nfeuser >nul
if errorlevel 1 (
    echo ❌ PostgreSQL: ERRO
) else (
    echo ✅ PostgreSQL: OK
)

REM Redis
docker-compose exec -T redis redis-cli ping | findstr "PONG" >nul
if errorlevel 1 (
    echo ❌ Redis: ERRO
) else (
    echo ✅ Redis: OK
)
echo.

REM Mostrar informações finais
echo ==========================================
echo 🎉 SETUP CONCLUÍDO COM SUCESSO!
echo ==========================================
echo.
echo 📱 Acesse a aplicação:
echo    • Frontend: http://localhost:5173
echo    • Backend API: http://localhost:8000/docs
echo.
echo 👤 Usuários padrão:
echo    • Admin: admin@nfe.com / admin123
echo    • Editor: editor@nfe.com / editor123
echo    • Viewer: viewer@nfe.com / viewer123
echo.
echo 🔧 Comandos úteis:
echo    • Ver logs: docker-compose logs -f
echo    • Parar: docker-compose down
echo    • Reiniciar: docker-compose restart
echo.
echo 📊 Status dos containers:
docker-compose ps
echo.
echo 🚀 Sistema NFE está pronto para uso!
echo.
pause
