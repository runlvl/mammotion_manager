# 🚀 MAMMOTION WEB CONTROL - SCHNELLSTART

## ✅ SOFORT STARTEN

### 1. Setup (einmalig)
```bash
cd mammotion-web-complete
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Redis starten
```bash
# Ubuntu/Debian:
sudo systemctl start redis-server

# macOS:
brew services start redis

# Docker (Alternative):
docker run -d -p 6379:6379 redis:alpine
```

### 3. Server starten
```bash
./start_server.sh  # Linux/macOS
# start_server.bat  # Windows
```

**ODER manuell:**
```bash
python -m uvicorn src.mammotion_web.app:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 Zugriff
- **Web-Interface**: http://localhost:8000
- **API-Dokumentation**: http://localhost:8000/docs
- **Health-Check**: http://localhost:8000/healthz

## 🔐 Login
Verwenden Sie Ihre **echten Mammotion-Zugangsdaten**:
- E-Mail: Ihre registrierte E-Mail-Adresse
- Passwort: Ihr Mammotion-Passwort

## 🎮 Funktionen
- ✅ **Geräte-Übersicht** mit Echtzeit-Status
- ✅ **Mäher-Steuerung** (Start, Stopp, Zur Station)
- ✅ **Live-Updates** über WebSocket
- ✅ **Responsive Design** für alle Geräte
- ✅ **Sichere Authentifizierung**

## 🛑 Server stoppen
**Ctrl+C** im Terminal drücken

## 🔧 Konfiguration
Kopieren Sie `.env.example` zu `.env` und passen Sie die Einstellungen an:
```bash
cp .env.example .env
```

## 📝 Logs
Logs werden in der Konsole angezeigt. Für Datei-Logging setzen Sie `LOG_FILE` in der `.env`.

---
**Alles bereit zum Starten!** 🎉
