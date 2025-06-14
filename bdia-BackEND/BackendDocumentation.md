### **Documentation de l’Application Backend BigDefend AI**

#### **1. Introduction**
BigDefend AI est une API backend développée avec **FastAPI** pour détecter les fraudes financières en temps réel pour les institutions bancaires. Elle permet de gérer des **transactions**, des **alertes de fraude**, et des **utilisateurs** avec des rôles distincts (`client_banque`, `admin`, `analyste`). L’application est ultra-sécurisée, conçue pour être compatible avec un frontend (ex. : React sur `http://localhost:3000`) et prête pour une intégration SIEM (ex. : Elasticsearch/Kibana).

**Objectifs** :
- Détecter les fraudes via un modèle de machine learning (`predict_fraudulence`).
- Gérer les utilisateurs avec des permissions basées sur les rôles.
- Générer des alertes pour les transactions suspectes et les actions sensibles.
- Fournir des logs structurés pour l’audit et l’analyse SIEM.
- Offrir une API robuste, sécurisée, et bien documentée.

**Technologies** :
- **Framework** : FastAPI
- **Base de données** : PostgreSQL (données) + MongoDB (logs)
- **Authentification** : JWT via FastAPI Users
- **ORM** : SQLAlchemy
- **Validation** : Pydantic
- **Logging** : Custom logger avec MongoDB
- **Sécurité** : Rate limiting (SlowAPI), CORS, validation stricte
- **Configuration** : Pydantic Settings (`.env`)

---

#### **2. Structure du Projet**
Le projet est organisé pour maximiser la modularité et la maintenabilité :

```
bdia-BackEND/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration (chargement .env)
│   │   └── database.py       # Connexion SQLAlchemy (PostgreSQL)
│   ├── logging/
│   │   ├── log_setup.py      # Configuration du logger (MongoDB + console)
│   │   └── mongodb_logger.py # Handler MongoDB pour les logs
│   ├── models/
│   │   ├── alert.py         # Modèle SQLAlchemy pour les alertes
│   │   ├── transaction.py   # Modèle SQLAlchemy pour les transactions
│   │   └── user.py          # Modèle SQLAlchemy pour les utilisateurs
│   ├── routers/
│   │   ├── alerts.py        # Routes pour les alertes
│   │   ├── transaction.py   # Routes pour les transactions
│   │   └── user.py          # Routes pour les utilisateurs
│   ├── schemas/
│   │   ├── alert.py         # Schémas Pydantic pour les alertes
│   │   ├── transaction.py   # Schémas Pydantic pour les transactions
│   │   └── user.py          # Schémas Pydantic pour les utilisateurs
│   ├── services/
│   │   └── fraud_detection.py # Service de détection de fraude
│   ├── auth/
│   │   ├── hash.py          # Gestion des mots de passe (hashage)
│   │   └── user_manager.py  # Gestion des utilisateurs (FastAPI Users)
│   └── main.py              # Point d’entrée de l’application
├── .env                     # Variables d’environnement
├── requirements.txt         # Dépendances Python
├── docker-compose.yml       # Configuration Docker
└── README.md                # Documentation sommaire
```

---

#### **3. Sécurité**
L’application est conçue avec un haut niveau de sécurité pour répondre aux exigences de production.

##### **3.1. Authentification**
- **Mécanisme** : JWT (JSON Web Tokens) via **FastAPI Users**.
- **Configuration** :
  - Tokens générés avec `SECRET_KEY` (stocké dans `.env`).
  - Durée de vie : 1 heure (`lifetime_seconds=3600`).
  - Endpoints : `/api/v1/auth/jwt/login`, `/api/v1/auth/jwt/logout`.
- **Rôles** :
  - `client_banque` : Banques clientes, accès limité (ajout/consultation de leurs transactions, consultation de leur profil).
  - `admin` : Accès complet (gestion des utilisateurs, transactions, alertes, suppression).
  - `analyste` : Consultation des transactions/alertes, export pour SIEM.
- **Protection** : Tous les endpoints (sauf `/`, `/health`, `/docs`) nécessitent un token JWT valide via `Depends(current_user)` ou `Depends(current_superuser)`.

##### **3.2. Permissions**
- **Granularité** : Chaque endpoint vérifie le rôle de l’utilisateur :
  - Exemple : `POST /api/v1/users/register` est réservé aux `admin` (superusers).
  - `client_banque` ne peut accéder qu’à ses propres données (`banque_id == user.id`).
- **Vérifications** :
  - Rôles sensibles (`admin`, `analyste`) : Création/modification réservée aux superusers.
  - Auto-suppression interdite (`DELETE /api/v1/users/{user_id}`).
  - Validation de `banque_id` dans les transactions (doit être un `client_banque`).

##### **3.3. Rate Limiting**
- **Outil** : **SlowAPI** pour limiter les requêtes.
- **Configuration** :
  - **Global** : Limite générale dans `main.py` (ex. : 10 requêtes/minute pour `/`).
  - **Par endpoint** :
    - `POST /api/v1/users/register` : 5/minute.
    - `POST /api/v1/transactions/add` : 10/minute.
    - `POST /api/v1/alerts/create` : 10/minute.
  - Clé : Adresse IP (`get_remote_address`).
- **Gestion des erreurs** : Retourne `429 Too Many Requests` si la limite est dépassée.

##### **3.4. CORS**
- Configuré dans `main.py` pour autoriser le frontend :
  - Origines : `settings.ALLOWED_ORIGINS` (ex. : `["http://localhost:3000"]`).
  - Méthodes : Toutes (`*`).
  - En-têtes : Tous (`*`).
  - Credentials : Autorisés (`allow_credentials=True`).

##### **3.5. Validation**
- **Schémas Pydantic** :
  - **Email** : Regex strict (`^[\w\.-]+@[\w\.-]+\.\w+$`) dans `schemas/user.py`.
  - **Mot de passe** : Minimum 8 caractères, majuscule, minuscule, chiffre, caractère spécial.
  - **Montant des transactions** : Positif (`transaction_amount > 0`).
  - **Rôles** : Limités via `Enum` (`client_banque`, `admin`, `analyste`).
- **Base de données** : Vérification des contraintes (ex. : unicité de `email`).

##### **3.6. Chiffrement**
- **Mots de passe** : Hashés avec `bcrypt` (via `app/auth/hash.py`).
- **Données sensibles** : Prêtes pour un chiffrement supplémentaire (ex. : `sqlalchemy-encrypted` pour `email` ou `location`).

##### **3.7. Gestion des erreurs**
- **HTTP Exceptions** : Codes d’erreur standards (400, 403, 404, 500).
- **Logs** : Toutes les erreurs sont loguées avec détails (IP, utilisateur, erreur).
- **Alertes** : Générées pour les actions sensibles (ex. : tentative d’inscription avec email existant).

---

#### **4. Routes**
L’API est organisée sous le préfixe `/api/v1` avec des tags pour la documentation.

##### **4.1. Authentification (`/api/v1/auth`)**
- **POST /auth/jwt/login**
  - **Description** : Authentifie un utilisateur et retourne un token JWT.
  - **Permissions** : Aucun (public).
  - **Entrée** : `username` (email), `password` (form-data).
  - **Sortie** : `{ "access_token": "...", "token_type": "bearer" }`.
  - **Logs** : Succès/échec avec IP.
- **POST /auth/register**
  - **Description** : Enregistre un nouvel utilisateur (redondant avec `/users/register`, utilisé pour tests).
  - **Permissions** : Public (mais restreint par logique interne).
  - **Entrée** : `UserCreate` (nom, email, password, role).
  - **Sortie** : `UserRead`.

##### **4.2. Alertes (`/api/v1/alerts`)**
- **POST /create**
  - **Description** : Crée une alerte manuelle.
  - **Permissions** : `admin`, `analyste`.
  - **Entrée** : `AlertCreate` (transaction_id, banque_id, message, etc.).
  - **Sortie** : `AlertRead`.
  - **Logs/Alerts** : Log pour création, alerte si `fraud_probability > 0.8`.
- **GET /all**
  - **Description** : Liste toutes les alertes.
  - **Permissions** : `analyste`, `admin`.
  - **Sortie** : Liste de `AlertRead`.
  - **Logs** : Nombre d’alertes récupérées.
- **GET /banque/{banque_id}**
  - **Description** : Liste les alertes d’une banque.
  - **Permissions** : `client_banque` (propre `banque_id`), `analyste`, `admin`.
  - **Sortie** : Liste de `AlertRead`.
  - **Logs** : Banque ciblée, nombre d’alertes.
- **PATCH /{alert_id}**
  - **Description** : Met à jour une alerte (ex. : status).
  - **Permissions** : `analyste`, `admin`.
  - **Entrée** : `AlertUpdate`.
  - **Sortie** : `AlertRead`.
  - **Logs/Alerts** : Champs modifiés, alerte si status passe à “résolu”.
- **DELETE /{alert_id}**
  - **Description** : Supprime une alerte.
  - **Permissions** : `admin`.
  - **Sortie** : `AlertRead`.
  - **Logs/Alerts** : Log et alerte pour suppression.
- **GET /export**
  - **Description** : Exporte les alertes pour SIEM.
  - **Permissions** : `analyste`, `admin`.
  - **Sortie** : Liste de `AlertRead`.
  - **Logs** : Nombre d’alertes exportées.

##### **4.3. Transactions (`/api/v1/transactions`)**
- **POST /add**
  - **Description** : Ajoute une transaction, détecte la fraude.
  - **Permissions** : `client_banque`, `analyste`, `admin`.
  - **Entrée** : `TransactionCreate` (transaction_id, banque_id, amount, etc.).
  - **Sortie** : `TransactionRead`.
  - **Logs/Alerts** : Log pour ajout, alerte si `fraud_probability > 0.8`.
- **GET /all**
  - **Description** : Liste toutes les transactions.
  - **Permissions** : `analyste`, `admin`.
  - **Sortie** : Liste de `TransactionRead`.
  - **Logs** : Nombre de transactions.
- **GET /banque/{banque_id}**
  - **Description** : Liste les transactions d’une banque.
  - **Permissions** : `client_banque` (propre `banque_id`), `analyste`, `admin`.
  - **Sortie** : Liste de `TransactionRead`.
  - **Logs** : Banque ciblée, nombre de transactions.
- **PATCH /{transaction_id}**
  - **Description** : Met à jour une transaction.
  - **Permissions** : `admin`.
  - **Entrée** : `TransactionUpdate`.
  - **Sortie** : `TransactionRead`.
  - **Logs/Alerts** : Champs modifiés, alerte si fraude détectée après mise à jour.
- **DELETE /{transaction_id}**
  - **Description** : Supprime une transaction.
  - **Permissions** : `admin`.
  - **Sortie** : `TransactionRead`.
  - **Logs/Alerts** : Log et alerte pour suppression.
- **GET /export**
  - **Description** : Exporte les transactions pour SIEM.
  - **Permissions** : `analyste`, `admin`.
  - **Sortie** : Liste de `TransactionRead`.
  - **Logs** : Nombre de transactions exportées.

##### **4.4. Utilisateurs (`/api/v1/users`)**
- **POST /register**
  - **Description** : Crée un utilisateur.
  - **Permissions** : `admin` (superuser).
  - **Entrée** : `UserCreate` (nom, email, password, role).
  - **Sortie** : `UserRead`.
  - **Logs/Alerts** : Log pour création, alerte pour `admin`/`analyste`.
- **GET /me**
  - **Description** : Récupère le profil de l’utilisateur connecté.
  - **Permissions** : Tous les rôles.
  - **Sortie** : `UserRead`.
  - **Logs** : Accès au profil.
- **GET /all**
  - **Description** : Liste tous les utilisateurs.
  - **Permissions** : `analyste`, `admin`.
  - **Sortie** : Liste de `UserRead`.
  - **Logs** : Nombre d’utilisateurs.
- **GET /{user_id}**
  - **Description** : Récupère un utilisateur spécifique.
  - **Permissions** : `client_banque` (propre profil), `analyste`, `admin`.
  - **Sortie** : `UserRead`.
  - **Logs** : Utilisateur ciblé.
- **PATCH /{user_id}**
  - **Description** : Met à jour un utilisateur.
  - **Permissions** : `admin` ou utilisateur lui-même (champs limités).
  - **Entrée** : `UserUpdate`.
  - **Sortie** : `UserRead`.
  - **Logs/Alerts** : Champs modifiés, alerte pour rôle ou superuser.
- **DELETE /{user_id}**
  - **Description** : Supprime un utilisateur.
  - **Permissions** : `admin`.
  - **Sortie** : `UserRead`.
  - **Logs/Alerts** : Log et alerte pour suppression.
- **POST /change-password**
  - **Description** : Change le mot de passe.
  - **Permissions** : Tous les rôles.
  - **Entrée** : `ChangePassword` (current_password, new_password).
  - **Sortie** : Message de succès.
  - **Logs/Alerts** : Log et alerte pour changement.

##### **4.5. Utilitaires**
- **GET /**
  - **Description** : Message de bienvenue.
  - **Permissions** : Public.
  - **Sortie** : `{ "message": "Bienvenue sur l'API BigDefend AI" }`.
- **GET /health**
  - **Description** : Vérifie l’état de l’application.
  - **Permissions** : Public.
  - **Sortie** : `{ "status": "healthy", "database": "ok", "logger": "ok" }`.
  - **Logs** : Statut de santé.

---

#### **5. Logs**
Les logs sont un élément central pour l’audit et l’intégration SIEM.

##### **5.1. Configuration**
- **Outil** : Python `logging` avec un handler personnalisé (`MongoDBHandler`).
- **Stockage** : MongoDB (`mongodb://mongodb:27017/bigdefend`, collection `logs`).
- **Console** : Logs également affichés dans la console pour le développement.
- **Fichier** : `app/logging/log_setup.py` et `app/logging/mongodb_logger.py`.

##### **5.2. Structure des logs**
- **Champs** :
  - `timestamp` : Date/heure de l’événement.
  - `level` : Niveau (`INFO`, `WARNING`, `ERROR`).
  - `message` : Description de l’événement.
  - `extra` : Détails structurés :
    - `category` : Type d’événement (`system`, `http`, `user_management`, `transaction`, `alert`, `error`).
    - `user_id` : ID de l’utilisateur (via JWT).
    - `role` : Rôle de l’utilisateur.
    - `ip_address` : Adresse IP du client.
    - `details` : Informations spécifiques (ex. : `transaction_id`, `fraud_score`).
- **Exemple** :
  ```json
  {
    "timestamp": 1623456789.123,
    "level": "INFO",
    "message": "Transaction processed successfully",
    "extra": {
      "category": "transaction",
      "user_id": 1,
      "role": "client_banque",
      "ip_address": "127.0.0.1",
      "details": {
        "transaction_id": "123",
        "fraud_score": 0.85,
        "is_fraud": true
      }
    }
  }
  ```

##### **5.3. Événements logués**
- **Système** : Démarrage/arrêt de l’application, santé (`/health`).
- **HTTP** : Toutes les requêtes (méthode, URL, statut, IP).
- **Utilisateurs** : Inscription, connexion, mise à jour, suppression, changement de mot de passe.
- **Transactions** : Ajout, consultation, mise à jour, suppression, export.
- **Alertes** : Création, consultation, mise à jour, suppression, export.
- **Erreurs** : Exceptions, tentatives non autorisées, validations échouées.

##### **5.4. Intégration SIEM**
- Les logs sont structurés pour une analyse dans Elasticsearch/Kibana.
- Export possible via un futur endpoint `/api/v1/logs/export` (voir recommandations).

---

#### **6. Alertes**
Les alertes sont utilisées pour signaler des événements suspects ou sensibles.

##### **6.1. Modèle**
- **Table** : `alerts` (PostgreSQL, `app/models/alert.py`).
- **Champs** :
  - `id` : Clé primaire.
  - `transaction_id` : ID de la transaction liée (nullable).
  - `banque_id` : ID de la banque (nullable).
  - `fraud_probability` : Probabilité de fraude (0 à 1).
  - `message` : Description de l’alerte.
  - `status` : État (`non traité`, `en cours`, `résolu`).
  - `date` : Date de création.

##### **6.2. Génération**
- **Automatique** :
  - **Transactions** : Si `fraud_probability > 0.8` dans `POST /api/v1/transactions/add` ou `PATCH /api/v1/transactions/{id}`.
  - **Utilisateurs** : Tentative d’inscription avec email existant, création d’`admin`/`analyste`, changement de rôle, suppression, changement de mot de passe.
- **Manuelle** : Via `POST /api/v1/alerts/create`.
- **Exemple** :
  ```json
  {
    "transaction_id": 1,
    "banque_id": 2,
    "fraud_probability": 0.89,
    "message": "Transaction suspecte détectée avec une probabilité de 0.89",
    "status": "non traité",
    "date": "2025-06-11T22:30:00"
  }
  ```

##### **6.3. Gestion**
- **Consultation** : `GET /api/v1/alerts/all`, `GET /api/v1/alerts/banque/{banque_id}`.
- **Mise à jour** : `PATCH /api/v1/alerts/{alert_id}` (ex. : changer `status`).
- **Suppression** : `DELETE /api/v1/{alert_id}`.
- **Export** : `GET /api/v1/alerts/export` pour SIEM.

##### **6.4. Logs associés**
- Chaque création, mise à jour, ou suppression d’alerte génère un log avec `category: "alert"`.

---

#### **8. Installation et Configuration**
1. **Pré-requis** :
   - Python 3.9+
   - Docker, Docker Compose
   - PostgreSQL, MongoDB (via Docker)

2. **Installation** :
   ```powershell
   git clone <repository>
   cd bdia-BackEND
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Configurer .env** :
   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"  # Copier la clé
   echo "SECRET_KEY=your_key_here" > .env
   echo "DATABASE_URL=postgresql://admin:secret@postgres:5432/bigdefend" >> .env
   echo "MONGO_URI=mongodb://mongodb:27017/bigdefend" >> .env
   echo "ALLOWED_ORIGINS=[\"http://localhost:3000\"]" >> .env
   ```

4. **Docker Compose** :
   ```yaml
   version: '3.8'
   services:
     postgres:
       image: postgres:13
       environment:
         POSTGRES_USER: admin
         POSTGRES_PASSWORD: secret
         POSTGRES_DB: bigdefend
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
     mongodb:
       image: mongo:5
       ports:
         - "27017:27017"
       volumes:
         - mongo_data:/data/db
   volumes:
     postgres_data:
     mongo_data:
   ```

5. **Lancer** :
   ```powershell
   docker-compose up -d
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

#### **9. Tests**
1. **Vérifier l’API** :
   ```powershell
   curl http://localhost:8000/  # {"message": "Bienvenue sur l'API BigDefend AI"}
   curl http://localhost:8000/health  # {"status": "healthy", ...}
   ```

2. **Créer un admin** :
   ```powershell
   docker exec -it postgres psql -U admin -d bigdefend -c "INSERT INTO users (email, hashed_password, nom, role, is_active, is_superuser, is_verified) VALUES ('admin@example.com', '$(python -c \"import bcrypt; print(bcrypt.hashpw(b'Admin123!', bcrypt.gensalt()).decode())\")', 'Admin', 'admin', true, true, true);"
   ```

3. **Obtenir un token** :
   ```powershell
   curl -X POST "http://localhost:8000/api/v1/auth/jwt/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin@example.com&password=Admin123!"
   ```

4. **Exemples d’appels** :
   - **Utilisateur** : `POST /api/v1/users/register`, `GET /api/v1/users/me`.
   - **Transaction** : `POST /api/v1/transactions/add`, `GET /api/v1/transactions/all`.
   - **Alerte** : `POST /api/v1/alerts/create`, `GET /api/v1/alerts/export`.

5. **Vérifier les logs** :
   ```powershell
   docker exec -it mongodb mongosh --eval 'db.logs.find().pretty()'
   ```

---

#### **10. Recommandations**
1. **Frontend** :
   - Utiliser `axios` pour appeler les endpoints :
     ```javascript
     import axios from 'axios';
     const api = axios.create({
       baseURL: 'http://localhost:8000/api/v1',
       headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
     });
     ```

2. **SIEM** :
   - Préparer l’intégration Elasticsearch/Kibana avant de passer à la phase suivante.

3. **Déploiement** :
   - Utiliser Nginx comme reverse proxy.
   - Héberger sur AWS/GCP/Heroku.

4. **Tests** :
   - Ajouter des tests unitaires avec `pytest`.

5. **Sécurité** :
   - Implémenter `sqlalchemy-encrypted` pour les données sensibles.
   - Ajouter un MFA pour les `admin`.

---

### **Explications supplémentaires**
- **Détail** : Chaque section est exhaustive pour répondre aux besoins académiques et professionnels.
- **Format** : Markdown pour une intégration facile dans un `README.md` ou une documentation web.
- **Cohérence** : Intègre tous les fichiers précédents (`main.py`, `user.py`, `transaction.py`, `alerts.py`).
- **Prochaines étapes** : Tu peux maintenant passer à l’intégration SIEM (Elasticsearch/Kibana) ou au frontend. Dis-moi si tu veux une documentation spécifique pour ces parties !
