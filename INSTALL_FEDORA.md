# Mammotion Linux App - Fedora Installation

Vollständige Installationsanleitung für Fedora 39+ (getestet auf Fedora 42).

## 🚀 Schnellinstallation (Empfohlen)

### Automatisches Installationsskript
```bash
# 1. App herunterladen und entpacken
cd ~/Downloads
tar -xzf mammotion-app.tar.gz
cd mammotion-app

# 2. Installationsskript ausführen
chmod +x install_fedora.sh
./install_fedora.sh

# 3. App starten
mammotion-app
```

Das Skript installiert automatisch:
- ✅ Alle System-Dependencies
- ✅ Python Virtual Environment
- ✅ App-Dependencies
- ✅ Desktop-Integration
- ✅ Startskript

## 🔧 Manuelle Installation

### Schritt 1: System-Dependencies
```bash
# System aktualisieren
sudo dnf update -y

# Python und Entwicklungstools
sudo dnf install -y python3 python3-pip python3-devel python3-venv gcc gcc-c++

# Qt6 für GUI
sudo dnf install -y qt6-qtbase-devel qt6-qttools-devel qt6-qtsvg-devel

# X11/Wayland-Dependencies
sudo dnf install -y libxcb-devel xcb-util-wm-devel xcb-util-image-devel

# Multimedia (für Kamera-Feed)
sudo dnf install -y gstreamer1-devel ffmpeg-devel opencv-devel
```

### Schritt 2: App installieren
```bash
# App-Verzeichnis erstellen
mkdir -p ~/Applications
cd ~/Applications
tar -xzf ~/Downloads/mammotion-app.tar.gz
cd mammotion-app

# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Dependencies installieren
pip install -r requirements.txt
```

### Schritt 3: Testen
```bash
# Tests ausführen
python3 test_gui_components.py
python3 test_real_api.py

# App starten
python3 main.py
```

## 🖥️ Desktop-Integration

### Desktop-Datei erstellen
```bash
cat > ~/.local/share/applications/mammotion-app.desktop << 'EOF'
[Desktop Entry]
Name=Mammotion Linux App
Comment=Mammotion Mähroboter Verwaltung
Exec=/home/$USER/Applications/mammotion-app/venv/bin/python /home/$USER/Applications/mammotion-app/main.py
Path=/home/$USER/Applications/mammotion-app
Icon=/home/$USER/Applications/mammotion-app/assets/mammotion-icon.png
Terminal=false
Type=Application
Categories=Utility;System;
Keywords=mammotion;mower;robot;
StartupNotify=true
EOF

# Desktop-Datenbank aktualisieren
update-desktop-database ~/.local/share/applications/
```

### Globaler Startbefehl
```bash
# Startskript erstellen
cat > ~/Applications/mammotion-app/start_mammotion.sh << 'EOF'
#!/bin/bash
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"
source venv/bin/activate
python3 main.py "$@"
EOF

chmod +x ~/Applications/mammotion-app/start_mammotion.sh

# Symlink für globalen Zugriff
sudo ln -sf ~/Applications/mammotion-app/start_mammotion.sh /usr/local/bin/mammotion-app
```

## 🔧 Fedora-spezifische Optimierungen

### SELinux-Konfiguration (falls nötig)
```bash
# Prüfe SELinux-Status
sestatus

# Falls SELinux Probleme verursacht:
sudo setsebool -P allow_execstack 1
sudo setsebool -P allow_execmem 1
```

### Wayland-Unterstützung
```bash
# Für optimale Wayland-Unterstützung
export QT_QPA_PLATFORM=wayland
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1

# In ~/.bashrc hinzufügen für permanente Konfiguration
echo 'export QT_QPA_PLATFORM=wayland' >> ~/.bashrc
```

### Performance-Optimierung
```bash
# GPU-Beschleunigung aktivieren (Intel/AMD)
sudo dnf install -y mesa-dri-drivers mesa-vulkan-drivers

# NVIDIA-Treiber (falls NVIDIA-GPU)
sudo dnf install -y akmod-nvidia xorg-x11-drv-nvidia-cuda
```

## 🚨 Problembehandlung

### Häufige Probleme

#### 1. Qt6-Fehler
```bash
# Lösung: Zusätzliche Qt6-Pakete installieren
sudo dnf install -y qt6-qtwayland qt6-qtx11extras
```

#### 2. Python-Import-Fehler
```bash
# Lösung: Virtual Environment neu erstellen
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. GUI startet nicht
```bash
# Lösung: X11-Fallback verwenden
export QT_QPA_PLATFORM=xcb
python3 main.py
```

#### 4. Netzwerk-Fehler
```bash
# Lösung: Firewall-Ports öffnen
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8883/tcp
sudo firewall-cmd --reload
```

### Log-Dateien
```bash
# App-Logs anzeigen
tail -f ~/Applications/mammotion-app/logs/mammotion_app_dev.log

# System-Logs für GUI-Probleme
journalctl --user -f | grep -i qt
```

## 📋 Systemanforderungen

### Minimum
- **OS**: Fedora 39+
- **RAM**: 2 GB
- **CPU**: x86_64 (64-bit)
- **GPU**: Integrierte Grafik
- **Netzwerk**: Internet-Verbindung

### Empfohlen
- **OS**: Fedora 40+
- **RAM**: 4 GB+
- **CPU**: Multi-Core x86_64
- **GPU**: Dedizierte Grafikkarte
- **Display**: 1920x1080+

## 🔄 Updates

### App aktualisieren
```bash
# Neue Version herunterladen
cd ~/Downloads
tar -xzf mammotion-app-new.tar.gz

# Backup der aktuellen Installation
cp -r ~/Applications/mammotion-app ~/Applications/mammotion-app.backup

# Neue Version installieren
cd mammotion-app-new
./install_fedora.sh
```

### Dependencies aktualisieren
```bash
cd ~/Applications/mammotion-app
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 🆘 Support

### Community-Support
- **GitHub**: Issues und Diskussionen
- **Fedora-Forum**: Fedora-spezifische Probleme
- **Reddit**: r/Fedora, r/homeautomation

### Logs sammeln
```bash
# Vollständige Logs für Support
cd ~/Applications/mammotion-app
tar -czf mammotion-logs.tar.gz logs/ *.log
```

## 🎯 Nächste Schritte

Nach erfolgreicher Installation:

1. **App starten**: `mammotion-app`
2. **Anmelden**: Mit echten Mammotion-Zugangsdaten
3. **Mäher hinzufügen**: Automatische Erkennung
4. **Steuerung testen**: Start, Stopp, Ladestation
5. **Erweiterte Features**: Kamera-Feed, Karten, Benachrichtigungen

Viel Spaß mit Ihrer Mammotion Linux App! 🎉
