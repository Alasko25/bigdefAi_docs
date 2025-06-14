# app/services/model_training.py

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.core.database import SyncSessionLocal  # ou get_db si asynchrone, mais ici sync
from app.models.transaction import Transaction
from app.logging.log_setup import logger

def retrain_model() -> bool:
    try:
        db: Session = SyncSessionLocal()
        data = db.query(Transaction).all()

        records = []
        for t in data:
            if t.is_fraud is not None:
                records.append({
                    "montant": t.montant,
                    "location_code": hash(getattr(t, "location", "unknown")) % 1000,
                    "hour": t.date.hour if hasattr(t.date, "hour") else 0,
                    "is_fraud": t.is_fraud
                })

        if not records:
            print("Aucune donnée valide pour entraîner le modèle.")
            return False

        df = pd.DataFrame(records)

        X = df.drop(columns=["is_fraud"])
        y = df["is_fraud"]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)

        # Sauvegarde des fichiers
        joblib.dump(model, "app/ml_models/fraud_detector.pkl")
        joblib.dump(scaler, "app/ml_models/scaler.pkl")

        return True

    except Exception as e:
        print(f"❌ Erreur lors du réentraînement : {e}")
        return False

    finally:
        db.close()
