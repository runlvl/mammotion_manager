#!/usr/bin/env python3
"""
Mammotion Linux App - Haupteinstiegspunkt

Startet die Mammotion Mähroboter-Verwaltungsanwendung mit vollständiger GUI.
"""

import sys
import os
from pathlib import Path

# Füge src-Verzeichnis zum Python-Pfad hinzu
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.utils.logging_config import setup_development_logging


def main():
    """Hauptfunktion der Anwendung"""
    
    # Logging konfigurieren
    setup_development_logging()
    
    try:
        # App erstellen und starten
        from src.views import create_app
        
        app = create_app()
        
        print("Mammotion Linux App wird gestartet...")
        print("GUI-Komponenten geladen:")
        print("✓ Login-Fenster")
        print("✓ Hauptfenster mit Status-Anzeige")
        print("✓ Steuerknöpfe")
        print("✓ Model-View-Controller-Architektur")
        print("\nHinweis: PyMammotion läuft im Mock-Modus (Entwicklung)")
        
        return app.run()
        
    except ImportError as e:
        print(f"Fehler beim Importieren von Abhängigkeiten: {e}")
        print("\nBitte installieren Sie alle Abhängigkeiten:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
