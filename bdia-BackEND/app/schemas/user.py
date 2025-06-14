from pydantic import BaseModel, EmailStr, Field, validator
from fastapi_users import schemas
from enum import Enum
import re
from typing import Optional

class Role(str, Enum):
    client_banque = "client_banque"
    admin = "admin"
    analyste = "analyste"

class UserCreate(schemas.BaseUserCreate):
    nom: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: Role = Role.client_banque

    @validator("email")
    def validate_email(cls, v: str):
        """Valide le format strict de l'email."""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, v):
            raise ValueError("Format d'email invalide")
        return v

    @validator("password")
    def validate_password(cls, v: str):
        """Valide la complexité du mot de passe."""
        if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", v):
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial")
        return v

class UserRead(schemas.BaseUser[int]):
    nom: str
    role: Role

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    role: Optional[Role] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None

    @validator("email", pre=True, always=True)
    def validate_email(cls, v: Optional[str]):
        if v:
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(pattern, v):
                raise ValueError("Format d'email invalide")
        return v

    @validator("password", pre=True, always=True)
    def validate_password(cls, v: Optional[str]):
        if v:
            if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", v):
                raise ValueError("Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial")
        return v

class ChangePassword(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=128)

    @validator("new_password")
    def validate_new_password(cls, v: str):
        if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", v):
            raise ValueError("Le nouveau mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule, un chiffre et un caractère spécial")
        return v