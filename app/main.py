"""Punto de entrada de la aplicación FastAPI.

Configura logging, CORS, rate limiting, handlers de error y monta los routers.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app.errors import register_error_handlers, _error_body
from app.rate_limit import limiter
from app.routers import auth, categories, products, users

# --- Logging estructurado (sencillo, a stdout) ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("tienda-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas al arrancar.

    Para un proyecto real usaríamos migraciones (Alembic); create_all alcanza
    para desarrollo local con SQLite.
    """
    # Importar los modelos asegura que estén registrados en Base.metadata.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Aplicación iniciada (entorno=%s)", settings.ENVIRONMENT)
    yield
    logger.info("Aplicación detenida")


app = FastAPI(
    title="Tienda API",
    version="1.0.0",
    description=(
        "API REST de una tienda online: autenticación con JWT, categorías y "
        "productos con paginación, filtros y búsqueda."
    ),
    lifespan=lifespan,
)

# --- Rate limiting ---
# El limiter se guarda en app.state y registramos el handler de 429.
app.state.limiter = limiter


from fastapi.responses import JSONResponse  # noqa: E402


async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content=_error_body(429, f"Límite de peticiones excedido: {exc.detail}"),
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Handlers de error consistentes (JSON) ---
register_error_handlers(app)


# --- Middleware de logging: registra método, path, status y duración ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# --- Routers ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(products.router)


@app.get("/", tags=["Salud"], summary="Estado de la API")
def root():
    """Endpoint raíz para verificar que la API está viva."""
    return {"status": "ok", "service": "tienda-api", "docs": "/docs"}
