"""
Test der Web-GUI ohne PyMammotion-Abhängigkeiten

Zeigt die robuste Web-Oberfläche mit großen UI-Elementen.
"""

import sys
import os
import logging

# Pfad für Imports hinzufügen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from views.web_gui import WebGUI


def test_web_gui():
    """Test-Funktion für die Web-GUI"""
    
    def on_login(email, password, remember):
        print(f"Login-Test: {email}, {password}, {remember}")
        
        # Simuliere erfolgreichen Login
        if email and password:
            return True
        else:
            return False
        
    def on_command(device_id, command):
        print(f"Command-Test: {device_id}, {command}")
        return True  # Simuliere erfolgreichen Befehl
        
    print("=== Mammotion Web-GUI Test ===")
    print()
    print("✓ Web-basierte Benutzeroberfläche")
    print("✓ Große UI-Elemente (80px Eingabefelder)")
    print("✓ Responsive Design")
    print("✓ Plattformunabhängig")
    print("✓ Keine Qt-Probleme")
    print()
    print("Starte Web-Server auf http://localhost:5000")
    print("Browser öffnet sich automatisch...")
    print()
    print("Drücken Sie Ctrl+C zum Beenden")
    print()
    
    # Web-GUI erstellen
    gui = WebGUI(port=5000)
    gui.set_login_callback(on_login)
    gui.set_command_callback(on_command)
    
    # Test-Mäher-Daten
    gui.update_mower_data({
        'status': 'Bereit',
        'battery_level': 85,
        'position': 'Ladestation',
        'model': 'Luba 2 AWD',
        'name': 'Test-Mäher'
    })
    
    try:
        gui.start(open_browser=True)
    except KeyboardInterrupt:
        print("\nWeb-GUI Test beendet")
    except Exception as e:
        print(f"Fehler: {e}")


if __name__ == "__main__":
    test_web_gui()
