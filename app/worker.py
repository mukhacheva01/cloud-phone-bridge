from uuid import UUID

from celery import Celery

from app.config import get_settings

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
def execute_phone_operation(
    job_id: str,
    operation: str,
    phone_ids: list[str],
    idempotency_key: str,
) -> dict[str, object]:
    # TODO: resolve phones, group by vendor, chunk calls and persist per-item results.
    return {
        "job_id": job_id,
        "operation": operation,
        "phone_ids": phone_ids,
        "idempotency_key": idempotency_key,
        "status": "queued",
    }


def enqueue_phone_operation(
    job_id: UUID,
    operation: str,
    phone_ids: list[UUID],
    idempotency_key: str,
) -> None:
    execute_phone_operation.delay(
        str(job_id), operation, [str(phone_id) for phone_id in phone_ids], idempotency_key
    )
