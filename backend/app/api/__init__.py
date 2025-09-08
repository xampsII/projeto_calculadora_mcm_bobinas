from .integracoes import router as integracoes_router
from .usuarios import usuarios_router
from .fornecedores import fornecedores_router
from .produtos import produtos_router

__all__ = [
    "integracoes_router",
    "usuarios_router",
    "fornecedores_router", 
    "produtos_router",
] 