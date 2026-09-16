from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    queued = "queued"
    running = "running"
    partially_succeeded = "partially_succeeded"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"


class PhoneIdsRequest(BaseModel):
    phone_ids: list[UUID] = Field(min_length=1, max_length=100)


class JobAccepted(BaseModel):
    job_id: UUID
    status: JobStatus


class ErrorInfo(BaseModel):
    code: str
    message: str
    retryable: bool = False
    vendor_code: str | None = None


class JobItem(BaseModel):
    phone_id: UUID
    status: str
    attempts: int = 0
    error: ErrorInfo | None = None


class JobSummary(BaseModel):
    total: int
    succeeded: int
    failed: int
    pending: int


class JobResponse(BaseModel):
    job_id: UUID
    operation: str
    status: JobStatus
    created_at: str
    updated_at: str
    attempts: int
    summary: JobSummary
    items: list[JobItem]


class Phone(BaseModel):
    phone_id: UUID
    vendor: str
    vendor_id: str
    status: str
    adb_status: str
    tags: list[str]
    updated_at: str


class ConnectionInfo(BaseModel):
    phone_id: UUID
    access_host: str
    access_port: int
    ticket: str
    expires_at: str
    adb_mode: str = "mock"
    network_mode: str = "local"


class ConnectionInfoResponse(BaseModel):
    items: list[ConnectionInfo]
