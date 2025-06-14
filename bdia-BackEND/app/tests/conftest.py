import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.credit_card_transaction import CreditCardTransaction
from app.auth.hash import hash_password
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
import asyncio

# Base de données de test (SQLite en mémoire)
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest_asyncio.fixture(autouse=True, scope="function")
async def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest_asyncio.fixture
async def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest_asyncio.fixture
async def override_get_db(db_session):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def admin_user(db_session):
    user = User(
        email="admin@example.com",
        hashed_password=hash_password("Admin123!"),
        nom="Admin",
        role="admin",
        is_active=True,
        is_superuser=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def analyste_user(db_session):
    user = User(
        email="analyste@example.com",
        hashed_password=hash_password("Analyste123!"),
        nom="Analyste",
        role="analyste",
        is_active=True,
        is_superuser=False,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def client_banque_user(db_session):
    user = User(
        email="banque@example.com",
        hashed_password=hash_password("Banque123!"),
        nom="Banque A",
        role="client_banque",
        is_active=True,
        is_superuser=False,
        is_verified=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def admin_token(client, admin_user):
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "admin@example.com", "password": "Admin123!"}
    )
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def analyste_token(client, analyste_user):
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "analyste@example.com", "password": "Analyste123!"}
    )
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def client_banque_token(client, client_banque_user):
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "banque@example.com", "password": "Banque123!"}
    )
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def mock_fraud_model():
    with patch("app.routers.credit_card_transaction.fraud_model") as mock:
        mock.predict.return_value = [1]
        mock.predict_proba.return_value = [[0.3, 0.7]]
        yield mock

@pytest_asyncio.fixture
async def credit_card_transaction(db_session, client_banque_user):
    transaction = CreditCardTransaction(
        time=123456.0,
        v1=-1.359807, v2=-0.072781, v3=2.536346, v4=1.378155,
        v5=-0.338321, v6=0.462388, v7=0.239599, v8=0.098698,
        v9=0.363787, v10=0.090794, v11=-0.551600, v12=-0.617801,
        v13=-0.991390, v14=-0.311169, v15=1.468177, v16=-0.470401,
        v17=0.207971, v18=0.025791, v19=0.403993, v20=0.251412,
        v21=-0.018307, v22=0.277838, v23=-0.110474, v24=0.066928,
        v25=0.128539, v26=-0.189115, v27=0.133558, v28=-0.021053,
        amount=149.62,
        is_fraud=False
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction

@pytest_asyncio.fixture
async def mock_elasticsearch():
    with patch("app.logging.elasticsearch_logger.Elasticsearch") as mock_es:
        mock_instance = AsyncMock()
        mock_es.return_value = mock_instance
        yield mock_instance