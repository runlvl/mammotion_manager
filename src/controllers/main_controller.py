"""
Main Controller - Zentrale Steuerungslogik der Mammotion App

Der Controller vermittelt zwischen dem Model (Datenlogik) und den Views (UI).
Er implementiert die Anwendungslogik und koordiniert alle Benutzerinteraktionen.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from PySide6.QtCore import QObject, Signal, QTimer

from ..models.mammotion_model import MammotionModel, MowerInfo, MowerStatus


class MainController(QObject):
    """
    Hauptcontroller der Anwendung
    
    Dieser Controller verwaltet die gesamte Anwendungslogik und koordiniert
    die Kommunikation zwischen Model und Views.
    """
    
    # Qt Signals für die Kommunikation mit Views
    login_status_changed = Signal(bool, str)  # success, message
    mower_status_updated = Signal(object)  # MowerInfo object
    mowers_list_updated = Signal(list)  # List[MowerInfo]
    current_mower_changed = Signal(object)  # MowerInfo object
    connection_status_changed = Signal(bool)  # connected
    error_occurred = Signal(str, str)  # title, message
    notification_requested = Signal(str, str, str)  # title, message, type
    
    def __init__(self):
        super().__init__()
        
        # Model initialisieren
        self.model = MammotionModel()
        self.model.add_observer(self._on_model_event)
        
        # Logging setup
        self.logger = logging.getLogger(__name__)
        
        # Status-Update Timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._refresh_current_mower_status)
        self.status_timer.setInterval(30000)  # 30 Sekunden
        
        # Async Event Loop für Qt Integration
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def _on_model_event(self, event_type: str, data: Any) -> None:
        """
        Callback für Model-Events
        
        Wandelt Model-Events in Qt-Signals um, damit Views reagieren können.
        """
        try:
            if event_type == "login_success":
                self.login_status_changed.emit(True, f"Erfolgreich eingeloggt als {data['email']}")
                self.connection_status_changed.emit(True)
                # Nach erfolgreichem Login Mäher suchen
                asyncio.create_task(self._discover_mowers_async())
                
            elif event_type == "login_failed":
                self.login_status_changed.emit(False, f"Login fehlgeschlagen: {data['error']}")
                self.connection_status_changed.emit(False)
                
            elif event_type == "logout":
                self.connection_status_changed.emit(False)
                self.status_timer.stop()
                
            elif event_type == "mowers_discovered":
                self.mowers_list_updated.emit(data)
                if data:  # Wenn Mäher gefunden wurden
                    self.status_timer.start()
                    self.notification_requested.emit(
                        "Mäher gefunden", 
                        f"{len(data)} Mäher erfolgreich verbunden", 
                        "success"
                    )
                    
            elif event_type == "current_mower_changed":
                self.current_mower_changed.emit(data)
                
            elif event_type == "mower_status_changed":
                self.mower_status_updated.emit(data)
                self._check_status_notifications(data)
                
            elif event_type == "discovery_failed":
                self.error_occurred.emit("Verbindungsfehler", f"Mäher konnten nicht gefunden werden: {data['error']}")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten von Model-Event {event_type}: {e}")
    
    def _check_status_notifications(self, mower_info: MowerInfo) -> None:
        """Prüft ob Status-Änderungen Benachrichtigungen auslösen sollen"""
        try:
            if mower_info.status == MowerStatus.ERROR and mower_info.error_message:
                self.notification_requested.emit(
                    "Mäher-Fehler",
                    f"{mower_info.name}: {mower_info.error_message}",
                    "error"
                )
            elif mower_info.status == MowerStatus.CHARGING and mower_info.battery_level >= 95:
                self.notification_requested.emit(
                    "Laden abgeschlossen",
                    f"{mower_info.name} ist vollständig geladen ({mower_info.battery_level}%)",
                    "info"
                )
            elif mower_info.battery_level <= 15:
                self.notification_requested.emit(
                    "Niedriger Akkustand",
                    f"{mower_info.name}: Akku bei {mower_info.battery_level}%",
                    "warning"
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Prüfen von Status-Benachrichtigungen: {e}")
    
    async def _discover_mowers_async(self) -> None:
        """Asynchrone Mäher-Suche"""
        try:
            await self.model.discover_mowers()
        except Exception as e:
            self.logger.error(f"Fehler bei der Mäher-Suche: {e}")
    
    def _refresh_current_mower_status(self) -> None:
        """Timer-Callback für regelmäßige Status-Updates"""
        if self.model.is_connected():
            asyncio.create_task(self.model.refresh_status())
    
    # Public Methods für Views
    
    def login(self, email: str, password: str) -> None:
        """
        Startet den Login-Prozess
        
        Args:
            email: E-Mail-Adresse
            password: Passwort
        """
        if not email or not password:
            self.login_status_changed.emit(False, "E-Mail und Passwort sind erforderlich")
            return
            
        # Async Login starten
        asyncio.create_task(self.model.login(email, password))
    
    def logout(self) -> None:
        """Beendet die aktuelle Sitzung"""
        asyncio.create_task(self.model.logout())
    
    def start_mowing(self, device_id: Optional[str] = None) -> None:
        """
        Startet den Mähvorgang
        
        Args:
            device_id: Optional - ID des Mähers, sonst aktueller Mäher
        """
        if not self.model.is_connected():
            self.error_occurred.emit("Nicht verbunden", "Bitte zuerst einloggen")
            return
            
        asyncio.create_task(self._start_mowing_async(device_id))
    
    async def _start_mowing_async(self, device_id: Optional[str]) -> None:
        """Asynchroner Mähstart"""
        try:
            success = await self.model.start_mowing(device_id)
            if success:
                mower = self.model.get_current_mower()
                if mower:
                    self.notification_requested.emit(
                        "Mähvorgang gestartet",
                        f"{mower.name} hat mit dem Mähen begonnen",
                        "success"
                    )
            else:
                self.error_occurred.emit("Fehler", "Mähvorgang konnte nicht gestartet werden")
        except Exception as e:
            self.error_occurred.emit("Fehler", f"Fehler beim Starten: {str(e)}")
    
    def stop_mowing(self, device_id: Optional[str] = None) -> None:
        """
        Stoppt den Mähvorgang
        
        Args:
            device_id: Optional - ID des Mähers, sonst aktueller Mäher
        """
        if not self.model.is_connected():
            self.error_occurred.emit("Nicht verbunden", "Bitte zuerst einloggen")
            return
            
        asyncio.create_task(self._stop_mowing_async(device_id))
    
    async def _stop_mowing_async(self, device_id: Optional[str]) -> None:
        """Asynchroner Mähstopp"""
        try:
            success = await self.model.stop_mowing(device_id)
            if success:
                mower = self.model.get_current_mower()
                if mower:
                    self.notification_requested.emit(
                        "Mähvorgang gestoppt",
                        f"{mower.name} wurde pausiert",
                        "info"
                    )
            else:
                self.error_occurred.emit("Fehler", "Mähvorgang konnte nicht gestoppt werden")
        except Exception as e:
            self.error_occurred.emit("Fehler", f"Fehler beim Stoppen: {str(e)}")
    
    def return_to_dock(self, device_id: Optional[str] = None) -> None:
        """
        Schickt Mäher zur Ladestation
        
        Args:
            device_id: Optional - ID des Mähers, sonst aktueller Mäher
        """
        if not self.model.is_connected():
            self.error_occurred.emit("Nicht verbunden", "Bitte zuerst einloggen")
            return
            
        asyncio.create_task(self._return_to_dock_async(device_id))
    
    async def _return_to_dock_async(self, device_id: Optional[str]) -> None:
        """Asynchrone Rückkehr zur Ladestation"""
        try:
            success = await self.model.return_to_dock(device_id)
            if success:
                mower = self.model.get_current_mower()
                if mower:
                    self.notification_requested.emit(
                        "Rückkehr zur Ladestation",
                        f"{mower.name} kehrt zur Ladestation zurück",
                        "info"
                    )
            else:
                self.error_occurred.emit("Fehler", "Rückkehr zur Ladestation fehlgeschlagen")
        except Exception as e:
            self.error_occurred.emit("Fehler", f"Fehler bei Rückkehr: {str(e)}")
    
    def set_current_mower(self, device_id: str) -> None:
        """
        Setzt den aktuell ausgewählten Mäher
        
        Args:
            device_id: ID des zu wählenden Mähers
        """
        success = self.model.set_current_mower(device_id)
        if not success:
            self.error_occurred.emit("Fehler", "Mäher konnte nicht ausgewählt werden")
    
    def get_current_mower(self) -> Optional[MowerInfo]:
        """Gibt den aktuell ausgewählten Mäher zurück"""
        return self.model.get_current_mower()
    
    def get_all_mowers(self) -> List[MowerInfo]:
        """Gibt alle verfügbaren Mäher zurück"""
        return self.model.get_all_mowers()
    
    def is_connected(self) -> bool:
        """Prüft ob eine Verbindung besteht"""
        return self.model.is_connected()
    
    def refresh_mower_status(self, device_id: Optional[str] = None) -> None:
        """Aktualisiert den Status eines Mähers manuell"""
        asyncio.create_task(self.model.refresh_status(device_id))
    
    def discover_mowers(self) -> None:
        """Startet eine neue Mäher-Suche"""
        if not self.model.is_connected():
            self.error_occurred.emit("Nicht verbunden", "Bitte zuerst einloggen")
            return
            
        asyncio.create_task(self.model.discover_mowers())
    
    def cleanup(self) -> None:
        """Cleanup beim Beenden der Anwendung"""
        try:
            self.status_timer.stop()
            if self.model.is_connected():
                asyncio.create_task(self.model.logout())
        except Exception as e:
            self.logger.error(f"Fehler beim Cleanup: {e}")
