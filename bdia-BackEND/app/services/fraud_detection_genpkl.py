# train_and_evaluate.py

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

# 1. Charger le dataset initial
df = pd.read_csv("synthetic_fraud_dataset.csv")

# 2. Nettoyage de base
df = df.dropna(subset=["Is_Fraud"])

# 3. Feature Engineering

np.random.seed(42)

# a) Transaction_Category
df["Transaction_Category"] = np.random.choice(["achat", "retrait", "virement"], size=len(df))
df = pd.get_dummies(df, columns=["Transaction_Category"])

# b) Is_Large_Transaction
df["Is_Large_Transaction"] = (df["Transaction_Amount"] > 0.5).astype(int)

# c) Balance_Change
df["Balance_Change"] = df["Transaction_Amount"] * np.random.uniform(-1.5, 1.5, size=len(df))

# d) Is_New_User
df["Is_New_User"] = np.random.choice([0, 1], size=len(df), p=[0.7, 0.3])

# e) Amount_vs_Balance
df["Amount_vs_Balance"] = df["Transaction_Amount"] / (df["Account_Balance"] + 1e-6)

# 4. Enregistrement du dataset enrichi
df.to_csv("synthetic_fraud_dataset_enriched.csv", index=False)
print("✅ Nouveau dataset enregistré : synthetic_fraud_dataset_enriched.csv")

# 5. Séparation des variables
X = df.drop("Is_Fraud", axis=1)
y = df["Is_Fraud"]

# Supprimer colonnes non numériques
non_numeric_cols = X.select_dtypes(exclude=["number"]).columns
X = X.drop(columns=non_numeric_cols)

# 6. Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 7. Rééquilibrage avec SMOTE
X_resampled, y_resampled = SMOTE(random_state=42).fit_resample(X_scaled, y)

# 8. Définir les modèles
models = {
    "RandomForest": RandomForestClassifier(random_state=42),
    "XGBoost": XGBClassifier(eval_metric="logloss", use_label_encoder=False, random_state=42)
}

# 9. Évaluation avec validation croisée
def evaluate_model_with_confusion(model, X, y, cv):
    accuracies, precisions, recalls, f1s, roc_aucs = [], [], [], [], []
    last_cm = None

    for fold_idx, (train_idx, test_idx) in enumerate(cv.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        accuracies.append(accuracy_score(y_test, y_pred))
        precisions.append(precision_score(y_test, y_pred))
        recalls.append(recall_score(y_test, y_pred))
        f1s.append(f1_score(y_test, y_pred))
        roc_aucs.append(roc_auc_score(y_test, y_prob))

        if fold_idx == cv.get_n_splits() - 1:
            last_cm = confusion_matrix(y_test, y_pred)

    print(f"\n--- {model.__class__.__name__} ---")
    print(f"Accuracy :  {np.mean(accuracies):.4f} ± {np.std(accuracies):.4f}")
    print(f"Precision:  {np.mean(precisions):.4f} ± {np.std(precisions):.4f}")
    print(f"Recall   :  {np.mean(recalls):.4f} ± {np.std(recalls):.4f}")
    print(f"F1-Score :  {np.mean(f1s):.4f} ± {np.std(f1s):.4f}")
    print(f"ROC-AUC  :  {np.mean(roc_aucs):.4f} ± {np.std(roc_aucs):.4f}")

    plt.figure(figsize=(5, 4))
    sns.heatmap(last_cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"Matrice de confusion - {model.__class__.__name__}")
    plt.xlabel("Prédit")
    plt.ylabel("Réel")
    plt.tight_layout()
    plt.show()

# 10. Cross-validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 11. Entraînement et sauvegarde
model_dir = "app/ml_models"
os.makedirs(model_dir, exist_ok=True)

for name, model in models.items():
    print(f"\n### Évaluation : {name} ###")
    evaluate_model_with_confusion(model, X_resampled, y_resampled, skf)
    joblib.dump(model, f"{model_dir}/{name}_model.pkl")

# 12. Sauvegarde du scaler
joblib.dump(scaler, f"{model_dir}/scaler.pkl")
print("✅ Modèles et scaler sauvegardés.")
