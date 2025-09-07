"""Device management router."""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..services.device_service import DeviceService
from ..core.exceptions import DeviceError, AuthenticationError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/devices")


def get_device_service() -> DeviceService:
    """Get device service instance."""
    return DeviceService()


def require_auth(request: Request) -> Dict[str, Any]:
    """Require authentication for API endpoints."""
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return request.session.get("user_data", {})


@router.get("/")
async def get_devices(
    request: Request,
    user_data: Dict[str, Any] = Depends(require_auth),
    device_service: DeviceService = Depends(get_device_service)
):
    """Get list of user's devices."""
    try:
        devices = await device_service.get_devices(user_data)
        return {"devices": devices}
    except Exception as e:
        logger.error(f"Failed to get devices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve devices")


@router.get("/{device_id}/status")
async def get_device_status(
    device_id: str,
    request: Request,
    user_data: Dict[str, Any] = Depends(require_auth),
    device_service: DeviceService = Depends(get_device_service)
):
    """Get device status."""
    try:
        status = await device_service.get_device_status(device_id, user_data)
        return status
    except DeviceError as e:
        logger.error(f"Device error for {device_id}: {e.message}")
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to get device status for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get device status")


@router.post("/{device_id}/command")
async def send_device_command(
    device_id: str,
    command_data: Dict[str, Any],
    request: Request,
    user_data: Dict[str, Any] = Depends(require_auth),
    device_service: DeviceService = Depends(get_device_service)
):
    """Send command to device."""
    try:
        result = await device_service.send_command(device_id, command_data, user_data)
        return {"success": True, "result": result}
    except DeviceError as e:
        logger.error(f"Device command error for {device_id}: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to send command to {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send command")


@router.post("/{device_id}/start")
async def start_mowing(
    device_id: str,
    request: Request,
    user_data: Dict[str, Any] = Depends(require_auth),
    device_service: DeviceService = Depends(get_device_service)
):
    """Start mowing operation."""
    try:
        result = await device_service.start_mowing(device_id, user_data)
        return {"success": True, "message": "Mowing started", "result": result}
    except DeviceError as e:
        logger.error(f"Failed to start mowing for {device_id}: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to start mowing for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start mowing")


@router.post("/{device_id}/stop")
async def stop_mowing(
    device_id: str,
    request: Request,
    user_data: Dict[str, Any] = Depends(require_auth),
    device_service: DeviceService = Depends(get_device_service)
):
    """Stop mowing operation."""
    try:
        result = await device_service.stop_mowing(device_id, user_data)
        return {"success": True, "message": "Mowing stopped", "result": result}
    except DeviceError as e:
        logger.error(f"Failed to stop mowing for {device_id}: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to stop mowing for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop mowing")


@router.post("/{device_id}/dock")
async def return_to_dock(
    device_id: str,
    request: Request,
    user_data: Dict[str, Any] = Depends(require_auth),
    device_service: DeviceService = Depends(get_device_service)
):
    """Return device to charging dock."""
    try:
        result = await device_service.return_to_dock(device_id, user_data)
        return {"success": True, "message": "Returning to dock", "result": result}
    except DeviceError as e:
        logger.error(f"Failed to dock {device_id}: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Failed to dock {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to return to dock")
