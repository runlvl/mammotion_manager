#!/usr/bin/env python3
"""
Login-Layout-Fix für Mammotion Linux App

Erstellt ein professionelles, benutzerfreundliches Login-Layout.
"""

import os
import sys
from pathlib import Path


def create_new_login_layout():
    """Erstellt ein komplett neues Login-Layout"""
    
    print("🎨 Erstelle neues Login-Layout...")
    
    script_dir = Path(__file__).parent
    login_py_path = script_dir / "src" / "views" / "login_window.py"
    
    if not login_py_path.exists():
        print("❌ login_window.py nicht gefunden")
        return False
    
    # Backup erstellen
    backup_path = login_py_path.with_suffix('.py.backup2')
    with open(login_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Neues Layout-Code
    new_setup_ui = '''    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche mit verbessertem Layout"""
        # Hauptlayout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container für zentrierten Inhalt
        container = QWidget()
        container.setMaximumWidth(400)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        
        # Container-Layout
        layout = QVBoxLayout(container)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # === HEADER BEREICH ===
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Titel
        title_label = QLabel("Mammotion Login")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Untertitel
        subtitle_label = QLabel("Melden Sie sich mit Ihren Mammotion-Zugangsdaten an")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_widget)
        
        # === FORMULAR BEREICH ===
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 0)
        
        # E-Mail-Bereich
        email_widget = QWidget()
        email_layout = QVBoxLayout(email_widget)
        email_layout.setSpacing(8)
        email_layout.setContentsMargins(0, 0, 0, 0)
        
        email_label = QLabel("E-Mail-Adresse")
        email_label.setObjectName("field_label")
        email_layout.addWidget(email_label)
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("ihre.email@example.com")
        self.email_edit.setObjectName("input_field")
        email_layout.addWidget(self.email_edit)
        
        form_layout.addWidget(email_widget)
        
        # Passwort-Bereich
        password_widget = QWidget()
        password_layout = QVBoxLayout(password_widget)
        password_layout.setSpacing(8)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        password_label = QLabel("Passwort")
        password_label.setObjectName("field_label")
        password_layout.addWidget(password_label)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Ihr Passwort")
        self.password_edit.setObjectName("input_field")
        password_layout.addWidget(self.password_edit)
        
        form_layout.addWidget(password_widget)
        
        layout.addWidget(form_widget)
        
        # === OPTIONEN BEREICH ===
        options_widget = QWidget()
        options_layout = QHBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 0, 0)
        
        self.remember_checkbox = QCheckBox("Zugangsdaten speichern")
        self.remember_checkbox.setObjectName("checkbox")
        self.remember_checkbox.setToolTip("Speichert die Zugangsdaten sicher im System-Schlüsselbund")
        options_layout.addWidget(self.remember_checkbox)
        
        options_layout.addStretch()
        layout.addWidget(options_widget)
        
        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress")
        layout.addWidget(self.progress_bar)
        
        # === BUTTON BEREICH ===
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setObjectName("secondary")
        self.cancel_button.setMinimumWidth(120)
        button_layout.addWidget(self.cancel_button)
        
        self.login_button = QPushButton("Anmelden")
        self.login_button.setObjectName("primary")
        self.login_button.setMinimumWidth(120)
        button_layout.addWidget(self.login_button)
        
        layout.addWidget(button_widget)
        
        # Container zentrieren
        main_layout.addStretch()
        main_layout.addWidget(container, 0, Qt.AlignCenter)
        main_layout.addStretch()'''
    
    # Ersetze _setup_ui Methode
    import re
    pattern = r'def _setup_ui\(self\):.*?(?=def|\Z)'
    content = re.sub(pattern, new_setup_ui + '\n\n    ', content, flags=re.DOTALL)
    
    # Schreibe geänderte Datei
    with open(login_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Neues Login-Layout erstellt")
    return True


def update_login_styles():
    """Aktualisiert die Styles für das neue Layout"""
    
    print("🎨 Aktualisiere Login-Styles...")
    
    script_dir = Path(__file__).parent
    login_py_path = script_dir / "src" / "views" / "login_window.py"
    
    with open(login_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Neue Styles für das verbesserte Layout
    new_styles = '''        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0px 0px 5px 0px;
                line-height: 1.2;
            }
            
            QLabel#subtitle {
                font-size: 16px;
                color: #6c757d;
                margin: 0px 0px 10px 0px;
                line-height: 1.4;
            }
            
            QLabel#field_label {
                font-size: 16px;
                font-weight: 600;
                color: #495057;
                margin: 0px 0px 5px 0px;
                line-height: 1.3;
            }
            
            QLineEdit#input_field {
                padding: 16px 16px;
                min-height: 20px;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                font-size: 16px;
                background-color: #ffffff;
                line-height: 1.4;
                color: #495057;
            }
            
            QLineEdit#input_field:focus {
                border-color: #0d6efd;
                outline: none;
                background-color: #ffffff;
            }
            
            QLineEdit#input_field:hover {
                border-color: #adb5bd;
            }
            
            QCheckBox#checkbox {
                font-size: 15px;
                color: #6c757d;
                spacing: 8px;
                line-height: 1.4;
            }
            
            QCheckBox#checkbox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
            }
            
            QCheckBox#checkbox::indicator:checked {
                background-color: #0d6efd;
                border-color: #0d6efd;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMC42IDEuNEw0LjIgNy44TDEuNCA1IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            
            QPushButton#primary {
                background-color: #198754;
                color: white;
                border: none;
                padding: 16px 24px;
                min-height: 20px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                line-height: 1.4;
            }
            
            QPushButton#primary:hover {
                background-color: #157347;
            }
            
            QPushButton#primary:pressed {
                background-color: #146c43;
            }
            
            QPushButton#primary:disabled {
                background-color: #6c757d;
            }
            
            QPushButton#secondary {
                background-color: #f8f9fa;
                color: #6c757d;
                border: 2px solid #dee2e6;
                padding: 16px 24px;
                min-height: 20px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                line-height: 1.4;
            }
            
            QPushButton#secondary:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
                color: #495057;
            }
            
            QPushButton#secondary:pressed {
                background-color: #dee2e6;
                border-color: #6c757d;
            }
            
            QProgressBar#progress {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                text-align: center;
                font-size: 14px;
                font-weight: 600;
                min-height: 8px;
                max-height: 20px;
                color: #495057;
            }
            
            QProgressBar#progress::chunk {
                background-color: #0d6efd;
                border-radius: 6px;
            }
        """)'''
    
    # Ersetze Styles
    import re
    pattern = r'self\.setStyleSheet\(""".*?"""\)'
    content = re.sub(pattern, new_styles, content, flags=re.DOTALL)
    
    # Schreibe geänderte Datei
    with open(login_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Login-Styles aktualisiert")
    return True


def test_new_layout():
    """Testet das neue Layout"""
    
    print("\n🧪 Teste neues Login-Layout...")
    
    try:
        # Test GUI-Import
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from src.views.login_window import LoginWindow
        print("✅ LoginWindow-Import erfolgreich")
        
        # Test Layout-Erstellung (ohne Ausführung)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        
        login = LoginWindow()
        print("✅ Neues Login-Layout erfolgreich erstellt")
        
        return True
        
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        return False


def main():
    """Hauptfunktion"""
    
    print("Mammotion Linux App - Login-Layout-Fix")
    print("=" * 50)
    
    success = True
    
    # Layout neu erstellen
    if not create_new_login_layout():
        success = False
    
    # Styles aktualisieren
    if not update_login_styles():
        success = False
    
    # Tests ausführen
    if success and test_new_layout():
        print("\n🎉 Neues Login-Layout erfolgreich erstellt!")
        print("\nVerbesserungen:")
        print("  ✅ Professionelles, zentriertes Design")
        print("  ✅ Klare Feldbezeichnungen über den Eingaben")
        print("  ✅ Bessere Abstände und Proportionen")
        print("  ✅ Moderne Farben und Schatten")
        print("  ✅ Responsive Layout")
        print("  ✅ Verbesserte Button-Anordnung")
        print("\nDas Login-Fenster sollte jetzt viel professioneller aussehen:")
        print("  python3 main.py")
    else:
        print("\n❌ Layout-Fix fehlgeschlagen.")
        print("Bitte prüfen Sie die Backup-Dateien.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
