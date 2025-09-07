"""
Mammotion Model - Zentrale Logik für die Kommunikation mit Mammotion Mährobotern

Diese Klasse abstrahiert die PyMammotion API und stellt eine saubere Schnittstelle
für die Controller bereit. Sie verwaltet die Verbindung, Authentifizierung und
alle Mäher-Operationen.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

# Mammotion API imports - ONLY real API, no fallbacks
from .real_mammotion_api import RealMammotionAPI


class MowerStatus(Enum):
    """Status-Enum für Mäher"""
    UNKNOWN = "unknown"
    IDLE = "idle"
    MOWING = "mowing"
    CHARGING = "charging"
    PAUSED = "paused"
    ERROR = "error"
    RETURNING = "returning"


@dataclass
class MowerInfo:
    """Datenklasse für Mäher-Informationen"""
    device_id: str
    name: str
    model: str
    battery_level: int
    status: MowerStatus
    position: Optional[Dict[str, float]] = None
    error_message: Optional[str] = None
    last_update: Optional[str] = None


class MammotionModel:
    """
    Zentrale Model-Klasse für Mammotion Mäher-Verwaltung
    
    Diese Klasse implementiert das Observer-Pattern, um Views über
    Änderungen zu benachrichtigen.
    """
    
    def __init__(self):
        self._observers: List[Callable] = []
        self._mowers: Dict[str, MowerInfo] = {}
        self._current_mower_id: Optional[str] = None
        self._is_connected: bool = False
        self._credentials: Optional[Dict[str, str]] = None
        
        # API-Client initialisieren - NUR echte API
        self._api_client = RealMammotionAPI()
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        self.logger.info("MammotionModel initialisiert mit echter Mammotion API")
        
    def _convert_local_to_mower_info(self, local_mower) -> MowerInfo:
        """Konvertiert LocalMowerInfo zu MowerInfo"""
        # Status-Mapping von lokaler zu echter Enum
        status_map = {
            "unknown": MowerStatus.UNKNOWN,
            "idle": MowerStatus.IDLE,
            "mowing": MowerStatus.MOWING,
            "charging": MowerStatus.CHARGING,
            "paused": MowerStatus.PAUSED,
            "error": MowerStatus.ERROR,
            "returning": MowerStatus.RETURNING
        }
        
        status = status_map.get(local_mower.status.value, MowerStatus.UNKNOWN)
        
        return MowerInfo(
            device_id=local_mower.device_id,
            name=local_mower.name,
            model=local_mower.model,
            battery_level=local_mower.battery_level,
            status=status,
            position=local_mower.position,
            error_message=local_mower.error_message,
            last_update=local_mower.last_update
        )
        
    def add_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Fügt einen Observer hinzu, der über Änderungen benachrichtigt wird"""
        self._observers.append(callback)
        
    def remove_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Entfernt einen Observer"""
        if callback in self._observers:
            self._observers.remove(callback)
            
    def _notify_observers(self, event_type: str, data: Any = None) -> None:
        """Benachrichtigt alle Observer über ein Event"""
        for callback in self._observers:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.error(f"Fehler beim Benachrichtigen eines Observers: {e}")
    
    async def login(self, email: str, password: str) -> bool:
        """
        Authentifizierung bei Mammotion - NUR echte API
        
        Args:
            email: E-Mail-Adresse
            password: Passwort
            
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            # NUR echte API verwenden - keine Fallbacks
            success = await self._api_client.login(email, password)
            if success:
                self._credentials = {"email": email, "password": password}
                self._is_connected = True
                self._notify_observers("login_success", {"email": email})
                return True
            else:
                self._notify_observers("login_failed", {"error": "Login fehlgeschlagen"})
                return False
            
        except Exception as e:
            self.logger.error(f"Login fehlgeschlagen: {e}")
            self._notify_observers("login_failed", {"error": str(e)})
            return False
    
    async def logout(self) -> None:
        """Beendet die Verbindung zu Mammotion"""
        self._is_connected = False
        self._credentials = None
        self._api_client = None
        self._mowers.clear()
        self._current_mower_id = None
        self._notify_observers("logout", None)
        
    async def discover_mowers(self) -> List[MowerInfo]:
        """
        Sucht nach verfügbaren Mähern - NUR echte API
        
        Returns:
            Liste der gefundenen Mäher
        """
        if not self._is_connected:
            raise RuntimeError("Nicht verbunden - bitte zuerst einloggen")
            
        try:
            # NUR echte API verwenden - keine Fallbacks oder Mock-Daten
            local_mowers = await self._api_client.discover_devices()
            mowers = [self._convert_local_to_mower_info(local_mower) for local_mower in local_mowers]
            
            # Mäher in internem Cache speichern
            self._mowers.clear()
            for mower in mowers:
                self._mowers[mower.device_id] = mower
                
            # Ersten Mäher als aktuell setzen
            if mowers and not self._current_mower_id:
                self._current_mower_id = mowers[0].device_id
                
            self.logger.info(f"Gefunden: {len(mowers)} Mäher")
            self._notify_observers("mowers_discovered", {"mowers": mowers})
            
            return mowers
            
        except Exception as e:
            self.logger.error(f"Fehler beim Suchen nach Mähern: {e}")
            self._notify_observers("discovery_failed", {"error": str(e)})
            return []
    
    def get_current_mower(self) -> Optional[MowerInfo]:
        """Gibt den aktuell ausgewählten Mäher zurück"""
        if self._current_mower_id and self._current_mower_id in self._mowers:
            return self._mowers[self._current_mower_id]
        return None
    
    def set_current_mower(self, device_id: str) -> bool:
        """Setzt den aktuell ausgewählten Mäher"""
        if device_id in self._mowers:
            self._current_mower_id = device_id
            self._notify_observers("current_mower_changed", self._mowers[device_id])
            return True
        return False
    
    def get_all_mowers(self) -> List[MowerInfo]:
        """Gibt alle verfügbaren Mäher zurück"""
        return list(self._mowers.values())
    
    async def start_mowing(self, device_id: Optional[str] = None) -> bool:
        """Startet den Mähvorgang - NUR echte API"""
        target_id = device_id or self._current_mower_id
        if not target_id or target_id not in self._mowers:
            return False
            
        try:
            # NUR echte API verwenden - keine Mock-Implementierung
            success = await self._api_client.start_mowing(target_id)
            if success:
                self._mowers[target_id].status = MowerStatus.MOWING
                self._notify_observers("mower_status_changed", self._mowers[target_id])
            return success
            
        except Exception as e:
            self.logger.error(f"Fehler beim Starten des Mähvorgangs: {e}")
            return False
    
    async def stop_mowing(self, device_id: Optional[str] = None) -> bool:
        """Stoppt den Mähvorgang - NUR echte API"""
        target_id = device_id or self._current_mower_id
        if not target_id or target_id not in self._mowers:
            return False
            
        try:
            # NUR echte API verwenden - keine Mock-Implementierung
            success = await self._api_client.stop_mowing(target_id)
            if success:
                self._mowers[target_id].status = MowerStatus.PAUSED
                self._notify_observers("mower_status_changed", self._mowers[target_id])
            return success
            
        except Exception as e:
            self.logger.error(f"Fehler beim Stoppen des Mähvorgangs: {e}")
            return False
    
    async def return_to_dock(self, device_id: Optional[str] = None) -> bool:
        """Schickt den Mäher zur Ladestation zurück - NUR echte API"""
        target_id = device_id or self._current_mower_id
        if not target_id or target_id not in self._mowers:
            return False
            
        try:
            # NUR echte API verwenden - keine Mock-Implementierung
            success = await self._api_client.return_to_dock(target_id)
            if success:
                self._mowers[target_id].status = MowerStatus.RETURNING
                self._notify_observers("mower_status_changed", self._mowers[target_id])
            return success
            
        except Exception as e:
            self.logger.error(f"Fehler beim Zurücksenden zur Ladestation: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Prüft ob eine Verbindung besteht"""
        return self._is_connected
    
    async def refresh_status(self, device_id: Optional[str] = None) -> bool:
        """Aktualisiert den Status eines Mähers - NUR echte API"""
        target_id = device_id or self._current_mower_id
        if not target_id or target_id not in self._mowers:
            return False
            
        try:
            # NUR echte API verwenden - keine Mock-Updates
            updated_mower = await self._api_client.get_device_status(target_id)
            if updated_mower:
                self._mowers[target_id] = self._convert_local_to_mower_info(updated_mower)
                self._notify_observers("mower_status_changed", self._mowers[target_id])
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren des Status: {e}")
            return False
