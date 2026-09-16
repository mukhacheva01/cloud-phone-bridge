from uuid import UUID, uuid4

from fastapi import APIRouter, Header, status

from app.schemas import JobAccepted, PhoneIdsRequest
from app.worker import enqueue_phone_operation

api_router = APIRouter()


async def submit_job(
    operation: str,
    payload: PhoneIdsRequest,
    idempotency_key: str,
) -> JobAccepted:
    job_id = uuid4()
    enqueue_phone_operation(job_id, operation, payload.phone_ids, idempotency_key)
    return JobAccepted(job_id=job_id)


@api_router.post(
    "/phones/batch-start",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def batch_start(
    payload: PhoneIdsRequest,
    idempotency_key: str = Header(min_length=8, max_length=128),
) -> JobAccepted:
    return await submit_job("start", payload, idempotency_key)


@api_router.post(
    "/phones/batch-stop",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
)
async def batch_stop(
    payload: PhoneIdsRequest,
    idempotency_key: str = Header(min_length=8, max_length=128),
) -> JobAccepted:
    return await submit_job("stop", payload, idempotency_key)


@api_router.get("/jobs/{job_id}")
async def get_job(job_id: UUID) -> dict[str, str]:
    return {"job_id": str(job_id), "status": "queued"}
