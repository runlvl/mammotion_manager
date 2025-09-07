#!/usr/bin/env python3
"""
Qt6-Kompatibilitäts-Fix für Mammotion Linux App

Behebt Kompatibilitätsprobleme mit neueren PySide6/Qt6-Versionen.
"""

import os
import sys
from pathlib import Path


def fix_qt6_compatibility():
    """Behebt Qt6-Kompatibilitätsprobleme"""
    
    print("🔧 Qt6-Kompatibilitäts-Fix für Mammotion Linux App")
    print("=" * 50)
    
    # Finde App-Verzeichnis
    script_dir = Path(__file__).parent
    app_py_path = script_dir / "src" / "views" / "app.py"
    
    if not app_py_path.exists():
        print("❌ app.py nicht gefunden. Bitte im App-Verzeichnis ausführen.")
        return False
    
    print(f"📁 Bearbeite: {app_py_path}")
    
    # Lese aktuelle Datei
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup erstellen
    backup_path = app_py_path.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup erstellt: {backup_path}")
    
    # Fixes anwenden
    fixes_applied = 0
    
    # Fix 1: AA_EnableHighDpiScaling
    old_pattern = """    # High DPI Support
    qt_app.setAttribute(qt_app.AA_EnableHighDpiScaling, True)
    qt_app.setAttribute(qt_app.AA_UseHighDpiPixmaps, True)"""
    
    new_pattern = """    # High DPI Support (Qt6-kompatibel)
    try:
        # Versuche Qt5-Style Attribute (für Rückwärtskompatibilität)
        if hasattr(qt_app, 'AA_EnableHighDpiScaling'):
            qt_app.setAttribute(qt_app.AA_EnableHighDpiScaling, True)
        if hasattr(qt_app, 'AA_UseHighDpiPixmaps'):
            qt_app.setAttribute(qt_app.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        # Qt6: High DPI ist standardmäßig aktiviert
        pass"""
    
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        fixes_applied += 1
        print("✅ Fix 1: AA_EnableHighDpiScaling-Kompatibilität")
    
    # Schreibe geänderte Datei
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🎉 {fixes_applied} Fixes angewendet!")
    return fixes_applied > 0


def fix_pymammotion_imports():
    """Behebt PyMammotion-Import-Probleme"""
    
    print("\n🔧 PyMammotion-Import-Fix")
    print("=" * 30)
    
    # Finde Model-Datei
    script_dir = Path(__file__).parent
    model_py_path = script_dir / "src" / "models" / "mammotion_model.py"
    
    if not model_py_path.exists():
        print("❌ mammotion_model.py nicht gefunden.")
        return False
    
    print(f"📁 Bearbeite: {model_py_path}")
    
    # Lese aktuelle Datei
    with open(model_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup erstellen
    backup_path = model_py_path.with_suffix('.py.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup erstellt: {backup_path}")
    
    # Fix: MowerData-Import entfernen
    old_import = "        from pymammotion.data.model import MowerData"
    new_import = "        # MowerData wird nicht benötigt - wir verwenden unsere eigene MowerInfo-Klasse"
    
    fixes_applied = 0
    if old_import in content:
        content = content.replace(old_import, new_import)
        fixes_applied += 1
        print("✅ Fix: MowerData-Import entfernt")
    
    # Schreibe geänderte Datei
    with open(model_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🎉 {fixes_applied} Import-Fixes angewendet!")
    return fixes_applied > 0


def test_fixes():
    """Testet ob die Fixes funktionieren"""
    
    print("\n🧪 Teste Fixes...")
    print("=" * 20)
    
    try:
        # Test GUI-Import
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from src.views import create_app
        print("✅ GUI-Import erfolgreich")
        
        # Test App-Erstellung (ohne Ausführung)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = create_app()
        print("✅ App-Erstellung erfolgreich")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False


def main():
    """Hauptfunktion"""
    
    print("Mammotion Linux App - Qt6-Kompatibilitäts-Fix")
    print("=" * 50)
    
    success = True
    
    # Qt6-Fixes anwenden
    if not fix_qt6_compatibility():
        success = False
    
    # PyMammotion-Fixes anwenden
    if not fix_pymammotion_imports():
        success = False
    
    # Tests ausführen
    if success and test_fixes():
        print("\n🎉 Alle Fixes erfolgreich angewendet!")
        print("\nDie App sollte jetzt funktionieren:")
        print("  python3 main.py")
    else:
        print("\n❌ Einige Fixes fehlgeschlagen.")
        print("Bitte prüfen Sie die Backup-Dateien und versuchen Sie es manuell.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
