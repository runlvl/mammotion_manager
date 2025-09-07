#!/usr/bin/env python3
"""
Test der GUI-Komponenten

Testet die GUI-Komponenten ohne tatsächliche Anzeige (für Headless-Umgebungen).
"""

import sys
import os
from pathlib import Path

# Füge src-Verzeichnis zum Python-Pfad hinzu
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.logging_config import setup_development_logging


def test_imports():
    """Testet alle GUI-Imports"""
    print("=== GUI-Import-Test ===")
    
    try:
        # PySide6 verfügbar?
        import PySide6
        from PySide6.QtWidgets import QApplication
        print("✓ PySide6 ist verfügbar")
        
        # Views importieren
        from src.views import LoginWindow, MainWindow, MammotionApp, create_app
        print("✓ GUI-Komponenten können importiert werden")
        
        # Models und Controllers
        from src.models import MammotionModel, MowerInfo, MowerStatus
        from src.controllers import MainController
        print("✓ Model und Controller können importiert werden")
        
        return True
    except Exception as e:
        print(f"✗ Import-Fehler: {e}")
        return False


def test_component_creation():
    """Testet die Erstellung von GUI-Komponenten (ohne Anzeige)"""
    print("\n=== GUI-Komponenten-Erstellungstest ===")
    
    try:
        # Minimal Qt App für Tests (global verwenden)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Headless-Modus
        
        from PySide6.QtWidgets import QApplication
        
        # Prüfe ob bereits eine App existiert
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Login Window
        from src.views import LoginWindow
        login_window = LoginWindow()
        print("✓ LoginWindow kann erstellt werden")
        login_window.close()
        
        # Main Window
        from src.views import MainWindow
        main_window = MainWindow()
        print("✓ MainWindow kann erstellt werden")
        main_window.close()
        
        print("✓ GUI-Komponenten erfolgreich erstellt")
        
        return True
    except Exception as e:
        print(f"✗ Komponenten-Erstellungsfehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_integration():
    """Testet die Integration zwischen Model und GUI"""
    print("\n=== Model-GUI-Integrationstest ===")
    
    try:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PySide6.QtWidgets import QApplication
        
        # Verwende existierende App oder erstelle neue
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Controller erstellen
        from src.controllers import MainController
        controller = MainController()
        print("✓ MainController erstellt")
        
        # Model-Daten erstellen
        from src.models import MowerInfo, MowerStatus
        mock_mower = MowerInfo(
            device_id="test_001",
            name="Test Mäher",
            model="Luba 2 AWD",
            battery_level=75,
            status=MowerStatus.IDLE,
            position={"lat": 52.5200, "lon": 13.4050}
        )
        print("✓ Mock-Mäher-Daten erstellt")
        
        # Main Window mit Mock-Daten
        from src.views import MainWindow
        main_window = MainWindow()
        main_window.update_current_mower(mock_mower)
        main_window.update_connection_status(True)
        print("✓ MainWindow mit Mock-Daten aktualisiert")
        
        # Cleanup
        controller.cleanup()
        main_window.close()
        
        return True
    except Exception as e:
        print(f"✗ Integrationsfehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_architecture_completeness():
    """Testet die Vollständigkeit der Architektur"""
    print("\n=== Architektur-Vollständigkeitstest ===")
    
    try:
        # Alle wichtigen Klassen verfügbar?
        from src.models import MammotionModel, MowerInfo, MowerStatus
        from src.controllers import MainController
        from src.views import LoginWindow, MainWindow, MammotionApp
        from src.utils import setup_logging, get_logger
        
        print("✓ Alle Architektur-Komponenten verfügbar")
        
        # Prüfe wichtige Methoden
        model = MammotionModel()
        assert hasattr(model, 'login'), "Model hat login-Methode"
        assert hasattr(model, 'discover_mowers'), "Model hat discover_mowers-Methode"
        assert hasattr(model, 'start_mowing'), "Model hat start_mowing-Methode"
        print("✓ Model-Interface vollständig")
        
        # Controller-Interface (ohne neue QApplication)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PySide6.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        controller = MainController()
        assert hasattr(controller, 'login'), "Controller hat login-Methode"
        assert hasattr(controller, 'start_mowing'), "Controller hat start_mowing-Methode"
        print("✓ Controller-Interface vollständig")
        
        return True
    except Exception as e:
        print(f"✗ Architektur-Fehler: {e}")
        return False


def main():
    """Hauptfunktion für GUI-Tests"""
    print("Mammotion Linux App - GUI-Komponenten-Test")
    print("=" * 50)
    
    # Logging konfigurieren
    setup_development_logging()
    
    # Tests ausführen
    tests_passed = 0
    total_tests = 4
    
    if test_imports():
        tests_passed += 1
    
    if test_component_creation():
        tests_passed += 1
    
    if test_model_integration():
        tests_passed += 1
    
    if test_architecture_completeness():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test-Ergebnis: {tests_passed}/{total_tests} Tests bestanden")
    
    if tests_passed == total_tests:
        print("✅ Alle GUI-Tests erfolgreich!")
        print("\nImplementierte Komponenten:")
        print("• LoginWindow - Anmeldefenster mit Validierung")
        print("• MainWindow - Hauptfenster mit Status und Steuerung")
        print("• StatusWidget - Mäher-Status-Anzeige")
        print("• ControlWidget - Steuerknöpfe")
        print("• MammotionApp - Hauptanwendungsklasse")
        print("• Vollständige MVC-Architektur")
        print("\nNächste Schritte:")
        print("- Phase 4: Kamera-Feed Integration")
        print("- Phase 5: Desktop-Benachrichtigungen")
        print("- Phase 6: Interaktive Karte")
    else:
        print("❌ Einige GUI-Tests fehlgeschlagen.")
    
    return 0 if tests_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
