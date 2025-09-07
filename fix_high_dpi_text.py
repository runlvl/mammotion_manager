#!/usr/bin/env python3
"""
High-DPI Text-Fix für Mammotion Linux App

Behebt gestauchte Texte und zu kleine UI-Elemente auf High-DPI-Displays.
"""

import os
import sys
import re
from pathlib import Path


def fix_login_window_styles():
    """Behebt Styles im Login-Fenster"""
    
    print("🔧 Fixe Login-Fenster Styles...")
    
    script_dir = Path(__file__).parent
    login_py_path = script_dir / "src" / "views" / "login_window.py"
    
    if not login_py_path.exists():
        print("❌ login_window.py nicht gefunden")
        return False
    
    # Backup erstellen
    backup_path = login_py_path.with_suffix('.py.backup')
    with open(login_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Neue Styles mit besserer High-DPI-Unterstützung
    new_styles = '''        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin: 15px 0;
                line-height: 1.3;
            }
            QLabel#subtitle {
                font-size: 16px;
                color: #7f8c8d;
                margin-bottom: 25px;
                line-height: 1.4;
            }
            QLabel {
                font-size: 16px;
                color: #2c3e50;
                line-height: 1.4;
                margin: 8px 0;
            }
            QLineEdit {
                padding: 16px 12px;
                min-height: 28px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 16px;
                background-color: white;
                line-height: 1.5;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            QPushButton#primary {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 16px 24px;
                min-height: 28px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                line-height: 1.4;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QPushButton#primary:hover {
                background-color: #229954;
            }
            QPushButton#primary:pressed {
                background-color: #1e8449;
            }
            QPushButton#primary:disabled {
                background-color: #95a5a6;
            }
            QPushButton#secondary {
                background-color: #ecf0f1;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                padding: 16px 24px;
                min-height: 28px;
                border-radius: 6px;
                font-size: 16px;
                line-height: 1.4;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QPushButton#secondary:hover {
                background-color: #d5dbdb;
                border-color: #95a5a6;
            }
            QPushButton#secondary:pressed {
                background-color: #bdc3c7;
            }
        """)'''
    
    # Ersetze alte Styles
    pattern = r'self\.setStyleSheet\(""".*?"""\)'
    content = re.sub(pattern, new_styles, content, flags=re.DOTALL)
    
    # Schreibe geänderte Datei
    with open(login_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Login-Fenster Styles aktualisiert")
    return True


def fix_main_window_styles():
    """Behebt Styles im Hauptfenster"""
    
    print("🔧 Fixe Hauptfenster Styles...")
    
    script_dir = Path(__file__).parent
    main_py_path = script_dir / "src" / "views" / "main_window.py"
    
    if not main_py_path.exists():
        print("❌ main_window.py nicht gefunden")
        return False
    
    # Backup erstellen
    backup_path = main_py_path.with_suffix('.py.backup')
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Fixe Status-Label Styles
    content = content.replace(
        'self.status_label.setStyleSheet("font-weight: bold; color: #e74c3c;")',
        'self.status_label.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 16px; line-height: 1.4;")'
    )
    
    # Fixe Connection-Label Styles
    content = content.replace(
        'self.connection_label.setStyleSheet("color: #27ae60; font-weight: bold;")',
        'self.connection_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 16px; line-height: 1.4;")'
    )
    content = content.replace(
        'self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold;")',
        'self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 16px; line-height: 1.4;")'
    )
    
    # Neue Button-Styles für Hauptfenster
    new_button_styles = '''        # Styling
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
                font-size: 16px;
                line-height: 1.4;
            }
            QLabel {
                font-size: 16px;
                line-height: 1.4;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                padding: 16px 20px;
                min-height: 32px;
                line-height: 1.4;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QPushButton#start {
                background-color: #27ae60;
            }
            QPushButton#start:hover {
                background-color: #229954;
            }
            QPushButton#stop {
                background-color: #e74c3c;
            }
            QPushButton#stop:hover {
                background-color: #c0392b;
            }
            QPushButton#dock {
                background-color: #f39c12;
            }
            QPushButton#dock:hover {
                background-color: #e67e22;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                text-align: center;
                font-size: 14px;
                font-weight: bold;
                min-height: 24px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 4px;
            }
            QComboBox {
                padding: 12px 8px;
                min-height: 24px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 16px;
                background-color: white;
                line-height: 1.4;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)'''
    
    # Ersetze Button-Styles
    pattern = r'# Styling\s*self\.setStyleSheet\(""".*?"""\)'
    content = re.sub(pattern, new_button_styles, content, flags=re.DOTALL)
    
    # Schreibe geänderte Datei
    with open(main_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Hauptfenster Styles aktualisiert")
    return True


def fix_app_dpi_settings():
    """Verbessert DPI-Einstellungen in der App"""
    
    print("🔧 Fixe App DPI-Einstellungen...")
    
    script_dir = Path(__file__).parent
    app_py_path = script_dir / "src" / "views" / "app.py"
    
    if not app_py_path.exists():
        print("❌ app.py nicht gefunden")
        return False
    
    # Backup erstellen
    backup_path = app_py_path.with_suffix('.py.backup')
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verbesserte DPI-Einstellungen
    new_dpi_code = '''    # High DPI Support (Qt6-kompatibel)
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
    qt_app.setFont(font)'''
    
    # Ersetze DPI-Code
    pattern = r'# High DPI Support.*?pass'
    content = re.sub(pattern, new_dpi_code, content, flags=re.DOTALL)
    
    # Schreibe geänderte Datei
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ App DPI-Einstellungen aktualisiert")
    return True


def test_fixes():
    """Testet die Fixes"""
    
    print("\n🧪 Teste High-DPI-Fixes...")
    
    try:
        # Test GUI-Import
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from src.views import create_app
        print("✅ GUI-Import erfolgreich")
        
        # Test App-Erstellung (ohne Ausführung)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        app = create_app()
        print("✅ App-Erstellung mit neuen Styles erfolgreich")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False


def main():
    """Hauptfunktion"""
    
    print("Mammotion Linux App - High-DPI Text-Fix")
    print("=" * 50)
    
    success = True
    
    # Alle Fixes anwenden
    if not fix_login_window_styles():
        success = False
    
    if not fix_main_window_styles():
        success = False
    
    if not fix_app_dpi_settings():
        success = False
    
    # Tests ausführen
    if success and test_fixes():
        print("\n🎉 Alle High-DPI-Fixes erfolgreich angewendet!")
        print("\nVerbesserungen:")
        print("  ✅ Größere Schriftarten (16px statt 14px)")
        print("  ✅ Bessere line-height (1.4-1.5)")
        print("  ✅ Mehr padding in allen Elementen")
        print("  ✅ Mindesthöhen für bessere Darstellung")
        print("  ✅ Optimierte Font-Familie")
        print("  ✅ Verbesserte DPI-Skalierung")
        print("\nDie App sollte jetzt viel besser lesbar sein:")
        print("  python3 main.py")
    else:
        print("\n❌ Einige Fixes fehlgeschlagen.")
        print("Bitte prüfen Sie die Backup-Dateien.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
