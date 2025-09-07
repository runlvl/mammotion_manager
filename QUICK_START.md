# Mammotion Linux App - Schnellstart

## 🚀 Sofort loslegen:

### 1. Entpacken
```bash
tar -xzf mammotion-app-complete.tar.gz
cd mammotion-app
```

### 2. Prüfen ob alle Dateien da sind
```bash
ls -la main.py requirements.txt
# Sollte beide Dateien anzeigen
```

### 3. Dependencies installieren
```bash
pip3 install -r requirements.txt
```

### 4. App starten
```bash
python3 main.py
```

## ✅ Erwartetes Ergebnis:

- **Login-Fenster** öffnet sich mit professionellem Layout
- **Titel**: "Mammotion Login" 
- **Felder**: E-Mail und Passwort mit Labels darüber
- **Buttons**: "Abbrechen" und "Anmelden" nebeneinander

## 🔧 Bei Problemen:

### Fehler: "Datei nicht gefunden"
```bash
# Prüfe Verzeichnisinhalt
ls -la
# main.py sollte sichtbar sein
```

### Fehler: "Module nicht gefunden"
```bash
# Installiere Dependencies
pip3 install PySide6 aiohttp
```

### GUI startet nicht
```bash
# Teste ohne GUI
python3 test_gui_components.py
```

## 📁 Vollständige Dateiliste:

```
mammotion-app/
├── main.py                    ← Hauptdatei zum Starten
├── requirements.txt           ← Dependencies
├── README.md                  ← Dokumentation
├── INSTALL_FEDORA.md         ← Fedora-Installation
├── src/                      ← Quellcode
│   ├── models/               ← API-Logik
│   ├── views/                ← GUI-Komponenten
│   └── controllers/          ← App-Logik
├── test_*.py                 ← Test-Dateien
└── fix_*.py                  ← Reparatur-Skripte
```

**Alle Dateien sind jetzt im Archiv enthalten!** ✅
