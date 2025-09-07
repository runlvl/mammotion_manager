from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from ..services.event_bus import EventBus
from .pymammotion_client import PyMammotionClient

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages cloud session, devices, and broadcasting updates."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._client: Optional[PyMammotionClient] = None
        self._devices_cache: Dict[str, Dict[str, Any]] = {}
        self.events = EventBus()

    async def authenticate(self, email: str, password: str) -> None:
        async with self._lock:
            if self._client is None:
                self._client = PyMammotionClient()
            await self._client.login(email, password)

    async def list_devices(self) -> List[Dict[str, Any]]:
        if not self._client:
            raise RuntimeError("Not authenticated")
        devices = await self._client.list_devices()
        self._devices_cache = {d["id"]: d for d in devices if "id" in d}
        return devices

    async def get_status(self, device_id: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("Not authenticated")
        status = await self._client.get_status(device_id)
        await self.events.publish(f"device:{device_id}", status)
        return status

    async def command(self, device_id: str, action: str, args: Optional[Dict[str, Any]] = None) -> None:
        if not self._client:
            raise RuntimeError("Not authenticated")
        await self._client.send_command(device_id, action, args or {})
        # Fetch fresh status after command
        try:
            status = await self._client.get_status(device_id)
            await self.events.publish(f"device:{device_id}", status)
        except Exception:
            pass
