"""
Echter Mammotion API-Client

Direkte Verbindung zu Mammotion-Servern ohne Mock-Modus.
Basiert auf der offiziellen PyMammotion-Bibliothek.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import json

# Versuche PyMammotion zu importieren
try:
    # Import the improved PyMammotion client
    from ..mammotion_web.api.pymammotion_client import PyMammotionClient, PyMammotionNotAvailable
    PYMAMMOTION_AVAILABLE = True
except ImportError as e:
    PYMAMMOTION_AVAILABLE = False
    PyMammotionClient = None
    PyMammotionNotAvailable = None
    logging.warning(f"PyMammotion nicht verfügbar: {e}")


@dataclass
class RealMowerInfo:
    """Echte Mäher-Informationen von Mammotion-Servern"""
    device_id: str
    name: str
    model: str
    battery_level: int
    status: str
    position_x: float = 0.0
    position_y: float = 0.0
    last_seen: Optional[datetime] = None
    firmware_version: str = "Unknown"
    serial_number: str = "Unknown"
    
    @property
    def battery_percentage(self) -> int:
        return max(0, min(100, self.battery_level))
    
    @property
    def is_online(self) -> bool:
        if not self.last_seen:
            return False
        return (datetime.now() - self.last_seen).seconds < 300  # 5 Minuten


class RealMammotionClient:
    """
    Echter Mammotion-API-Client
    
    Verbindet sich direkt mit Mammotion-Servern und verwaltet echte Mähroboter.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
        self._pymammotion_client: Optional[PyMammotionClient] = None
        self._authenticated = False
        self._user_info: Optional[Dict[str, Any]] = None
        self._devices: List[RealMowerInfo] = []
        
        # Mammotion API-Endpunkte
        self.base_url = "https://api.mammotion.com"
        self.auth_url = f"{self.base_url}/auth"
        self.devices_url = f"{self.base_url}/devices"
        
    async def __aenter__(self):
        """Async Context Manager Entry"""
        await self._ensure_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager Exit"""
        await self.close()
        
    async def _ensure_session(self):
        """Stellt sicher, dass eine HTTP-Session existiert"""
        if not self._session:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    'User-Agent': 'Mammotion-Linux-App/1.0',
                    'Content-Type': 'application/json'
                }
            )
            
    async def authenticate(self, email: str, password: str) -> bool:
        """
        Authentifiziert sich bei Mammotion-Servern
        
        Args:
            email: Mammotion-E-Mail-Adresse
            password: Mammotion-Passwort
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        self.logger.info(f"Versuche Anmeldung bei Mammotion für {email}")
        
        # Versuche zuerst PyMammotion, dann HTTP-Fallback
        if PYMAMMOTION_AVAILABLE:
            try:
                result = await self._authenticate_with_pymammotion(email, password)
                if result:
                    return True
                else:
                    self.logger.info("PyMammotion-Authentifizierung fehlgeschlagen, versuche HTTP-Fallback...")
            except Exception as e:
                self.logger.warning(f"PyMammotion-Authentifizierung fehlgeschlagen: {e}, versuche HTTP-Fallback...")
        
        # HTTP-Fallback
        return await self._authenticate_with_http(email, password)
            
    async def _authenticate_with_pymammotion(self, email: str, password: str) -> bool:
        """Authentifizierung über PyMammotion-Bibliothek"""
        try:
            self.logger.info("Initialisiere PyMammotion-Client...")
            self._pymammotion_client = PyMammotionClient()
            
            # Login-Versuch mit verbessertem Error Handling
            await self._pymammotion_client.login(email, password)
            
            if self._pymammotion_client.is_authenticated:
                self._authenticated = True
                self.logger.info("Erfolgreich bei Mammotion angemeldet (PyMammotion)")
                
                # Teste Verbindung mit Health Check
                if await self._pymammotion_client.health_check():
                    self.logger.info("PyMammotion Health Check erfolgreich")
                    return True
                else:
                    self.logger.warning("PyMammotion Health Check fehlgeschlagen")
                    return False
            else:
                self.logger.error("Anmeldung bei Mammotion fehlgeschlagen")
                return False
                
        except PyMammotionNotAvailable as e:
            self.logger.warning(f"PyMammotion nicht verfügbar: {e}")
            return False
        except Exception as e:
            self.logger.error(f"PyMammotion-Authentifizierung fehlgeschlagen: {e}")
            return False
            
    async def _authenticate_with_http(self, email: str, password: str) -> bool:
        """Authentifizierung über direkte HTTP-Anfragen - NUR echte API"""
        try:
            await self._ensure_session()
            
            # Login-Daten
            login_data = {
                "email": email,
                "password": password,
                "device_type": "linux_app"
            }
            
            # Login-Anfrage
            async with self._session.post(self.auth_url, json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get('success') and result.get('access_token'):
                        self._user_info = result
                        self._authenticated = True
                        
                        # Authorization-Header für weitere Anfragen setzen
                        self._session.headers['Authorization'] = f"Bearer {result['access_token']}"
                        
                        self.logger.info("Erfolgreich bei Mammotion angemeldet (HTTP)")
                        return True
                    else:
                        self.logger.error(f"Login fehlgeschlagen: {result.get('message', 'Unbekannter Fehler')}")
                        return False
                else:
                    self.logger.error(f"HTTP-Fehler beim Login: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"HTTP-Authentifizierung fehlgeschlagen: {e}")
            return False
            
    async def discover_devices(self) -> List[RealMowerInfo]:
        """
        Sucht nach verfügbaren Mammotion-Geräten
        
        Returns:
            Liste der gefundenen Mähroboter
        """
        if not self._authenticated:
            self.logger.error("Nicht authentifiziert - kann keine Geräte suchen")
            return []
            
        self.logger.info("Suche nach Mammotion-Geräten...")
        
        # Versuche zuerst PyMammotion, dann HTTP-Fallback
        if self._pymammotion_client:
            try:
                devices = await self._discover_with_pymammotion()
                if devices:
                    return devices
                else:
                    self.logger.info("PyMammotion-Gerätesuche lieferte keine Ergebnisse, versuche HTTP-Fallback...")
            except Exception as e:
                self.logger.warning(f"PyMammotion-Gerätesuche fehlgeschlagen: {e}, versuche HTTP-Fallback...")
        
        # HTTP-Fallback
        return await self._discover_with_http()
            
    async def _discover_with_pymammotion(self) -> List[RealMowerInfo]:
        """Geräte-Suche über PyMammotion"""
        try:
            self.logger.info("Suche Geräte mit PyMammotion...")
            devices_data = await self._pymammotion_client.list_devices()
            
            devices = []
            for device_info in devices_data:
                mower = RealMowerInfo(
                    device_id=device_info.get('id', 'unknown'),
                    name=device_info.get('name', 'Mammotion Mäher'),
                    model=device_info.get('model', 'Luba'),
                    battery_level=device_info.get('battery_level', 0),
                    status=device_info.get('status', 'unknown'),
                    position_x=device_info.get('position', {}).get('lat', 0.0),
                    position_y=device_info.get('position', {}).get('lon', 0.0),
                    firmware_version=device_info.get('firmware_version', 'Unknown'),
                    serial_number=device_info.get('serial_number', device_info.get('id', 'Unknown')),
                    last_seen=datetime.now()
                )
                devices.append(mower)
                
            self._devices = devices
            self.logger.info(f"{len(devices)} Mammotion-Geräte gefunden")
            return devices
            
        except Exception as e:
            self.logger.error(f"Geräte-Suche mit PyMammotion fehlgeschlagen: {e}")
            return []
            
    async def _discover_with_http(self) -> List[RealMowerInfo]:
        """Geräte-Suche über HTTP-API - NUR echte API"""
        try:
            await self._ensure_session()
            
            async with self._session.get(self.devices_url) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    devices = []
                    for device_data in result.get('devices', []):
                        mower = RealMowerInfo(
                            device_id=device_data.get('id', 'unknown'),
                            name=device_data.get('name', 'Mammotion Mäher'),
                            model=device_data.get('model', 'Luba'),
                            battery_level=device_data.get('battery_level', 0),
                            status=device_data.get('status', 'unknown'),
                            position_x=device_data.get('position_x', 0.0),
                            position_y=device_data.get('position_y', 0.0),
                            firmware_version=device_data.get('firmware_version', 'Unknown'),
                            serial_number=device_data.get('serial_number', 'Unknown'),
                            last_seen=datetime.now()
                        )
                        devices.append(mower)
                        
                    self._devices = devices
                    self.logger.info(f"{len(devices)} Mammotion-Geräte gefunden")
                    return devices
                else:
                    self.logger.error(f"HTTP-Fehler bei Geräte-Suche: {response.status}")
                    raise Exception(f"HTTP {response.status}")
                    
        except Exception as e:
            self.logger.error(f"HTTP-Geräte-Suche fehlgeschlagen: {e}")
            # Keine Demo-Geräte, keine Fallbacks - nur echte API
            return []
            
    async def send_command(self, device_id: str, command: str, parameters: Optional[Dict] = None) -> bool:
        """
        Sendet einen Befehl an einen Mähroboter
        
        Args:
            device_id: ID des Zielgeräts
            command: Befehlsname (start_mowing, stop_mowing, return_to_dock)
            parameters: Optionale Befehlsparameter
            
        Returns:
            True wenn erfolgreich gesendet
        """
        if not self._authenticated:
            self.logger.error("Nicht authentifiziert - kann keinen Befehl senden")
            return False
            
        self.logger.info(f"Sende Befehl '{command}' an Gerät {device_id}")
        
        try:
            if self._pymammotion_client:
                # PyMammotion-Befehl
                await self._pymammotion_client.send_command(device_id, command, parameters)
                return True
            else:
                # Echter HTTP-Befehl - keine Demo-Simulation
                await self._ensure_session()
                
                command_data = {
                    'command': command,
                    'parameters': parameters or {}
                }
                
                url = f"{self.devices_url}/{device_id}/commands"
                async with self._session.post(url, json=command_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('success', False)
                    else:
                        self.logger.error(f"HTTP-Fehler bei Befehl: {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Befehl senden fehlgeschlagen: {e}")
            return False
            
    async def get_device_status(self, device_id: str) -> Optional[RealMowerInfo]:
        """
        Holt den aktuellen Status eines Geräts
        
        Args:
            device_id: ID des Geräts
            
        Returns:
            Aktuelle Geräteinformationen oder None
        """
        if not self._authenticated:
            return None
            
        try:
            if self._pymammotion_client:
                # PyMammotion-Status
                status_data = await self._pymammotion_client.get_status(device_id)
                
                return RealMowerInfo(
                    device_id=device_id,
                    name=status_data.get('name', 'Mammotion Mäher'),
                    model=status_data.get('model', 'Luba'),
                    battery_level=status_data.get('battery_level', 0),
                    status=status_data.get('status', 'unknown'),
                    position_x=status_data.get('position', {}).get('lat', 0.0),
                    position_y=status_data.get('position', {}).get('lon', 0.0),
                    firmware_version=status_data.get('firmware_version', 'Unknown'),
                    serial_number=status_data.get('serial_number', 'Unknown'),
                    last_seen=datetime.now()
                )
            else:
                # HTTP-Status
                await self._ensure_session()
                
                url = f"{self.devices_url}/{device_id}/status"
                async with self._session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return RealMowerInfo(
                            device_id=device_id,
                            name=data.get('name', 'Mammotion Mäher'),
                            model=data.get('model', 'Luba'),
                            battery_level=data.get('battery_level', 0),
                            status=data.get('status', 'unknown'),
                            position_x=data.get('position_x', 0.0),
                            position_y=data.get('position_y', 0.0),
                            firmware_version=data.get('firmware_version', 'Unknown'),
                            serial_number=data.get('serial_number', 'Unknown'),
                            last_seen=datetime.now()
                        )
                    else:
                        return None
                        
        except Exception as e:
            self.logger.error(f"Status abrufen fehlgeschlagen: {e}")
            return None
            
    async def close(self):
        """Schließt alle Verbindungen"""
        if self._session:
            await self._session.close()
            self._session = None
            
        if self._pymammotion_client:
            # PyMammotion-Client schließen falls möglich
            try:
                await self._pymammotion_client.close()
            except Exception as e:
                self.logger.warning(f"Fehler beim Schließen des PyMammotion-Clients: {e}")
            self._pymammotion_client = None
            
        self._authenticated = False
        self.logger.info("Mammotion-Client geschlossen")
        
    @property
    def is_authenticated(self) -> bool:
        """Gibt zurück ob authentifiziert"""
        return self._authenticated
        
    @property
    def devices(self) -> List[RealMowerInfo]:
        """Gibt die Liste der gefundenen Geräte zurück"""
        return self._devices.copy()
        
    @property
    def user_info(self) -> Optional[Dict[str, Any]]:
        """Gibt Benutzerinformationen zurück"""
        return self._user_info
