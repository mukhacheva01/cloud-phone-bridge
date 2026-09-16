import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from redis import Redis

from app.config import get_settings

redis = Redis.from_url(get_settings().redis_url, decode_responses=True)
AUDIT_KEY = "bridge:audit"


def record_event(action: str, actor: str, resource: str, resource_id: UUID | str, metadata: dict[str, object] | None = None) -> str:
    event_id = str(uuid4())
    event = {"event_id": event_id, "timestamp": datetime.now(timezone.utc).isoformat(), "action": action, "actor": actor, "resource": resource, "resource_id": str(resource_id), "metadata": metadata or {}}
    redis.lpush(AUDIT_KEY, json.dumps(event))
    redis.ltrim(AUDIT_KEY, 0, 9999)
    return event_id


def list_events(limit: int = 50) -> list[dict[str, object]]:
    return [json.loads(item) for item in redis.lrange(AUDIT_KEY, 0, max(0, min(limit, 200) - 1))]
