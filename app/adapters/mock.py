from app.adapters.base import AdapterCapabilities, VendorAdapter
from app.store import store


class MockAdapter(VendorAdapter):
    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities(max_batch_size=20, supports_custom_apk=True)

    async def start(self, vendor_ids: list[str]) -> dict[str, bool]:
        return {vendor_id: True for vendor_id in vendor_ids}

    async def stop(self, vendor_ids: list[str]) -> dict[str, bool]:
        return {vendor_id: True for vendor_id in vendor_ids}

    async def get_connection_info(self, vendor_ids: list[str]) -> list[dict[str, object]]:
        return [
            {
                "vendor_id": vendor_id,
                "access_host": "127.0.0.1",
                "access_port": 14308,
                "ticket": f"mock-ticket-{vendor_id}",
                "expires_at": "2099-01-01T00:00:00Z",
            }
            for vendor_id in vendor_ids
        ]


mock_adapter = MockAdapter()
