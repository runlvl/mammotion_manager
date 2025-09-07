"""
Login Window - Anmeldefenster für die Mammotion App

Dieses Fenster ermöglicht es dem Benutzer, sich mit seinen Mammotion-Zugangsdaten
anzumelden. Es bietet auch die Option, Zugangsdaten zu speichern.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QProgressBar, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QPalette

from ..utils.logging_config import LoggerMixin


class LoginWindow(QDialog, LoggerMixin):
    """
    Login-Dialog für Mammotion-Authentifizierung
    
    Signals:
        login_requested(str, str, bool): E-Mail, Passwort, Speichern
        login_cancelled(): Login abgebrochen
    """
    
    login_requested = Signal(str, str, bool)
    login_cancelled = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mammotion Login")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel#title {
                font-size: 26px;
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
            }
            QLineEdit:focus {
                border-color: #3498db;
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
                border: 1px solid #bdc3c7;
                padding: 16px 24px;
                min-height: 28px;
                border-radius: 6px;
                font-size: 16px;
                line-height: 1.4;
            }
            QPushButton#secondary:hover {
                background-color: #d5dbdb;
            }
            QCheckBox {
                font-size: 12px;
                color: #2c3e50;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
        """)
        
        self._setup_ui()
        self._connect_signals()
        
        # Status-Tracking
        self._is_logging_in = False
        
    def _setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_layout = QVBoxLayout()
        
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
        
        layout.addLayout(header_layout)
        
        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Formular
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # E-Mail-Feld
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("ihre.email@example.com")
        form_layout.addRow("E-Mail:", self.email_edit)
        
        # Passwort-Feld
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Ihr Passwort")
        form_layout.addRow("Passwort:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Optionen
        options_layout = QHBoxLayout()
        
        self.remember_checkbox = QCheckBox("Zugangsdaten speichern")
        self.remember_checkbox.setToolTip("Speichert die Zugangsdaten sicher im System-Schlüsselbund")
        options_layout.addWidget(self.remember_checkbox)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Progress Bar (initial versteckt)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Abbrechen")
        self.cancel_button.setObjectName("secondary")
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.login_button = QPushButton("Anmelden")
        self.login_button.setObjectName("primary")
        self.login_button.setDefault(True)
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
        
        # Initial Focus
        self.email_edit.setFocus()
        
    def _connect_signals(self):
        """Verbindet Signals mit Slots"""
        self.login_button.clicked.connect(self._on_login_clicked)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        
        # Enter-Taste in Feldern
        self.email_edit.returnPressed.connect(self._on_login_clicked)
        self.password_edit.returnPressed.connect(self._on_login_clicked)
        
    def _on_login_clicked(self):
        """Behandelt Login-Button-Klick"""
        email = self.email_edit.text().strip()
        password = self.password_edit.text()
        remember = self.remember_checkbox.isChecked()
        
        # Validierung
        if not email:
            self._show_error("Bitte geben Sie Ihre E-Mail-Adresse ein.")
            self.email_edit.setFocus()
            return
            
        if not password:
            self._show_error("Bitte geben Sie Ihr Passwort ein.")
            self.password_edit.setFocus()
            return
            
        if "@" not in email:
            self._show_error("Bitte geben Sie eine gültige E-Mail-Adresse ein.")
            self.email_edit.setFocus()
            return
        
        # Login-Prozess starten
        self._start_login_process()
        self.login_requested.emit(email, password, remember)
        
    def _on_cancel_clicked(self):
        """Behandelt Cancel-Button-Klick"""
        if self._is_logging_in:
            # Login abbrechen
            self._stop_login_process()
        
        self.login_cancelled.emit()
        self.reject()
        
    def _start_login_process(self):
        """Startet den visuellen Login-Prozess"""
        self._is_logging_in = True
        
        # UI-Elemente deaktivieren
        self.email_edit.setEnabled(False)
        self.password_edit.setEnabled(False)
        self.remember_checkbox.setEnabled(False)
        self.login_button.setEnabled(False)
        self.login_button.setText("Anmelden...")
        
        # Progress Bar anzeigen
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Unbestimmter Progress
        
        # Cancel-Button zu "Abbrechen" ändern
        self.cancel_button.setText("Abbrechen")
        
    def _stop_login_process(self):
        """Stoppt den visuellen Login-Prozess"""
        self._is_logging_in = False
        
        # UI-Elemente wieder aktivieren
        self.email_edit.setEnabled(True)
        self.password_edit.setEnabled(True)
        self.remember_checkbox.setEnabled(True)
        self.login_button.setEnabled(True)
        self.login_button.setText("Anmelden")
        
        # Progress Bar verstecken
        self.progress_bar.setVisible(False)
        
        # Cancel-Button zurücksetzen
        self.cancel_button.setText("Abbrechen")
        
    def _show_error(self, message: str):
        """Zeigt eine Fehlermeldung an"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Eingabefehler")
        msg_box.setText(message)
        msg_box.exec()
        
    def on_login_success(self):
        """Wird aufgerufen wenn Login erfolgreich war"""
        self._stop_login_process()
        self.accept()
        
    def on_login_failed(self, error_message: str):
        """Wird aufgerufen wenn Login fehlgeschlagen ist"""
        self._stop_login_process()
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Login fehlgeschlagen")
        msg_box.setText("Die Anmeldung ist fehlgeschlagen.")
        msg_box.setInformativeText(error_message)
        msg_box.exec()
        
        # Focus zurück auf Passwort-Feld
        self.password_edit.clear()
        self.password_edit.setFocus()
        
    def set_credentials(self, email: str, password: str = ""):
        """Setzt Zugangsdaten (z.B. aus gespeicherten Daten)"""
        self.email_edit.setText(email)
        if password:
            self.password_edit.setText(password)
            self.remember_checkbox.setChecked(True)
        
        # Focus auf das leere Feld setzen
        if password:
            self.login_button.setFocus()
        else:
            self.password_edit.setFocus()
            
    def clear_form(self):
        """Leert das Formular"""
        self.email_edit.clear()
        self.password_edit.clear()
        self.remember_checkbox.setChecked(False)
        self.email_edit.setFocus()
