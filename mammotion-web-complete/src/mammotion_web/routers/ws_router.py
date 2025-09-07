"""WebSocket router for real-time communication with real devices."""

import logging
import json
import asyncio
from typing import Dict, Any, List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

from ..services.device_service import DeviceService
from ..core.exceptions import WebSocketError

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for real device communication."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.device_service = DeviceService()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket client {client_id} connected")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"WebSocket client {client_id} disconnected")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client."""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            if websocket.client_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to {client_id}: {str(e)}")
                    self.disconnect(client_id)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {str(e)}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time device communication."""
    await manager.connect(websocket, client_id)
    
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connected",
            "client_id": client_id,
            "timestamp": asyncio.get_event_loop().time()
        }, client_id)
        
        while True:
            try:
                # Wait for message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                await handle_websocket_message(message, client_id)
                
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                await manager.send_personal_message({
                    "type": "heartbeat",
                    "timestamp": asyncio.get_event_loop().time()
                }, client_id)
                
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {str(e)}")
        manager.disconnect(client_id)


async def handle_websocket_message(message: Dict[str, Any], client_id: str):
    """Handle incoming WebSocket messages for real device operations."""
    try:
        message_type = message.get("type")
        
        if message_type == "get_devices":
            user_data = message.get("user_data", {})
            try:
                devices = await manager.device_service.get_devices(user_data)
                await manager.send_personal_message({
                    "type": "devices",
                    "data": devices
                }, client_id)
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Failed to get devices: {str(e)}"
                }, client_id)
            
        elif message_type == "get_device_status":
            device_id = message.get("device_id")
            user_data = message.get("user_data", {})
            
            if device_id:
                try:
                    status = await manager.device_service.get_device_status(device_id, user_data)
                    await manager.send_personal_message({
                        "type": "device_status",
                        "device_id": device_id,
                        "data": status
                    }, client_id)
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Failed to get device status: {str(e)}"
                    }, client_id)
            
        elif message_type == "send_command":
            device_id = message.get("device_id")
            command_data = message.get("command_data", {})
            user_data = message.get("user_data", {})
            
            if device_id and command_data:
                try:
                    result = await manager.device_service.send_command(device_id, command_data, user_data)
                    await manager.send_personal_message({
                        "type": "command_result",
                        "device_id": device_id,
                        "data": result
                    }, client_id)
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Command failed: {str(e)}"
                    }, client_id)
            
        elif message_type == "ping":
            await manager.send_personal_message({
                "type": "pong",
                "timestamp": asyncio.get_event_loop().time()
            }, client_id)
            
        else:
            await manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, client_id)
            
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Internal server error: {str(e)}"
        }, client_id)
