from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
import time

logger = logging.getLogger(__name__)

try:
    # PyMammotion imports (correct imports based on actual library structure)
    from pymammotion import MammotionHTTP  # type: ignore
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
    
    Features:
    - Robust error handling with retries
    - Connection health monitoring
    - Automatic cleanup on failures
    - Comprehensive logging
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        if not PYMAMMOTION_AVAILABLE:
            raise PyMammotionNotAvailable(
                "PyMammotion is not available. Please install and configure it."
            )
        self._http: Optional[MammotionHTTP] = None
        self._cloud: Optional[CloudIOTGateway] = None
        self._mgr: Optional[MammotionMixedDeviceManager] = None
        self._lock = asyncio.Lock()
        self._authenticated = False
        self._last_login_time: Optional[float] = None
        self._max_retries = max_retries
        self._retry_delay = retry_delay

    async def login(self, email: str, password: str, mfa_code: Optional[str] = None) -> None:
        """Login to Mammotion cloud via PyMammotion with robust error handling and retries"""
        async with self._lock:
            last_error = None
            
            for attempt in range(self._max_retries):
                try:
                    logger.info(f"Starting PyMammotion login for {email} (attempt {attempt + 1}/{self._max_retries})")
                    
                    # Create HTTP client first
                    self._http = MammotionHTTP()
                    
                    # Login via HTTP client first
                    logger.debug("Attempting login via MammotionHTTP...")
                    login_response = await self._http.login_by_email(email, password)
                    
                    # Check login success
                    if not login_response or not login_response.data or not login_response.data.accessToken:
                        error_msg = "Login failed - no access token received"
                        logger.error(error_msg)
                        raise RuntimeError(f"Login failed at Mammotion cloud: {error_msg}")
                    
                    logger.info("HTTP login successful, initializing cloud gateway...")
                    
                    # Create cloud gateway with HTTP client
                    self._cloud = CloudIOTGateway(self._http)
                    
                    # Initialize device manager
                    self._mgr = MammotionMixedDeviceManager()
                    await self._mgr.init_cloud_connection(self._cloud)
                    
                    self._authenticated = True
                    self._last_login_time = time.time()
                    logger.info("PyMammotion login completed successfully")
                    return
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"PyMammotion login attempt {attempt + 1} failed: {e}")
                    
                    # Clean up on failure
                    await self._cleanup_connection()
                    
                    # Wait before retry (unless last attempt)
                    if attempt < self._max_retries - 1:
                        logger.info(f"Retrying in {self._retry_delay} seconds...")
                        await asyncio.sleep(self._retry_delay)
            
            # All attempts failed
            logger.error(f"All {self._max_retries} login attempts failed")
            raise RuntimeError(f"PyMammotion login failed after {self._max_retries} attempts: {last_error}")

    async def _cleanup_connection(self) -> None:
        """Clean up connection state"""
        self._authenticated = False
        self._last_login_time = None
        
        if self._mgr:
            try:
                if hasattr(self._mgr, 'close'):
                    await self._mgr.close()
            except Exception as e:
                logger.debug(f"Error closing device manager: {e}")
            self._mgr = None
            
        if self._cloud:
            try:
                if hasattr(self._cloud, 'close'):
                    await self._cloud.close()
            except Exception as e:
                logger.debug(f"Error closing cloud gateway: {e}")
            self._cloud = None
            
        if self._http:
            try:
                if hasattr(self._http, 'close'):
                    await self._http.close()
            except Exception as e:
                logger.debug(f"Error closing HTTP client: {e}")
            self._http = None

    async def list_devices(self) -> List[Dict[str, Any]]:
        """List devices with improved error handling and retry logic"""
        if not self._mgr or not self._authenticated:
            raise RuntimeError("Not authenticated")
        
        try:
            logger.debug("Retrieving devices from Mammotion cloud...")
            devices = await self._mgr.get_devices_by_account_response()
            
            if not devices:
                logger.warning("No devices found in account")
                return []
            
            # Normalize to dicts with robust attribute access
            out: List[Dict[str, Any]] = []
            for d in devices:
                try:
                    device_info = {
                        "id": getattr(d, "device_name", None) or getattr(d, "device_id", None) or "unknown",
                        "name": getattr(d, "device_name", "Mower"),
                        "model": getattr(d, "product_model", "Unknown"),
                        "battery_level": getattr(d, "battery_level", 0),
                        "status": getattr(d, "work_mode", "unknown"),
                        "online": getattr(d, "online", False),
                        "product_key": getattr(d, "product_key", None),
                        "device_secret": getattr(d, "device_secret", None),
                    }
                    out.append(device_info)
                    logger.debug(f"Found device: {device_info['name']} ({device_info['id']})")
                except Exception as e:
                    logger.warning(f"Error processing device data: {e}")
                    
            logger.info(f"Successfully retrieved {len(out)} devices")
            return out
            
        except Exception as e:
            logger.error(f"Failed to list devices: {e}")
            raise RuntimeError(f"Failed to retrieve device list: {e}")

    async def get_status(self, device_id: str) -> Dict[str, Any]:
        """Get device status with improved error handling"""
        if not self._mgr or not self._authenticated:
            raise RuntimeError("Not authenticated")
            
        try:
            logger.debug(f"Getting status for device: {device_id}")
            dev = await self._mgr.get_device_by_name(device_id)
            
            if not dev:
                raise RuntimeError(f"Device {device_id} not found")
            
            # Build status dict with safe attribute access
            status = {
                "device_id": device_id,
                "status": getattr(dev, "work_mode", "unknown"),
                "battery_level": getattr(dev, "battery_level", 0),
                "position": {
                    "lat": getattr(dev, "latitude", 0.0),
                    "lon": getattr(dev, "longitude", 0.0),
                },
                "online": getattr(dev, "online", False),
                "error_code": getattr(dev, "error_code", 0),
                "last_update": getattr(dev, "last_update", None),
            }
            
            logger.debug(f"Device status retrieved: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Failed to get device status: {e}")
            raise RuntimeError(f"Failed to get status for device {device_id}: {e}")

    async def send_command(self, device_id: str, action: str, args: Optional[Dict[str, Any]] = None) -> None:
        """Send command to device with improved error handling and validation"""
        if not self._mgr or not self._authenticated:
            raise RuntimeError("Not authenticated")
            
        try:
            logger.info(f"Sending command '{action}' to device {device_id}")
            dev = await self._mgr.get_device_by_name(device_id)
            
            if not dev:
                raise RuntimeError(f"Device {device_id} not found")
            
            action = action.lower()
            
            # Map high-level actions to device methods with error handling
            if action in ("start", "start_mowing"):
                if hasattr(dev, "start_map_hash"):
                    await dev.start_map_hash()
                else:
                    raise RuntimeError("Start mowing not supported by device")
                    
            elif action in ("pause",):
                if hasattr(dev, "pause_device"):
                    await dev.pause_device()
                else:
                    raise RuntimeError("Pause not supported by device")
                    
            elif action in ("resume",):
                if hasattr(dev, "resume_device"):
                    await dev.resume_device()
                else:
                    raise RuntimeError("Resume not supported by device")
                    
            elif action in ("stop", "stop_mowing"):
                if hasattr(dev, "stop_device"):
                    await dev.stop_device()
                else:
                    raise RuntimeError("Stop not supported by device")
                    
            elif action in ("return", "return_to_dock", "dock"):
                if hasattr(dev, "return_to_dock"):
                    await dev.return_to_dock()
                else:
                    raise RuntimeError("Return to dock not supported by device")
                    
            elif action in ("edge_cut",):
                if hasattr(dev, "start_edge_cut"):
                    await dev.start_edge_cut()
                else:
                    raise RuntimeError("Edge cut not supported by device")
            else:
                raise ValueError(f"Unsupported action: {action}")
                
            logger.info(f"Command '{action}' sent successfully to device {device_id}")
            
        except Exception as e:
            logger.error(f"Failed to send command '{action}' to device {device_id}: {e}")
            raise

    async def close(self) -> None:
        """Close all connections with proper cleanup"""
        async with self._lock:
            try:
                logger.debug("Closing PyMammotion client...")
                await self._cleanup_connection()
                logger.info("PyMammotion client closed successfully")
                
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")

    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated"""
        return self._authenticated

    @property 
    def connection_age(self) -> Optional[float]:
        """Get connection age in seconds"""
        if self._last_login_time:
            return time.time() - self._last_login_time
        return None

    async def health_check(self) -> bool:
        """Perform a health check on the connection"""
        try:
            if not self._authenticated or not self._mgr:
                logger.debug("Health check failed: not authenticated")
                return False
            
            # Check connection age
            age = self.connection_age
            if age and age > 3600:  # 1 hour
                logger.warning(f"Connection is old ({age:.0f}s), may need refresh")
            
            # Try to list devices as a health check
            await self.list_devices()
            logger.debug("Health check passed")
            return True
            
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def ensure_connection(self) -> None:
        """Ensure connection is healthy, reconnect if needed"""
        if not await self.health_check():
            logger.info("Connection unhealthy, authentication required")
            raise RuntimeError("Connection lost, re-authentication required")

    async def with_retry(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with retry logic"""
        last_error = None
        
        for attempt in range(self._max_retries):
            try:
                # Ensure connection is healthy
                await self.ensure_connection()
                
                # Execute operation
                return await operation(*args, **kwargs)
                
            except Exception as e:
                last_error = e
                logger.warning(f"Operation attempt {attempt + 1} failed: {e}")
                
                # Wait before retry (unless last attempt)
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(self._retry_delay)
        
        raise RuntimeError(f"Operation failed after {self._max_retries} attempts: {last_error}")
