from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_users import FastAPIUsers
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, async_engine, init_db
from app.core.config import settings
from app.logging.log_setup import logger, setup_logging
from app.models.user import User as UserModel
from app.auth.user_manager import get_user_manager
from app.routers import alerts, transaction, user , credit_card_transaction
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from app.schemas.user import UserRead, UserCreate
from sqlalchemy import text

# Initialiser l'application FastAPI
app = FastAPI(
    title="BigDefend AI",
    description="API de détection de fraude pour les institutions financières",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurer le rate limiting global
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configurer CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration de l'authentification
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)

bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/jwt/login")
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[UserModel, int](
    get_user_manager,
    [auth_backend],
)

# Inclure les routeurs
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(transaction.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(credit_card_transaction.router, prefix="/api/v1")
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/v1/auth/jwt",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/auth",
    tags=["Auth"],
)

# Initialiser les bases de données
@app.on_event("startup")
async def startup_event():
    # Configurer le logging
    setup_logging()
    # Créer les tables SQL (mode asynchrone)
    await init_db()
    logger.info(
        "Application started",
        extra={
            "category": "system",
            "details": {"event": "startup"}
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(
        "Application shutdown",
        extra={
            "category": "system",
            "details": {"event": "shutdown"}
        }
    )
    await async_engine.dispose()

# Endpoint racine
@app.get("/", tags=["Root"])
@limiter.limit("10/minute")
async def root(request: Request):
    return {"message": "Bienvenue sur l'API BigDefend AI"}

# Endpoint de santé
@app.get("/health", tags=["Health"])
@limiter.limit("10/minute")

# Endpoint de santé
@app.get("/health", tags=["Health"])
@limiter.limit("10/minute")
async def health(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))  # Utilisation de text() pour SQLAlchemy 2.0
        logger.info(
            "Health check performed",
            extra={
                "category": "system",
                "details": {"status": "healthy"}
            }
        )
        return {"status": "healthy", "database": "ok", "logger": "ok"}
    except Exception as e:
        error_details = {
            "error": str(e),
            "type": type(e).__name__,
            "ip_address": request.client.host,
            "database_url": settings.DATABASE_URL
        }
        logger.error(
            "Health check failed",
            extra={
                "category": "error",
                "details": error_details
            }
        )
        raise HTTPException(status_code=500, detail=f"Health check failed: {error_details}")

# Middleware pour ajouter des logs
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        logger.info(
            "HTTP request processed",
            extra={
                "category": "http",
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "ip_address": request.client.host
            }
        )
        return response
    except Exception as e:
        logger.error(
            "HTTP request failed",
            extra={
                "category": "error",
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "ip_address": request.client.host
            }
        )
        raise