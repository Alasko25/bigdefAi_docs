from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.auth.user_manager import get_user_manager, UserManager
from app.schemas.user import UserCreate, UserRead, UserUpdate, ChangePassword
from app.models.user import User
from app.models.alert import Alert
from app.core.database import get_db
from app.auth.hash import hash_password, verify_password
from app.logging.log_setup import logger
from datetime import datetime
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from app.models.user import User as UserModel
from app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

# Configuration FastAPI Users
bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy
)

fastapi_users = FastAPIUsers[UserModel, int](get_user_manager, [auth_backend])
current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserRead)
@limiter.limit("5/minute")
async def register(
    user: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    superuser: UserModel = Depends(current_superuser),
    user_manager: UserManager = Depends(get_user_manager)
):
    try:
        # Vérifier si l'email existe
        existing_user = await user_manager.get_by_email(user.email)
        if existing_user:
            logger.warning(
                "Attempt to register with existing email",
                extra={
                    "category": "user_management",
                    "email": user.email,
                    "details": {
                        "role": user.role,
                        "ip_address": request.client.host
                    }
                }
            )
            alert = Alert(
                transaction_id=None,
                banque_id=None,
                fraud_probability=0.0,
                message=f"Tentative d'inscription avec un email existant : {user.email}",
                status="non traité",
                date=datetime.utcnow()
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)

            logger.info(
                "Alert generated for duplicate email registration",
                extra={
                    "category": "alert",
                    "alert_id": alert.id,
                    "email": user.email,
                    "details": {
                        "message": alert.message,
                        "ip_address": request.client.host
                    }
                }
            )
            raise HTTPException(status_code=400, detail="Email déjà utilisé")

        # Vérifier les rôles sensibles
        if user.role in ["admin", "analyste"]:
            if not superuser.is_superuser:
                logger.error(
                    "Unauthorized attempt to create admin or analyste",
                    extra={
                        "category": "error",
                        "user_id": superuser.id,
                        "email": user.email,
                        "details": {
                            "role": user.role,
                            "ip_address": request.client.host
                        }
                    }
                )
                raise HTTPException(status_code=403, detail="Seuls les superusers peuvent créer des admins ou analystes")

        # Créer l'utilisateur
        new_user = await user_manager.create(user)
        
        logger.info(
            "User registered successfully",
            extra={
                "category": "user_management",
                "user_id": new_user.id,
                "email": new_user.email,
                "role": new_user.role,
                "details": {
                    "ip_address": request.client.host,
                    "created_by": superuser.id
                }
            }
        )

        # Alerte pour rôles sensibles
        if user.role in ["admin", "analyste"]:
            alert = Alert(
                transaction_id=None,
                banque_id=None,
                fraud_probability=0.0,
                message=f"Nouvel utilisateur {user.role} créé : {new_user.email}",
                status="non traité",
                date=datetime.utcnow()
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)

            logger.info(
                "Alert generated for new admin/analyste user",
                extra={
                    "category": "alert",
                    "alert_id": alert.id,
                    "user_id": new_user.id,
                    "details": {
                        "message": alert.message,
                        "role": user.role,
                        "ip_address": request.client.host
                    }
                }
            )

        return new_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to register user",
            extra={
                "category": "error",
                "email": user.email,
                "details": {
                    "error": str(e),
                    "ip_address": request.client.host
                }
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'inscription : {str(e)}")

@router.get("/me", response_model=UserRead)
@limiter.limit("10/minute")
async def get_current_user(request: Request, user: UserModel = Depends(current_user)):
    try:
        logger.info(
            "User profile accessed",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "details": {"ip_address": request.client.host}
            }
        )
        return user

    except Exception as e:
        logger.error(
            "Failed to retrieve user profile",
            extra={
                "category": "error",
                "user_id": user.id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération du profil : {str(e)}")

@router.get("/all", response_model=List[UserRead])
@limiter.limit("10/minute")
async def get_all_users(request: Request, db: AsyncSession = Depends(get_db), user: UserModel = Depends(current_user)):
    try:
        # Vérifier les permissions
        if user.role not in ["analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to access all users",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admins peuvent lister tous les utilisateurs")

        result = await db.execute(select(User))
        users = result.scalars().all()
        logger.info(
            "Retrieved all users",
            extra={
                "category": "query",
                "user_id": user.id,
                "role": user.role,
                "details": {"count": len(users), "ip_address": request.client.host}
            }
        )
        return users

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve all users",
            extra={
                "category": "error",
                "user_id": user.id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des utilisateurs : {str(e)}")

@router.get("/{user_id}", response_model=UserRead)
@limiter.limit("10/minute")
async def get_user(user_id: int, request: Request, db: AsyncSession = Depends(get_db), user: UserModel = Depends(current_user)):
    try:
        # Vérifier les permissions
        if user.role == "client_banque" and user.id != user_id:
            logger.error(
                "Unauthorized attempt to access another user's profile",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "target_user_id": user_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Vous ne pouvez accéder qu'à votre propre profil")
        if user.role not in ["client_banque", "analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to access user profile",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "target_user_id": user_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Accès non autorisé")

        result = await db.execute(select(User).filter(User.id == user_id))
        db_user = result.scalars().first()
        if not db_user:
            logger.warning(
                "User not found",
                extra={
                    "category": "user_management",
                    "user_id": user.id,
                    "target_user_id": user_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        logger.info(
            "User profile retrieved",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "target_user_id": user_id,
                "role": user.role,
                "details": {"ip_address": request.client.host}
            }
        )
        return db_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve user profile",
            extra={
                "category": "error",
                "user_id": user.id,
                "target_user_id": user_id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de l'utilisateur : {str(e)}")

@router.patch("/{user_id}", response_model=UserRead)
@limiter.limit("5/minute")
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(current_user)
):
    try:
        # Vérifier les permissions
        if user.role != "admin" and user.id != user_id:
            logger.error(
                "Unauthorized attempt to update user",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "target_user_id": user_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les admins ou l'utilisateur lui-même peuvent mettre à jour un profil")

        result = await db.execute(select(User).filter(User.id == user_id))
        db_user = result.scalars().first()
        if not db_user:
            logger.warning(
                "User not found",
                extra={
                    "category": "user_management",
                    "user_id": user.id,
                    "target_user_id": user_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        # Vérifier les changements sensibles
        if update_data.role and update_data.role != db_user.role:
            if not user.is_superuser:
                logger.error(
                    "Unauthorized attempt to change user role",
                    extra={
                        "category": "error",
                        "user_id": user.id,
                        "target_user_id": user_id,
                        "role": user.role,
                        "details": {"new_role": update_data.role, "ip_address": request.client.host}
                    }
                )
                raise HTTPException(status_code=403, detail="Seuls les superusers peuvent changer le rôle")

        # Mettre à jour les champs non nuls
        for field, value in update_data.dict(exclude_unset=True).items():
            if field == "password":
                value = hash_password(value)
                setattr(db_user, "hashed_password", value)
            elif field != "password":
                setattr(db_user, field, value)

        await db.commit()
        await db.refresh(db_user)

        logger.info(
            "User updated successfully",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "target_user_id": user_id,
                "role": user.role,
                "details": {
                    "updated_fields": list(update_data.dict(exclude_unset=True).keys()),
                    "ip_address": request.client.host
                }
            }
        )

        # Alerte pour changements sensibles
        if update_data.role or update_data.is_superuser:
            alert = Alert(
                transaction_id=None,
                banque_id=None,
                fraud_probability=0.0,
                message=f"Profil utilisateur modifié : {db_user.email} (nouveau rôle : {db_user.role})",
                status="non traité",
                date=datetime.utcnow()
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)

            logger.info(
                "Alert generated for sensitive user update",
                extra={
                    "category": "alert",
                    "alert_id": alert.id,
                    "user_id": user.id,
                    "target_user_id": user_id,
                    "details": {
                        "message": alert.message,
                        "ip_address": request.client.host
                    }
                }
            )

        return db_user

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to update user",
            extra={
                "category": "error",
                "user_id": user.id,
                "target_user_id": user_id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de l'utilisateur : {str(e)}")

@router.delete("/{user_id}", response_model=UserRead)
@limiter.limit("5/minute")
async def delete_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(current_superuser)
):
    try:
        # Vérifier que l'utilisateur n'est pas lui-même
        if user.id == user_id:
            logger.error(
                "Attempt to delete own account",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Vous ne pouvez pas supprimer votre propre compte")

        result = await db.execute(select(User).filter(User.id == user_id))
        db_user = result.scalars().first()
        if not db_user:
            logger.warning(
                "User not found",
                extra={
                    "category": "user_management",
                    "user_id": user.id,
                    "target_user_id": user_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        db.delete(db_user)
        await db.commit()

        logger.info(
            "User deleted successfully",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "target_user_id": user_id,
                "role": user.role,
                "details": {"ip_address": request.client.host}
            }
        )

        # Alerte pour suppression
        alert = Alert(
            transaction_id=None,
            banque_id=None,
            fraud_probability=0.0,
            message=f"Utilisateur supprimé : {db_user.email}",
            status="non traité",
            date=datetime.utcnow()
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        logger.info(
            "Alert generated for user deletion",
            extra={
                "category": "alert",
                "alert_id": alert.id,
                "user_id": user.id,
                "target_user_id": user_id,
                "details": {
                    "message": alert.message,
                    "ip_address": request.client.host
                }
            }
        )

        return db_user

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to delete user",
            extra={
                "category": "error",
                "user_id": user.id,
                "target_user_id": user_id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de l'utilisateur : {str(e)}")

@router.post("/change-password")
@limiter.limit("5/minute")
async def change_password(
    data: ChangePassword,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(current_user)
):
    try:
        # Vérifier le mot de passe actuel
        if not verify_password(data.current_password, user.hashed_password):
            logger.warning(
                "Incorrect current password",
                extra={
                    "category": "user_management",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")

        # Mettre à jour le mot de passe
        user.hashed_password = hash_password(data.new_password)
        await db.commit()
        await db.refresh(user)

        logger.info(
            "Password changed successfully",
            extra={
                "category": "user_management",
                "user_id": user.id,
                "role": user.role,
                "details": {"ip_address": request.client.host}
            }
        )

        # Alerte pour changement de mot de passe
        alert = Alert(
            transaction_id=None,
            banque_id=None,
            fraud_probability=0.0,
            message=f"Changement de mot de passe pour l'utilisateur : {user.email}",
            status="non traité",
            date=datetime.utcnow()
        )
        db.add(alert)
        await db.commit()
        await db.refresh(alert)

        logger.info(
            "Alert generated for password change",
            extra={
                "category": "alert",
                "alert_id": alert.id,
                "user_id": user.id,
                "details": {
                    "message": alert.message,
                    "ip_address": request.client.host
                }
            }
        )

        return {"message": "Mot de passe changé avec succès"}

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to change password",
            extra={
                "category": "error",
                "user_id": user.id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors du changement de mot de passe : {str(e)}")