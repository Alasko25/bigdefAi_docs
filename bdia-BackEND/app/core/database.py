from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base

# Configuration du moteur asynchrone
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Active les logs SQL pour le débogage
    future=True  # Compatibilité avec SQLAlchemy 2.0
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    """
    Fournit une session asynchrone pour les routes FastAPI.
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

async def init_db():
    """
    Crée les tables dans la base de données.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)