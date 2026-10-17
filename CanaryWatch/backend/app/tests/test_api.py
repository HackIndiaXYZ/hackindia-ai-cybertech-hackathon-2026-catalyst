import os
os.environ["DATABASE_URL"] = "sqlite:///./test_canarywatch.db"
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine

client = TestClient(app)

def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def test_health():
    assert client.get("/api/v1/health").status_code == 200

def test_create_trigger_and_rotate():
    created = client.post("/api/v1/honeytokens", json={
        "name": "Test canary", "kind": "API credential", "environment": "test", "severity": "high"
    })
    assert created.status_code == 200
    token = created.json()
    assert token["status"] == "active"
    triggered = client.post(f"/api/v1/demo/trigger/{token['id']}")
    assert triggered.status_code == 200
    assert triggered.json()["incident"]["severity"] == "high"
    assert client.post(f"/api/v1/demo/trigger/{token['id']}").status_code == 409
    rotated = client.post(f"/api/v1/honeytokens/{token['id']}/rotate")
    assert rotated.status_code == 200
    assert rotated.json()["rotation_of"] == token["id"]

def test_unknown_token():
    assert client.post("/api/v1/demo/trigger/not-real").status_code == 404
