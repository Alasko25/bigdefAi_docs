# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_transaction_endpoint():
    response = client.post("/transaction", json={"amount": 1000, "currency": "USD"})
    assert response.status_code == 200