from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.transaction import Transaction
from app.models.alert import Alert
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from app.core.database import get_db
from app.services.fraud_detection import predict_fraud
from app.logging.log_setup import logger
from app.routers.user import fastapi_users, current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List
from datetime import datetime

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/transactions", tags=["Transactions"])

async def validate_banque_id(banque_id: int, db: AsyncSession):
    """Valide que banque_id correspond à un utilisateur client_banque."""
    result = await db.execute(
        select(User).filter(User.id == banque_id, User.role == "client_banque")
    )
    user = result.scalars().first()
    if not user:
        logger.error(
            "Invalid banque_id: not a client_banque user",
            extra={"category": "error", "bank_id": banque_id}
        )
        raise HTTPException(status_code=400, detail="banque_id must correspond to a client_banque user")
    return user

async def validate_customer_id(customer_id: int, db: AsyncSession):
    """Valide que customer_id existe."""
    result = await db.execute(select(Transaction).where(Transaction.customer_id == customer_id))
    transaction = result.scalars().first()
    if transaction:
        logger.error(
            "Invalid customer_id: already exists",
            extra={"category": "error", "customer_id": customer_id}
        )
        raise HTTPException(status_code=400, detail="customer_id already exists")
    return True

@router.post("/add", response_model=TransactionRead)
@limiter.limit("10/minute")
async def add_transaction(
    transaction: TransactionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        # Vérifier les permissions
        if user.role not in ["client_banque", "analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to add transaction",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les client_banque, analystes et admins peuvent ajouter des transactions")

        # Valider banque_id et customer_id
        await validate_banque_id(transaction.banque_id, db)
        await validate_customer_id(transaction.customer_id, db)

        # Valider transaction_amount
        if transaction.transaction_amount <= 0:
            logger.error(
                "Invalid transaction_amount",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "bank_id": transaction.banque_id,
                    "details": {"transaction_amount": transaction.transaction_amount}
                }
            )
            raise HTTPException(status_code=400, detail="transaction_amount must be positive")

        fraud_score = predict_fraud(transaction.dict())
        is_fraud = fraud_score > 0.8

        new_transaction = Transaction(
            customer_id=transaction.customer_id,
            customer_name=transaction.customer_name,
            gender=transaction.gender,
            age=transaction.age,
            state=transaction.state,
            city=transaction.city,
            bank_branch=transaction.bank_branch,
            account_type=transaction.account_type,
            transaction_id=transaction.transaction_id,
            transaction_date=transaction.transaction_date,
            transaction_time=transaction.transaction_time,
            transaction_amount=transaction.transaction_amount,
            merchant_id=transaction.merchant_id,
            transaction_type=transaction.transaction_type,
            merchant_category=transaction.merchant_category,
            account_balance=transaction.account_balance,
            transaction_device=transaction.transaction_device,
            transaction_location=transaction.transaction_location,
            device_type=transaction.device_type,
            transaction_currency=transaction.transaction_currency,
            customer_contact=transaction.customer_contact,
            transaction_description=transaction.transaction_description,
            customer_email=transaction.customer_email,
            banque_id=transaction.banque_id,
            is_fraud=is_fraud,
            fraud_probability=fraud_score
        )

        db.add(new_transaction)
        await db.commit()
        await db.refresh(new_transaction)

        logger.info(
            "Transaction processed successfully",
            extra={
                "category": "prediction",
                "transaction_id": new_transaction.transaction_id,
                "user_id": user.id,
                "bank_id": transaction.banque_id,
                "role": user.role,
                "details": {
                    "fraud_score": fraud_score,
                    "is_fraud": is_fraud,
                    "ip_address": request.client.host
                }
            }
        )

        if is_fraud:
            alert = Alert(
                transaction_id=new_transaction.id,
                banque_id=transaction.banque_id,
                fraud_probability=fraud_score,
                message=f"Transaction suspecte détectée avec une probabilité de {fraud_score:.2f}",
                status="non traité",
                date=datetime.utcnow()
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)

            logger.info(
                "Fraud alert generated",
                extra={
                    "category": "alert",
                    "alert_id": alert.id,
                    "transaction_id": new_transaction.transaction_id,
                    "user_id": user.id,
                    "bank_id": transaction.banque_id,
                    "role": user.role,
                    "details": {
                        "fraud_score": fraud_score,
                        "message": alert.message,
                        "ip_address": request.client.host
                    }
                }
            )

        return new_transaction

    except IntegrityError as e:
        await db.rollback()
        logger.error(
            "Failed to process transaction due to integrity error",
            extra={
                "category": "error",
                "transaction_id": transaction.transaction_id,
                "user_id": user.id,
                "bank_id": transaction.banque_id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(
            status_code=400,
            detail=f"Erreur d'intégrité: vérifiez les clés étrangères (banque_id) : {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to process transaction",
            extra={
                "category": "error",
                "transaction_id": transaction.transaction_id,
                "user_id": user.id,
                "bank_id": transaction.banque_id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur pendant l'ajout de la transaction : {str(e)}")

@router.get("/all", response_model=List[TransactionRead])
@limiter.limit("20/minute")
async def get_all_transactions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        if user.role not in ["analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to access all transactions",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admins peuvent accéder à toutes les transactions")

        result = await db.execute(select(Transaction))
        transactions = result.scalars().all()
        logger.info(
            "Retrieved all transactions",
            extra={
                "category": "query",
                "user_id": user.id,
                "role": user.role,
                "details": {"count": len(transactions), "ip_address": request.client.host}
            }
        )
        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to retrieve all transactions",
            extra={
                "category": "error",
                "user_id": user.id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des transactions : {str(e)}")

@router.get("/banque/{banque_id}", response_model=List[TransactionRead])
@limiter.limit("20/minute")
async def get_transactions_by_banque(
    banque_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        if user.role == "client_banque" and user.id != banque_id:
            logger.error(
                "Unauthorized attempt to access transactions for another banque",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "bank_id": banque_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Vous ne pouvez accéder qu'aux transactions de votre banque")
        if user.role not in ["client_banque", "analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to access banque transactions",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "bank_id": banque_id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les client_banque, analystes et admins peuvent accéder aux transactions par banque")

        await validate_banque_id(banque_id, db)

        result = await db.execute(select(Transaction).filter(Transaction.banque_id == banque_id))
        transactions = result.scalars().all()
        logger.info(
            f"Retrieved transactions for banque {banque_id}",
            extra={
                "category": "query",
                "user_id": user.id,
                "bank_id": banque_id,
                "role": user.role,
                "details": {"count": len(transactions), "ip_address": request.client.host}
            }
        )
        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve transactions for banque {banque_id}",
            extra={
                "category": "error",
                "user_id": user.id,
                "bank_id": banque_id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des transactions : {str(e)}")

@router.get("/by_type/{transaction_type}", response_model=List[TransactionRead])
@limiter.limit("20/minute")
async def get_transactions_by_type(
    transaction_type: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        if user.role not in ["client_banque", "analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to access transactions",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Unauthorized access to transactions")

        query = select(Transaction).where(Transaction.transaction_type == transaction_type)
        if user.role == "client_banque":
            query = query.where(Transaction.banque_id == user.id)

        result = await db.execute(query)
        transactions = result.scalars().all()
        if not transactions:
            logger.warning(
                f"No transactions found for type {transaction_type}",
                extra={
                    "category": "query",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="No transactions found for this type")

        logger.info(
            f"Retrieved transactions for type {transaction_type}",
            extra={
                "category": "query",
                "user_id": user.id,
                "role": user.role,
                "details": {"count": len(transactions), "ip_address": request.client.host}
            }
        )
        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve transactions for type {transaction_type}",
            extra={
                "category": "error",
                "user_id": user.id,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des transactions : {str(e)}")

@router.patch("/{transaction_id}", response_model=TransactionRead)
@limiter.limit("10/minute")
async def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        if user.role != "admin":
            logger.error(
                "Unauthorized attempt to update transaction",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "transaction_id": transaction_id,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les admins peuvent mettre à jour des transactions")

        result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
        db_transaction = result.scalars().first()
        if not db_transaction:
            logger.warning(
                "Transaction not found",
                extra={
                    "category": "transaction",
                    "transaction_id": transaction_id,
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(db_transaction, field, value)

        if any(field in update_data.dict(exclude_unset=True) for field in ["transaction_amount", "transaction_type", "transaction_location"]):
            fraud_score = predict_fraud(db_transaction.__dict__)
            db_transaction.fraud_probability = fraud_score
            db_transaction.is_fraud = fraud_score > 0.8

        await db.commit()
        await db.refresh(db_transaction)

        logger.info(
            "Transaction updated",
            extra={
                "category": "transaction",
                "transaction_id": transaction_id,
                "user_id": user.id,
                "bank_id": db_transaction.banque_id,
                "role": user.role,
                "details": {
                    "updated_fields": list(update_data.dict(exclude_unset=True).keys()),
                    "fraud_score": db_transaction.fraud_probability,
                    "ip_address": request.client.host
                }
            }
        )

        if db_transaction.is_fraud:
            alert = Alert(
                transaction_id=db_transaction.id,
                banque_id=db_transaction.banque_id,
                fraud_probability=db_transaction.fraud_probability,
                message=f"Transaction modifiée suspecte détectée avec une probabilité de {db_transaction.fraud_probability:.2f}",
                status="non traité",
                date=datetime.utcnow()
            )
            db.add(alert)
            await db.commit()
            await db.refresh(alert)

            logger.info(
                "Fraud alert generated for updated transaction",
                extra={
                    "category": "alert",
                    "alert_id": alert.id,
                    "transaction_id": transaction_id,
                    "user_id": user.id,
                    "bank_id": db_transaction.banque_id,
                    "role": user.role,
                    "details": {
                        "fraud_score": db_transaction.fraud_probability,
                        "message": alert.message,
                        "ip_address": request.client.host
                    }
                }
            )

        return db_transaction

    except IntegrityError as e:
        await db.rollback()
        logger.error(
            "Failed to update transaction due to integrity error",
            extra={
                "category": "error",
                "transaction_id": transaction_id,
                "user_id": user.id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(
            status_code=400,
            detail=f"Erreur d'intégrité: vérifiez les clés étrangères : {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to update transaction",
            extra={
                "category": "error",
                "transaction_id": transaction_id,
                "user_id": user.id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la transaction : {str(e)}")

@router.delete("/{transaction_id}", response_model=TransactionRead)
@limiter.limit("5/minute")
async def delete_transaction(
    transaction_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        if user.role != "admin":
            logger.error(
                "Unauthorized attempt to delete transaction",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "transaction_id": transaction_id,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les admins peuvent supprimer des transactions")

        result = await db.execute(select(Transaction).filter(Transaction.id == transaction_id))
        db_transaction = result.scalars().first()
        if not db_transaction:
            logger.warning(
                "Transaction not found",
                extra={
                    "category": "transaction",
                    "transaction_id": transaction_id,
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=404, detail="Transaction non trouvée")

        db.delete(db_transaction)
        await db.commit()

        logger.info(
            "Transaction deleted",
            extra={
                "category": "transaction",
                "transaction_id": transaction_id,
                "user_id": user.id,
                "bank_id": db_transaction.banque_id,
                "role": user.role,
                "details": {"ip_address": request.client.host}
            }
        )
        return db_transaction

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            "Failed to delete transaction",
            extra={
                "category": "error",
                "transaction_id": transaction_id,
                "user_id": user.id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression de la transaction : {str(e)}")

@router.get("/export", response_model=List[TransactionRead])
@limiter.limit("5/minute")
async def export_transactions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_user)
):
    try:
        if user.role not in ["analyste", "admin"]:
            logger.error(
                "Unauthorized attempt to export transactions",
                extra={
                    "category": "error",
                    "user_id": user.id,
                    "role": user.role,
                    "ip_address": request.client.host
                }
            )
            raise HTTPException(status_code=403, detail="Seuls les analystes et admins peuvent exporter les transactions")

        result = await db.execute(select(Transaction))
        transactions = result.scalars().all()
        logger.info(
            "Transactions exported for SIEM",
            extra={
                "category": "export",
                "user_id": user.id,
                "role": user.role,
                "details": {
                    "count": len(transactions),
                    "ip_address": request.client.host
                }
            }
        )
        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to export transactions",
            extra={
                "category": "error",
                "user_id": user.id,
                "role": user.role,
                "details": {"error": str(e), "ip_address": request.client.host}
            }
        )
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exportation des transactions : {str(e)}")