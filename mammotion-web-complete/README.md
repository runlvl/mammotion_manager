# 🚀 Mammotion Web Control - Komplettpaket

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
- **API-Docs**: http://localhost:8000/docs

## 🔐 Login
Verwenden Sie Ihre echten Mammotion-Zugangsdaten.

## 🛑 Stoppen
**Ctrl+C** im Terminal

---
**Alles bereit zum Starten!** 🎉
