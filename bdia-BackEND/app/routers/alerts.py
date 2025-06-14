from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.alert import Alert
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertRead
from app.core.database import get_db
from app.logging.log_setup import logger
from app.routers.user import fastapi_users, current_user
from datetime import datetime
from enum import Enum
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Statuts valides pour les alertes
class AlertStatus(str, Enum): 
    non_traite = "non traité"
    traite = "traité"
    archive = "archivé"

router = APIRouter(prefix="/alerts", tags=["Alerts"])

async def validate_banque_id(banque_id: int, db: AsyncSession):
    """Valide que banque_id correspond à un utilisateur client_banque."""
    result = await db.execute(
        select(User).where(User.id == banque_id, User.role == "client_banque")
    )
    user = result.scalars().first()
    if not user:
        logger.error(
            "Invalid banque_id: not a client_banque user",
            extra={"category": "error", "bank_id": banque_id}
        )
        raise HTTPException(status_code=400, detail="banque_id must correspond to a client_banque user")
    return user

@router.post("/create", response_model=AlertRead)
@limiter.limit("10/minute")
async def create_alert(
    alert: AlertCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        # Vérifier les permissions
        if user.role not in ["client_banque", "analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to create alert",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les client_banque, analystes et admins peuvent créer des alertes")

        # Valider banque_id
        await validate_banque_id(alert.banque_id, db)

        # Valider fraud_probability
        if not 0 <= alert.fraud_probability <= 1:
            logger.error(
                "Invalid fraud_probability",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "bank_id": alert.banque_id,
                    "details": {"fraud_probability": alert.fraud_probability}
                }
            )
            raise HTTPException(status_code=400, detail="fraud_probability must be between 0 and 1")

        db_alert = Alert(
            transaction_id=alert.transaction_id,
            banque_id=alert.banque_id,
            fraud_probability=alert.fraud_probability,
            message=alert.message,
            status=AlertStatus.non_traite,
            date=datetime.utcnow()
        )
        db.add(db_alert)
        await db.commit()
        await db.refresh(db_alert)

        logger.info(
            "Alert created manually",
            extra={
                "category": "alert",
                "alert_id": db_alert.id,
                "transaction_id": alert.transaction_id,
                "bank_id": alert.banque_id,
                "user_id": user.id,
                "role": user.role,
                "details": {
                    "fraud_score": alert.fraud_probability,
                    "message": alert.message,
                    "ip_address": request.client.host
                }
            }
        )
        return db_alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to create alert",
            extra={
                "category": "error",
                "transaction_id": alert.transaction_id,
                "bank_id": alert.banque_id,
                "user_id": user.id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'alerte : {str(e)}")

@router.get("/all", response_model=List[AlertRead])
@limiter.limit("20/minute")
async def get_all_alerts(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        # Vérifier les permissions
        if user.role not in ["analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to access all alerts",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admins peuvent accéder à toutes les alertes")

        result = await db.execute(select(Alert))
        alerts = result.scalars().all()
        logger.info(
            "Retrieved all alerts",
            extra={
                "category": "query",
                "user_id": user.id,
                "role": user.role,
                "details": {"count": len(alerts), "ip_address": request.client.host}
            }
        )
        return alerts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve all alerts",
            extra={
                "category": "error",
                "user_id": user.id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des alertes : {str(e)}")

@router.get("/by_banque_id/{banque_id}", response_model=List[AlertRead])
@limiter.limit("20/minute")
async def get_alerts_by_banque(
    banque_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        # Vérifier les permissions
        if user.role == "client_banque" and user.id != banque_id:
            logger.error(
                "Unauthorized attempt to access alerts for another banque",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "bank_id": banque_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Vous ne pouvez accéder qu'aux alertes de votre banque")
        if user.role not in ["client_banque", "analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to access banque alerts",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "bank_id": banque_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les client_banque, analystes et admins peuvent accéder aux alertes par banque")

        # Valider banque_id
        await validate_banque_id(banque_id, db)

        result = await db.execute(select(Alert).where(Alert.banque_id == banque_id))
        alerts = result.scalars().all()
        logger.info(
            f"Retrieved alerts for banque {banque_id}",
            extra={
                "category": "query",
                "user_id": user.id,
                "bank_id": banque_id,
                "role": user.role,
                "details": {"count": len(alerts), "ip_address": request.client.host}
            }
        )
        return alerts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve alerts for banque {banque_id}",
            extra={
                "category": "error",
                "user_id": user.id,
                "bank_id": banque_id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des alertes : {str(e)}")

@router.patch("/{alert_id}/status", response_model=AlertRead)
@limiter.limit("10/minute")
async def update_alert_status(
    alert_id: int,
    status: AlertStatus,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        # Vérifier les permissions
        if user.role not in ["analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to update alert status",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "alert_id": alert_id,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admins peuvent mettre à jour le statut des alertes")

        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        db_alert = result.scalars().first()
        if not db_alert:
            logger.warning(
                "Alert not found",
                extra={
                    "category": "alert",
                    "alert_id": alert_id,
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Alerte non trouvée")

        db_alert.status = status.value
        await db.commit()
        await db.refresh(db_alert)

        logger.info(
            "Alert status updated successfully",
            extra={
                "category": "alert",
                "alert_id": alert_id,
                "transaction_id": db_alert.transaction_id,
                "bank_id": db_alert.banque_id,
                "user_id": user.id,
                "role": user.role,
                "details": {
                    "new_status": status.value,
                    "ip_address": request.client.host
                }
            }
        )
        return db_alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to update alert status",
            extra={
                "category": "error",
                "alert_id": alert_id,
                "user_id": user.id,
                "details": {
                    "error": str(e),
                    "ip_address": request.client.host
                }
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de l'alerte : {str(e)}")

@router.delete("/{alert_id}", response_model=AlertRead)
@limiter.limit("10/minute")
async def delete_alert(
    alert_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        # Vérification des permissions
        if user.role != "admin":
            logger.error(
                "Unauthorized attempt to delete alert",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "alert_id": alert_id,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les utilisateurs admin peuvent supprimer des alertes")

        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        db_alert = result.scalars().first()
        if not db_alert:
            logger.warning(
                "Alert not found",
                extra={
                    "category": "alert",
                    "alert_id": alert_id,
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Alerte non trouvée")

        await db.delete(db_alert)
        await db.commit()

        logger.info(
            "Alert deleted successfully",
            extra={
                "category": "alert",
                "alert_id": alert_id,
                "transaction_id": db_alert.transaction_id,
                "bank_id": db_alert.banque_id,
                "user_id": user.id,
                "role": user.role,
                "details": {
                    "ip_address": request.client.host
                }
            }
        )
        return db_alert

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete alert",
            extra={
                "category": "error",
                "alert_id": alert_id,
                "user_id": user.id,
                "details": {
                    "error": str(e),
                    "ip_address": request.client.host
                }
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de l'alerte : {str(e)}")

@router.get("/export", response_model=List[AlertRead])
@limiter.limit("5/minute")
async def export_alerts(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        # Vérification des permissions
        if user.role not in ["analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to export alerts",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admin peuvent exporter les alertes")

        result = await db.execute(select(Alert))
        alerts = result.scalars().all()
        logger.info(
            "Alerts exported successfully",
            extra={
                "category": "export",
                "user_id": user.id,
                "role": user.role,
                "details": {
                    "count": len(alerts),
                    "ip_address": request.client.host
                }
            }
        )
        return alerts

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to export alerts",
            extra={
                "category": "error",
                "user_id": user.id,
                "details": {
                    "error": str(e),
                    "ip_address": request.client.host
                }
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exportation des alertes : {str(e)}")