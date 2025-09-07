"""Device management service using real pymammotion library."""

import logging
import asyncio
from typing import Dict, Any, List, Optional

from pymammotion.mammotion.devices.mammotion import (
    MammotionDeviceManager, 
    MammotionCloud, 
    MammotionHTTP, 
    MammotionMQTT
)
from pymammotion.mammotion.commands.mammotion_command import MammotionCommand
from pymammotion.aliyun.cloud_gateway import CloudIOTGateway

from ..core.exceptions import DeviceError

logger = logging.getLogger(__name__)


class DeviceService:
    """Service for managing real Mammotion devices."""
    
    def __init__(self):
        """Initialize device service."""
        self.logger = logger
        self.devices_cache = {}
        self.device_manager = None
    
    async def get_devices(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get list of user's devices from Mammotion cloud.
        
        Args:
            user_data: User session data with cloud credentials
            
        Returns:
            List of real device information
        """
        try:
            cloud_gateway = user_data.get("cloud_gateway")
            if not cloud_gateway:
                raise DeviceError("No cloud gateway available")
            
            user_id = user_data.get("user_id")
            self.logger.info(f"Getting devices from cloud for user: {user_id}")
            
            # Fetch devices from cloud using real pymammotion methods
            try:
                # Get device list from cloud using list_binding_by_account
                cloud_devices = await cloud_gateway.list_binding_by_account()
                
                devices = []
                if cloud_devices and hasattr(cloud_devices, 'data') and cloud_devices.data:
                    for device_data in cloud_devices.data:
                        # Create device info from cloud data
                        device_info = {
                            "id": device_data.get("iotId", device_data.get("deviceName")),
                            "name": device_data.get("deviceName", "Mammotion Device"),
                            "model": device_data.get("productKey", "Unknown"),
                            "status": device_data.get("status", "unknown"),
                            "battery": 0,  # Will be updated from device properties
                            "online": device_data.get("status") == "ONLINE",
                            "last_seen": device_data.get("utcActiveTime"),
                            "firmware": device_data.get("firmwareVersion"),
                            "area_completed": 0,
                            "total_area": 0,
                            "cutting_height": 0,
                            "location": {},
                            "cloud_data": device_data
                        }
                        devices.append(device_info)
                        
                        # Cache device for later operations
                        self.devices_cache[device_info["id"]] = device_data
                
                self.logger.info(f"Found {len(devices)} devices for user {user_id}")
                return devices
                
            except Exception as e:
                self.logger.error(f"Error fetching devices from cloud: {str(e)}")
                # Return empty list if no devices found
                return []
            
        except Exception as e:
            self.logger.error(f"Error getting devices from cloud: {str(e)}")
            raise DeviceError(f"Failed to retrieve devices: {str(e)}")
    
    async def get_device_status(self, device_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get real device status from cloud.
        
        Args:
            device_id: Device ID
            user_data: User session data
            
        Returns:
            Real device status information
        """
        try:
            cloud_gateway = user_data.get("cloud_gateway")
            if not cloud_gateway:
                raise DeviceError("No cloud gateway available")
            
            # Get real-time status from cloud
            try:
                device_status = await cloud_gateway.get_device_properties(device_id)
                
                if not device_status:
                    raise DeviceError(f"Device {device_id} not found or offline")
                
                # Extract status from device properties response
                properties = {}
                if hasattr(device_status, 'data') and device_status.data:
                    properties = device_status.data
                
                return {
                    "id": device_id,
                    "status": properties.get("status", "unknown"),
                    "battery": properties.get("batteryLevel", 0),
                    "online": properties.get("online", False),
                    "last_seen": properties.get("lastSeen"),
                    "current_task": properties.get("currentTask"),
                    "location": properties.get("location", {}),
                    "error_code": properties.get("errorCode"),
                    "raw_data": properties
                }
                
            except Exception as e:
                self.logger.error(f"Error getting device status from cloud: {str(e)}")
                # Return basic status if cloud call fails
                return {
                    "id": device_id,
                    "status": "unknown",
                    "battery": 0,
                    "online": False,
                    "error": str(e)
                }
            
        except DeviceError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting device status: {str(e)}")
            raise DeviceError(f"Failed to get device status: {str(e)}")
    
    async def send_command(self, device_id: str, command_data: Dict[str, Any], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send real command to device via cloud.
        
        Args:
            device_id: Device ID
            command_data: Command data
            user_data: User session data
            
        Returns:
            Command execution result
        """
        try:
            cloud_gateway = user_data.get("cloud_gateway")
            if not cloud_gateway:
                raise DeviceError("No cloud gateway available")
            
            # Check if device exists in cache
            device_data = self.devices_cache.get(device_id)
            if not device_data:
                raise DeviceError("Device not found")
            
            # Create Mammotion command
            command = command_data.get("command")
            
            try:
                # Send command via cloud gateway
                result = await cloud_gateway.send_cloud_command(device_id, command_data)
                
                if not result or not result.get("success", True):
                    raise DeviceError(f"Command failed: {result.get('error', 'Unknown error') if result else 'No response'}")
                
                self.logger.info(f"Sent command '{command}' to device {device_id}")
                
                return {
                    "command": command,
                    "status": "executed",
                    "result": result,
                    "timestamp": result.get("timestamp") if result else None
                }
                
            except Exception as e:
                self.logger.error(f"Error sending command to cloud: {str(e)}")
                raise DeviceError(f"Command execution failed: {str(e)}")
            
        except DeviceError:
            raise
        except Exception as e:
            self.logger.error(f"Error sending command: {str(e)}")
            raise DeviceError(f"Failed to send command: {str(e)}")
    
    async def start_mowing(self, device_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start real mowing operation using MammotionCommand."""
        try:
            # Create command using MammotionCommand
            command = MammotionCommand()
            start_job_cmd = command.start_job()
            
            command_data = {
                "command": "start_job",
                "data": start_job_cmd
            }
            
            return await self.send_command(device_id, command_data, user_data)
        except Exception as e:
            self.logger.error(f"Error starting mowing: {str(e)}")
            raise DeviceError(f"Failed to start mowing: {str(e)}")
    
    async def stop_mowing(self, device_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop real mowing operation using MammotionCommand."""
        try:
            # Create command using MammotionCommand
            command = MammotionCommand()
            cancel_job_cmd = command.cancel_job()
            
            command_data = {
                "command": "cancel_job",
                "data": cancel_job_cmd
            }
            
            return await self.send_command(device_id, command_data, user_data)
        except Exception as e:
            self.logger.error(f"Error stopping mowing: {str(e)}")
            raise DeviceError(f"Failed to stop mowing: {str(e)}")
    
    async def return_to_dock(self, device_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return real device to charging dock using MammotionCommand."""
        try:
            # Create command using MammotionCommand
            command = MammotionCommand()
            return_dock_cmd = command.return_to_dock()
            
            command_data = {
                "command": "return_to_dock",
                "data": return_dock_cmd
            }
            
            return await self.send_command(device_id, command_data, user_data)
        except Exception as e:
            self.logger.error(f"Error returning to dock: {str(e)}")
            raise DeviceError(f"Failed to return to dock: {str(e)}")
