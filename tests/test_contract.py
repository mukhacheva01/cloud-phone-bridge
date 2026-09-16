from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


PHONE_ID = str(UUID(int=1))


def test_batch_requires_idempotency_key() -> None:
    with TestClient(app) as client:
        response = client.post("/v1/phones/batch-start", json={"phone_ids": [PHONE_ID]})
    assert response.status_code == 422


def test_batch_returns_queued_job() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/phones/batch-start",
            headers={"Idempotency-Key": "contract-test-001"},
            json={"phone_ids": [PHONE_ID]},
        )
    assert response.status_code == 202
    assert response.json()["status"] == "queued"


def test_connection_info_is_enveloped() -> None:
    with TestClient(app) as client:
        response = client.post("/v1/phones/connection-info", json={"phone_ids": [PHONE_ID]})
    assert response.status_code == 200
    assert isinstance(response.json()["items"], list)
