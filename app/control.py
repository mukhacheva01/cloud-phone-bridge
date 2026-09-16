import json
from datetime import datetime, timezone
from uuid import UUID

from redis import Redis

from app.config import get_settings
from app.store import store

redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
LOCK_TTL = 120


def acquire_phone_locks(phone_ids: list[UUID], owner: str) -> list[str]:
    acquired: list[str] = []
    for phone_id in sorted(phone_ids, key=str):
        key = f"bridge:lock:phone:{phone_id}"
        if redis.set(key, owner, nx=True, ex=LOCK_TTL):
            acquired.append(key)
        else:
            for item in acquired:
                redis.delete(item)
            raise RuntimeError(f"Phone is busy: {phone_id}")
    return acquired


def release_phone_locks(keys: list[str]) -> None:
    for key in keys:
        redis.delete(key)


def retry_job(job_id: UUID) -> dict[str, object]:
    job = store.get_job(job_id)
    if not job:
        raise KeyError("Job not found")
    job["status"] = "queued"
    job["next_retry_at"] = None
    job["last_error"] = None
    for item in job["items"]:
        if item["status"] == "failed":
            item["status"] = "queued"
            item["error"] = None
    return store.save_job(job)
