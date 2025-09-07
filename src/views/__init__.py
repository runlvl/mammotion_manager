"""Views Package - Benutzeroberfläche und GUI-Komponenten"""

# Import nur die Web-GUI per Default, PySide6-abhängige Imports nur bei Bedarf
try:
    from .login_window import LoginWindow
    from .main_window import MainWindow, StatusWidget, ControlWidget  
    from .app import MammotionApp, create_app
    
    __all__ = [
        'LoginWindow', 
        'MainWindow', 
        'StatusWidget', 
        'ControlWidget',
        'MammotionApp', 
        'create_app',
        'WebGUI'
    ]
except ImportError:
    # PySide6 nicht verfügbar - nur Web-GUI
    __all__ = ['WebGUI']

# Web-GUI ist immer verfügbar
from .web_gui import WebGUI
