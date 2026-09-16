from dataclasses import dataclass


@dataclass
class MockFailureMode:
    rate_limit_every: int = 0
    offline_phone_ids: set[str] | None = None
    timeout_seconds: int = 60

    def should_fail_rate_limit(self, attempt: int) -> bool:
        return self.rate_limit_every > 0 and attempt % self.rate_limit_every == 0

    def is_offline(self, phone_id: str) -> bool:
        return phone_id in (self.offline_phone_ids or set())


failure_mode = MockFailureMode()
