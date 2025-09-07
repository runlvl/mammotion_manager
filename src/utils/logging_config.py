"""
Logging-Konfiguration für die Mammotion App

Zentralisierte Logging-Konfiguration mit verschiedenen Log-Leveln
und Ausgabeformaten für Entwicklung und Produktion.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> None:
    """
    Konfiguriert das Logging-System
    
    Args:
        log_level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional - Pfad zur Log-Datei
        console_output: Ob Logs auch auf der Konsole ausgegeben werden sollen
    """
    
    # Log-Level konvertieren
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Root Logger konfigurieren
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Bestehende Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Formatter definieren
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File Handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Spezielle Logger für externe Bibliotheken konfigurieren
    # PyMammotion Logger
    pymammotion_logger = logging.getLogger('pymammotion')
    pymammotion_logger.setLevel(logging.WARNING)  # Weniger verbose
    
    # PySide6 Logger
    pyside_logger = logging.getLogger('PySide6')
    pyside_logger.setLevel(logging.WARNING)
    
    # Asyncio Logger
    asyncio_logger = logging.getLogger('asyncio')
    asyncio_logger.setLevel(logging.WARNING)
    
    logging.info(f"Logging konfiguriert - Level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """
    Erstellt einen Logger mit dem gegebenen Namen
    
    Args:
        name: Name des Loggers (normalerweise __name__)
        
    Returns:
        Konfigurierter Logger
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin-Klasse für einfaches Logging in anderen Klassen
    
    Verwendung:
        class MyClass(LoggerMixin):
            def some_method(self):
                self.logger.info("Das ist eine Log-Nachricht")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Gibt einen Logger für die aktuelle Klasse zurück"""
        return logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")


# Vordefinierte Log-Konfigurationen
def setup_development_logging() -> None:
    """Konfiguration für Entwicklung - ausführliche Logs"""
    setup_logging(
        log_level="DEBUG",
        log_file="logs/mammotion_app_dev.log",
        console_output=True
    )


def setup_production_logging() -> None:
    """Konfiguration für Produktion - weniger verbose"""
    setup_logging(
        log_level="INFO",
        log_file="logs/mammotion_app.log",
        console_output=False
    )


def setup_testing_logging() -> None:
    """Konfiguration für Tests - minimal"""
    setup_logging(
        log_level="WARNING",
        console_output=True
    )
