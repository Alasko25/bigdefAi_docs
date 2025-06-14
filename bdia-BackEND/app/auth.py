from fastapi_users.authentication import JWTAuthentication, AuthenticationBackend
from fastapi_users import FastAPIUsers

SECRET = "votre-secret-super-secret"  # Changez ceci pour un vrai secret en production

# Configuration JWT
jwt_authentication = JWTAuthentication(
    secret=SECRET,
    lifetime_seconds=3600,
    tokenUrl="auth/jwt/login"
)

# Créez un backend d'authentification
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=None,
    get_strategy=lambda: jwt_authentication,
)

fastapi_users = FastAPIUsers(
    get_user_manager,
    [auth_backend],  # Passez le backend ici, pas la stratégie directement
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)