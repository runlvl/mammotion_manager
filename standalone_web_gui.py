"""
Standalone Web-GUI für Mammotion

Robuste, plattformunabhängige Benutzeroberfläche mit großen UI-Elementen.
Löst alle Qt-Größenprobleme durch Web-Technologie.
"""

import logging
import webbrowser
import threading
from typing import Optional, Callable, Dict, Any
from flask import Flask, render_template_string, request, jsonify, redirect


class StandaloneMammotionWebGUI:
    """
    Standalone Web-GUI für Mammotion
    
    Garantiert große UI-Elemente ohne Plattform-spezifische Probleme.
    """
    
    def __init__(self, port: int = 5000):
        self.port = port
        self.app = Flask(__name__)
        self.app.secret_key = 'mammotion-secret-2024'
        
        # Status
        self.is_logged_in = False
        self.user_email = ""
        self.mower_data = {
            'status': 'Bereit',
            'battery_level': 85,
            'position': 'Ladestation',
            'model': 'Luba 2 AWD',
            'name': 'Test-Mäher'
        }
        
        # Callbacks
        self.on_login: Optional[Callable] = None
        self.on_command: Optional[Callable] = None
        
        self._setup_routes()
        
    def _setup_routes(self):
        """Richtet die Flask-Routen ein"""
        
        @self.app.route('/')
        def index():
            if self.is_logged_in:
                return self._render_dashboard()
            else:
                return self._render_login()
                
        @self.app.route('/login', methods=['POST'])
        def login():
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            remember = request.form.get('remember') == 'on'
            
            if not email or not password:
                return jsonify({'success': False, 'message': 'E-Mail und Passwort sind erforderlich'})
                
            # Für Demo: Jeder Login ist erfolgreich
            if email and password:
                self.is_logged_in = True
                self.user_email = email
                return jsonify({'success': True, 'redirect': '/'})
            else:
                return jsonify({'success': False, 'message': 'Ungültige Zugangsdaten'})
                
        @self.app.route('/command', methods=['POST'])
        def command():
            if not self.is_logged_in:
                return jsonify({'success': False, 'message': 'Nicht angemeldet'})
                
            cmd = request.form.get('command')
            
            # Simuliere Befehlsausführung
            if cmd == 'start_mowing':
                self.mower_data['status'] = 'Mäht'
            elif cmd == 'stop_mowing':
                self.mower_data['status'] = 'Gestoppt'
            elif cmd == 'return_to_dock':
                self.mower_data['status'] = 'Kehrt zur Ladestation zurück'
                
            return jsonify({'success': True})
            
        @self.app.route('/status')
        def status():
            return jsonify({
                'logged_in': self.is_logged_in,
                'user_email': self.user_email,
                'mower_data': self.mower_data
            })
            
        @self.app.route('/logout')
        def logout():
            self.is_logged_in = False
            self.user_email = ""
            return redirect('/')
            
    def _render_login(self) -> str:
        """Rendert die Login-Seite mit GROSSEN UI-Elementen"""
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
            box-shadow: 0 15px 50px rgba(0,0,0,0.15);
            padding: 80px 60px;
            width: 100%;
            max-width: 650px;
            border: 3px solid #dee2e6;
        }
        
        .header {
            text-align: center;
            margin-bottom: 60px;
        }
        
        .title {
            font-size: 52px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            letter-spacing: -2px;
        }
        
        .subtitle {
            font-size: 28px;
            color: #6c757d;
            margin-bottom: 20px;
            font-weight: 500;
        }
        
        .description {
            font-size: 20px;
            color: #6c757d;
            line-height: 1.6;
            margin-bottom: 40px;
        }
        
        .separator {
            height: 3px;
            background: linear-gradient(90deg, #dee2e6, #adb5bd, #dee2e6);
            margin: 40px 0;
            border-radius: 2px;
        }
        
        .form-group {
            margin-bottom: 40px;
        }
        
        .form-label {
            display: block;
            font-size: 22px;
            font-weight: 600;
            color: #495057;
            margin-bottom: 15px;
        }
        
        .form-input {
            width: 100%;
            padding: 30px 30px;
            font-size: 20px;
            border: 4px solid #dee2e6;
            border-radius: 18px;
            background: white;
            color: #495057;
            transition: all 0.3s ease;
            min-height: 90px;
            line-height: 1.4;
            font-family: inherit;
        }
        
        .form-input:focus {
            outline: none;
            border-color: #0d6efd;
            box-shadow: 0 0 0 4px rgba(13, 110, 253, 0.25);
            background: #ffffff;
        }
        
        .form-input:hover {
            border-color: #adb5bd;
        }
        
        .form-input::placeholder {
            color: #adb5bd;
            font-size: 18px;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            margin: 40px 0;
        }
        
        .checkbox {
            width: 32px;
            height: 32px;
            margin-right: 20px;
            accent-color: #0d6efd;
            cursor: pointer;
        }
        
        .checkbox-label {
            font-size: 20px;
            color: #6c757d;
            cursor: pointer;
            user-select: none;
        }
        
        .button-group {
            display: flex;
            gap: 30px;
            justify-content: center;
            margin-top: 50px;
        }
        
        .btn {
            padding: 25px 50px;
            font-size: 20px;
            font-weight: 600;
            border: none;
            border-radius: 18px;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 200px;
            min-height: 80px;
            font-family: inherit;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #198754, #20c997);
            color: white;
            box-shadow: 0 5px 20px rgba(25, 135, 84, 0.3);
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, #157347, #1aa179);
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(25, 135, 84, 0.4);
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
            transform: translateY(-3px);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        .progress {
            width: 100%;
            height: 18px;
            background: #f8f9fa;
            border-radius: 10px;
            border: 3px solid #dee2e6;
            margin: 25px 0;
            overflow: hidden;
            display: none;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #0d6efd, #0b5ed7, #0d6efd);
            animation: progress-wave 2s infinite;
            border-radius: 6px;
        }
        
        @keyframes progress-wave {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }
        
        .error-message {
            background: linear-gradient(135deg, #f8d7da, #f1aeb5);
            color: #721c24;
            padding: 20px 25px;
            border-radius: 12px;
            border: 3px solid #f5c6cb;
            margin: 25px 0;
            font-size: 18px;
            font-weight: 500;
            display: none;
        }
        
        .success-message {
            background: linear-gradient(135deg, #d1e7dd, #a3cfbb);
            color: #0f5132;
            padding: 20px 25px;
            border-radius: 12px;
            border: 3px solid #badbcc;
            margin: 25px 0;
            font-size: 18px;
            font-weight: 500;
            display: none;
        }
        
        @media (max-width: 768px) {
            .login-container {
                padding: 50px 30px;
            }
            
            .title {
                font-size: 40px;
            }
            
            .subtitle {
                font-size: 22px;
            }
            
            .button-group {
                flex-direction: column;
                gap: 20px;
            }
            
            .btn {
                width: 100%;
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
            <div class="success-message" id="successMessage"></div>
            
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
            const successMessage = document.getElementById('successMessage');
            
            // UI für Login-Prozess
            loginBtn.disabled = true;
            loginBtn.textContent = 'Verbinde mit Mammotion...';
            progress.style.display = 'block';
            errorMessage.style.display = 'none';
            successMessage.style.display = 'none';
            
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
                    successMessage.textContent = 'Anmeldung erfolgreich! Weiterleitung zum Dashboard...';
                    successMessage.style.display = 'block';
                    
                    setTimeout(() => {
                        window.location.href = result.redirect || '/';
                    }, 1500);
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
            if (e.key === 'Enter' && !document.getElementById('loginBtn').disabled) {
                document.getElementById('loginForm').dispatchEvent(new Event('submit'));
            }
        });
        
        // Demo-Daten einfügen für schnellen Test
        document.getElementById('email').value = 'test@mammotion.com';
        document.getElementById('password').value = 'testpassword';
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
            background: linear-gradient(135deg, white, #f8f9fa);
            padding: 25px 50px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #dee2e6;
        }
        
        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .user-info {
            display: flex;
            align-items: center;
            gap: 25px;
        }
        
        .user-email {
            font-size: 18px;
            color: #6c757d;
            font-weight: 500;
        }
        
        .logout-btn {
            padding: 12px 25px;
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .logout-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(220, 53, 69, 0.3);
        }
        
        .container {
            max-width: 1400px;
            margin: 50px auto;
            padding: 0 30px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 40px;
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
            border: 2px solid #dee2e6;
        }
        
        .card-title {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 30px;
            border-bottom: 3px solid #dee2e6;
            padding-bottom: 15px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            border-bottom: 2px solid #f8f9fa;
        }
        
        .status-item:last-child {
            border-bottom: none;
        }
        
        .status-label {
            font-size: 20px;
            color: #495057;
            font-weight: 500;
        }
        
        .status-value {
            font-size: 20px;
            font-weight: 700;
            color: #198754;
            background: #f8f9fa;
            padding: 8px 15px;
            border-radius: 8px;
        }
        
        .control-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
        }
        
        .control-btn {
            padding: 25px 20px;
            font-size: 20px;
            font-weight: 600;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 80px;
            font-family: inherit;
        }
        
        .btn-start {
            background: linear-gradient(135deg, #198754, #20c997);
            color: white;
            box-shadow: 0 5px 20px rgba(25, 135, 84, 0.3);
        }
        
        .btn-stop {
            background: linear-gradient(135deg, #dc3545, #e55353);
            color: white;
            box-shadow: 0 5px 20px rgba(220, 53, 69, 0.3);
        }
        
        .btn-dock {
            background: linear-gradient(135deg, #0d6efd, #3d8bfd);
            color: white;
            grid-column: 1 / -1;
            box-shadow: 0 5px 20px rgba(13, 110, 253, 0.3);
        }
        
        .control-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .control-btn:active {
            transform: translateY(-1px);
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
            
            .header {
                padding: 20px 25px;
                flex-direction: column;
                gap: 15px;
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
                <h2 class="card-title">🤖 Mäher-Status</h2>
                <div class="status-item">
                    <span class="status-label">Status:</span>
                    <span class="status-value" id="mowerStatus">{{ mower_data.status }}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Akku:</span>
                    <span class="status-value" id="batteryLevel">{{ mower_data.battery_level }}%</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Position:</span>
                    <span class="status-value" id="position">{{ mower_data.position }}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Modell:</span>
                    <span class="status-value" id="model">{{ mower_data.model }}</span>
                </div>
            </div>
            
            <div class="card">
                <h2 class="card-title">🎮 Steuerung</h2>
                <div class="control-buttons">
                    <button class="control-btn btn-start" onclick="sendCommand('start_mowing')">
                        ▶️ Mähen starten
                    </button>
                    <button class="control-btn btn-stop" onclick="sendCommand('stop_mowing')">
                        ⏹️ Mähen stoppen
                    </button>
                    <button class="control-btn btn-dock" onclick="sendCommand('return_to_dock')">
                        🏠 Zur Ladestation
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
                    // Erfolgs-Animation
                    const btn = event.target;
                    const originalText = btn.textContent;
                    btn.textContent = '✅ Erfolgreich!';
                    btn.style.background = '#28a745';
                    
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.style.background = '';
                        updateStatus();
                    }, 2000);
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
        
        // Status alle 10 Sekunden aktualisieren
        setInterval(updateStatus, 10000);
    </script>
</body>
</html>
        """, user_email=self.user_email, mower_data=self.mower_data)
        
    def start(self, open_browser: bool = True):
        """Startet die Web-GUI"""
        if open_browser:
            threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{self.port}')).start()
            
        print(f"🌐 Web-GUI gestartet auf http://localhost:{self.port}")
        print("📱 Große UI-Elemente garantiert!")
        print("🔧 Keine Qt-Probleme mehr!")
        
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)


def main():
    """Hauptfunktion"""
    print("=== Mammotion Standalone Web-GUI ===")
    print()
    print("✅ Lösung für Qt-Größenprobleme:")
    print("   • 90px hohe Eingabefelder (garantiert!)")
    print("   • 80px hohe Buttons")
    print("   • 20-52px Schriftgrößen")
    print("   • Responsive Design")
    print("   • Plattformunabhängig")
    print()
    print("🚀 Demo-Login:")
    print("   E-Mail: test@mammotion.com")
    print("   Passwort: testpassword")
    print()
    print("Drücken Sie Ctrl+C zum Beenden")
    print()
    
    gui = StandaloneMammotionWebGUI(port=5000)
    
    try:
        gui.start(open_browser=True)
    except KeyboardInterrupt:
        print("\n✅ Web-GUI beendet")
    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    main()
