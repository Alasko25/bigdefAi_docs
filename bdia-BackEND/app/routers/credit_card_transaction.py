from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import joblib
import numpy as np
from app.core.database import get_db
from app.models.credit_card_transaction import CreditCardTransaction
from app.schemas.credit_card_transaction import CreditCardTransactionCreate, CreditCardTransactionOut, CreditCardTransactionUpdate
from app.routers.user import fastapi_users
from app.models.user import User
from app.logging.log_setup import logger
from app.schemas.user import Role
from datetime import datetime

router = APIRouter(prefix="/credit_card_transactions", tags=["Credit Card Transactions"])

# Load ML model
try:
    fraud_model = joblib.load("app/ml_models/fraud_model.pkl")
except FileNotFoundError:
    logger.error("Fraud model not found")
    fraud_model = None

@router.post("/add", response_model=CreditCardTransactionOut)
async def add_credit_card_transaction(
    transaction: CreditCardTransactionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    try:
        # Preload user attributes to avoid lazy loading
        user_id = current_user.id
        user_role = current_user.role

        # Check permissions
        if user_role != Role.client_banque:
            logger.error(
                "Unauthorized attempt to add credit card transaction",
                extra={
                    "category": "error",
                    "user_id": user_id,
                    "role": user_role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les clients banque peuvent ajouter des transactions")

        # Validate amount
        if transaction.amount <= 0:
            logger.error(
                "Invalid amount",
                extra={
                    "category": "error",
                    "user_id": user_id,
                    "amount": transaction.amount,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=400, detail="Amount must be positive")

        # Predict fraud
        if fraud_model:
            features = np.array([[
                transaction.time, transaction.v1, transaction.v2, transaction.v3, transaction.v4,
                transaction.v5, transaction.v6, transaction.v7, transaction.v8, transaction.v9,
                transaction.v10, transaction.v11, transaction.v12, transaction.v13, transaction.v14,
                transaction.v15, transaction.v16, transaction.v17, transaction.v18, transaction.v19,
                transaction.v20, transaction.v21, transaction.v22, transaction.v23, transaction.v24,
                transaction.v25, transaction.v26, transaction.v27, transaction.v28, transaction.amount
            ]])
            is_fraud = bool(fraud_model.predict(features)[0])
            fraud_probability = fraud_model.predict_proba(features)[0][1]
        else:
            is_fraud = False
            fraud_probability = 0.0

        # Create transaction
        db_transaction = CreditCardTransaction(
            **transaction.dict(),
            is_fraud=is_fraud
        )
        db.add(db_transaction)
        await db.commit()
        await db.refresh(db_transaction)

        # Log fraud alert if detected
        if is_fraud:
            logger.info(
                "Transaction frauduleuse détectée",
                extra={
                    "category": "alert",
                    "user_id": user_id,
                    "role": user_role,
                    "ip_address": request.client.host,
                    "details": {
                        "transaction_id": db_transaction.id,
                        "fraud_probability": fraud_probability,
                        "amount": transaction.amount
                    }
                }
            )

        logger.info(
            "Credit card transaction added successfully",
            extra={
                "category": "transaction",
                "transaction_id": db_transaction.id,
                "user_id": user_id,
                "role": user_role,
                "ip_address": request.client.host
            }
        )
        return db_transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to add credit card transaction",
            extra={
                "category": "error",
                "user_id": user_id if 'user_id' in locals() else None,
                "role": user_role if 'user_role' in locals() else None,
                "ip_address": request.client.host,
                "details": {"error": str(e)}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout de la transaction : {str(e)}")

@router.get("/", response_model=List[CreditCardTransactionOut])
async def get_all_credit_card_transactions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    try:
        # Preload user attributes
        user_id = current_user.id
        user_role = current_user.role

        # Check permissions
        if user_role not in [Role.analyste, Role.admin]:
            logger.error(
                "Unauthorized attempt to list credit card transactions",
                extra={
                    "category": "error",
                    "user_id": user_id,
                    "role": user_role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admins peuvent lister les transactions")

        result = await db.execute(select(CreditCardTransaction))
        transactions = result.scalars().all()
        logger.info(
            "Retrieved all credit card transactions",
            extra={
                "category": "query",
                "user_id": user_id,
                "role": user_role,
                "count": len(transactions),
                "ip_address": request.client.host
            }
        )
        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve credit card transactions",
            extra={
                "category": "error",
                "user_id": user_id if 'user_id' in locals() else None,
                "role": user_role if 'user_role' in locals() else None,
                "ip_address": request.client.host,
                "details": {"error": str(e)}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des transactions : {str(e)}")

@router.get("/all", response_model=List[CreditCardTransactionOut])
async def get_all_credit_card_transactions_alias(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    # Alias for GET /
    return await get_all_credit_card_transactions(request, db, current_user)

@router.patch("/{transaction_id}", response_model=CreditCardTransactionOut)
async def update_credit_card_transaction(
    transaction_id: int,
    update_data: CreditCardTransactionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    try:
        # Preload user attributes
        user_id = current_user.id
        user_role = current_user.role

        # Check permissions
        if user_role != Role.admin:
            logger.error(
                "Unauthorized attempt to update credit card transaction",
                extra={
                    "category": "error",
                    "user_id": user_id,
                    "role": user_role,
                    "transaction_id": transaction_id,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les admins peuvent mettre à jour des transactions")

        # Fetch transaction
        result = await db.execute(select(CreditCardTransaction).filter(CreditCardTransaction.id == transaction_id))
        db_transaction = result.scalars().first()
        if not db_transaction:
            logger.warning(
                "Credit card transaction not found",
                extra={
                    "category": "transaction",
                    "transaction_id": transaction_id,
                    "user_id": user_id,
                    "role": user_role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_transaction, field, value)

        # Recompute fraud if features changed
        if any(field in update_dict for field in ["time", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9",
                                                 "v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18",
                                                 "v19", "v20", "v21", "v22", "v23", "v24", "v25", "v26", "v27",
                                                 "v28", "amount"]):
            if fraud_model:
                features = np.array([[
                    db_transaction.time, db_transaction.v1, db_transaction.v2, db_transaction.v3,
                    db_transaction.v4, db_transaction.v5, db_transaction.v6, db_transaction.v7,
                    db_transaction.v8, db_transaction.v9, db_transaction.v10, db_transaction.v11,
                    db_transaction.v12, db_transaction.v13, db_transaction.v14, db_transaction.v15,
                    db_transaction.v16, db_transaction.v17, db_transaction.v18, db_transaction.v19,
                    db_transaction.v20, db_transaction.v21, db_transaction.v22, db_transaction.v23,
                    db_transaction.v24, db_transaction.v25, db_transaction.v26, db_transaction.v27,
                    db_transaction.v28, db_transaction.amount
                ]])
                db_transaction.is_fraud = bool(fraud_model.predict(features)[0])
                fraud_probability = fraud_model.predict_proba(features)[0][1]
            else:
                db_transaction.is_fraud = False
                fraud_probability = 0.0

            # Log fraud alert if detected
            if db_transaction.is_fraud:
                logger.info(
                    "Transaction frauduleuse détectée après mise à jour",
                    extra={
                        "category": "alert",
                        "user_id": user_id,
                        "role": user_role,
                        "ip_address": request.client.host,
                        "details": {
                            "transaction_id": db_transaction.id,
                            "fraud_probability": fraud_probability,
                            "amount": db_transaction.amount
                        }
                    }
                )

        await db.commit()
        await db.refresh(db_transaction)

        logger.info(
            "Credit card transaction updated successfully",
            extra={
                "category": "transaction",
                "transaction_id": transaction_id,
                "user_id": user_id,
                "role": user_role,
                "updated_fields": list(update_dict.keys()),
                "ip_address": request.client.host
            }
        )
        return db_transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to update credit card transaction",
            extra={
                "category": "error",
                "user_id": user_id if 'user_id' in locals() else None,
                "role": user_role if 'user_role' in locals() else None,
                "transaction_id": transaction_id,
                "ip_address": request.client.host,
                "details": {"error": str(e)}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la transaction : {str(e)}")

@router.delete("/{transaction_id}", response_model=CreditCardTransactionOut)
async def delete_credit_card_transaction(
    transaction_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    try:
        # Preload user attributes
        user_id = current_user.id
        user_role = current_user.role

        # Check permissions
        if user_role != Role.admin:
            logger.error(
                "Unauthorized attempt to delete credit card transaction",
                extra={
                    "category": "error",
                    "user_id": user_id,
                    "role": user_role,
                    "transaction_id": transaction_id,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les admins peuvent supprimer des transactions")

        # Fetch transaction
        result = await db.execute(select(CreditCardTransaction).filter(CreditCardTransaction.id == transaction_id))
        db_transaction = result.scalars().first()
        if not db_transaction:
            logger.warning(
                "Credit card transaction not found",
                extra={
                    "category": "transaction",
                    "transaction_id": transaction_id,
                    "user_id": user_id,
                    "role": user_role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        db.delete(db_transaction)
        await db.commit()

        logger.info(
            "Credit card transaction deleted successfully",
            extra={
                "category": "transaction",
                "transaction_id": transaction_id,
                "user_id": user_id,
                "role": user_role,
                "ip_address": request.client.host
            }
        )
        return db_transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to delete credit card transaction",
            extra={
                "category": "error",
                "user_id": user_id if 'user_id' in locals() else None,
                "role": user_role if 'user_role' in locals() else None,
                "transaction_id": transaction_id,
                "ip_address": request.client.host,
                "details": {"error": str(e)}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la transaction : {str(e)}")

@router.get("/export", response_model=List[CreditCardTransactionOut])
async def export_credit_card_transactions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    try:
        # Preload user attributes
        user_id = current_user.id
        user_role = current_user.role

        # Check permissions
        if user_role not in [Role.analyste, Role.admin]:
            logger.error(
                "Unauthorized attempt to export credit card transactions",
                extra={
                    "category": "error",
                    "user_id": user_id,
                    "role": user_role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admins peuvent exporter les transactions")

        result = await db.execute(select(CreditCardTransaction))
        transactions = result.scalars().all()
        logger.info(
            "Credit card transactions exported successfully",
            extra={
                "category": "export",
                "user_id": user_id,
                "role": user_role,
                "count": len(transactions),
                "ip_address": request.client.host
            }
        )
        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to export credit card transactions",
            extra={
                "category": "error",
                "user_id": user_id if 'user_id' in locals() else None,
                "role": user_role if 'user_role' in locals() else None,
                "ip_address": request.client.host,
                "details": {"error": str(e)}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exportation des transactions : {str(e)}")