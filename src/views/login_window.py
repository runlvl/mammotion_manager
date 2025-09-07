"""
EXTREME Login-Fenster mit RIESIGEN Eingabefeldern

Diese Version erzwingt große UI-Elemente über mehrere Methoden gleichzeitig.
"""

import logging
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QProgressBar, QWidget, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QPalette


class ExtremeLoginWindow(QDialog):
    """
    EXTREME Login-Fenster mit RIESIGEN UI-Elementen
    
    Erzwingt große Eingabefelder über:
    - setFixedHeight()
    - setSizePolicy()
    - Stylesheet min-height
    - Große Fonts
    - Extremes Padding
    """
    
    login_requested = Signal(str, str, bool)
    login_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Fenster-Konfiguration - NOCH GRÖßER
        self.setWindowTitle("Mammotion Mähroboter - Anmeldung")
        self.setModal(True)
        self.setFixedSize(700, 800)  # Noch größeres Fenster
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
        self._setup_extreme_ui()
        self._setup_extreme_styles()
        self._connect_signals()
        
    def _setup_extreme_ui(self):
        """Erstellt die EXTREME Benutzeroberfläche"""
        # Hauptlayout mit RIESIGEN Abständen
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container
        container = QWidget()
        container.setObjectName("extreme_container")
        
        # Container-Layout mit EXTREMEN Abständen
        layout = QVBoxLayout(container)
        layout.setContentsMargins(80, 80, 80, 80)  # RIESIGE Ränder
        layout.setSpacing(50)  # RIESIGE Abstände
        
        # === HEADER ===
        header_widget = self._create_extreme_header()
        layout.addWidget(header_widget)
        
        # RIESIGER Abstand
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # === FORMULAR ===
        form_widget = self._create_extreme_form()
        layout.addWidget(form_widget)
        
        # === OPTIONEN ===
        options_widget = self._create_extreme_options()
        layout.addWidget(options_widget)
        
        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("extreme_progress")
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(15)
        layout.addWidget(self.progress_bar)
        
        # === BUTTONS ===
        buttons_widget = self._create_extreme_buttons()
        layout.addWidget(buttons_widget)
        
        # Container zentrieren
        main_layout.addStretch()
        main_layout.addWidget(container, 0, Qt.AlignCenter)
        main_layout.addStretch()
        
    def _create_extreme_header(self) -> QWidget:
        """Erstellt den EXTREMEN Header"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)
        
        # RIESIGER Titel
        title = QLabel("Mammotion")
        title.setObjectName("extreme_title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Untertitel
        subtitle = QLabel("Mähroboter-Verwaltung")
        subtitle.setObjectName("extreme_subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Beschreibung
        description = QLabel("Melden Sie sich mit Ihren Mammotion-Zugangsdaten an,\num Ihren Mähroboter zu verwalten.")
        description.setObjectName("extreme_description")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("extreme_separator")
        layout.addWidget(line)
        
        return widget
        
    def _create_extreme_form(self) -> QWidget:
        """Erstellt das EXTREME Formular"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(45)  # RIESIGE Abstände zwischen Feldern
        
        # E-Mail-Bereich
        email_group = self._create_extreme_input_group(
            "E-Mail-Adresse",
            "ihre.email@mammotion.com",
            False
        )
        self.email_edit = email_group.findChild(QLineEdit)
        layout.addWidget(email_group)
        
        # Passwort-Bereich
        password_group = self._create_extreme_input_group(
            "Passwort",
            "Ihr Mammotion-Passwort",
            True
        )
        self.password_edit = password_group.findChild(QLineEdit)
        layout.addWidget(password_group)
        
        return widget
        
    def _create_extreme_input_group(self, label_text: str, placeholder: str, is_password: bool) -> QWidget:
        """Erstellt eine EXTREME Eingabegruppe"""
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)  # Großer Abstand zwischen Label und Feld
        
        # Label
        label = QLabel(label_text)
        label.setObjectName("extreme_label")
        layout.addWidget(label)
        
        # EXTREMES Eingabefeld
        input_field = QLineEdit()
        input_field.setObjectName("extreme_input")
        input_field.setPlaceholderText(placeholder)
        
        # MEHRFACHE Größen-Erzwingung
        input_field.setFixedHeight(80)  # ERZWINGE 80px Höhe
        input_field.setMinimumHeight(80)
        input_field.setMaximumHeight(80)
        input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # RIESIGE Schrift im Eingabefeld
        font = QFont()
        font.setPointSize(16)  # Große Schrift
        input_field.setFont(font)
        
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
            
        layout.addWidget(input_field)
        
        return group
        
    def _create_extreme_options(self) -> QWidget:
        """Erstellt EXTREME Optionen"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.remember_checkbox = QCheckBox("Zugangsdaten sicher speichern")
        self.remember_checkbox.setObjectName("extreme_checkbox")
        self.remember_checkbox.setFixedHeight(50)  # RIESIGE Checkbox
        self.remember_checkbox.setToolTip("Speichert Ihre Zugangsdaten verschlüsselt")
        
        # Große Schrift für Checkbox
        font = QFont()
        font.setPointSize(16)
        self.remember_checkbox.setFont(font)
        
        layout.addWidget(self.remember_checkbox)
        layout.addStretch()
        
        return widget
        
    def _create_extreme_buttons(self) -> QWidget:
        """Erstellt EXTREME Buttons"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)  # RIESIGER Abstand zwischen Buttons
        
        # RIESIGE Buttons
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setObjectName("extreme_secondary")
        self.cancel_button.setFixedSize(QSize(180, 70))  # RIESIGE Buttons!
        
        # Große Schrift für Buttons
        font = QFont()
        font.setPointSize(16)
        font.setWeight(QFont.Bold)
        self.cancel_button.setFont(font)
        
        self.login_button = QPushButton("Anmelden")
        self.login_button.setObjectName("extreme_primary")
        self.login_button.setFixedSize(QSize(180, 70))  # RIESIGE Buttons!
        self.login_button.setFont(font)
        
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.login_button)
        
        return widget
        
    def _setup_extreme_styles(self):
        """EXTREME Styles mit erzwungenen Größen"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
            }
            
            QWidget#extreme_container {
                background-color: white;
                border-radius: 20px;
                border: 2px solid #dee2e6;
            }
            
            QLabel#extreme_title {
                font-size: 48px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0px;
                line-height: 1.1;
                letter-spacing: -2px;
            }
            
            QLabel#extreme_subtitle {
                font-size: 26px;
                font-weight: 500;
                color: #6c757d;
                margin: 0px;
                line-height: 1.3;
            }
            
            QLabel#extreme_description {
                font-size: 20px;
                color: #6c757d;
                margin: 0px;
                line-height: 1.5;
            }
            
            QFrame#extreme_separator {
                color: #dee2e6;
                margin: 20px 0px;
                border: none;
                background-color: #dee2e6;
                max-height: 2px;
            }
            
            QLabel#extreme_label {
                font-size: 20px;
                font-weight: 600;
                color: #495057;
                margin: 0px;
                line-height: 1.3;
            }
            
            QLineEdit#extreme_input {
                padding: 25px 25px;
                min-height: 80px;
                max-height: 80px;
                border: 4px solid #dee2e6;
                border-radius: 15px;
                font-size: 18px;
                background-color: #ffffff;
                line-height: 1.4;
                color: #495057;
                selection-background-color: #0d6efd;
            }
            
            QLineEdit#extreme_input:focus {
                border-color: #0d6efd;
                outline: none;
                background-color: #ffffff;
            }
            
            QLineEdit#extreme_input:hover {
                border-color: #adb5bd;
            }
            
            QCheckBox#extreme_checkbox {
                font-size: 18px;
                color: #6c757d;
                spacing: 15px;
                line-height: 1.4;
            }
            
            QCheckBox#extreme_checkbox::indicator {
                width: 28px;
                height: 28px;
                border: 4px solid #dee2e6;
                border-radius: 8px;
                background-color: #ffffff;
            }
            
            QCheckBox#extreme_checkbox::indicator:checked {
                background-color: #0d6efd;
                border-color: #0d6efd;
            }
            
            QPushButton#extreme_primary {
                background-color: #198754;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: 600;
                line-height: 1.4;
            }
            
            QPushButton#extreme_primary:hover {
                background-color: #157347;
            }
            
            QPushButton#extreme_primary:pressed {
                background-color: #146c43;
            }
            
            QPushButton#extreme_primary:disabled {
                background-color: #6c757d;
            }
            
            QPushButton#extreme_secondary {
                background-color: #f8f9fa;
                color: #6c757d;
                border: 4px solid #dee2e6;
                border-radius: 15px;
                font-size: 18px;
                font-weight: 500;
                line-height: 1.4;
            }
            
            QPushButton#extreme_secondary:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
                color: #495057;
            }
            
            QPushButton#extreme_secondary:pressed {
                background-color: #dee2e6;
                border-color: #6c757d;
            }
            
            QProgressBar#extreme_progress {
                border: 3px solid #dee2e6;
                border-radius: 8px;
                text-align: center;
                font-size: 16px;
                font-weight: 600;
                color: #495057;
                background-color: #f8f9fa;
            }
            
            QProgressBar#extreme_progress::chunk {
                background-color: #0d6efd;
                border-radius: 5px;
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
LoginWindow = ExtremeLoginWindow
