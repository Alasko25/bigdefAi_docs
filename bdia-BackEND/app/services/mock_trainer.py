# app/services/mock_trainer.py
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from app.logging.log_setup import logger

def create_fake_model():
    # Simuler des données basées sur : montant, heure (extrait depuis date)
    # Exemple : [montant, heure de la transaction]
    X = np.array([
        [100.0, 10],   # normal
        [200.0, 14],   # normal
        [5000.0, 3],   # frauduleux
        [50.0, 23]     # normal
    ])
    y = [0, 0, 1, 0]  # 1 = fraude, 0 = normale

    # Mise à l'échelle
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Entraînement du modèle
    model = RandomForestClassifier(n_estimators=10)
    model.fit(X_scaled, y)

    # Sauvegarde du modèle et du scaler
    os.makedirs("app/ml_models", exist_ok=True)
    joblib.dump(model, "app/ml_models/fraud_detector.pkl")
    joblib.dump(scaler, "app/ml_models/scaler.pkl")

    print("✅ Modèle factice adapté à TransactionInput généré avec succès.")
