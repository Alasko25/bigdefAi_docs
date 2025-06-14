import pytest
from pymongo import MongoClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_login_success(client, admin_user, mock_elasticsearch):
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "admin@example.com", "password": "Admin123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    mock_elasticsearch.index.assert_called_once()

@pytest.mark.asyncio
async def test_login_invalid_password(client, admin_user):
    response = await client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "admin@example.com", "password": "WrongPass!"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_user(client, admin_token, mock_elasticsearch):
    user_data = {
        "nom": "Banque B",
        "email": "banque2@example.com",
        "password": "Banque123!",
        "role": "client_banque"
    }
    response = await client.post(
        "/api/v1/users/register",
        json=user_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "banque2@example.com"
    mock_elasticsearch.index.assert_called_once()

@pytest.mark.asyncio
async def test_register_analyste(client, admin_token, mock_elasticsearch):
    user_data = {
        "nom": "Analyste Y",
        "email": "analyste2@example.com",
        "password": "Analyste123!",
        "role": "analyste"
    }
    response = await client.post(
        "/api/v1/users/register",
        json=user_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    mock_elasticsearch.index.assert_called()

@pytest.mark.asyncio
async def test_register_unauthorized(client, client_banque_token):
    user_data = {
        "nom": "Analyste Z",
        "email": "analyste3@example.com",
        "password": "Analyste123!",
        "role": "analyste"
    }
    response = await client.post(
        "/api/v1/users/register",
        json=user_data,
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 403
    assert "Seuls les superusers peuvent créer" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_me(client, admin_token):
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@example.com"

@pytest.mark.asyncio
async def test_get_all_users(client, analyste_token):
    response = await client.get(
        "/api/v1/users/all",
        headers={"Authorization": f"Bearer {analyste_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_all_users_unauthorized(client, client_banque_token):
    response = await client.get(
        "/api/v1/users/all",
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 403
    assert "Seuls les analystes et admins" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_user(client, admin_token, client_banque_user, mock_elasticsearch):
    update_data = {"nom": "Banque A Modifiée"}
    response = await client.patch(
        f"/api/v1/users/{client_banque_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["nom"] == "Banque A Modifiée"
    mock_elasticsearch.index.assert_called()

@pytest.mark.asyncio
async def test_delete_user(client, admin_token, client_banque_user, mock_elasticsearch):
    response = await client.delete(
        f"/api/v1/users/{client_banque_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    mock_elasticsearch.index.assert_called()

@pytest.mark.asyncio
async def test_change_password(client, client_banque_token, mock_elasticsearch):
    password_data = {
        "current_password": "Banque123!",
        "new_password": "NewPass123!"
    }
    response = await client.post(
        "/api/v1/users/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Mot de passe changé avec succès"
    mock_elasticsearch.index.assert_called()