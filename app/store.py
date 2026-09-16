import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from redis import Redis

from app.config import get_settings

settings = get_settings()
redis = Redis.from_url(settings.redis_url, decode_responses=True)
PHONES_KEY = "bridge:phones"
JOBS_KEY = "bridge:jobs"
IDEMPOTENCY_PREFIX = "bridge:idempotency:"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class RedisStore:
    def __init__(self) -> None:
        self.ensure_seeded()

    def ensure_seeded(self) -> None:
        if redis.exists(PHONES_KEY):
            return
        pipe = redis.pipeline()
        for index in range(1, 101):
            phone_id = str(UUID(int=index))
            pipe.hset(PHONES_KEY, phone_id, json.dumps({
                "phone_id": phone_id, "vendor": "mock", "vendor_id": f"mock-{index:03d}",
                "status": "stopped", "adb_status": "offline", "tags": ["demo"], "updated_at": now(),
            }))
        pipe.execute()

    def phones(self) -> list[dict[str, object]]:
        return [json.loads(value) for value in redis.hvals(PHONES_KEY)]

    def get_phone(self, phone_id: UUID) -> dict[str, object] | None:
        value = redis.hget(PHONES_KEY, str(phone_id))
        return json.loads(value) if value else None

    def create_job(self, operation: str, phone_ids: list[UUID], key: str) -> dict[str, object]:
        existing = redis.get(IDEMPOTENCY_PREFIX + key)
        if existing:
            return self.get_job(UUID(existing))  # type: ignore[return-value]
        job_id = uuid4()
        job = {
            "job_id": str(job_id), "operation": operation, "status": "queued",
            "created_at": now(), "updated_at": now(), "attempts": 0,
            "items": [{"phone_id": str(phone_id), "status": "queued", "attempts": 0, "error": None} for phone_id in phone_ids],
        }
        pipe = redis.pipeline()
        pipe.set(IDEMPOTENCY_PREFIX + key, str(job_id), nx=True)
        pipe.hset(JOBS_KEY, str(job_id), json.dumps(job))
        result = pipe.execute()
        if not result[0]:
            return self.get_job(UUID(redis.get(IDEMPOTENCY_PREFIX + key)))  # type: ignore[arg-type,return-value]
        return job

    def get_job(self, job_id: UUID) -> dict[str, object] | None:
        value = redis.hget(JOBS_KEY, str(job_id))
        return json.loads(value) if value else None

    def save_job(self, job: dict[str, object]) -> dict[str, object]:
        job["updated_at"] = now()
        redis.hset(JOBS_KEY, str(job["job_id"]), json.dumps(job))
        return job

    def apply_operation(self, job_id: UUID) -> dict[str, object]:
        job = self.get_job(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        job["status"] = "running"
        job["attempts"] = int(job.get("attempts", 0)) + 1
        for item in job["items"]:  # type: ignore[union-attr]
            phone = self.get_phone(UUID(item["phone_id"]))  # type: ignore[index]
            if not phone:
                item.update(status="failed", error={"code": "NOT_FOUND", "message": "Phone not found", "retryable": False})  # type: ignore[union-attr]
                continue
            target = "running" if job["operation"] == "start" else "stopped"
            phone.update(status=target, adb_status="online" if target == "running" else "offline", updated_at=now())
            redis.hset(PHONES_KEY, str(phone["phone_id"]), json.dumps(phone))
            item.update(status="succeeded", attempts=int(item.get("attempts", 0)) + 1, error=None)  # type: ignore[union-attr]
        failed = sum(item["status"] == "failed" for item in job["items"])  # type: ignore[index]
        job["status"] = "failed" if failed == len(job["items"]) else "partially_succeeded" if failed else "succeeded"  # type: ignore[arg-type]
        return self.save_job(job)


store = RedisStore()
