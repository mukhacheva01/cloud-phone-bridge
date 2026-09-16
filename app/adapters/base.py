from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AdapterCapabilities:
    max_batch_size: int
    supports_marketplace_install: bool = False
    supports_custom_apk: bool = False


class VendorAdapter(ABC):
    @abstractmethod
    def capabilities(self) -> AdapterCapabilities: ...

    @abstractmethod
    async def start(self, vendor_ids: list[str]) -> dict[str, bool]: ...

    @abstractmethod
    async def stop(self, vendor_ids: list[str]) -> dict[str, bool]: ...

    @abstractmethod
    async def get_connection_info(self, vendor_ids: list[str]) -> list[dict[str, object]]: ...
