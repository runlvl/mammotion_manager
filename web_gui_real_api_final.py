#!/usr/bin/env python3
"""
Mammotion Web-GUI mit echter API-Integration v2

Kombiniert:
- Große, perfekt sichtbare UI-Elemente (Web-Technologie)
- Echte Mammotion-API mit korrekten Aliyun IoT-Endpunkten
- Intelligenter Fallback auf realistische Demo-Daten

Löst alle UI-Probleme und bietet echte API-Anbindung.
"""

import asyncio
import webbrowser
import threading
import time
import logging
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from real_mammotion_api_v2 import RealMammotionAPIv2

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask-App erstellen
app = Flask(__name__)
app.secret_key = 'mammotion_secret_2024'

# Globale API-Instanz
api_instance = None
current_user = None
current_devices = []

# HTML-Templates mit großen UI-Elementen
LOGIN_TEMPLATE = """
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 60px;
            width: 100%;
            max-width: 600px;
            text-align: center;
        }
        
        .logo {
            font-size: 52px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .subtitle {
            font-size: 24px;
            color: #7f8c8d;
            margin-bottom: 15px;
        }
        
        .description {
            font-size: 20px;
            color: #95a5a6;
            margin-bottom: 50px;
            line-height: 1.5;
        }
        
        .api-info {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 40px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        }
        
        .form-group {
            margin-bottom: 35px;
            text-align: left;
        }
        
        .form-group label {
            display: block;
            font-size: 22px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .form-group input {
            width: 100%;
            height: 90px;  /* EXTREME Höhe */
            padding: 30px 25px;  /* EXTREME Padding */
            font-size: 20px;  /* GROSSE Schrift */
            border: 4px solid #bdc3c7;
            border-radius: 15px;
            background: #f8f9fa;
            transition: all 0.3s ease;
            line-height: 1.5;
        }
        
        .form-group input:focus {
            outline: none;
            border-color: #3498db;
            background: white;
            box-shadow: 0 0 20px rgba(52, 152, 219, 0.2);
            transform: translateY(-2px);
        }
        
        .form-group input::placeholder {
            color: #95a5a6;
            font-size: 18px;
        }
        
        .button-group {
            display: flex;
            gap: 25px;
            margin-top: 50px;
        }
        
        .btn {
            flex: 1;
            height: 80px;  /* GROSSE Buttons */
            font-size: 20px;  /* GROSSE Schrift */
            font-weight: bold;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            box-shadow: 0 10px 20px rgba(46, 204, 113, 0.3);
        }
        
        .btn-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(46, 204, 113, 0.4);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #95a5a6, #7f8c8d);
            color: white;
            box-shadow: 0 10px 20px rgba(149, 165, 166, 0.3);
        }
        
        .btn-secondary:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(149, 165, 166, 0.4);
        }
        
        .loading {
            display: none;
            margin-top: 30px;
        }
        
        .loading-spinner {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #3498db;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .status-message {
            margin-top: 25px;
            padding: 20px;
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
        }
        
        .status-success {
            background: #d5f4e6;
            color: #27ae60;
            border: 2px solid #27ae60;
        }
        
        .status-error {
            background: #fdf2f2;
            color: #e74c3c;
            border: 2px solid #e74c3c;
        }
        
        @media (max-width: 768px) {
            .login-container {
                padding: 40px 30px;
            }
            
            .logo {
                font-size: 42px;
            }
            
            .subtitle {
                font-size: 20px;
            }
            
            .description {
                font-size: 18px;
            }
            
            .button-group {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">Mammotion</div>
        <div class="subtitle">Mähroboter-Verwaltung</div>
        <div class="description">
            Melden Sie sich mit Ihren Mammotion-Zugangsdaten an
        </div>
        
        <div class="api-info">
            🔗 Echte API-Integration mit Aliyun IoT<br>
            📡 Verbindet sich mit echten Mammotion-Servern<br>
            🎯 Große UI-Elemente garantiert!
        </div>
        
        <form id="loginForm" method="POST">
            <div class="form-group">
                <label for="email">E-Mail-Adresse</label>
                <input type="email" id="email" name="email" 
                       placeholder="ihre.email@mammotion.com" 
                       required>
            </div>
            
            <div class="form-group">
                <label for="password">Passwort</label>
                <input type="password" id="password" name="password" 
                       placeholder="Ihr Mammotion-Passwort" 
                       required>
            </div>
            
            <div class="button-group">
                <button type="button" class="btn btn-secondary" onclick="window.close()">
                    Abbrechen
                </button>
                <button type="submit" class="btn btn-primary">
                    Anmelden
                </button>
            </div>
        </form>
        
        <div class="loading" id="loading">
            <div class="loading-spinner"></div>
            <p style="margin-top: 20px; font-size: 18px; color: #3498db;">
                Verbinde mit Mammotion-Servern...
            </p>
        </div>
        
        {% if message %}
        <div class="status-message status-{{ 'success' if success else 'error' }}">
            {{ message }}
        </div>
        {% endif %}
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Loading anzeigen
            document.getElementById('loading').style.display = 'block';
            document.querySelector('.button-group').style.display = 'none';
            
            // Form absenden
            setTimeout(() => {
                this.submit();
            }, 1000);
        });
        
        // Auto-Focus auf erstes leeres Feld
        window.onload = function() {
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            
            if (!email.value) {
                email.focus();
            } else if (!password.value) {
                password.focus();
            }
        };
    </script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
        }
        
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .header h1 {
            font-size: 48px;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .header .subtitle {
            font-size: 24px;
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        
        .api-status {
            display: inline-block;
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
        }
        
        .device-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .device-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #ecf0f1;
        }
        
        .device-name {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }
        
        .device-status {
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: linear-gradient(135deg, #27ae60, #2ecc71);
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .status-item {
            text-align: center;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 15px;
            border: 3px solid #ecf0f1;
        }
        
        .status-value {
            font-size: 36px;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 10px;
        }
        
        .status-label {
            font-size: 18px;
            color: #7f8c8d;
            font-weight: 600;
        }
        
        .control-section {
            margin-top: 40px;
        }
        
        .control-title {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 25px;
            text-align: center;
        }
        
        .control-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .control-btn {
            height: 80px;  /* GROSSE Buttons */
            font-size: 20px;  /* GROSSE Schrift */
            font-weight: bold;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: white;
        }
        
        .btn-start {
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            box-shadow: 0 10px 20px rgba(46, 204, 113, 0.3);
        }
        
        .btn-stop {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            box-shadow: 0 10px 20px rgba(231, 76, 60, 0.3);
        }
        
        .btn-dock {
            background: linear-gradient(135deg, #f39c12, #e67e22);
            box-shadow: 0 10px 20px rgba(243, 156, 18, 0.3);
        }
        
        .control-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
        }
        
        .control-btn:active {
            transform: translateY(0);
        }
        
        .footer {
            background: white;
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        
        .footer-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
        }
        
        .footer-btn {
            padding: 15px 30px;
            font-size: 18px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-refresh {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
        }
        
        .btn-logout {
            background: linear-gradient(135deg, #95a5a6, #7f8c8d);
            color: white;
        }
        
        .footer-btn:hover {
            transform: translateY(-2px);
        }
        
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        
        .loading-content {
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
        }
        
        .loading-spinner {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #3498db;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .device-grid {
                grid-template-columns: 1fr;
            }
            
            .dashboard-container {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 36px;
            }
            
            .device-name {
                font-size: 24px;
            }
            
            .control-buttons {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>Mammotion Dashboard</h1>
            <div class="subtitle">Live-Daten von Ihren Mährobotern</div>
            <div class="api-status">
                🔗 Echte API verbunden - {{ user_info.get('email', 'Unbekannt') }}
            </div>
        </div>
        
        <div class="device-grid">
            {% for device in devices %}
            <div class="device-card">
                <div class="device-header">
                    <div class="device-name">{{ device.get('deviceName', 'Unbekannter Mäher') }}</div>
                    <div class="device-status">{{ device.get('status', 'Offline') }}</div>
                </div>
                
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-value">{{ device.get('properties', {}).get('battery_level', 0) }}%</div>
                        <div class="status-label">Akku</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">{{ device.get('properties', {}).get('working_status', 'Unbekannt') }}</div>
                        <div class="status-label">Status</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">{{ device.get('properties', {}).get('position', {}).get('latitude', 0) | round(4) }}</div>
                        <div class="status-label">Breitengrad</div>
                    </div>
                    <div class="status-item">
                        <div class="status-value">{{ device.get('properties', {}).get('position', {}).get('longitude', 0) | round(4) }}</div>
                        <div class="status-label">Längengrad</div>
                    </div>
                </div>
                
                <div class="control-section">
                    <div class="control-title">Steuerung</div>
                    <div class="control-buttons">
                        <button class="control-btn btn-start" onclick="sendCommand('{{ device.get('deviceId') }}', 'start_mowing')">
                            🚀 Starten
                        </button>
                        <button class="control-btn btn-stop" onclick="sendCommand('{{ device.get('deviceId') }}', 'stop_mowing')">
                            ⏹️ Stoppen
                        </button>
                        <button class="control-btn btn-dock" onclick="sendCommand('{{ device.get('deviceId') }}', 'return_to_dock')">
                            🏠 Zur Ladestation
                        </button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="footer">
            <div class="footer-buttons">
                <button class="footer-btn btn-refresh" onclick="location.reload()">
                    🔄 Aktualisieren
                </button>
                <button class="footer-btn btn-logout" onclick="logout()">
                    🚪 Abmelden
                </button>
            </div>
            <p style="margin-top: 20px; color: #7f8c8d; font-size: 16px;">
                Letzte Aktualisierung: {{ datetime.now().strftime('%H:%M:%S') }}
            </p>
        </div>
    </div>
    
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-content">
            <div class="loading-spinner"></div>
            <p style="font-size: 18px; color: #3498db;">Befehl wird ausgeführt...</p>
        </div>
    </div>
    
    <script>
        function sendCommand(deviceId, command) {
            // Loading anzeigen
            document.getElementById('loadingOverlay').style.display = 'flex';
            
            fetch('/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device_id: deviceId,
                    command: command
                })
            })
            .then(response => response.json())
            .then(data => {
                // Loading verstecken
                document.getElementById('loadingOverlay').style.display = 'none';
                
                if (data.success) {
                    alert(`✅ Befehl "${command}" erfolgreich gesendet!`);
                    // Seite nach kurzer Verzögerung neu laden
                    setTimeout(() => location.reload(), 1000);
                } else {
                    alert(`❌ Fehler beim Senden des Befehls: ${data.error}`);
                }
            })
            .catch(error => {
                document.getElementById('loadingOverlay').style.display = 'none';
                alert(`❌ Netzwerkfehler: ${error}`);
            });
        }
        
        function logout() {
            if (confirm('Möchten Sie sich wirklich abmelden?')) {
                window.location.href = '/logout';
            }
        }
        
        // Auto-Refresh alle 30 Sekunden
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Hauptseite - zeigt Login oder Dashboard"""
    global current_user, current_devices
    
    if current_user:
        return render_template_string(DASHBOARD_TEMPLATE, 
                                    user_info=current_user, 
                                    devices=current_devices,
                                    datetime=datetime)
    else:
        return render_template_string(LOGIN_TEMPLATE)

@app.route('/', methods=['POST'])
def login():
    """Login-Handler"""
    global api_instance, current_user, current_devices
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Bitte füllen Sie alle Felder aus.",
                                    success=False)
    
    async def do_login():
        global api_instance, current_user, current_devices
        
        try:
            # API-Instanz erstellen
            api_instance = RealMammotionAPIv2()
            await api_instance.__aenter__()
            
            # Authentifizierung versuchen
            logger.info(f"Versuche Anmeldung für {email}")
            success = await api_instance.authenticate(email, password)
            
            if success:
                current_user = api_instance.user_info
                current_user['email'] = email
                
                # Geräte laden
                devices = await api_instance.get_devices()
                current_devices = devices
                
                logger.info(f"Anmeldung erfolgreich! {len(devices)} Geräte gefunden.")
                return True
            else:
                logger.error("Anmeldung fehlgeschlagen")
                return False
                
        except Exception as e:
            logger.error(f"Login-Fehler: {e}")
            return False
    
    # Async-Login ausführen
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(do_login())
    finally:
        loop.close()
    
    if success:
        return redirect(url_for('index'))
    else:
        return render_template_string(LOGIN_TEMPLATE, 
                                    message="Anmeldung fehlgeschlagen. Bitte überprüfen Sie Ihre Zugangsdaten.",
                                    success=False)

@app.route('/command', methods=['POST'])
def send_command():
    """Befehl an Mäher senden"""
    global api_instance
    
    if not api_instance or not current_user:
        return jsonify({'success': False, 'error': 'Nicht angemeldet'})
    
    data = request.get_json()
    device_id = data.get('device_id')
    command = data.get('command')
    
    if not device_id or not command:
        return jsonify({'success': False, 'error': 'Fehlende Parameter'})
    
    async def do_command():
        try:
            result = await api_instance.send_command(device_id, command)
            return result
        except Exception as e:
            logger.error(f"Befehl-Fehler: {e}")
            return False
    
    # Async-Befehl ausführen
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(do_command())
    finally:
        loop.close()
    
    if success:
        return jsonify({'success': True, 'message': f'Befehl "{command}" erfolgreich gesendet'})
    else:
        return jsonify({'success': False, 'error': 'Befehl konnte nicht gesendet werden'})

@app.route('/logout')
def logout():
    """Logout-Handler"""
    global api_instance, current_user, current_devices
    
    # Cleanup
    if api_instance:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(api_instance.__aexit__(None, None, None))
            loop.close()
        except:
            pass
        api_instance = None
    
    current_user = None
    current_devices = []
    
    return redirect(url_for('index'))

def open_browser():
    """Öffnet den Browser nach kurzer Verzögerung"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("🎉 MAMMOTION WEB-GUI MIT ECHTER API v2")
    print("=" * 60)
    print()
    print("✅ Lösung für Qt-Größenprobleme:")
    print("   • 90px hohe Eingabefelder (garantiert!)")
    print("   • 80px hohe Buttons")
    print("   • 20-52px Schriftgrößen")
    print()
    print("🔗 Echte Mammotion-API-Integration:")
    print("   • Aliyun IoT-Endpunkte (iot-auth-global.aliyuncs.com)")
    print("   • Mammotion-Cloud-Verbindung")
    print("   • Intelligenter Fallback auf Demo-Daten")
    print()
    print("🚀 Demo-Login (falls echte Server nicht erreichbar):")
    print("   E-Mail: test@mammotion.com")
    print("   Passwort: testpassword")
    print()
    print("🌐 Web-GUI gestartet auf http://localhost:5000")
    print("📱 Browser öffnet sich automatisch...")
    print()
    print("⏹️  Zum Beenden: Ctrl+C drücken")
    print("=" * 60)
    
    # Browser in separatem Thread öffnen
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Flask-App starten
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Mammotion Web-GUI beendet.")
        print("Vielen Dank für die Nutzung!")

if __name__ == '__main__':
    main()
