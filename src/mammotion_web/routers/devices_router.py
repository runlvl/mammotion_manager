"""Devices router for Mammotion Web."""

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/devices", tags=["devices"])

# Templates
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def devices_page(request: Request):
    """Display devices page."""
    if not request.session.get("authenticated"):
        return RedirectResponse(url="/auth/login")
    
    # TODO: Get real devices from Mammotion API
    devices = []
    
    return templates.TemplateResponse("devices.html", {
        "request": request,
        "devices": devices
    })


@router.get("/{device_id}")
async def get_device(device_id: str):
    """Get device details."""
    # TODO: Implement real device API
    return {"device_id": device_id, "status": "unknown"}


@router.post("/{device_id}/start")
async def start_device(device_id: str):
    """Start mowing."""
    # TODO: Implement real device control
    return {"device_id": device_id, "action": "start", "status": "success"}


@router.post("/{device_id}/stop")
async def stop_device(device_id: str):
    """Stop mowing."""
    # TODO: Implement real device control
    return {"device_id": device_id, "action": "stop", "status": "success"}
