from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


PHONE_IDS = [str(UUID(int=index)) for index in range(1, 101)]


def test_seeded_inventory_has_100_phones() -> None:
    with TestClient(app) as client:
        response = client.get("/v1/phones")
    assert response.status_code == 200
    assert len(response.json()) == 100


def test_batch_start_stop_and_idempotency() -> None:
    with TestClient(app) as client:
        start = client.post(
            "/v1/phones/batch-start",
            headers={"Idempotency-Key": "test-start-001"},
            json={"phone_ids": PHONE_IDS},
        )
        assert start.status_code == 202
        assert start.json()["status"] == "succeeded"
        job_id = start.json()["job_id"]

        repeated = client.post(
            "/v1/phones/batch-start",
            headers={"Idempotency-Key": "test-start-001"},
            json={"phone_ids": PHONE_IDS},
        )
        assert repeated.json()["job_id"] == job_id

        job = client.get(f"/v1/jobs/{job_id}")
        assert job.status_code == 200
        assert len(job.json()["items"]) == 100
        assert all(item["status"] == "succeeded" for item in job.json()["items"])

        running = client.get("/v1/phones?status_filter=running")
        assert len(running.json()) == 100

        stop = client.post(
            "/v1/phones/batch-stop",
            headers={"Idempotency-Key": "test-stop-001"},
            json={"phone_ids": PHONE_IDS},
        )
        assert stop.status_code == 202
        assert stop.json()["status"] == "succeeded"
