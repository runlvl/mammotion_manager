"""
Web-basierte GUI für die Mammotion App

Verwendet Flask für eine robuste, plattformunabhängige Benutzeroberfläche.
Garantiert große UI-Elemente ohne Qt-Probleme.
"""

import logging
import asyncio
import threading
import webbrowser
from typing import Optional, Callable, Dict, Any
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os
import signal


class WebGUI:
    """
    Web-basierte GUI für die Mammotion App
    
    Vorteile:
    - Plattformunabhängig
    - Keine Qt-Probleme
    - Responsive Design
    - Große UI-Elemente garantiert
    """
    
    def __init__(self, port: int = 5000):
        self.logger = logging.getLogger(__name__)
        self.port = port
        self.app = Flask(__name__)
        self.app.secret_key = 'mammotion-secret-key-2024'
        
        # Callbacks
        self.on_login: Optional[Callable] = None
        self.on_command: Optional[Callable] = None
        
        # Status
        self.is_logged_in = False
        self.user_email = ""
        self.mower_data = {}
        self.login_in_progress = False
        
        # Flask-Routen einrichten
        self._setup_routes()
        
    def _setup_routes(self):
        """Richtet die Flask-Routen ein"""
        
        @self.app.route('/')
        def index():
            """Hauptseite - Login oder Dashboard"""
            if self.is_logged_in:
                return self._render_dashboard()
            else:
                return self._render_login()
                
        @self.app.route('/login', methods=['POST'])
        def login():
            """Login-Verarbeitung"""
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember') == 'on'
            
            if not email or not password:
                return jsonify({'success': False, 'message': 'E-Mail und Passwort sind erforderlich'})
                
            # Login-Callback aufrufen
            if self.on_login:
                self.login_in_progress = True
                success = self.on_login(email, password, remember)
                self.login_in_progress = False
                
                if success:
                    self.is_logged_in = True
                    self.user_email = email
                    return jsonify({'success': True, 'redirect': '/'})
                else:
                    return jsonify({'success': False, 'message': 'Anmeldung fehlgeschlagen'})
            else:
                return jsonify({'success': False, 'message': 'Login-Handler nicht verfügbar'})
                
        @self.app.route('/command', methods=['POST'])
        def command():
            """Mäher-Befehle"""
            if not self.is_logged_in:
                return jsonify({'success': False, 'message': 'Nicht angemeldet'})
                
            cmd = request.form.get('command')
            device_id = request.form.get('device_id', 'default')
            
            if self.on_command:
                success = self.on_command(device_id, cmd)
                return jsonify({'success': success})
            else:
                return jsonify({'success': False, 'message': 'Command-Handler nicht verfügbar'})
                
        @self.app.route('/status')
        def status():
            """Status-API"""
            return jsonify({
                'logged_in': self.is_logged_in,
                'user_email': self.user_email,
                'mower_data': self.mower_data,
                'login_in_progress': self.login_in_progress
            })
            
        @self.app.route('/logout')
        def logout():
            """Logout"""
            self.is_logged_in = False
            self.user_email = ""
            self.mower_data = {}
            return redirect('/')
            
    def _render_login(self) -> str:
        """Rendert die Login-Seite"""
        return render_template_string("""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mammotion Mähroboter - Anmeldung</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 60px;
            width: 100%;
            max-width: 600px;
            border: 2px solid #dee2e6;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        
        .title {
            font-size: 48px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            letter-spacing: -2px;
        }
        
        .subtitle {
            font-size: 24px;
            color: #6c757d;
            margin-bottom: 15px;
        }
        
        .description {
            font-size: 18px;
            color: #6c757d;
            line-height: 1.5;
            margin-bottom: 30px;
        }
        
        .separator {
            height: 2px;
            background: #dee2e6;
            margin: 30px 0;
        }
        
        .form-group {
            margin-bottom: 35px;
        }
        
        .form-label {
            display: block;
            font-size: 20px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 12px;
        }
        
        .form-input {
            width: 100%;
            padding: 25px 25px;
            font-size: 18px;
            border: 4px solid #dee2e6;
            border-radius: 15px;
            background: white;
            color: #495057;
            transition: all 0.3s ease;
            min-height: 80px;
            line-height: 1.4;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #0d6efd;
            box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.25);
        }
        
        .form-input:hover {
            border-color: #adb5bd;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            margin: 30px 0;
        }
        
        .checkbox {
            width: 28px;
            height: 28px;
            margin-right: 15px;
            accent-color: #0d6efd;
        }
        
        .checkbox-label {
            font-size: 18px;
            color: #6c757d;
            cursor: pointer;
        }
        
        .button-group {
            display: flex;
            gap: 25px;
            justify-content: center;
            margin-top: 40px;
        }
        
        .btn {
            padding: 20px 40px;
            font-size: 18px;
            font-weight: 600;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 180px;
            min-height: 70px;
        }
        
        .btn-primary {
            background: #198754;
            color: white;
        }
        
        .btn-primary:hover {
            background: #157347;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #6c757d;
            border: 4px solid #dee2e6;
        }
        
        .btn-secondary:hover {
            background: #e9ecef;
            border-color: #adb5bd;
            color: #495057;
            transform: translateY(-2px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .progress {
            width: 100%;
            height: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 3px solid #dee2e6;
            margin: 20px 0;
            overflow: hidden;
            display: none;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #0d6efd, #0b5ed7);
            animation: progress-animation 2s infinite;
        }
        
        @keyframes progress-animation {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px 20px;
            border-radius: 10px;
            border: 2px solid #f5c6cb;
            margin: 20px 0;
            font-size: 16px;
            display: none;
        }
        
        @media (max-width: 768px) {
            .login-container {
                padding: 40px 30px;
            }
            
            .title {
                font-size: 36px;
            }
            
            .subtitle {
                font-size: 20px;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="header">
            <h1 class="title">Mammotion</h1>
            <h2 class="subtitle">Mähroboter-Verwaltung</h2>
            <p class="description">
                Melden Sie sich mit Ihren Mammotion-Zugangsdaten an,<br>
                um Ihren Mähroboter zu verwalten.
            </p>
            <div class="separator"></div>
        </div>
        
        <form id="loginForm">
            <div class="form-group">
                <label class="form-label" for="email">E-Mail-Adresse</label>
                <input type="email" id="email" name="email" class="form-input" 
                       placeholder="ihre.email@mammotion.com" required>
            </div>
            
            <div class="form-group">
                <label class="form-label" for="password">Passwort</label>
                <input type="password" id="password" name="password" class="form-input" 
                       placeholder="Ihr Mammotion-Passwort" required>
            </div>
            
            <div class="checkbox-group">
                <input type="checkbox" id="remember" name="remember" class="checkbox">
                <label class="checkbox-label" for="remember">Zugangsdaten sicher speichern</label>
            </div>
            
            <div class="progress" id="progress">
                <div class="progress-bar"></div>
            </div>
            
            <div class="error-message" id="errorMessage"></div>
            
            <div class="button-group">
                <button type="button" class="btn btn-secondary" onclick="window.close()">
                    Abbrechen
                </button>
                <button type="submit" class="btn btn-primary" id="loginBtn">
                    Anmelden
                </button>
            </div>
        </form>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const loginBtn = document.getElementById('loginBtn');
            const progress = document.getElementById('progress');
            const errorMessage = document.getElementById('errorMessage');
            
            // UI für Login-Prozess
            loginBtn.disabled = true;
            loginBtn.textContent = 'Verbinde mit Mammotion...';
            progress.style.display = 'block';
            errorMessage.style.display = 'none';
            
            // Form-Daten sammeln
            const formData = new FormData(this);
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    loginBtn.textContent = 'Erfolgreich angemeldet!';
                    setTimeout(() => {
                        window.location.href = result.redirect || '/';
                    }, 1000);
                } else {
                    throw new Error(result.message || 'Anmeldung fehlgeschlagen');
                }
            } catch (error) {
                errorMessage.textContent = error.message;
                errorMessage.style.display = 'block';
                
                // UI zurücksetzen
                loginBtn.disabled = false;
                loginBtn.textContent = 'Anmelden';
                progress.style.display = 'none';
            }
        });
        
        // Enter-Taste für Login
        document.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                document.getElementById('loginForm').dispatchEvent(new Event('submit'));
            }
        });
    </script>
</body>
</html>
        """)
        
    def _render_dashboard(self) -> str:
        """Rendert das Dashboard"""
        return render_template_string("""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mammotion Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Ubuntu', 'Roboto', sans-serif;
            background: #f8f9fa;
            min-height: 100vh;
        }
        
        .header {
            background: white;
            padding: 20px 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .user-email {
            font-size: 16px;
            color: #6c757d;
        }
        
        .logout-btn {
            padding: 10px 20px;
            background: #dc3545;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .container {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .card-title {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #dee2e6;
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-label {
            font-size: 18px;
            color: #495057;
        }
        
        .status-value {
            font-size: 18px;
            font-weight: 600;
            color: #198754;
        }
        
        .control-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .control-btn {
            padding: 20px;
            font-size: 18px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 70px;
        }
        
        .btn-start {
            background: #198754;
            color: white;
        }
        
        .btn-stop {
            background: #dc3545;
            color: white;
        }
        
        .btn-dock {
            background: #0d6efd;
            color: white;
            grid-column: 1 / -1;
        }
        
        .control-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .control-buttons {
                grid-template-columns: 1fr;
            }
            
            .btn-dock {
                grid-column: 1;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Mammotion Dashboard</div>
        <div class="user-info">
            <span class="user-email">{{ user_email }}</span>
            <button class="logout-btn" onclick="window.location.href='/logout'">Abmelden</button>
        </div>
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <div class="card">
                <h2 class="card-title">Mäher-Status</h2>
                <div class="status-item">
                    <span class="status-label">Status:</span>
                    <span class="status-value" id="mowerStatus">Bereit</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Akku:</span>
                    <span class="status-value" id="batteryLevel">85%</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Position:</span>
                    <span class="status-value" id="position">Ladestation</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Modell:</span>
                    <span class="status-value" id="model">Luba 2 AWD</span>
                </div>
            </div>
            
            <div class="card">
                <h2 class="card-title">Steuerung</h2>
                <div class="control-buttons">
                    <button class="control-btn btn-start" onclick="sendCommand('start_mowing')">
                        Mähen starten
                    </button>
                    <button class="control-btn btn-stop" onclick="sendCommand('stop_mowing')">
                        Mähen stoppen
                    </button>
                    <button class="control-btn btn-dock" onclick="sendCommand('return_to_dock')">
                        Zur Ladestation
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        async function sendCommand(command) {
            try {
                const formData = new FormData();
                formData.append('command', command);
                formData.append('device_id', 'default');
                
                const response = await fetch('/command', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Befehl erfolgreich gesendet!');
                    updateStatus();
                } else {
                    alert('Fehler beim Senden des Befehls: ' + (result.message || 'Unbekannter Fehler'));
                }
            } catch (error) {
                alert('Netzwerkfehler: ' + error.message);
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/status');
                const data = await response.json();
                
                if (data.mower_data) {
                    document.getElementById('mowerStatus').textContent = data.mower_data.status || 'Unbekannt';
                    document.getElementById('batteryLevel').textContent = (data.mower_data.battery_level || 0) + '%';
                    document.getElementById('position').textContent = data.mower_data.position || 'Unbekannt';
                    document.getElementById('model').textContent = data.mower_data.model || 'Unbekannt';
                }
            } catch (error) {
                console.error('Status-Update fehlgeschlagen:', error);
            }
        }
        
        // Status alle 5 Sekunden aktualisieren
        setInterval(updateStatus, 5000);
        updateStatus();
    </script>
</body>
</html>
        """, user_email=self.user_email)
        
    def set_login_callback(self, callback: Callable[[str, str, bool], bool]):
        """Setzt den Login-Callback"""
        self.on_login = callback
        
    def set_command_callback(self, callback: Callable[[str, str], bool]):
        """Setzt den Command-Callback"""
        self.on_command = callback
        
    def update_mower_data(self, data: Dict[str, Any]):
        """Aktualisiert die Mäher-Daten"""
        self.mower_data = data
        
    def start(self, open_browser: bool = True):
        """Startet den Web-Server"""
        if open_browser:
            # Browser nach kurzer Verzögerung öffnen
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{self.port}')).start()
            
        self.logger.info(f"Web-GUI gestartet auf http://localhost:{self.port}")
        
        # Flask in separatem Thread starten
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
        
    def stop(self):
        """Stoppt den Web-Server"""
        # Graceful shutdown
        os.kill(os.getpid(), signal.SIGINT)


def test_web_gui():
    """Test-Funktion für die Web-GUI"""
    def on_login(email, password, remember):
        print(f"Login: {email}, {password}, {remember}")
        return True  # Simuliere erfolgreichen Login
        
    def on_command(device_id, command):
        print(f"Command: {device_id}, {command}")
        return True  # Simuliere erfolgreichen Befehl
        
    gui = WebGUI(port=5000)
    gui.set_login_callback(on_login)
    gui.set_command_callback(on_command)
    
    # Test-Mäher-Daten
    gui.update_mower_data({
        'status': 'Bereit',
        'battery_level': 85,
        'position': 'Ladestation',
        'model': 'Luba 2 AWD'
    })
    
    try:
        gui.start(open_browser=True)
    except KeyboardInterrupt:
        print("Web-GUI gestoppt")


if __name__ == "__main__":
    test_web_gui()
