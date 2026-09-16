from dataclasses import dataclass
from uuid import UUID

from app.config import get_settings

settings = get_settings()
ALLOWED_COMMANDS = {"get-state", "screenshot", "install-apk", "push-file"}


@dataclass(frozen=True, slots=True)
class AdbResult:
    phone_id: UUID
    status: str
    command: str
    duration_ms: int
    output: str | None = None


class MockAdbManager:
    async def execute(self, phone_id: UUID, command: str) -> AdbResult:
        if command not in ALLOWED_COMMANDS:
            raise ValueError(f"ADB command is not allowed: {command}")
        return AdbResult(phone_id=phone_id, status="succeeded", command=command, duration_ms=42, output="mock-ok")


adb_manager = MockAdbManager()
