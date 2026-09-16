from datetime import datetime, timezone
from threading import Lock
from uuid import UUID, uuid4


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryStore:
    def __init__(self) -> None:
        self.lock = Lock()
        self.phones: dict[UUID, dict[str, object]] = {}
        self.jobs: dict[UUID, dict[str, object]] = {}
        self.idempotency: dict[str, UUID] = {}
        self.seed(100)

    def seed(self, count: int) -> None:
        for index in range(1, count + 1):
            phone_id = UUID(int=index)
            self.phones[phone_id] = {
                "phone_id": phone_id,
                "vendor": "mock",
                "vendor_id": f"mock-{index:03d}",
                "status": "stopped",
                "adb_status": "offline",
                "tags": ["demo"],
                "updated_at": now(),
            }

    def create_job(self, operation: str, phone_ids: list[UUID], key: str) -> dict[str, object]:
        with self.lock:
            existing = self.idempotency.get(key)
            if existing:
                return self.jobs[existing]
            job_id = uuid4()
            job = {
                "job_id": job_id,
                "operation": operation,
                "status": "queued",
                "created_at": now(),
                "updated_at": now(),
                "items": [
                    {"phone_id": phone_id, "status": "queued", "error": None}
                    for phone_id in phone_ids
                ],
            }
            self.jobs[job_id] = job
            self.idempotency[key] = job_id
            return job

    def get_job(self, job_id: UUID) -> dict[str, object] | None:
        return self.jobs.get(job_id)

    def apply_operation(self, job_id: UUID) -> dict[str, object]:
        with self.lock:
            job = self.jobs[job_id]
            job["status"] = "running"
            for item in job["items"]:
                phone = self.phones.get(item["phone_id"])
                if not phone:
                    item.update(status="failed", error={"code": "NOT_FOUND", "message": "Phone not found"})
                    continue
                item["status"] = "running"
                target = "running" if job["operation"] == "start" else "stopped"
                phone["status"] = target
                phone["adb_status"] = "online" if target == "running" else "offline"
                phone["updated_at"] = now()
                item["status"] = "succeeded"
            failed = sum(item["status"] == "failed" for item in job["items"])
            job["status"] = "failed" if failed == len(job["items"]) else "partially_succeeded" if failed else "succeeded"
            job["updated_at"] = now()
            return job


store = MemoryStore()
