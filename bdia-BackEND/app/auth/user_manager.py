# app/auth/user_manager.py
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from app.models.user import User
from app.core.database import get_db
from app.logging.log_setup import logger

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = "SECRET"  # Utilisez settings.SECRET_KEY en prod
    verification_token_secret = "SECRET"

    async def on_after_register(self, user: User, request: Request = None):
        logger.info(
            "User registered",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "bank_id": getattr(user, "banque_id", None),
                "details": {
                    "username": user.nom,
                    "email": user.email,
                    "role": user.role,
                    "ip_address": request.client.host if request else "unknown",
                    "action": "register"
                }
            }
        )

    async def on_after_verify(self, user: User, request: Request = None):
        logger.info(
            "User verified",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "bank_id": getattr(user, "banque_id", None),
                "details": {
                    "username": user.nom,
                    "ip_address": request.client.host if request else "unknown",
                    "action": "verify"
                }
            }
        )

    async def on_after_forgot_password(self, user: User, token: str, request: Request = None):
        logger.info(
            "Password reset requested",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "bank_id": getattr(user, "banque_id", None),
                "details": {
                    "username": user.nom,
                    "ip_address": request.client.host if request else "unknown",
                    "action": "forgot_password",
                    "token_issued": True
                }
            }
        )

async def get_user_manager(user_db=Depends(get_db)):
    yield UserManager(SQLAlchemyUserDatabase(user_db, User))