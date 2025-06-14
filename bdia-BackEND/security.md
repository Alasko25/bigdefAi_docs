# Politique de sécurité - BigDefend AI Backend

## 1. Authentification
- **Méthode** : JSON Web Tokens (JWT) avec OAuth2.
- **Implémentation** : 
  - Endpoint `/auth/token` pour générer des tokens.
  - Vérification des tokens via `python-jose` et `fastapi-jwt-auth`.
  - Secret stocké dans `.env` (JWT_SECRET_KEY).
- **Rôles** : Restriction d’accès basée sur `banque_id` (ex. : seules les banques peuvent voir leurs transactions).

## 2. Autorisation
- **Règles** :
  - Les endpoints `/transactions/*` exigent un token JWT valide.
  - `/transactions/banque/{banque_id}` est limité à l’utilisateur lié à `banque_id`.
- **Implémentation** : Vérification dans `jwt_handler.py`.

## 3. Sécurisation des communications
- **HTTPS** : Certificat SSL via Nginx (Let’s Encrypt en production).
- **CORS** : Limité aux origines du frontend (`https://frontend.bigdefend.ai`).
- **Secrets** : Stockés dans `.env` (ex. : JWT_SECRET_KEY, DATABASE_URL).

## 4. Bases de données
- **PostgreSQL** :
  - Utilisateur non-root (`app_user`) avec permissions limitées.
  - Connexion SSL activée (`sslmode=require`).
- **MongoDB** :
  - Authentification activée avec utilisateur `admin`.
  - Connexion via URI sécurisée.
- **Elasticsearch** :
  - Sécurité X-Pack activée avec mot de passe pour l’utilisateur `elastic`.

## 5. Protection contre les attaques
- **Rate Limiting** : À implémenter avec `slowapi`.
- **Validation** : Schémas Pydantic pour filtrer les entrées.
- **Injection SQL** : Requêtes paramétrées via SQLAlchemy.

## 6. Prochaines étapes
- Intégrer un SIEM (ex. : Wazuh) pour la détection des intrusions.
- Automatiser les backups avec `pg_dump` et `mongodump`.
- Implémenter un gestionnaire de secrets (ex. : AWS Secrets Manager).