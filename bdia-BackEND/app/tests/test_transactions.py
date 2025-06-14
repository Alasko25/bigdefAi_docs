import pytest
from pymongo import MongoClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_add_transaction(client, client_banque_token, client_banque_user, mock_fraud_detection):
    mock_fraud_detection.return_value = 0.9
    transaction_data = {
        "transaction_id": "TX456",
        "banque_id": client_banque_user.id,
        "transaction_amount": 2000.0,
        "location": "Paris"
    }
    response = await client.post(
        "/api/v1/transactions/add",
        json=transaction_data,
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_fraud"] == True
    # Vérifier l'alerte
    mongo_client = MongoClient(settings.MONGO_URI)
    log = mongo_client.test_bigdefend.logs.find_one({"extra.category": "alert"})
    assert log
    assert "Transaction suspecte détectée" in log["message"]

@pytest.mark.asyncio
async def test_add_transaction_unauthorized_banque(client, client_banque_token, admin_user):
    transaction_data = {
        "transaction_id": "TX789",
        "banque_id": admin_user.id,
        "transaction_amount": 2000.0,
        "location": "Paris"
    }
    response = await client.post(
        "/api/v1/transactions/add",
        json=transaction_data,
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 403
    assert "Banque ID invalide" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_all_transactions(client, analyste_token):
    response = await client.get(
        "/api/v1/transactions/all",
        headers={"Authorization": f"Bearer {analyste_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_transactions_by_banque(client, client_banque_token, client_banque_user):
    response = await client.get(
        f"/api/v1/transactions/banque/{client_banque_user.id}",
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_transaction(client, admin_token, transaction):
    update_data = {"transaction_amount": 3000.0}
    response = await client.patch(
        f"/api/v1/transactions/{transaction.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["transaction_amount"] == 3000.0

@pytest.mark.asyncio
async def test_delete_transaction(client, admin_token, transaction):
    response = await client.delete(
        f"/api/v1/transactions/{transaction.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    # Vérifier l'alerte
    mongo_client = MongoClient(settings.MONGO_URI)
    log = mongo_client.test_bigdefend.logs.find_one({"extra.category": "alert"})
    assert log
    assert "Transaction supprimée" in log["message"]

@pytest.mark.asyncio
async def test_export_transactions(client, analyste_token):
    response = await client.get(
        "/api/v1/transactions/export",
        headers={"Authorization": f"Bearer {analyste_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)