from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


def test_batch_contract_accepts_100_devices() -> None:
    ids = [str(UUID(int=i)) for i in range(1, 101)]
    with TestClient(app) as client:
        response = client.post("/v1/phones/batch-start", headers={"Idempotency-Key": "load-smoke-100"}, json={"phone_ids": ids})
    assert response.status_code == 202
    assert response.json()["status"] == "queued"
