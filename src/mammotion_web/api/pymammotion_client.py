from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)

try:
    # PyMammotion imports (subject to library versions)
    from pymammotion.aliyun.cloud_gateway import CloudIOTGateway  # type: ignore
    from pymammotion.mammotion.devices.mammotion import (  # type: ignore
        MammotionMixedDeviceManager,
    )
    PYMAMMOTION_AVAILABLE = True
except Exception as e:  # pragma: no cover
    logger.error("PyMammotion import failed: %s", e)
    PYMAMMOTION_AVAILABLE = False


class PyMammotionNotAvailable(RuntimeError):
    pass


class PyMammotionClient:
    """Strict wrapper around PyMammotion; no simulation or demo logic.

    Responsibilities:
    - Login via OAuth/Cloud gateway
    - Manage device manager
    - List devices, get status
    - Send control commands
    - (Optional) subscribe to telemetry if available
    """

    def __init__(self) -> None:
        if not PYMAMMOTION_AVAILABLE:
            raise PyMammotionNotAvailable(
                "PyMammotion is not available. Please install and configure it."
            )
        self._cloud: Optional[CloudIOTGateway] = None
        self._mgr: Optional[MammotionMixedDeviceManager] = None
        self._lock = asyncio.Lock()

    async def login(self, email: str, password: str, mfa_code: Optional[str] = None) -> None:
        async with self._lock:
            self._cloud = CloudIOTGateway()
            # Note: API may differ; adjust to correct method in your env
            login_res = await self._cloud.login_by_oauth(email, password)  # type: ignore[attr-defined]
            if not getattr(login_res, "success", False):
                raise RuntimeError("Login failed at Mammotion cloud")

            self._mgr = MammotionMixedDeviceManager()
            await self._mgr.init_cloud_connection(self._cloud)

    async def list_devices(self) -> List[Dict[str, Any]]:
        if not self._mgr:
            raise RuntimeError("Not authenticated")
        devices = await self._mgr.get_devices_by_account_response()
        # Normalize to dicts
        out: List[Dict[str, Any]] = []
        for d in devices:
            out.append(
                {
                    "id": getattr(d, "device_name", None) or getattr(d, "device_id", None),
                    "name": getattr(d, "device_name", "Mower"),
                    "model": getattr(d, "product_model", None),
                    "battery_level": getattr(d, "battery_level", None),
                    "status": getattr(d, "work_mode", None),
                    "online": getattr(d, "online", None),
                }
            )
        return out

    async def get_status(self, device_id: str) -> Dict[str, Any]:
        if not self._mgr:
            raise RuntimeError("Not authenticated")
        dev = await self._mgr.get_device_by_name(device_id)
        # Build status dict (attributes may vary by lib version)
        status = {
            "device_id": device_id,
            "status": getattr(dev, "work_mode", None),
            "battery_level": getattr(dev, "battery_level", None),
            "position": {
                "lat": getattr(dev, "latitude", None),
                "lon": getattr(dev, "longitude", None),
            },
        }
        return status

    async def send_command(self, device_id: str, action: str, args: Optional[Dict[str, Any]] = None) -> None:
        if not self._mgr:
            raise RuntimeError("Not authenticated")
        dev = await self._mgr.get_device_by_name(device_id)
        action = action.lower()
        # Map high-level actions to device methods; adjust to library methods
        if action in ("start", "start_mowing"):
            await dev.start_map_hash()  # type: ignore[attr-defined]
        elif action in ("pause",):
            if hasattr(dev, "pause_device"):
                await dev.pause_device()  # type: ignore[attr-defined]
            else:
                raise RuntimeError("Pause not supported by library/device")
        elif action in ("resume",):
            if hasattr(dev, "resume_device"):
                await dev.resume_device()  # type: ignore[attr-defined]
            else:
                raise RuntimeError("Resume not supported by library/device")
        elif action in ("stop", "stop_mowing"):
            await dev.stop_device()  # type: ignore[attr-defined]
        elif action in ("return", "return_to_dock", "dock"):
            await dev.return_to_dock()  # type: ignore[attr-defined]
        elif action in ("edge_cut",):
            if hasattr(dev, "start_edge_cut"):
                await dev.start_edge_cut()  # type: ignore[attr-defined]
            else:
                raise RuntimeError("Edge cut not supported")
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def close(self) -> None:
        # Best-effort close
        self._mgr = None
        self._cloud = None
