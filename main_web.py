"""
Mammotion Linux App - Web-GUI Version

Verwendet eine robuste Web-basierte Benutzeroberfläche statt Qt.
Garantiert große UI-Elemente ohne Plattform-spezifische Probleme.
"""

import asyncio
import logging
import sys
import os
import threading
import time
from typing import Optional

# Pfad für Imports hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.real_mammotion_client import RealMammotionClient, RealMowerInfo
from views.web_gui import WebGUI
from utils.logging_config import setup_logging


class MammotionWebApp:
    """
    Hauptanwendung mit Web-GUI
    
    Kombiniert die echte Mammotion-API mit einer robusten Web-Oberfläche.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Komponenten
        self.web_gui: Optional[WebGUI] = None
        self.mammotion_client: Optional[RealMammotionClient] = None
        
        # Status
        self.is_running = False
        self.current_mowers = []
        
    async def initialize(self):
        """Initialisiert die Anwendung"""
        self.logger.info("Initialisiere Mammotion Web-App...")
        
        # Web-GUI erstellen
        self.web_gui = WebGUI(port=5000)
        self.web_gui.set_login_callback(self._handle_login)
        self.web_gui.set_command_callback(self._handle_command)
        
        # Mammotion-Client erstellen
        self.mammotion_client = RealMammotionClient()
        
        self.logger.info("Mammotion Web-App initialisiert")
        
    def _handle_login(self, email: str, password: str, remember: bool) -> bool:
        """
        Behandelt Login-Versuche
        
        Args:
            email: E-Mail-Adresse
            password: Passwort
            remember: Zugangsdaten speichern
            
        Returns:
            True wenn erfolgreich
        """
        self.logger.info(f"Login-Versuch für {email}")
        
        try:
            # Verwende einen Thread-Pool für async Operationen um Event-Loop-Konflikte zu vermeiden
            import concurrent.futures
            import threading
            
            def run_async_login():
                """Führt das async Login in einem separaten Thread aus"""
                try:
                    # Neuen Event Loop für diesen Thread erstellen
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def do_login():
                        async with self.mammotion_client as client:
                            # Authentifizierung
                            success = await client.authenticate(email, password)
                            
                            if success:
                                # Mäher suchen
                                mowers = await client.discover_devices()
                                self.current_mowers = mowers
                                
                                # GUI mit Mäher-Daten aktualisieren
                                if mowers:
                                    mower_data = {
                                        'status': mowers[0].status,
                                        'battery_level': mowers[0].battery_level,
                                        'position': f"{mowers[0].position_x:.1f}, {mowers[0].position_y:.1f}",
                                        'model': mowers[0].model,
                                        'name': mowers[0].name
                                    }
                                    self.web_gui.update_mower_data(mower_data)
                                
                                self.logger.info(f"Login erfolgreich - {len(mowers)} Mäher gefunden")
                                return True
                            else:
                                self.logger.error("Login fehlgeschlagen")
                                return False
                    
                    result = loop.run_until_complete(do_login())
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Async Login-Fehler: {e}")
                    return False
                finally:
                    try:
                        loop.close()
                    except:
                        pass
            
            # Login in Thread-Pool ausführen mit Timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_async_login)
                # 30 Sekunden Timeout für Login
                result = future.result(timeout=30)
                return result
            
        except concurrent.futures.TimeoutError:
            self.logger.error("Login-Timeout nach 30 Sekunden")
            return False
        except Exception as e:
            self.logger.error(f"Login-Fehler: {e}")
            return False
            
    def _handle_command(self, device_id: str, command: str) -> bool:
        """
        Behandelt Mäher-Befehle
        
        Args:
            device_id: Geräte-ID
            command: Befehl
            
        Returns:
            True wenn erfolgreich
        """
        self.logger.info(f"Befehl '{command}' für Gerät {device_id}")
        
        try:
            # Verwende einen Thread-Pool für async Operationen
            import concurrent.futures
            
            def run_async_command():
                """Führt das async Command in einem separaten Thread aus"""
                try:
                    # Neuen Event Loop für diesen Thread erstellen
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    async def do_command():
                        async with self.mammotion_client as client:
                            # Befehl senden
                            success = await client.send_command(device_id, command)
                            
                            if success:
                                # Status aktualisieren
                                await self._update_status()
                                
                            return success
                    
                    result = loop.run_until_complete(do_command())
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Async Command-Fehler: {e}")
                    return False
                finally:
                    try:
                        loop.close()
                    except:
                        pass
            
            # Command in Thread-Pool ausführen mit Timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_async_command)
                # 15 Sekunden Timeout für Befehle
                result = future.result(timeout=15)
                return result
                
        except concurrent.futures.TimeoutError:
            self.logger.error("Command-Timeout nach 15 Sekunden")
            return False
        except Exception as e:
            self.logger.error(f"Command-Fehler: {e}")
            return False
            
    async def _update_status(self):
        """Aktualisiert den Mäher-Status"""
        try:
            if self.current_mowers:
                device_id = self.current_mowers[0].device_id
                
                async with self.mammotion_client as client:
                    updated_info = await client.get_device_status(device_id)
                    
                    if updated_info:
                        # GUI aktualisieren
                        mower_data = {
                            'status': updated_info.status,
                            'battery_level': updated_info.battery_level,
                            'position': f"{updated_info.position_x:.1f}, {updated_info.position_y:.1f}",
                            'model': updated_info.model,
                            'name': updated_info.name
                        }
                        self.web_gui.update_mower_data(mower_data)
                        
        except Exception as e:
            self.logger.error(f"Status-Update-Fehler: {e}")
            
    def run(self):
        """Startet die Anwendung"""
        self.logger.info("Starte Mammotion Web-App...")
        self.is_running = True
        
        try:
            # Web-GUI starten (blockiert)
            self.web_gui.start(open_browser=True)
            
        except KeyboardInterrupt:
            self.logger.info("Anwendung durch Benutzer beendet")
        except Exception as e:
            self.logger.error(f"Unerwarteter Fehler: {e}")
        finally:
            self.is_running = False
            self.logger.info("Mammotion Web-App beendet")


async def main():
    """Hauptfunktion"""
    # Logging konfigurieren
    setup_logging()
    
    print("Mammotion Linux App (Web-GUI) wird gestartet...")
    print("GUI-Komponenten geladen:")
    print("✓ Web-basierte Benutzeroberfläche")
    print("✓ Responsive Design mit großen UI-Elementen")
    print("✓ Echte Mammotion-API-Integration")
    print("✓ Plattformunabhängige Darstellung")
    print()
    print("Hinweis: Öffnet automatisch Browser-Fenster")
    print("URL: http://localhost:5000")
    print()
    
    try:
        # App erstellen und initialisieren
        app = MammotionWebApp()
        await app.initialize()
        
        # App starten (blockiert bis beendet)
        app.run()
        
    except Exception as e:
        logging.error(f"Fehler beim Ausführen der App: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nAnwendung beendet")
        sys.exit(0)
    except Exception as e:
        print(f"Kritischer Fehler: {e}")
        sys.exit(1)
