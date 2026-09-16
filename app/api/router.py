from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.adapters.mock import mock_adapter
from app.config import get_settings
from app.schemas import ConnectionInfoResponse, JobAccepted, JobResponse, Phone, PhoneIdsRequest
from app.store import store
from app.worker import enqueue_phone_operation

api_router = APIRouter()
settings = get_settings()


def require_auth(authorization: str | None) -> None:
    expected = f"Bearer {settings.api_bearer_token}"
    if settings.app_env == "development" and settings.api_bearer_token == "change-me":
        return
    if authorization != expected:
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Invalid bearer token"})


def submit_job(operation: str, payload: PhoneIdsRequest, key: str, authorization: str | None) -> JobAccepted:
    require_auth(authorization)
    missing = [phone_id for phone_id in payload.phone_ids if not store.get_phone(phone_id)]
    if missing:
        raise HTTPException(status_code=400, detail={"code": "UNKNOWN_PHONE", "phone_ids": [str(x) for x in missing]})
    job = store.create_job(operation, payload.phone_ids, key)
    enqueue_phone_operation(UUID(job["job_id"]))
    return JobAccepted(job_id=UUID(job["job_id"]), status="queued")


@api_router.get("/phones", response_model=list[Phone])
async def list_phones(status_filter: str | None = None, authorization: str | None = Header(default=None)) -> list[Phone]:
    require_auth(authorization)
    phones = store.phones()
    if status_filter:
        phones = [phone for phone in phones if phone["status"] == status_filter]
    return [Phone(**phone) for phone in phones]


@api_router.post("/phones/batch-start", response_model=JobAccepted, status_code=status.HTTP_202_ACCEPTED)
async def batch_start(payload: PhoneIdsRequest, idempotency_key: str = Header(min_length=8, max_length=128), authorization: str | None = Header(default=None)) -> JobAccepted:
    return submit_job("start", payload, idempotency_key, authorization)


@api_router.post("/phones/batch-stop", response_model=JobAccepted, status_code=status.HTTP_202_ACCEPTED)
async def batch_stop(payload: PhoneIdsRequest, idempotency_key: str = Header(min_length=8, max_length=128), authorization: str | None = Header(default=None)) -> JobAccepted:
    return submit_job("stop", payload, idempotency_key, authorization)


@api_router.post("/phones/connection-info", response_model=ConnectionInfoResponse)
async def connection_info(payload: PhoneIdsRequest, authorization: str | None = Header(default=None)) -> ConnectionInfoResponse:
    require_auth(authorization)
    items = []
    for phone_id in payload.phone_ids:
        phone = store.get_phone(phone_id)
        if not phone:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "phone_id": str(phone_id)})
        info = (await mock_adapter.get_connection_info([phone["vendor_id"]]))[0]
        items.append({"phone_id": phone_id, **info})
    return ConnectionInfoResponse(items=items)


@api_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: UUID, authorization: str | None = Header(default=None)) -> JobResponse:
    require_auth(authorization)
    job = store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Job not found"})
    items = job["items"]
    summary = {"total": len(items), "succeeded": sum(x["status"] == "succeeded" for x in items), "failed": sum(x["status"] == "failed" for x in items), "pending": sum(x["status"] in ("queued", "running") for x in items)}
    return JobResponse(**job, summary=summary)
