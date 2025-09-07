"""
App - Hauptanwendungsklasse

Diese Klasse koordiniert alle Komponenten der Anwendung und verbindet
Model, View und Controller miteinander.
"""

import sys
import asyncio
from typing import Optional

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, QObject, Signal

from .login_window import LoginWindow
from .main_window import MainWindow
from ..controllers.main_controller import MainController
from ..utils.logging_config import LoggerMixin


class NotificationHandler(QObject):
    """Handler für Desktop-Benachrichtigungen"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def show_notification(self, title: str, message: str, notification_type: str):
        """
        Zeigt eine Desktop-Benachrichtigung
        
        Args:
            title: Titel der Benachrichtigung
            message: Nachrichtentext
            notification_type: Typ (success, info, warning, error)
        """
        # Für jetzt verwenden wir QMessageBox
        # In einer späteren Version können wir echte Desktop-Notifications implementieren
        
        if notification_type == "error":
            QMessageBox.critical(None, title, message)
        elif notification_type == "warning":
            QMessageBox.warning(None, title, message)
        else:
            QMessageBox.information(None, title, message)


class MammotionApp(QObject, LoggerMixin):
    """
    Hauptanwendungsklasse der Mammotion App
    
    Koordiniert alle Komponenten und verwaltet den Anwendungslebenszyklus.
    """
    
    def __init__(self, qt_app: QApplication):
        super().__init__()
        self.qt_app = qt_app
        
        # Komponenten
        self.controller = MainController()
        self.main_window: Optional[MainWindow] = None
        self.login_window: Optional[LoginWindow] = None
        self.notification_handler = NotificationHandler()
        
        # Status
        self._is_initialized = False
        
        # Event Loop für Async-Integration
        self.async_timer = QTimer()
        self.async_timer.timeout.connect(self._process_async_events)
        self.async_timer.start(50)  # 50ms Intervall
        
        self._setup_connections()
        
    def _setup_connections(self):
        """Verbindet Controller-Signals mit App-Methoden"""
        # Controller -> App
        self.controller.login_status_changed.connect(self._on_login_status_changed)
        self.controller.connection_status_changed.connect(self._on_connection_status_changed)
        self.controller.mower_status_updated.connect(self._on_mower_status_updated)
        self.controller.mowers_list_updated.connect(self._on_mowers_list_updated)
        self.controller.current_mower_changed.connect(self._on_current_mower_changed)
        self.controller.error_occurred.connect(self._on_error_occurred)
        self.controller.notification_requested.connect(self._on_notification_requested)
        
    def _process_async_events(self):
        """Verarbeitet Async-Events im Qt Event Loop"""
        try:
            # Kurz den Async Event Loop laufen lassen
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Bereits laufender Loop - nichts zu tun
                pass
            else:
                # Pending Tasks verarbeiten
                pending = asyncio.all_tasks(loop)
                if pending:
                    loop.run_until_complete(asyncio.sleep(0))
        except Exception as e:
            self.logger.debug(f"Async event processing: {e}")
            
    def initialize(self):
        """Initialisiert die Anwendung"""
        if self._is_initialized:
            return
            
        self.logger.info("Initialisiere Mammotion App...")
        
        # Hauptfenster erstellen
        self.main_window = MainWindow()
        self._connect_main_window_signals()
        
        # Login-Dialog anzeigen
        self._show_login()
        
        self._is_initialized = True
        self.logger.info("App erfolgreich initialisiert")
        
    def _connect_main_window_signals(self):
        """Verbindet Hauptfenster-Signals"""
        if not self.main_window:
            return
            
        # Main Window -> Controller
        self.main_window.login_requested.connect(self._show_login)
        self.main_window.logout_requested.connect(self.controller.logout)
        self.main_window.mower_selection_changed.connect(self.controller.set_current_mower)
        
        # Control Widget -> Controller
        control_widget = self.main_window.get_control_widget()
        control_widget.start_mowing_requested.connect(self.controller.start_mowing)
        control_widget.stop_mowing_requested.connect(self.controller.stop_mowing)
        control_widget.return_to_dock_requested.connect(self.controller.return_to_dock)
        control_widget.refresh_status_requested.connect(self.controller.refresh_mower_status)
        
    def _show_login(self):
        """Zeigt den Login-Dialog"""
        if self.login_window:
            self.login_window.close()
            
        self.login_window = LoginWindow(self.main_window)
        
        # Login Window -> Controller
        self.login_window.login_requested.connect(self._on_login_requested)
        self.login_window.login_cancelled.connect(self._on_login_cancelled)
        
        # Dialog anzeigen
        self.login_window.show()
        
    def _on_login_requested(self, email: str, password: str, remember: bool):
        """Behandelt Login-Anfrage"""
        self.logger.info(f"Login-Versuch für {email}")
        self.controller.login(email, password)
        
        # TODO: remember-Flag für Passwort-Speicherung verwenden
        
    def _on_login_cancelled(self):
        """Behandelt Login-Abbruch"""
        if not self.controller.is_connected():
            # Wenn nicht verbunden und Login abgebrochen -> App beenden
            self.quit()
        
    def _on_login_status_changed(self, success: bool, message: str):
        """Behandelt Login-Status-Änderung"""
        if not self.login_window:
            return
            
        if success:
            self.login_window.on_login_success()
            self.main_window.show()
            self.logger.info("Login erfolgreich")
        else:
            self.login_window.on_login_failed(message)
            self.logger.warning(f"Login fehlgeschlagen: {message}")
            
    def _on_connection_status_changed(self, connected: bool):
        """Behandelt Verbindungsstatus-Änderung"""
        if self.main_window:
            self.main_window.update_connection_status(connected)
            
        if not connected and self.main_window and self.main_window.isVisible():
            # Verbindung verloren -> Login erneut anzeigen
            self._show_login()
            
    def _on_mower_status_updated(self, mower_info):
        """Behandelt Mäher-Status-Update"""
        if self.main_window:
            self.main_window.update_current_mower(mower_info)
            
    def _on_mowers_list_updated(self, mowers: list):
        """Behandelt Update der Mäher-Liste"""
        if self.main_window:
            self.main_window.update_mower_list(mowers)
            
    def _on_current_mower_changed(self, mower_info):
        """Behandelt Änderung des aktuellen Mähers"""
        if self.main_window:
            self.main_window.update_current_mower(mower_info)
            
    def _on_error_occurred(self, title: str, message: str):
        """Behandelt Fehler"""
        self.logger.error(f"{title}: {message}")
        if self.main_window:
            self.main_window.show_error(title, message)
            
    def _on_notification_requested(self, title: str, message: str, notification_type: str):
        """Behandelt Benachrichtigungsanfrage"""
        self.logger.info(f"Notification: {title} - {message}")
        self.notification_handler.show_notification(title, message, notification_type)
        
    def run(self) -> int:
        """Startet die Anwendung"""
        try:
            self.initialize()
            return self.qt_app.exec()
        except Exception as e:
            self.logger.error(f"Fehler beim Ausführen der App: {e}")
            return 1
        finally:
            self.cleanup()
            
    def quit(self):
        """Beendet die Anwendung"""
        self.logger.info("Beende Anwendung...")
        self.qt_app.quit()
        
    def cleanup(self):
        """Cleanup beim Beenden"""
        try:
            self.async_timer.stop()
            
            if self.controller:
                self.controller.cleanup()
                
            if self.login_window:
                self.login_window.close()
                
            if self.main_window:
                self.main_window.close()
                
            self.logger.info("Cleanup abgeschlossen")
        except Exception as e:
            self.logger.error(f"Fehler beim Cleanup: {e}")


def create_app() -> MammotionApp:
    """
    Factory-Funktion zum Erstellen der Anwendung
    
    Returns:
        Konfigurierte MammotionApp-Instanz
    """
    # Qt Application erstellen
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Mammotion Linux App")
    qt_app.setApplicationVersion("0.1.0")
    qt_app.setOrganizationName("Mammotion Linux App Team")
    
    # High DPI Support (Qt6-kompatibel)
    try:
        # Versuche Qt5-Style Attribute (für Rückwärtskompatibilität)
        if hasattr(qt_app, 'AA_EnableHighDpiScaling'):
            qt_app.setAttribute(qt_app.AA_EnableHighDpiScaling, True)
        if hasattr(qt_app, 'AA_UseHighDpiPixmaps'):
            qt_app.setAttribute(qt_app.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # Qt6: High DPI ist standardmäßig aktiviert
        pass
    
    # Zusätzliche Font-Optimierungen für High-DPI
    font = qt_app.font()
    if font.pointSize() < 12:
        font.setPointSize(12)  # Mindestschriftgröße für bessere Lesbarkeit
    qt_app.setFont(font)
    
    # Mammotion App erstellen
    app = MammotionApp(qt_app)
    
    return app
