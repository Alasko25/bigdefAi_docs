# app/services/fraud_detection.py

import joblib
import numpy as np
from app.models.schemas import TransactionInput
from app.logging.log_setup import logger

# Chargement du modèle (RandomForest ou XGBoost)
model = joblib.load("app/ml_models/RandomForest.pkl")
scaler = joblib.load("app/ml_models/scaler.pkl")

def preprocess_transaction(transaction: TransactionInput) -> np.ndarray:
    try:
        features = np.array([[
            transaction.transaction_amount,
            transaction.account_balance,
            transaction.transaction_amount / (transaction.account_balance + 1e-6),
            float(transaction.transaction_category == "achat"),
            float(transaction.transaction_category == "retrait"),
            float(transaction.transaction_category == "virement"),
            float(transaction.transaction_amount > 0.5),
            transaction.balance_change,
            transaction.is_new_user
        ]])

        logger.debug(
            "Preprocessing transaction",
            extra={
                "category": "preprocessing",
                "transaction_id": transaction.transaction_id,
                "user_id": transaction.user_id,
                "bank_id": getattr(transaction, "banque_id", None),
                "details": features.tolist()
            }
        )
        return features

    except Exception as e:
        logger.error(
            "Failed to preprocess transaction",
            extra={
                "category": "error",
                "transaction_id": transaction.transaction_id,
                "user_id": transaction.user_id,
                "bank_id": getattr(transaction, "banque_id", None),
                "details": {"error": str(e)}
            }
        )
        raise RuntimeError(f"Erreur pendant le prétraitement : {str(e)}")

def predict_fraud(transaction_dict: dict) -> float:
    try:
        transaction_input = TransactionInput(**transaction_dict)
        features = preprocess_transaction(transaction_input)
        scaled = scaler.transform(features)
        prob_fraud = model.predict_proba(scaled)[0][1]

        logger.info(
            "Fraud prediction completed",
            extra={
                "category": "prediction",
                "transaction_id": transaction_input.transaction_id,
                "user_id": transaction_input.user_id,
                "bank_id": getattr(transaction_input, "banque_id", None),
                "details": {"fraud_score": prob_fraud}
            }
        )

        if prob_fraud > 0.8:
            logger.warning(
                "Potential fraud detected",
                extra={
                    "category": "alert",
                    "transaction_id": transaction_input.transaction_id,
                    "user_id": transaction_input.user_id,
                    "bank_id": getattr(transaction_input, "banque_id", None),
                    "details": {"fraud_score": prob_fraud}
                }
            )

        return float(prob_fraud)

    except Exception as e:
        logger.error(
            "Fraud prediction failed",
            extra={
                "category": "error",
                "transaction_id": transaction_dict.get("transaction_id"),
                "user_id": transaction_dict.get("user_id"),
                "bank_id": transaction_dict.get("banque_id"),
                "details": {"error": str(e)}
            }
        )
        raise RuntimeError(f"Erreur pendant la prédiction : {str(e)}")
