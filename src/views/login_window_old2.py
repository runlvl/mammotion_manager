"""
Login-Fenster für die Mammotion Linux App

Professionelles, benutzerfreundliches Login-Interface.
"""

import logging
from typing import Optional, Callable
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QProgressBar, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont


class LoginWindow(QDialog):
    """
    Login-Fenster für Mammotion-Anmeldung
    
    Signals:
        login_requested: Wird ausgelöst wenn Login versucht wird
        login_cancelled: Wird ausgelöst wenn Abbrechen geklickt wird
    """
    
    login_requested = Signal(str, str, bool)  # email, password, remember
    login_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # Fenster-Konfiguration
        self.setWindowTitle("Mammotion Login")
        self.setModal(True)
        self.setFixedSize(450, 550)
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
        self._setup_styles()
        self._connect_signals()
        
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptlayout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container für zentrierten Inhalt
        container = QWidget()
        container.setObjectName("container")
        
        # Container-Layout
        layout = QVBoxLayout(container)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # === HEADER ===
        header_widget = self._create_header()
        layout.addWidget(header_widget)
        
        # === FORMULAR ===
        form_widget = self._create_form()
        layout.addWidget(form_widget)
        
        # === OPTIONEN ===
        options_widget = self._create_options()
        layout.addWidget(options_widget)
        
        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progress")
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # === BUTTONS ===
        buttons_widget = self._create_buttons()
        layout.addWidget(buttons_widget)
        
        # Container zum Hauptlayout hinzufügen
        main_layout.addStretch()
        main_layout.addWidget(container, 0, Qt.AlignCenter)
        main_layout.addStretch()
        
    def _create_header(self) -> QWidget:
        """Erstellt den Header-Bereich"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Titel
        title = QLabel("Mammotion Login")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Untertitel
        subtitle = QLabel("Melden Sie sich mit Ihren Mammotion-Zugangsdaten an")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setObjectName("separator")
        layout.addWidget(line)
        
        return widget
        
    def _create_form(self) -> QWidget:
        """Erstellt das Formular"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)
        
        # E-Mail-Bereich
        email_group = QWidget()
        email_layout = QVBoxLayout(email_group)
        email_layout.setContentsMargins(0, 0, 0, 0)
        email_layout.setSpacing(8)
        
        email_label = QLabel("E-Mail-Adresse")
        email_label.setObjectName("field_label")
        email_layout.addWidget(email_label)
        
        self.email_edit = QLineEdit()
        self.email_edit.setObjectName("input_field")
        self.email_edit.setPlaceholderText("ihre.email@example.com")
        email_layout.addWidget(self.email_edit)
        
        layout.addWidget(email_group)
        
        # Passwort-Bereich
        password_group = QWidget()
        password_layout = QVBoxLayout(password_group)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)
        
        password_label = QLabel("Passwort")
        password_label.setObjectName("field_label")
        password_layout.addWidget(password_label)
        
        self.password_edit = QLineEdit()
        self.password_edit.setObjectName("input_field")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Ihr Passwort")
        password_layout.addWidget(self.password_edit)
        
        layout.addWidget(password_group)
        
        return widget
        
    def _create_options(self) -> QWidget:
        """Erstellt den Optionen-Bereich"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.remember_checkbox = QCheckBox("Zugangsdaten speichern")
        self.remember_checkbox.setObjectName("checkbox")
        self.remember_checkbox.setToolTip("Speichert die Zugangsdaten sicher im System")
        layout.addWidget(self.remember_checkbox)
        
        layout.addStretch()
        
        return widget
        
    def _create_buttons(self) -> QWidget:
        """Erstellt den Button-Bereich"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setObjectName("secondary")
        self.cancel_button.setMinimumWidth(130)
        layout.addWidget(self.cancel_button)
        
        self.login_button = QPushButton("Anmelden")
        self.login_button.setObjectName("primary")
        self.login_button.setMinimumWidth(130)
        layout.addWidget(self.login_button)
        
        return widget
        
    def _setup_styles(self):
        """Konfiguriert die Styles"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            
            QWidget#container {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #dee2e6;
            }
            
            QLabel#title {
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0px;
                line-height: 1.2;
            }
            
            QLabel#subtitle {
                font-size: 16px;
                color: #6c757d;
                margin: 0px;
                line-height: 1.4;
            }
            
            QFrame#separator {
                color: #dee2e6;
                margin: 10px 0px;
            }
            
            QLabel#field_label {
                font-size: 16px;
                font-weight: 600;
                color: #495057;
                margin: 0px;
                line-height: 1.3;
            }
            
            QLineEdit#input_field {
                padding: 18px 16px;
                min-height: 24px;
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
                spacing: 10px;
                line-height: 1.4;
            }
            
            QCheckBox#checkbox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
            }
            
            QCheckBox#checkbox::indicator:checked {
                background-color: #0d6efd;
                border-color: #0d6efd;
            }
            
            QCheckBox#checkbox::indicator:hover {
                border-color: #adb5bd;
            }
            
            QPushButton#primary {
                background-color: #198754;
                color: white;
                border: none;
                padding: 18px 24px;
                min-height: 24px;
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
                padding: 18px 24px;
                min-height: 24px;
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
                min-height: 12px;
                max-height: 24px;
                color: #495057;
            }
            
            QProgressBar#progress::chunk {
                background-color: #0d6efd;
                border-radius: 6px;
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
            self.login_button.setText("Anmelden...")
        else:
            self.login_button.setText("Anmelden")
            
    def show_error(self, message: str):
        """Zeigt eine Fehlermeldung"""
        self.set_login_in_progress(False)
        # TODO: Implementiere Fehler-Anzeige
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
