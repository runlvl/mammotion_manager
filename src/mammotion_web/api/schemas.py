from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str
    password: str
    mfa_code: Optional[str] = None


class LoginResponse(BaseModel):
    success: bool
    message: str = ""


class DeviceSummary(BaseModel):
    device_id: str = Field(alias="id")
    name: str
    model: Optional[str] = None
    battery_level: Optional[int] = None
    status: Optional[str] = None
    online: Optional[bool] = None

    class Config:
        populate_by_name = True


class CommandRequest(BaseModel):
    action: str
    args: Dict[str, Any] = {}


class DeviceStatus(BaseModel):
    device_id: str
    status: Optional[str] = None
    battery_level: Optional[int] = None
    position: Optional[Dict[str, float]] = None


class ErrorResponse(BaseModel):
    detail: str
