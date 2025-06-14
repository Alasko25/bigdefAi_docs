import pytest
from pymongo import MongoClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_create_alert(client, admin_token, client_banque_user):
    alert_data = {
        "transaction_id": None,
        "banque_id": client_banque_user.id,
        "fraud_probability": 0.7,
        "message": "Alerte manuelle",
        "status": "non traité"
    }
    response = await client.post(
        "/api/v1/alerts/create",
        json=alert_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Alerte manuelle"
    # Vérifier le log
    mongo_client = MongoClient(settings.MONGO_URI)
    log = mongo_client.test_bigdefend.logs.find_one({"extra.category": "alert"})
    assert log
    assert "Alerte créée" in log["message"]

@pytest.mark.asyncio
async def test_get_all_alerts(client, analyste_token):
    response = await client.get(
        "/api/v1/alerts/all",
        headers={"Authorization": f"Bearer {analyste_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_alerts_by_banque(client, client_banque_token, client_banque_user):
    response = await client.get(
        f"/api/v1/alerts/banque/{client_banque_user.id}",
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_alert(client, admin_token, alert):
    update_data = {"status": "résolu"}
    response = await client.patch(
        f"/api/v1/alerts/{alert.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "résolu"

@pytest.mark.asyncio
async def test_delete_alert(client, admin_token, alert):
    response = await client.delete(
        f"/api/v1/alerts/{alert.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    # Vérifier l'alerte
    mongo_client = MongoClient(settings.MONGO_URI)
    log = mongo_client.test_bigdefend.logs.find_one({"extra.category": "alert"})
    assert log
    assert "Alerte supprimée" in log["message"]

@pytest.mark.asyncio
async def test_export_alerts(client, analyste_token):
    response = await client.get(
        "/api/v1/alerts/export",
        headers={"Authorization": f"Bearer {analyste_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)