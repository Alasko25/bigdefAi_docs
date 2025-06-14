import pytest
from app.logging.log_setup import logger

@pytest.mark.asyncio
async def test_add_credit_card_transaction(client, client_banque_token, mock_fraud_model, mock_elasticsearch):
    transaction_data = {
        "time": 123456.0,
        "v1": -1.359807, "v2": -0.072781, "v3": 2.536346, "v4": 1.378155,
        "v5": -0.338321, "v6": 0.462388, "v7": 0.239599, "v8": 0.098698,
        "v9": 0.363787, "v10": 0.090794, "v11": -0.551600, "v12": -0.617801,
        "v13": -0.991390, "v14": -0.311169, "v15": 1.468177, "v16": -0.470401,
        "v17": 0.207971, "v18": 0.025791, "v19": 0.403993, "v20": 0.251412,
        "v21": -0.018307, "v22": 0.277838, "v23": -0.110474, "v24": 0.066928,
        "v25": 0.128539, "v26": -0.189115, "v27": 0.133558, "v28": -0.021053,
        "amount": 149.62
    }
    response = await client.post(
        "/api/v1/credit_card_transactions/add",
        json=transaction_data,
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["amount"] == 149.62
    assert response.json()["is_fraud"] == True  # Simulé par mock_fraud_model
    # Vérifier le log Elasticsearch (mock)
    mock_elasticsearch.index.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_credit_card_transactions(client, analyste_token, credit_card_transaction, mock_elasticsearch):
    response = await client.get(
        "/api/v1/credit_card_transactions/",
        headers={"Authorization": f"Bearer {analyste_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["amount"] == 149.62
    mock_elasticsearch.index.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_credit_card_transactions_unauthorized(client, client_banque_token):
    response = await client.get(
        "/api/v1/credit_card_transactions/",
        headers={"Authorization": f"Bearer {client_banque_token}"}
    )
    assert response.status_code == 403
    assert "Seuls les analystes et admins" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_credit_card_transaction(client, admin_token, credit_card_transaction, mock_fraud_model, mock_elasticsearch):
    update_data = {"amount": 200.0, "is_fraud": True}
    response = await client.patch(
        f"/api/v1/credit_card_transactions/{credit_card_transaction.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 200.0
    assert response.json()["is_fraud"] == True
    mock_elasticsearch.index.assert_called()

@pytest.mark.asyncio
async def test_delete_credit_card_transaction(client, admin_token, credit_card_transaction, mock_elasticsearch):
    response = await client.delete(
        f"/api/v1/credit_card_transactions/{credit_card_transaction.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 149.62
    mock_elasticsearch.index.assert_called()

@pytest.mark.asyncio
async def test_export_credit_card_transactions(client, analyste_token, credit_card_transaction, mock_elasticsearch):
    response = await client.get(
        "/api/v1/credit_card_transactions/export",
        headers={"Authorization": f"Bearer {analyste_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["amount"] == 149.62
    mock_elasticsearch.index.assert_called()