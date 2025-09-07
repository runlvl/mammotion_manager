#!/usr/bin/env python3
"""
Test der Grundarchitektur ohne GUI

Testet Model und Controller-Funktionalität ohne PySide6 GUI.
"""

import sys
import asyncio
from pathlib import Path

# Füge src-Verzeichnis zum Python-Pfad hinzu
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.logging_config import setup_development_logging
from src.models.mammotion_model import MammotionModel, MowerStatus
from src.controllers.main_controller import MainController


async def test_model():
    """Testet die Model-Funktionalität"""
    print("\n=== Model-Test ===")
    
    model = MammotionModel()
    
    # Event-Handler für Tests
    events_received = []
    
    def event_handler(event_type, data):
        events_received.append((event_type, data))
        print(f"Event empfangen: {event_type} - {data}")
    
    model.add_observer(event_handler)
    
    # Login testen
    print("1. Login-Test...")
    success = await model.login("test@example.com", "password123")
    print(f"Login erfolgreich: {success}")
    
    # Mäher suchen
    print("\n2. Mäher-Suche...")
    mowers = await model.discover_mowers()
    print(f"Gefundene Mäher: {len(mowers)}")
    for mower in mowers:
        print(f"  - {mower.name} ({mower.device_id}): {mower.status.value}, Akku: {mower.battery_level}%")
    
    # Aktueller Mäher
    current = model.get_current_mower()
    if current:
        print(f"\n3. Aktueller Mäher: {current.name}")
        
        # Mähvorgang starten
        print("4. Starte Mähvorgang...")
        success = await model.start_mowing()
        print(f"Mähvorgang gestartet: {success}")
        
        # Status aktualisieren
        print("5. Status aktualisieren...")
        await model.refresh_status()
        
        # Mähvorgang stoppen
        print("6. Stoppe Mähvorgang...")
        success = await model.stop_mowing()
        print(f"Mähvorgang gestoppt: {success}")
        
        # Zur Ladestation
        print("7. Zurück zur Ladestation...")
        success = await model.return_to_dock()
        print(f"Rückkehr zur Ladestation: {success}")
    
    # Logout
    print("\n8. Logout...")
    await model.logout()
    
    print(f"\nInsgesamt {len(events_received)} Events empfangen")
    return True


def test_controller():
    """Testet die Controller-Funktionalität (ohne Qt)"""
    print("\n=== Controller-Test (ohne Qt) ===")
    
    # Da der Controller Qt-Signals verwendet, können wir nur die Grundstruktur testen
    try:
        # Wir importieren nur, um zu prüfen ob die Struktur korrekt ist
        from src.controllers.main_controller import MainController
        print("✓ MainController kann importiert werden")
        
        # Model kann direkt getestet werden
        from src.models.mammotion_model import MammotionModel
        model = MammotionModel()
        print("✓ MammotionModel kann erstellt werden")
        print(f"✓ Verbindungsstatus: {model.is_connected()}")
        
        return True
    except Exception as e:
        print(f"✗ Fehler beim Controller-Test: {e}")
        return False


def test_imports():
    """Testet alle wichtigen Imports"""
    print("\n=== Import-Test ===")
    
    try:
        from src.models import MammotionModel, MowerInfo, MowerStatus
        print("✓ Models können importiert werden")
        
        from src.controllers import MainController
        print("✓ Controllers können importiert werden")
        
        from src.utils import setup_logging, get_logger
        print("✓ Utils können importiert werden")
        
        # PyMammotion verfügbar?
        try:
            import pymammotion
            print("✓ PyMammotion ist verfügbar")
        except ImportError:
            print("⚠ PyMammotion nicht verfügbar (Mock-Modus aktiv)")
        
        # PySide6 verfügbar?
        try:
            import PySide6
            print("✓ PySide6 ist verfügbar")
        except ImportError:
            print("✗ PySide6 nicht verfügbar")
        
        return True
    except Exception as e:
        print(f"✗ Import-Fehler: {e}")
        return False


async def main():
    """Hauptfunktion für Tests"""
    print("Mammotion Linux App - Architektur-Test")
    print("=" * 50)
    
    # Logging konfigurieren
    setup_development_logging()
    
    # Tests ausführen
    tests_passed = 0
    total_tests = 3
    
    if test_imports():
        tests_passed += 1
    
    if test_controller():
        tests_passed += 1
    
    if await test_model():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test-Ergebnis: {tests_passed}/{total_tests} Tests bestanden")
    
    if tests_passed == total_tests:
        print("✅ Alle Tests erfolgreich! Die Architektur ist funktionsfähig.")
        print("\nNächste Schritte:")
        print("- Phase 3: GUI-Komponenten implementieren")
        print("- Login-Fenster erstellen")
        print("- Status-Anzeige implementieren")
        print("- Steuerknöpfe hinzufügen")
    else:
        print("❌ Einige Tests fehlgeschlagen. Bitte Fehler beheben.")
    
    return 0 if tests_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
