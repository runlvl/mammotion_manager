#!/bin/bash
# Mammotion Linux App - Fedora Installation Script
# Für Fedora 39+ (getestet auf Fedora 42)

set -e  # Exit on error

echo "🐧 Mammotion Linux App - Fedora Installation"
echo "=============================================="

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfe ob Fedora
if ! grep -q "Fedora" /etc/os-release; then
    print_warning "Dieses Skript ist für Fedora optimiert. Andere Distributionen können funktionieren."
fi

# Prüfe Fedora-Version
FEDORA_VERSION=$(grep VERSION_ID /etc/os-release | cut -d= -f2 | tr -d '"')
print_status "Erkannte Fedora-Version: $FEDORA_VERSION"

if [ "$FEDORA_VERSION" -lt 39 ]; then
    print_warning "Fedora $FEDORA_VERSION ist älter als empfohlen (39+). Installation kann fehlschlagen."
fi

# Schritt 1: System-Dependencies
print_status "Schritt 1: Installiere System-Dependencies..."

# Prüfe ob sudo verfügbar
if ! command -v sudo &> /dev/null; then
    print_error "sudo ist nicht verfügbar. Bitte als root ausführen oder sudo installieren."
    exit 1
fi

# System aktualisieren
print_status "Aktualisiere System-Pakete..."
sudo dnf update -y

# Python und Entwicklungstools
print_status "Installiere Python und Entwicklungstools..."
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    python3-venv \
    gcc \
    gcc-c++ \
    make \
    cmake

# Qt6 für PySide6
print_status "Installiere Qt6-Dependencies..."
sudo dnf install -y \
    qt6-qtbase-devel \
    qt6-qttools-devel \
    qt6-qtsvg-devel \
    qt6-qtmultimedia-devel

# X11/Wayland-Dependencies
print_status "Installiere GUI-Dependencies..."
sudo dnf install -y \
    libxcb-devel \
    xcb-util-wm-devel \
    xcb-util-image-devel \
    xcb-util-keysyms-devel \
    xcb-util-renderutil-devel \
    libX11-devel \
    libXext-devel \
    libXrender-devel

# Multimedia-Dependencies (für zukünftige Kamera-Integration)
print_status "Installiere Multimedia-Dependencies..."
sudo dnf install -y \
    gstreamer1-devel \
    gstreamer1-plugins-base-devel \
    ffmpeg-devel \
    opencv-devel

# Netzwerk-Dependencies
print_status "Installiere Netzwerk-Dependencies..."
sudo dnf install -y \
    openssl-devel \
    libcurl-devel

print_success "System-Dependencies installiert!"

# Schritt 2: App-Verzeichnis erstellen
print_status "Schritt 2: Erstelle App-Verzeichnis..."

APP_DIR="$HOME/Applications/mammotion-app"
mkdir -p "$HOME/Applications"

# Prüfe ob App bereits existiert
if [ -d "$APP_DIR" ]; then
    print_warning "App-Verzeichnis existiert bereits: $APP_DIR"
    read -p "Überschreiben? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$APP_DIR"
        print_status "Altes Verzeichnis entfernt"
    else
        print_error "Installation abgebrochen"
        exit 1
    fi
fi

# Kopiere App-Dateien (angenommen, das Skript ist im App-Verzeichnis)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp -r "$SCRIPT_DIR" "$APP_DIR"
print_success "App-Dateien kopiert nach: $APP_DIR"

# Schritt 3: Python Virtual Environment
print_status "Schritt 3: Erstelle Python Virtual Environment..."

cd "$APP_DIR"

# Virtual Environment erstellen
python3 -m venv venv
print_success "Virtual Environment erstellt"

# Virtual Environment aktivieren
source venv/bin/activate

# pip aktualisieren
print_status "Aktualisiere pip..."
pip install --upgrade pip setuptools wheel

# Schritt 4: Python-Dependencies installieren
print_status "Schritt 4: Installiere Python-Dependencies..."

# Installiere Dependencies aus requirements.txt
if [ -f "requirements.txt" ]; then
    print_status "Installiere aus requirements.txt..."
    pip install -r requirements.txt
else
    print_status "Installiere Kern-Dependencies manuell..."
    pip install PySide6>=6.9.0 aiohttp>=3.8.0 asyncio-mqtt>=0.13.0
fi

print_success "Python-Dependencies installiert!"

# Schritt 5: App testen
print_status "Schritt 5: Teste App-Installation..."

# GUI-Tests
print_status "Führe GUI-Tests aus..."
if python3 test_gui_components.py > /dev/null 2>&1; then
    print_success "GUI-Tests erfolgreich!"
else
    print_warning "GUI-Tests fehlgeschlagen - App kann trotzdem funktionieren"
fi

# API-Tests
print_status "Führe API-Tests aus..."
if python3 test_real_api.py > /dev/null 2>&1; then
    print_success "API-Tests erfolgreich!"
else
    print_warning "API-Tests fehlgeschlagen - App kann trotzdem funktionieren"
fi

# Schritt 6: Desktop-Integration
print_status "Schritt 6: Erstelle Desktop-Integration..."

# Desktop-Verzeichnis erstellen
mkdir -p "$HOME/.local/share/applications"

# Desktop-Datei erstellen
cat > "$HOME/.local/share/applications/mammotion-app.desktop" << EOF
[Desktop Entry]
Name=Mammotion Linux App
Comment=Mammotion Mähroboter Verwaltung und Steuerung
Exec=$APP_DIR/venv/bin/python $APP_DIR/main.py
Path=$APP_DIR
Icon=$APP_DIR/assets/mammotion-icon.png
Terminal=false
Type=Application
Categories=Utility;System;
Keywords=mammotion;mower;robot;lawn;
StartupNotify=true
EOF

# Desktop-Datenbank aktualisieren
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications/"
    print_success "Desktop-Integration erstellt!"
else
    print_warning "update-desktop-database nicht gefunden - Desktop-Integration manuell"
fi

# Schritt 7: Startskript erstellen
print_status "Schritt 7: Erstelle Startskript..."

cat > "$APP_DIR/start_mammotion.sh" << 'EOF'
#!/bin/bash
# Mammotion App Starter

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$APP_DIR"

# Virtual Environment aktivieren
source venv/bin/activate

# App starten
python3 main.py "$@"
EOF

chmod +x "$APP_DIR/start_mammotion.sh"

# Symlink für globalen Zugriff
sudo ln -sf "$APP_DIR/start_mammotion.sh" /usr/local/bin/mammotion-app 2>/dev/null || true

print_success "Startskript erstellt!"

# Schritt 8: Firewall-Konfiguration (optional)
print_status "Schritt 8: Konfiguriere Firewall (optional)..."

if command -v firewall-cmd &> /dev/null; then
    print_status "Firewalld erkannt - konfiguriere Ports für Mammotion..."
    
    # Ports für Mammotion-Kommunikation öffnen (falls nötig)
    # sudo firewall-cmd --permanent --add-port=8883/tcp  # MQTT
    # sudo firewall-cmd --permanent --add-port=443/tcp   # HTTPS
    # sudo firewall-cmd --reload
    
    print_success "Firewall-Konfiguration übersprungen (nicht erforderlich)"
else
    print_status "Firewalld nicht gefunden - überspringe Firewall-Konfiguration"
fi

# Installation abgeschlossen
echo ""
echo "🎉 Installation erfolgreich abgeschlossen!"
echo "=========================================="
echo ""
echo "📍 App installiert in: $APP_DIR"
echo "🚀 Starten mit: mammotion-app"
echo "🖥️  Oder über Desktop: Mammotion Linux App"
echo "📁 Oder direkt: $APP_DIR/start_mammotion.sh"
echo ""
echo "📋 Nächste Schritte:"
echo "   1. App starten: mammotion-app"
echo "   2. Mit Mammotion-Zugangsdaten anmelden"
echo "   3. Mäher konfigurieren und steuern"
echo ""
echo "🔧 Bei Problemen:"
echo "   - Logs: $APP_DIR/logs/"
echo "   - Tests: cd $APP_DIR && python3 test_gui_components.py"
echo "   - Support: GitHub Issues oder Community"
echo ""

# Deaktiviere Virtual Environment
deactivate 2>/dev/null || true

print_success "Installation abgeschlossen! 🎉"
