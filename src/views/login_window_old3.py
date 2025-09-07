"""
Professionelles Login-Fenster für die Mammotion Linux App

Optimiert für moderne Displays mit großen, gut lesbaren UI-Elementen.
"""

import logging
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QProgressBar, QWidget, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QPalette


class ProfessionalLoginWindow(QDialog):
    """
    Professionelles Login-Fenster mit großen, gut lesbaren UI-Elementen
    
    Optimiert für:
    - High-DPI-Displays
    - Große, komfortable Eingabefelder (50px+ Höhe)
    - Professionelle Typografie
    - Moderne Farbgebung
    """
    
    login_requested = Signal(str, str, bool)  # email, password, remember
    login_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Fenster-Konfiguration
        self.setWindowTitle("Mammotion Mähroboter - Anmeldung")
        self.setModal(True)
        self.setFixedSize(600, 700)  # Größeres Fenster
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # UI-Elemente
        self.email_edit = None
        self.password_edit = None
        self.remember_checkbox = None
        self.login_button = None
        self.cancel_button = None
        self.progress_bar = None
        
        # Status
        self._is_logging_in = False
        
        # UI erstellen
        self._setup_ui()
        self._setup_professional_styles()
        self._connect_signals()
        
    def _setup_ui(self):
        """Erstellt die professionelle Benutzeroberfläche"""
        # Hauptlayout mit großzügigen Abständen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container für zentrierten Inhalt
        container = QWidget()
        container.setObjectName("main_container")
        
        # Container-Layout mit großzügigen Abständen
        layout = QVBoxLayout(container)
        layout.setContentsMargins(60, 60, 60, 60)  # Große Ränder
        layout.setSpacing(40)  # Große Abstände zwischen Bereichen
        
        # === HEADER BEREICH ===
        header_widget = self._create_professional_header()
        layout.addWidget(header_widget)
        
        # Großer Abstand nach Header
        layout.addItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # === FORMULAR BEREICH ===
        form_widget = self._create_professional_form()
        layout.addWidget(form_widget)
        
        # === OPTIONEN BEREICH ===
        options_widget = self._create_professional_options()
        layout.addWidget(options_widget)
        
        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("professional_progress")
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(12)
        self.progress_bar.setMaximumHeight(12)
        layout.addWidget(self.progress_bar)
        
        # === BUTTONS ===
        buttons_widget = self._create_professional_buttons()
        layout.addWidget(buttons_widget)
        
        # Container zentrieren
        main_layout.addStretch()
        main_layout.addWidget(container, 0, Qt.AlignCenter)
        main_layout.addStretch()
        
    def _create_professional_header(self) -> QWidget:
        """Erstellt den professionellen Header-Bereich"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Haupttitel - sehr groß und prominent
        title = QLabel("Mammotion")
        title.setObjectName("main_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Untertitel
        subtitle = QLabel("Mähroboter-Verwaltung")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Beschreibung
        description = QLabel("Melden Sie sich mit Ihren Mammotion-Zugangsdaten an,\num Ihren Mähroboter zu verwalten.")
        description.setObjectName("description")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Elegante Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("elegant_separator")
        layout.addWidget(line)
        
        return widget
        
    def _create_professional_form(self) -> QWidget:
        """Erstellt das professionelle Formular"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(35)  # Große Abstände zwischen Feldern
        
        # E-Mail-Bereich
        email_group = self._create_input_group(
            "E-Mail-Adresse",
            "ihre.email@mammotion.com",
            False
        )
        self.email_edit = email_group.findChild(QLineEdit)
        layout.addWidget(email_group)
        
        # Passwort-Bereich
        password_group = self._create_input_group(
            "Passwort",
            "Ihr Mammotion-Passwort",
            True
        )
        self.password_edit = password_group.findChild(QLineEdit)
        layout.addWidget(password_group)
        
        return widget
        
    def _create_input_group(self, label_text: str, placeholder: str, is_password: bool) -> QWidget:
        """Erstellt eine professionelle Eingabegruppe"""
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)  # Abstand zwischen Label und Eingabefeld
        
        # Label
        label = QLabel(label_text)
        label.setObjectName("input_label")
        layout.addWidget(label)
        
        # Eingabefeld - SEHR GROSS
        input_field = QLineEdit()
        input_field.setObjectName("professional_input")
        input_field.setPlaceholderText(placeholder)
        input_field.setMinimumHeight(60)  # Sehr große Höhe!
        input_field.setMaximumHeight(60)
        
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
            
        layout.addWidget(input_field)
        
        return group
        
    def _create_professional_options(self) -> QWidget:
        """Erstellt den professionellen Optionen-Bereich"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.remember_checkbox = QCheckBox("Zugangsdaten sicher speichern")
        self.remember_checkbox.setObjectName("professional_checkbox")
        self.remember_checkbox.setMinimumHeight(40)  # Große Checkbox
        self.remember_checkbox.setToolTip("Speichert Ihre Zugangsdaten verschlüsselt im System-Schlüsselbund")
        layout.addWidget(self.remember_checkbox)
        
        layout.addStretch()
        
        return widget
        
    def _create_professional_buttons(self) -> QWidget:
        """Erstellt den professionellen Button-Bereich"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)  # Großer Abstand zwischen Buttons
        
        # Abbrechen-Button
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setObjectName("professional_secondary")
        self.cancel_button.setMinimumSize(QSize(160, 55))  # Sehr große Buttons!
        self.cancel_button.setMaximumSize(QSize(160, 55))
        layout.addWidget(self.cancel_button)
        
        # Anmelden-Button
        self.login_button = QPushButton("Anmelden")
        self.login_button.setObjectName("professional_primary")
        self.login_button.setMinimumSize(QSize(160, 55))  # Sehr große Buttons!
        self.login_button.setMaximumSize(QSize(160, 55))
        layout.addWidget(self.login_button)
        
        return widget
        
    def _setup_professional_styles(self):
        """Konfiguriert die professionellen Styles"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
            }
            
            QWidget#main_container {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #dee2e6;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            }
            
            QLabel#main_title {
                font-size: 42px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0px;
                line-height: 1.1;
                letter-spacing: -1px;
            }
            
            QLabel#subtitle {
                font-size: 22px;
                font-weight: 500;
                color: #6c757d;
                margin: 0px;
                line-height: 1.3;
            }
            
            QLabel#description {
                font-size: 18px;
                color: #6c757d;
                margin: 0px;
                line-height: 1.5;
            }
            
            QFrame#elegant_separator {
                color: #dee2e6;
                margin: 15px 0px;
                border: none;
                background-color: #dee2e6;
                max-height: 1px;
            }
            
            QLabel#input_label {
                font-size: 18px;
                font-weight: 600;
                color: #495057;
                margin: 0px;
                line-height: 1.3;
            }
            
            QLineEdit#professional_input {
                padding: 18px 20px;
                border: 3px solid #dee2e6;
                border-radius: 12px;
                font-size: 18px;
                background-color: #ffffff;
                line-height: 1.4;
                color: #495057;
                selection-background-color: #0d6efd;
            }
            
            QLineEdit#professional_input:focus {
                border-color: #0d6efd;
                outline: none;
                background-color: #ffffff;
                box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.25);
            }
            
            QLineEdit#professional_input:hover {
                border-color: #adb5bd;
            }
            
            QCheckBox#professional_checkbox {
                font-size: 17px;
                color: #6c757d;
                spacing: 12px;
                line-height: 1.4;
            }
            
            QCheckBox#professional_checkbox::indicator {
                width: 24px;
                height: 24px;
                border: 3px solid #dee2e6;
                border-radius: 6px;
                background-color: #ffffff;
            }
            
            QCheckBox#professional_checkbox::indicator:checked {
                background-color: #0d6efd;
                border-color: #0d6efd;
            }
            
            QCheckBox#professional_checkbox::indicator:hover {
                border-color: #adb5bd;
            }
            
            QPushButton#professional_primary {
                background-color: #198754;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: 600;
                line-height: 1.4;
            }
            
            QPushButton#professional_primary:hover {
                background-color: #157347;
                transform: translateY(-1px);
            }
            
            QPushButton#professional_primary:pressed {
                background-color: #146c43;
                transform: translateY(0px);
            }
            
            QPushButton#professional_primary:disabled {
                background-color: #6c757d;
            }
            
            QPushButton#professional_secondary {
                background-color: #f8f9fa;
                color: #6c757d;
                border: 3px solid #dee2e6;
                border-radius: 12px;
                font-size: 18px;
                font-weight: 500;
                line-height: 1.4;
            }
            
            QPushButton#professional_secondary:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
                color: #495057;
                transform: translateY(-1px);
            }
            
            QPushButton#professional_secondary:pressed {
                background-color: #dee2e6;
                border-color: #6c757d;
                transform: translateY(0px);
            }
            
            QProgressBar#professional_progress {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                text-align: center;
                font-size: 14px;
                font-weight: 600;
                color: #495057;
                background-color: #f8f9fa;
            }
            
            QProgressBar#professional_progress::chunk {
                background-color: #0d6efd;
                border-radius: 4px;
            }
        """)
        
    def _connect_signals(self):
        """Verbindet die Signale"""
        self.login_button.clicked.connect(self._on_login_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        
        # Enter-Taste für Login
        self.email_edit.returnPressed.connect(self._on_login_clicked)
        self.password_edit.returnPressed.connect(self._on_login_clicked)
        
    def _on_login_clicked(self):
        """Behandelt Login-Button-Klick"""
        if self._is_logging_in:
            return
            
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        remember = self.remember_checkbox.isChecked()
        
        # Validierung
        if not email:
            self.email_edit.setFocus()
            return
            
        if not password:
            self.password_edit.setFocus()
            return
            
        # Login-Prozess starten
        self.set_login_in_progress(True)
        self.login_requested.emit(email, password, remember)
        
    def _on_cancel_clicked(self):
        """Behandelt Abbrechen-Button-Klick"""
        self.login_cancelled.emit()
        self.reject()
        
    def set_login_in_progress(self, in_progress: bool):
        """Setzt den Login-Status"""
        self._is_logging_in = in_progress
        
        # UI-Elemente deaktivieren/aktivieren
        self.email_edit.setEnabled(not in_progress)
        self.password_edit.setEnabled(not in_progress)
        self.remember_checkbox.setEnabled(not in_progress)
        self.login_button.setEnabled(not in_progress)
        
        # Progress Bar anzeigen/verstecken
        self.progress_bar.setVisible(in_progress)
        if in_progress:
            self.progress_bar.setRange(0, 0)  # Unbestimmter Progress
        
        # Button-Text ändern
        if in_progress:
            self.login_button.setText("Verbinde mit Mammotion...")
        else:
            self.login_button.setText("Anmelden")
            
    def show_error(self, message: str):
        """Zeigt eine Fehlermeldung"""
        self.set_login_in_progress(False)
        self.logger.error(f"Login-Fehler: {message}")
        
    def get_credentials(self) -> tuple[str, str, bool]:
        """Gibt die eingegebenen Zugangsdaten zurück"""
        return (
            self.email_edit.text().strip(),
            self.password_edit.text(),
            self.remember_checkbox.isChecked()
        )
        
    def set_credentials(self, email: str, password: str = "", remember: bool = False):
        """Setzt die Zugangsdaten"""
        self.email_edit.setText(email)
        self.password_edit.setText(password)
        self.remember_checkbox.setChecked(remember)
        
        # Fokus auf Passwort setzen wenn E-Mail bereits ausgefüllt
        if email and not password:
            self.password_edit.setFocus()
        elif not email:
            self.email_edit.setFocus()


# Alias für Kompatibilität
LoginWindow = ProfessionalLoginWindow
