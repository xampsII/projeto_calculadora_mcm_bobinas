#!/bin/bash
set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "=========================================="
echo "🐳 SISTEMA NFE - SETUP DOCKER"
echo "=========================================="
echo -e "${NC}"

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"
}

# Verificar pré-requisitos
check_prerequisites() {
    log "🔍 Verificando pré-requisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado!"
        echo "📥 Instale Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose não está instalado!"
        echo "📥 Instale Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Verificar se Docker está rodando
    if ! docker info &> /dev/null; then
        error "Docker não está rodando!"
        echo "🚀 Inicie o Docker Desktop ou Docker daemon"
        exit 1
    fi
    
    log "✅ Pré-requisitos OK!"
}

# Criar diretórios necessários
create_directories() {
    log "📁 Criando diretórios necessários..."
    
    mkdir -p docker/postgres/init
    mkdir -p docker/backend
    mkdir -p backend/uploads
    mkdir -p scripts
    
    log "✅ Diretórios criados!"
}

# Tornar scripts executáveis
make_executable() {
    log "🔧 Configurando permissões..."
    
    if [ -f "docker/backend/init.sh" ]; then
        chmod +x docker/backend/init.sh
    fi
    
    if [ -f "scripts/export_sqlite_to_postgres.py" ]; then
        chmod +x scripts/export_sqlite_to_postgres.py
    fi
    
    log "✅ Permissões configuradas!"
}

# Verificar se há dados SQLite para migrar
check_sqlite_data() {
    log "🔍 Verificando dados existentes..."
    
    if [ -f "backend/nfe_system.db" ]; then
        log "📊 Encontrado banco SQLite com dados!"
        echo -e "${BLUE}   • O sistema migrará automaticamente os dados para PostgreSQL${NC}"
    else
        log "📝 Nenhum banco SQLite encontrado, iniciando com dados de exemplo"
    fi
}

# Parar containers existentes
stop_existing() {
    log "🛑 Parando containers existentes..."
    
    if docker-compose ps -q &> /dev/null; then
        docker-compose down
        log "✅ Containers parados!"
    else
        log "ℹ️  Nenhum container rodando"
    fi
}

# Limpar cache Docker (opcional)
clean_docker() {
    read -p "🧹 Limpar cache Docker? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log "🧹 Limpando cache Docker..."
        docker system prune -f
        log "✅ Cache limpo!"
    fi
}

# Construir e iniciar containers
start_containers() {
    log "🏗️  Construindo e iniciando containers..."
    echo -e "${YELLOW}   ⏳ Isso pode demorar alguns minutos na primeira vez...${NC}"
    
    # Usar docker-compose ou docker compose conforme disponível
    if command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        COMPOSE_CMD="docker compose"
    fi
    
    $COMPOSE_CMD up --build -d
    
    log "✅ Containers iniciados!"
}

# Aguardar serviços ficarem prontos
wait_for_services() {
    log "⏳ Aguardando serviços ficarem prontos..."
    
    # Aguardar PostgreSQL
    echo -n "   🔄 Aguardando PostgreSQL"
    while ! docker-compose exec -T db pg_isready -U nfeuser &> /dev/null; do
        echo -n "."
        sleep 2
    done
    echo -e " ${GREEN}✅${NC}"
    
    # Aguardar Backend
    echo -n "   🔄 Aguardando Backend"
    while ! curl -s http://localhost:8000/health &> /dev/null; do
        echo -n "."
        sleep 3
    done
    echo -e " ${GREEN}✅${NC}"
    
    # Aguardar Frontend
    echo -n "   🔄 Aguardando Frontend"
    while ! curl -s http://localhost:5173 &> /dev/null; do
        echo -n "."
        sleep 3
    done
    echo -e " ${GREEN}✅${NC}"
    
    log "🎉 Todos os serviços estão prontos!"
}

# Verificar saúde dos serviços
check_health() {
    log "🏥 Verificando saúde dos serviços..."
    
    # Backend
    if curl -s http://localhost:8000/health | grep -q "ok"; then
        echo -e "   ${GREEN}✅ Backend: OK${NC}"
    else
        echo -e "   ${RED}❌ Backend: ERRO${NC}"
    fi
    
    # Frontend
    if curl -s http://localhost:5173 | grep -q "html"; then
        echo -e "   ${GREEN}✅ Frontend: OK${NC}"
    else
        echo -e "   ${RED}❌ Frontend: ERRO${NC}"
    fi
    
    # PostgreSQL
    if docker-compose exec -T db pg_isready -U nfeuser &> /dev/null; then
        echo -e "   ${GREEN}✅ PostgreSQL: OK${NC}"
    else
        echo -e "   ${RED}❌ PostgreSQL: ERRO${NC}"
    fi
    
    # Redis
    if docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        echo -e "   ${GREEN}✅ Redis: OK${NC}"
    else
        echo -e "   ${RED}❌ Redis: ERRO${NC}"
    fi
}

# Mostrar informações finais
show_final_info() {
    echo -e "${CYAN}"
    echo "=========================================="
    echo "🎉 SETUP CONCLUÍDO COM SUCESSO!"
    echo "=========================================="
    echo -e "${NC}"
    
    echo -e "${BLUE}📱 Acesse a aplicação:${NC}"
    echo -e "   • Frontend: ${GREEN}http://localhost:5173${NC}"
    echo -e "   • Backend API: ${GREEN}http://localhost:8000/docs${NC}"
    
    echo -e "${BLUE}👤 Usuários padrão:${NC}"
    echo -e "   • Admin: ${GREEN}admin@nfe.com${NC} / ${GREEN}admin123${NC}"
    echo -e "   • Editor: ${GREEN}editor@nfe.com${NC} / ${GREEN}editor123${NC}"
    echo -e "   • Viewer: ${GREEN}viewer@nfe.com${NC} / ${GREEN}viewer123${NC}"
    
    echo -e "${BLUE}🔧 Comandos úteis:${NC}"
    echo -e "   • Ver logs: ${GREEN}docker-compose logs -f${NC}"
    echo -e "   • Parar: ${GREEN}docker-compose down${NC}"
    echo -e "   • Reiniciar: ${GREEN}docker-compose restart${NC}"
    
    echo -e "${BLUE}📊 Status dos containers:${NC}"
    docker-compose ps
    
    echo -e "${GREEN}"
    echo "🚀 Sistema NFE está pronto para uso!"
    echo -e "${NC}"
}

# Função principal
main() {
    check_prerequisites
    create_directories
    make_executable
    check_sqlite_data
    stop_existing
    clean_docker
    start_containers
    wait_for_services
    check_health
    show_final_info
}

# Verificar argumentos
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "🐳 Sistema NFE - Setup Docker"
    echo ""
    echo "Uso: ./setup-docker.sh"
    echo ""
    echo "Este script configura automaticamente o Sistema NFE usando Docker."
    echo ""
    echo "Pré-requisitos:"
    echo "• Docker instalado e rodando"
    echo "• Docker Compose instalado"
    echo "• Portas 5173, 8000, 5432, 6379 livres"
    echo ""
    exit 0
fi

# Executar setup
main "$@"
