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
    status: JobStatus = JobStatus.queued


class Phone(BaseModel):
    phone_id: UUID
    vendor: str
    vendor_id: str
    status: str
    adb_status: str
    tags: list[str]
    updated_at: str


class ConnectionInfoRequest(PhoneIdsRequest):
    pass


class ConnectionInfo(BaseModel):
    phone_id: UUID
    access_host: str
    access_port: int
    ticket: str
    expires_at: str
