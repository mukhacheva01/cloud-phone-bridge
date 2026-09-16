from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.adapters.mock import mock_adapter
from app.schemas import ConnectionInfo, JobAccepted, Phone, PhoneIdsRequest
from app.store import store

api_router = APIRouter()


def submit_job(operation: str, payload: PhoneIdsRequest, idempotency_key: str) -> JobAccepted:
    missing = [phone_id for phone_id in payload.phone_ids if phone_id not in store.phones]
    if missing:
        raise HTTPException(status_code=400, detail={"code": "UNKNOWN_PHONE", "phone_ids": missing})
    job = store.create_job(operation, payload.phone_ids, idempotency_key)
    store.apply_operation(job["job_id"])
    return JobAccepted(job_id=job["job_id"], status=job["status"])


@api_router.get("/phones", response_model=list[Phone])
async def list_phones(status_filter: str | None = None) -> list[Phone]:
    phones = list(store.phones.values())
    if status_filter:
        phones = [phone for phone in phones if phone["status"] == status_filter]
    return [Phone(**phone) for phone in phones]


@api_router.get("/phones/{phone_id}", response_model=Phone)
async def get_phone(phone_id: UUID) -> Phone:
    phone = store.phones.get(phone_id)
    if not phone:
        raise HTTPException(status_code=404, detail="Phone not found")
    return Phone(**phone)


@api_router.post("/phones/batch-start", response_model=JobAccepted, status_code=status.HTTP_202_ACCEPTED)
async def batch_start(payload: PhoneIdsRequest, idempotency_key: str = Header(min_length=8, max_length=128)) -> JobAccepted:
    return submit_job("start", payload, idempotency_key)


@api_router.post("/phones/batch-stop", response_model=JobAccepted, status_code=status.HTTP_202_ACCEPTED)
async def batch_stop(payload: PhoneIdsRequest, idempotency_key: str = Header(min_length=8, max_length=128)) -> JobAccepted:
    return submit_job("stop", payload, idempotency_key)


@api_router.post("/phones/connection-info", response_model=list[ConnectionInfo])
async def connection_info(payload: PhoneIdsRequest) -> list[ConnectionInfo]:
    result = []
    for phone_id in payload.phone_ids:
        phone = store.phones.get(phone_id)
        if not phone:
            raise HTTPException(status_code=404, detail=f"Phone {phone_id} not found")
        info = (await mock_adapter.get_connection_info([phone["vendor_id"]]))[0]
        result.append(ConnectionInfo(phone_id=phone_id, **info))
    return result


@api_router.get("/jobs/{job_id}")
async def get_job(job_id: UUID) -> dict[str, object]:
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
