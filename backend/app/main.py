from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
import logging
import time
from contextlib import asynccontextmanager

from app.config import get_settings
from app.database import engine
from app.models import load_all_models
from app.api import integracoes_router, usuarios_router, fornecedores_router, produtos_router, produtos_finais_router
from app.api.uploads import router as uploads_router
from app.api.notas import router as notas_router
from app.api.unidades import router as unidades_router
from app.api.materias_primas import router as materias_primas_router

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Garante que todos os modelos sejam carregados
load_all_models()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle da aplicação"""
    # Startup
    logger.info("Iniciando aplicação NFE...")
    
    # Criar tabelas se não existirem (código síncrono)
    try:
        from app.models.base import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Encerrando aplicação NFE...")


# Criação da aplicação FastAPI
DEBUG = getattr(settings, "DEBUG", True)

app = FastAPI(
    title="Sistema NFE - Notas Fiscais Eletrônicas",
    description="Sistema completo para gestão de notas fiscais eletrônicas, matérias-primas, fornecedores e produtos",
    version="1.0.0",
    debug=DEBUG,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
    lifespan=lifespan
)

# Middleware CORS
# Configuração explícita para desenvolvimento
cors_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.1.5173",
    "http://127.0.1.5174",
    "http://127.0.1.5175"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Middleware de hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Gerar ou ler X-Request-ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
        import uuid
        request_id = str(uuid.uuid4())
    
    # Adicionar request_id ao logger
    logger.info(
        f"[{request_id}] Request: {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'} - "
        f"User-Agent: {request.headers.get('user-agent', 'unknown')}"
    )
    
    response = await call_next(request)
    
    # Adicionar X-Request-ID ao response
    response.headers["X-Request-ID"] = request_id
    
    # Log da resposta
    process_time = time.time() - start_time
    logger.info(
        f"[{request_id}] Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação de requisição"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erro de validação",
            "errors": exc.errors(),
            "path": request.url.path
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler para exceções HTTP"""
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    # Log detalhado para erros de SQLAlchemy
    if hasattr(exc, '__class__') and 'sqlalchemy' in str(exc.__class__).lower():
        logger.error(f"SQLAlchemy error details: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Erro de banco de dados",
                "error_type": exc.__class__.__name__,
                "message": str(exc),
                "path": request.url.path
            }
        )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "path": request.url.path
        }
    )


# Health check
@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da aplicação"""
    # Verificar conexão com banco
    db_status = False
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
    
    return {
        "status": "ok",
        "db": db_status,
        "timestamp": time.time(),
        "debug": DEBUG
    }

# Test endpoint simples
@app.get("/test")
async def test_endpoint():
    """Endpoint de teste simples"""
    return {
        "message": "Backend funcionando!",
        "timestamp": time.time(),
        "cors_origins": settings.cors_origins_list
    }

# Test endpoint para debug
@app.post("/test-notas")
async def test_notas():
    """Endpoint de teste para debug"""
    return {
        "message": "Teste OK!",
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/")
async def root():
    """Endpoint raiz da aplicação"""
    return {
        "message": "Sistema NFE - API de Notas Fiscais Eletrônicas",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# inclui todos os routers disponíveis
app.include_router(notas_router)
app.include_router(integracoes_router)
app.include_router(usuarios_router)
app.include_router(fornecedores_router)
app.include_router(produtos_router)
app.include_router(produtos_finais_router)
app.include_router(uploads_router)
app.include_router(unidades_router)
app.include_router(materias_primas_router)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 
