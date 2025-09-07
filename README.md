# 🤖 Mammotion Manager

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)

A comprehensive web-based management system for Mammotion robotic lawn mowers on Linux. Control and monitor your Mammotion devices through both a quick-start Flask interface and a professional FastAPI backend.

## ✨ Features

### 🚀 Quick Start Flask Interface
- **Instant Launch**: Single-command startup with `python3 web_gui_real_api_final.py`
- **Large UI Elements**: 90px input fields, 80px buttons - perfect for all screen types
- **Real API Integration**: Connects to genuine Mammotion/Aliyun IoT endpoints
- **Intelligent Fallback**: Realistic demo mode when cloud services are unavailable
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### 🏗️ Professional FastAPI Backend
- **Modern Architecture**: FastAPI with async support and automatic OpenAPI docs
- **Real-time Updates**: WebSocket support for live device status
- **Session Management**: Redis-based persistent sessions
- **Modular Design**: Clean separation of routers, services, and data models
- **Enterprise Ready**: Structured logging, health checks, and configuration management

### 🌐 Universal Features
- **Device Control**: Start, stop, pause, and return-to-dock commands
- **Live Monitoring**: Real-time battery, position, and status updates
- **Multi-Device Support**: Manage multiple Mammotion mowers from one interface
- **Secure Authentication**: Login with your Mammotion account credentials
- **Cross-Platform**: Optimized for Linux with Fedora installation scripts

## 🚀 Quick Start

### Option A: Instant Flask GUI (Recommended for First-Time Users)

```bash
# 1. Clone and enter directory
git clone https://github.com/runlvl/mammotion_manager.git
cd mammotion_manager

# 2. Install Python dependencies
pip3 install flask aiohttp asyncio-mqtt

# 3. Launch immediately
python3 web_gui_real_api_final.py
```

**✅ Browser opens automatically at http://localhost:5000**

### Option B: FastAPI Professional Backend

```bash
# 1. Clone repository
git clone https://github.com/runlvl/mammotion_manager.git
cd mammotion_manager

# 2. Install dependencies
pip install -r mammotion-web-complete/requirements.txt

# 3. Start Redis (required for sessions)
sudo systemctl start redis-server  # Ubuntu/Debian
# OR: docker run -d -p 6379:6379 redis:alpine

# 4. Launch FastAPI server
uvicorn src.mammotion_web.app:app --host 0.0.0.0 --port 8000

# 5. Access web interface
open http://localhost:8000
```

**📚 API Documentation available at http://localhost:8000/docs**

## 📦 Installation

### Automated Fedora Installation

```bash
# Download and run the installation script
chmod +x install_fedora.sh
./install_fedora.sh

# Start the application
mammotion-app
```

### Manual Installation

```bash
# Install system dependencies (Fedora/RHEL)
sudo dnf install python3 python3-pip python3-venv redis

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### Systemd Service (Production)

```bash
# Install as system service
sudo cp systemd/mammotion-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mammotion-web
sudo systemctl start mammotion-web
```

## 🔐 Authentication

### Using Real Mammotion Credentials
1. Launch the application (Flask or FastAPI)
2. Navigate to the web interface
3. Enter your **actual** Mammotion account email and password
4. The system will attempt to connect to official Mammotion/Aliyun IoT servers

### Demo Mode
If real authentication fails, the system automatically falls back to realistic demo mode with:
- Simulated Luba 2 AWD mower
- Live-updating battery and status information
- Fully functional command interface

## 🏗️ Architecture

### Project Structure

```
mammotion_manager/
├── 📁 src/mammotion_web/          # FastAPI application core
│   ├── 🐍 app.py                 # FastAPI app with middleware
│   ├── 🐍 main.py                # Application entry point
│   ├── 📁 routers/               # API route handlers
│   │   ├── 🐍 auth_router.py     # Authentication endpoints
│   │   ├── 🐍 devices_router.py  # Device management
│   │   └── 🐍 ws_router.py       # WebSocket real-time updates
│   ├── 📁 services/              # Business logic layer
│   │   ├── 🐍 mammotion_service.py # Core Mammotion API integration
│   │   └── 🐍 event_bus.py       # Event system for real-time updates
│   ├── 📁 api/                   # External API clients
│   │   ├── 🐍 pymammotion_client.py # PyMammotion wrapper
│   │   └── 🐍 device_manager.py  # Device state management
│   └── 📁 core/                  # Core utilities
│       ├── 🐍 session.py         # Redis session management
│       └── 🐍 logging.py         # Structured logging
├── 🌐 web_gui_real_api_final.py  # Flask quick-start interface
├── 🐍 real_mammotion_api_v2.py   # Real API client with fallback
├── 📁 systemd/                   # Linux service integration
├── 📁 mammotion-web-complete/    # Standalone distribution
└── 🐍 install_fedora.sh         # Automated installer
```

### Technology Stack

- **Backend**: FastAPI (async), Flask (quick-start)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Real-time**: WebSocket connections for live updates
- **Sessions**: Redis-based persistent authentication
- **API Integration**: Direct Mammotion/Aliyun IoT endpoints
- **Fallback**: Intelligent demo mode with realistic data

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Mammotion API
REGION=eu
COUNTRY_CODE=DE

# Security
SECRET_KEY=your-secure-secret-key-here
SESSION_EXPIRE_HOURS=24

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Advanced Configuration

The FastAPI version supports extensive configuration through environment variables and the `src/mammotion_web/config.py` settings system:

- **Regional Settings**: Configure for EU, US, or Asia regions
- **Session Management**: Customize session expiration and storage
- **Logging**: Structured JSON logging with configurable levels
- **Security**: CORS, session middleware, and request validation

## 🎮 Usage

### Web Interface Controls

1. **Login Page**: Enter Mammotion credentials or use demo mode
2. **Dashboard**: Overview of all connected mowers
3. **Device Control**: Individual mower management with real-time status
4. **Live Updates**: Automatic refresh of battery, position, and work status

### Available Commands

- **▶️ Start Mowing**: Begin automated lawn cutting
- **⏹️ Stop/Pause**: Halt current operation
- **🏠 Return to Dock**: Send mower back to charging station
- **🔄 Status Update**: Refresh device information

### API Endpoints (FastAPI Version)

- `GET /` - Web interface dashboard
- `POST /auth/login` - User authentication
- `GET /devices` - List all connected devices
- `POST /devices/{device_id}/commands` - Send device commands
- `WS /ws` - WebSocket for real-time updates
- `GET /docs` - Interactive API documentation

## 🤝 Contributing

We welcome contributions to improve Mammotion Manager!

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/runlvl/mammotion_manager.git
cd mammotion_manager
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Run tests
python3 test_real_api.py
python3 test_gui_components.py
```

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Include tests for new features
- Update documentation as needed

## 🐛 Troubleshooting

### Common Issues

**Flask GUI doesn't start:**
```bash
# Ensure dependencies are installed
pip3 install flask aiohttp
python3 web_gui_real_api_final.py
```

**FastAPI requires Redis:**
```bash
# Start Redis service
sudo systemctl start redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

**Authentication failures:**
- The system automatically falls back to demo mode
- Check your Mammotion account credentials
- Ensure internet connectivity for cloud API access

**Port conflicts:**
- Flask interface uses port 5000
- FastAPI interface uses port 8000
- Modify ports in configuration if needed

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python3 web_gui_real_api_final.py
```

### Log Files

- Flask version: Console output only
- FastAPI version: Check `logs/` directory
- Systemd service: `journalctl -u mammotion-web -f`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyMammotion**: Python library for Mammotion device integration
- **FastAPI**: Modern, high-performance web framework
- **Aliyun IoT Platform**: Cloud infrastructure for device connectivity
- **Mammotion**: For creating innovative robotic lawn care solutions

## 📞 Support

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Community support and questions
- **Documentation**: Comprehensive guides in the `/docs` folder

---

**Made with ❤️ for the robotic lawn care community**

*Compatible with Mammotion Luba, Luba 2, and other Mammotion robotic mowers*
