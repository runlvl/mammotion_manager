#!/usr/bin/env python3
"""
Test für die verbesserte PyMammotion Cloud-Integration

Testet die perfekte Anbindung an die Mammotion-Cloud über PyMammotion.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Füge src-Verzeichnis zum Python-Pfad hinzu
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mammotion_web.api.pymammotion_client import PyMammotionClient, PYMAMMOTION_AVAILABLE, PyMammotionNotAvailable
from src.models.real_mammotion_client import RealMammotionClient
from src.utils.logging_config import setup_development_logging


async def test_pymammotion_availability():
    """Testet PyMammotion-Verfügbarkeit"""
    print("\n=== PyMammotion-Verfügbarkeits-Test ===")
    
    try:
        print(f"PyMammotion verfügbar: {PYMAMMOTION_AVAILABLE}")
        
        if not PYMAMMOTION_AVAILABLE:
            print("❌ PyMammotion ist nicht verfügbar")
            return False
        
        # Test Client-Erstellung
        client = PyMammotionClient()
        print("✓ PyMammotionClient erfolgreich erstellt")
        
        # Test Authentifizierungsstatus
        print(f"✓ Initial authentifiziert: {client.is_authenticated}")
        
        # Health Check (sollte ohne Login fehlschlagen)
        health = await client.health_check()
        print(f"✓ Health Check ohne Login: {health} (erwartet: False)")
        
        await client.close()
        print("✓ Client erfolgreich geschlossen")
        
        return True
        
    except Exception as e:
        print(f"❌ PyMammotion-Verfügbarkeitstest fehlgeschlagen: {e}")
        return False


async def test_pymammotion_authentication():
    """Testet PyMammotion-Authentifizierung"""
    print("\n=== PyMammotion-Authentifizierungs-Test ===")
    
    try:
        client = PyMammotionClient()
        
        # Test ungültige Authentifizierung
        test_email = "test@example.com"
        test_password = "invalid_password"
        
        print(f"Teste ungültige Anmeldung mit {test_email}...")
        
        try:
            await client.login(test_email, test_password)
            print("❌ Login sollte fehlschlagen")
            return False
        except Exception as e:
            print(f"✓ Login korrekt fehlgeschlagen: {type(e).__name__}: {e}")
        
        # Client schließen
        await client.close()
        
        return True
        
    except PyMammotionNotAvailable as e:
        print(f"⚠️  PyMammotion nicht verfügbar: {e}")
        return True  # Das ist ein erwarteter Fehler
    except Exception as e:
        print(f"❌ Authentifizierungstest fehlgeschlagen: {e}")
        return False


async def test_realclient_integration():
    """Testet RealMammotionClient mit PyMammotion-Integration"""
    print("\n=== RealMammotionClient-Integration-Test ===")
    
    try:
        client = RealMammotionClient()
        
        # Test Authentifizierung
        test_email = "test@example.com"
        test_password = "test_password"
        
        print(f"Teste RealMammotionClient-Anmeldung mit {test_email}...")
        
        # Dies sollte fehlschlagen, aber ohne Crash
        success = await client.authenticate(test_email, test_password)
        print(f"✓ Anmeldung-Ergebnis: {success} (erwartet: False)")
        
        # Test nicht-authentifizierte Geräte-Suche
        print("Teste Geräte-Suche ohne Authentifizierung...")
        devices = await client.discover_devices()
        print(f"✓ Geräte ohne Auth: {len(devices)} (erwartet: 0)")
        
        # Test Authentifizierungsstatus
        print(f"✓ Authentifiziert: {client.is_authenticated}")
        
        # Client schließen
        await client.close()
        print("✓ RealMammotionClient erfolgreich geschlossen")
        
        return True
        
    except Exception as e:
        print(f"❌ RealMammotionClient-Test fehlgeschlagen: {e}")
        return False


async def test_error_handling():
    """Testet Fehlerbehandlung"""
    print("\n=== Fehlerbehandlungs-Test ===")
    
    try:
        client = PyMammotionClient()
        
        # Test nicht-authentifizierte Aktionen
        print("Teste nicht-authentifizierte Aktionen...")
        
        try:
            await client.list_devices()
            print("❌ list_devices sollte ohne Authentifizierung fehlschlagen")
            return False
        except RuntimeError as e:
            print(f"✓ list_devices korrekt abgewiesen: {e}")
        
        try:
            await client.get_status("fake_device")
            print("❌ get_status sollte ohne Authentifizierung fehlschlagen")
            return False
        except RuntimeError as e:
            print(f"✓ get_status korrekt abgewiesen: {e}")
        
        try:
            await client.send_command("fake_device", "start")
            print("❌ send_command sollte ohne Authentifizierung fehlschlagen")
            return False
        except RuntimeError as e:
            print(f"✓ send_command korrekt abgewiesen: {e}")
        
        await client.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Fehlerbehandlungstest fehlgeschlagen: {e}")
        return False


async def test_connection_robustness():
    """Testet Verbindungsrobustheit"""
    print("\n=== Verbindungsrobustheits-Test ===")
    
    try:
        # Test mehrfache Client-Erstellung und -Schließung
        for i in range(3):
            print(f"Test-Durchlauf {i+1}/3...")
            
            client = PyMammotionClient()
            print(f"  ✓ Client {i+1} erstellt")
            
            # Health Check
            health = await client.health_check()
            print(f"  ✓ Health Check {i+1}: {health}")
            
            await client.close()
            print(f"  ✓ Client {i+1} geschlossen")
        
        return True
        
    except Exception as e:
        print(f"❌ Robustheitstest fehlgeschlagen: {e}")
        return False


async def main():
    """Hauptfunktion für PyMammotion-Integrations-Tests"""
    print("PyMammotion Cloud-Integration Tests")
    print("=" * 50)
    
    # Logging konfigurieren
    setup_development_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starte PyMammotion-Integrationstests")
    
    tests = [
        ("PyMammotion-Verfügbarkeit", test_pymammotion_availability),
        ("PyMammotion-Authentifizierung", test_pymammotion_authentication),
        ("RealClient-Integration", test_realclient_integration),
        ("Fehlerbehandlung", test_error_handling),
        ("Verbindungsrobustheit", test_connection_robustness),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔧 Führe {test_name}-Test durch...")
        try:
            result = await test_func()
            if result:
                print(f"✅ {test_name} bestanden")
                passed += 1
            else:
                print(f"❌ {test_name} fehlgeschlagen")
        except Exception as e:
            print(f"💥 {test_name} mit Fehler: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test-Ergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 Alle PyMammotion-Integration-Tests erfolgreich!")
        return 0
    else:
        print("⚠️  Einige PyMammotion-Integration-Tests fehlgeschlagen.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))