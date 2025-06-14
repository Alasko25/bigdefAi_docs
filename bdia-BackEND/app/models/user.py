from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    # Colonne ID requise comme clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Champs obligatoires de fastapi-users
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=1024), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Champs personnalisés
    nom = Column(String, nullable=False)
    role = Column(String, default="client_banque")