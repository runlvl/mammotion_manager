# Mammotion Web Control - Lokale Installation

## 🚀 Schnellstart für Ihr System

### 1. Verzeichnis erstellen
```bash
mkdir -p ~/mammotion-web-local
cd ~/mammotion-web-local
```

### 2. Dependencies installieren
```bash
pip3 install -r requirements.txt
```

### 3. Redis starten (falls nicht läuft)
```bash
# Ubuntu/Debian:
sudo systemctl start redis-server

# Fedora/RHEL:
sudo systemctl start redis

# Oder Docker:
docker run -d -p 6379:6379 redis:alpine
```

### 4. App starten
```bash
python -m uvicorn src.mammotion_web.app:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Browser öffnen
```
http://localhost:8000
```

## ✅ Das ist Ihr lokales Projekt!

Alle Dateien sind jetzt in `~/mammotion-web-local/` verfügbar.
