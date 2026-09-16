from uuid import UUID

from celery import Celery

from app.config import get_settings
from app.store import store

settings = get_settings()
celery_app = Celery("cloud_phone_bridge", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
)


@celery_app.task(
    name="phones.execute_operation",
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def execute_phone_operation(job_id: str) -> dict[str, object]:
    return store.apply_operation(UUID(job_id))


def enqueue_phone_operation(job_id: UUID) -> None:
    execute_phone_operation.delay(str(job_id))
