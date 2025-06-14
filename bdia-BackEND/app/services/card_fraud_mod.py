import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import joblib
import os

def train_fraud_model(data_path="creditcard.csv"):
    # Charger le dataset
    df = pd.read_csv(data_path)
    X = df.drop(columns=["Class"])
    y = df["Class"]

    # Diviser en train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Appliquer SMOTE
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    # Entraîner XGBoost
    model = XGBClassifier(scale_pos_weight=1, random_state=42)
    model.fit(X_train_res, y_train_res)

    # Évaluer avec AUPRC
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auprc = average_precision_score(y_test, y_pred_proba)
    print(f"AUPRC: {auprc}")

    # Sauvegarder le modèle
    model_dir = os.path.join("..", "ml_models")  # remonte un dossier pour être dans 'app/ml_models'
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, "fraud_model.pkl"))

if __name__ == "__main__":
    train_fraud_model()