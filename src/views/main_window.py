"""
Main Window - Hauptfenster der Mammotion App

Das Hauptfenster zeigt den Status des Mähers an und bietet Steuerungsmöglichkeiten.
Es ist das zentrale Interface der Anwendung.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QProgressBar, QComboBox, QFrame,
    QStatusBar, QMenuBar, QMessageBox, QTabWidget, QGroupBox,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon, QAction

from ..models.mammotion_model import MowerInfo, MowerStatus
from ..utils.logging_config import LoggerMixin


class StatusWidget(QWidget, LoggerMixin):
    """Widget zur Anzeige des Mäher-Status"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_mower = None
        
    def _setup_ui(self):
        """Erstellt die Status-UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Mäher-Auswahl
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Mäher:"))
        
        self.mower_combo = QComboBox()
        self.mower_combo.setMinimumWidth(200)
        selection_layout.addWidget(self.mower_combo)
        
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Status-Informationen
        status_group = QGroupBox("Status")
        status_layout = QGridLayout(status_group)
        
        # Status-Label
        status_layout.addWidget(QLabel("Status:"), 0, 0)
        self.status_label = QLabel("Nicht verbunden")
        self.status_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        status_layout.addWidget(self.status_label, 0, 1)
        
        # Akku-Anzeige
        status_layout.addWidget(QLabel("Akku:"), 1, 0)
        battery_layout = QHBoxLayout()
        
        self.battery_bar = QProgressBar()
        self.battery_bar.setRange(0, 100)
        self.battery_bar.setValue(0)
        self.battery_bar.setTextVisible(True)
        battery_layout.addWidget(self.battery_bar)
        
        self.battery_label = QLabel("0%")
        self.battery_label.setMinimumWidth(40)
        battery_layout.addWidget(self.battery_label)
        
        status_layout.addLayout(battery_layout, 1, 1)
        
        # Position (falls verfügbar)
        status_layout.addWidget(QLabel("Position:"), 2, 0)
        self.position_label = QLabel("Unbekannt")
        status_layout.addWidget(self.position_label, 2, 1)
        
        # Letzte Aktualisierung
        status_layout.addWidget(QLabel("Aktualisiert:"), 3, 0)
        self.last_update_label = QLabel("Nie")
        status_layout.addWidget(self.last_update_label, 3, 1)
        
        layout.addWidget(status_group)
        
        # Styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
        """)
        
    def update_mower_info(self, mower_info: MowerInfo):
        """Aktualisiert die Anzeige mit neuen Mäher-Informationen"""
        self._current_mower = mower_info
        
        # Status
        status_text = self._get_status_text(mower_info.status)
        status_color = self._get_status_color(mower_info.status)
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"font-weight: bold; color: {status_color};")
        
        # Akku
        self.battery_bar.setValue(mower_info.battery_level)
        self.battery_label.setText(f"{mower_info.battery_level}%")
        
        # Akku-Farbe je nach Level
        if mower_info.battery_level <= 15:
            battery_color = "#e74c3c"  # Rot
        elif mower_info.battery_level <= 30:
            battery_color = "#f39c12"  # Orange
        else:
            battery_color = "#27ae60"  # Grün
            
        self.battery_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {battery_color};
                border-radius: 3px;
            }}
        """)
        
        # Position
        if mower_info.position:
            lat = mower_info.position.get('lat', 0)
            lon = mower_info.position.get('lon', 0)
            self.position_label.setText(f"{lat:.4f}, {lon:.4f}")
        else:
            self.position_label.setText("Unbekannt")
            
        # Letzte Aktualisierung
        if mower_info.last_update:
            self.last_update_label.setText(mower_info.last_update)
        else:
            self.last_update_label.setText("Nie")
            
    def _get_status_text(self, status: MowerStatus) -> str:
        """Konvertiert Status-Enum zu deutschem Text"""
        status_map = {
            MowerStatus.UNKNOWN: "Unbekannt",
            MowerStatus.IDLE: "Bereit",
            MowerStatus.MOWING: "Mäht",
            MowerStatus.CHARGING: "Lädt",
            MowerStatus.PAUSED: "Pausiert",
            MowerStatus.ERROR: "Fehler",
            MowerStatus.RETURNING: "Kehrt zurück"
        }
        return status_map.get(status, "Unbekannt")
        
    def _get_status_color(self, status: MowerStatus) -> str:
        """Gibt die Farbe für den Status zurück"""
        color_map = {
            MowerStatus.UNKNOWN: "#95a5a6",
            MowerStatus.IDLE: "#3498db",
            MowerStatus.MOWING: "#27ae60",
            MowerStatus.CHARGING: "#f39c12",
            MowerStatus.PAUSED: "#e67e22",
            MowerStatus.ERROR: "#e74c3c",
            MowerStatus.RETURNING: "#9b59b6"
        }
        return color_map.get(status, "#95a5a6")
        
    def update_mower_list(self, mowers: list):
        """Aktualisiert die Mäher-Auswahlliste"""
        self.mower_combo.clear()
        for mower in mowers:
            self.mower_combo.addItem(f"{mower.name} ({mower.model})", mower.device_id)
            
    def get_selected_mower_id(self) -> str:
        """Gibt die ID des ausgewählten Mähers zurück"""
        return self.mower_combo.currentData()


class ControlWidget(QWidget, LoggerMixin):
    """Widget für Mäher-Steuerung"""
    
    start_mowing_requested = Signal()
    stop_mowing_requested = Signal()
    return_to_dock_requested = Signal()
    refresh_status_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._current_status = MowerStatus.UNKNOWN
        
    def _setup_ui(self):
        """Erstellt die Steuerungs-UI"""
        layout = QVBoxLayout(self)
        
        # Hauptsteuerung
        control_group = QGroupBox("Steuerung")
        control_layout = QGridLayout(control_group)
        
        # Start/Stop Button
        self.start_stop_button = QPushButton("Mähen starten")
        self.start_stop_button.setMinimumHeight(50)
        self.start_stop_button.clicked.connect(self._on_start_stop_clicked)
        control_layout.addWidget(self.start_stop_button, 0, 0, 1, 2)
        
        # Zur Ladestation
        self.dock_button = QPushButton("Zur Ladestation")
        self.dock_button.setMinimumHeight(40)
        self.dock_button.clicked.connect(self.return_to_dock_requested.emit)
        control_layout.addWidget(self.dock_button, 1, 0, 1, 2)
        
        # Status aktualisieren
        self.refresh_button = QPushButton("Status aktualisieren")
        self.refresh_button.clicked.connect(self.refresh_status_requested.emit)
        control_layout.addWidget(self.refresh_button, 2, 0, 1, 2)
        
        layout.addWidget(control_group)
        
        # Styling
        self.setStyleSheet("""
            QWidget {
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
        """)
        
    def _on_start_stop_clicked(self):
        """Behandelt Start/Stop-Button-Klick"""
        if self._current_status == MowerStatus.MOWING:
            self.stop_mowing_requested.emit()
        else:
            self.start_mowing_requested.emit()
            
    def update_status(self, status: MowerStatus):
        """Aktualisiert die Buttons basierend auf dem Status"""
        self._current_status = status
        
        if status == MowerStatus.MOWING:
            self.start_stop_button.setText("Mähen stoppen")
            self.start_stop_button.setObjectName("stop")
        else:
            self.start_stop_button.setText("Mähen starten")
            self.start_stop_button.setObjectName("start")
            
        # Button-Verfügbarkeit
        can_control = status not in [MowerStatus.UNKNOWN, MowerStatus.ERROR]
        self.start_stop_button.setEnabled(can_control)
        self.dock_button.setEnabled(can_control and status != MowerStatus.CHARGING)
        
        # Style neu anwenden
        self.setStyleSheet(self.styleSheet())


class MainWindow(QMainWindow, LoggerMixin):
    """Hauptfenster der Mammotion App"""
    
    # Signals für Controller
    login_requested = Signal()
    logout_requested = Signal()
    mower_selection_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mammotion Linux App")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._setup_menu()
        self._setup_status_bar()
        
        # Status-Tracking
        self._is_connected = False
        self._current_mower = None
        
    def _setup_ui(self):
        """Erstellt die Hauptbenutzeroberfläche"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Linke Seite: Status
        left_layout = QVBoxLayout()
        
        self.status_widget = StatusWidget()
        left_layout.addWidget(self.status_widget)
        
        left_layout.addStretch()
        layout.addLayout(left_layout, 2)
        
        # Rechte Seite: Steuerung
        right_layout = QVBoxLayout()
        
        self.control_widget = ControlWidget()
        right_layout.addWidget(self.control_widget)
        
        right_layout.addStretch()
        layout.addLayout(right_layout, 1)
        
        # Signals verbinden
        self.status_widget.mower_combo.currentTextChanged.connect(self._on_mower_selection_changed)
        
    def _setup_menu(self):
        """Erstellt die Menüleiste"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu("Datei")
        
        login_action = QAction("Anmelden...", self)
        login_action.triggered.connect(self.login_requested.emit)
        file_menu.addAction(login_action)
        
        logout_action = QAction("Abmelden", self)
        logout_action.triggered.connect(self.logout_requested.emit)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu("Hilfe")
        
        about_action = QAction("Über...", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _setup_status_bar(self):
        """Erstellt die Statusleiste"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.connection_label = QLabel("Nicht verbunden")
        self.status_bar.addPermanentWidget(self.connection_label)
        
    def _on_mower_selection_changed(self):
        """Behandelt Änderung der Mäher-Auswahl"""
        mower_id = self.status_widget.get_selected_mower_id()
        if mower_id:
            self.mower_selection_changed.emit(mower_id)
            
    def _show_about(self):
        """Zeigt About-Dialog"""
        QMessageBox.about(
            self,
            "Über Mammotion Linux App",
            "Mammotion Linux App v0.1.0\n\n"
            "Eine moderne Linux-Anwendung zur Verwaltung\n"
            "von Mammotion Mährobotern.\n\n"
            "Features:\n"
            "• Mäher-Steuerung\n"
            "• Status-Überwachung\n"
            "• Desktop-Benachrichtigungen\n"
            "• Multi-Mäher-Unterstützung"
        )
        
    # Public Methods für Controller
    
    def update_connection_status(self, connected: bool):
        """Aktualisiert den Verbindungsstatus"""
        self._is_connected = connected
        
        if connected:
            self.connection_label.setText("Verbunden")
            self.connection_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.connection_label.setText("Nicht verbunden")
            self.connection_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            
    def update_mower_list(self, mowers: list):
        """Aktualisiert die Liste der verfügbaren Mäher"""
        self.status_widget.update_mower_list(mowers)
        
    def update_current_mower(self, mower_info: MowerInfo):
        """Aktualisiert die Anzeige des aktuellen Mähers"""
        self._current_mower = mower_info
        self.status_widget.update_mower_info(mower_info)
        self.control_widget.update_status(mower_info.status)
        
    def show_error(self, title: str, message: str):
        """Zeigt eine Fehlermeldung"""
        QMessageBox.critical(self, title, message)
        
    def show_info(self, title: str, message: str):
        """Zeigt eine Informationsmeldung"""
        QMessageBox.information(self, title, message)
        
    def get_control_widget(self) -> ControlWidget:
        """Gibt das Control-Widget zurück (für Signal-Verbindungen)"""
        return self.control_widget
