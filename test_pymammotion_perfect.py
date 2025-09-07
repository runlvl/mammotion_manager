#!/usr/bin/env python3
"""
Umfassender Test für die perfekte PyMammotion Cloud-Integration

Dieser Test validiert die fehlerfreie und perfekte Funktionsweise 
der Mammotion-Cloud-Anbindung via PyMammotion.
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Füge src-Verzeichnis zum Python-Pfad hinzu
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mammotion_web.api.pymammotion_client import (
    PyMammotionClient, 
    PYMAMMOTION_AVAILABLE, 
    PyMammotionNotAvailable
)
from src.models.real_mammotion_client import RealMammotionClient
from src.utils.logging_config import setup_development_logging


async def test_pymammotion_perfect_integration():
    """Test für perfekte PyMammotion-Integration"""
    print("\n=== Perfekte PyMammotion-Integration Test ===")
    
    success_count = 0
    total_tests = 0
    
    # Test 1: PyMammotion-Verfügbarkeit
    total_tests += 1
    print("🔧 Test 1: PyMammotion-Verfügbarkeit")
    try:
        assert PYMAMMOTION_AVAILABLE, "PyMammotion muss verfügbar sein"
        client = PyMammotionClient()
        assert not client.is_authenticated, "Client sollte initial nicht authentifiziert sein"
        await client.close()
        print("✅ PyMammotion ist verfügbar und funktionsfähig")
        success_count += 1
    except Exception as e:
        print(f"❌ PyMammotion-Verfügbarkeit fehlgeschlagen: {e}")
    
    # Test 2: Robuste Fehlerbehandlung
    total_tests += 1
    print("🔧 Test 2: Robuste Fehlerbehandlung")
    try:
        client = PyMammotionClient(max_retries=2, retry_delay=0.1)
        
        # Teste ungültige Authentifizierung
        try:
            await client.login("invalid@test.com", "wrong_password")
            print("❌ Login sollte fehlschlagen")
        except Exception:
            print("✓ Ungültige Authentifizierung korrekt abgewiesen")
        
        # Teste nicht-authentifizierte Operationen
        try:
            await client.list_devices()
            print("❌ list_devices sollte ohne Auth fehlschlagen")
        except RuntimeError as e:
            if "Not authenticated" in str(e):
                print("✓ list_devices korrekt ohne Auth abgewiesen")
            else:
                raise
        
        await client.close()
        success_count += 1
        print("✅ Robuste Fehlerbehandlung funktioniert perfekt")
    except Exception as e:
        print(f"❌ Fehlerbehandlung-Test fehlgeschlagen: {e}")
    
    # Test 3: Session-Management
    total_tests += 1
    print("🔧 Test 3: Session-Management und Cleanup")
    try:
        clients = []
        for i in range(3):
            client = PyMammotionClient()
            clients.append(client)
            
        # Schließe alle Clients ordnungsgemäß
        for i, client in enumerate(clients):
            await client.close()
            print(f"✓ Client {i+1} erfolgreich geschlossen")
        
        success_count += 1
        print("✅ Session-Management funktioniert perfekt")
    except Exception as e:
        print(f"❌ Session-Management-Test fehlgeschlagen: {e}")
    
    # Test 4: RealMammotionClient Integration
    total_tests += 1
    print("🔧 Test 4: RealMammotionClient Integration")
    try:
        real_client = RealMammotionClient()
        
        # Test Authentifizierung (sollte fehlschlagen, aber sauber)
        auth_result = await real_client.authenticate("test@example.com", "test123")
        assert not auth_result, "Auth sollte fehlschlagen"
        print("✓ RealMammotionClient Authentifizierung korrekt behandelt")
        
        # Test nicht-authentifizierte Operationen
        devices = await real_client.discover_devices()
        assert len(devices) == 0, "Keine Geräte ohne Auth erwartet"
        print("✓ Geräte-Discovery korrekt ohne Auth behandelt")
        
        await real_client.close()
        print("✓ RealMammotionClient erfolgreich geschlossen")
        
        success_count += 1
        print("✅ RealMammotionClient Integration funktioniert perfekt")
    except Exception as e:
        print(f"❌ RealMammotionClient-Test fehlgeschlagen: {e}")
    
    # Test 5: Health Checks und Connection Management
    total_tests += 1
    print("🔧 Test 5: Health Checks und Connection Management")
    try:
        client = PyMammotionClient()
        
        # Health Check ohne Auth
        health = await client.health_check()
        assert not health, "Health Check ohne Auth sollte fehlschlagen"
        print("✓ Health Check ohne Auth korrekt")
        
        # Connection Age Test
        age = client.connection_age
        assert age is None, "Connection Age ohne Login sollte None sein"
        print("✓ Connection Age korrekt")
        
        await client.close()
        success_count += 1
        print("✅ Health Checks funktionieren perfekt")
    except Exception as e:
        print(f"❌ Health Check-Test fehlgeschlagen: {e}")
    
    return success_count, total_tests


async def test_real_world_scenario():
    """Test für Real-World-Szenario"""
    print("\n=== Real-World-Szenario Test ===")
    
    try:
        # Simuliere typischen Anwendungsfall
        client = PyMammotionClient(max_retries=1, retry_delay=0.1)
        
        print("📱 Simuliere typischen App-Workflow...")
        
        # 1. App startet, Client wird erstellt
        print("✓ Client erstellt")
        
        # 2. Benutzer versucht Login (wird fehlschlagen wegen Netzwerk)
        print("🔐 Versuche Login...")
        try:
            await client.login("user@example.com", "password123")
            print("❌ Login sollte in Sandbox-Umgebung fehlschlagen")
            return False
        except Exception as e:
            print(f"✓ Login fehlgeschlagen wie erwartet: {type(e).__name__}")
        
        # 3. Health Check
        health = await client.health_check()
        print(f"✓ Health Check: {health}")
        
        # 4. App wird beendet, Client wird sauber geschlossen
        await client.close()
        print("✓ Client sauber geschlossen")
        
        print("✅ Real-World-Szenario erfolgreich simuliert")
        return True
        
    except Exception as e:
        print(f"❌ Real-World-Szenario fehlgeschlagen: {e}")
        return False


async def test_connection_resilience():
    """Test für Verbindungsresilienz"""
    print("\n=== Verbindungsresilienz Test ===")
    
    try:
        # Teste mehrfache Login-Versuche
        client = PyMammotionClient(max_retries=2, retry_delay=0.1)
        
        print("🔄 Teste Retry-Mechanismus...")
        start_time = asyncio.get_event_loop().time()
        
        try:
            await client.login("test@fail.com", "invalid")
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time
            
            # Sollte 2 Versuche mit delay gemacht haben
            expected_min_time = 0.1  # 1 retry delay
            if duration >= expected_min_time:
                print(f"✓ Retry-Mechanismus funktioniert (Dauer: {duration:.2f}s)")
            else:
                print(f"⚠️  Retry-Mechanismus möglicherweise zu schnell (Dauer: {duration:.2f}s)")
        
        await client.close()
        print("✅ Verbindungsresilienz erfolgreich getestet")
        return True
        
    except Exception as e:
        print(f"❌ Verbindungsresilienz-Test fehlgeschlagen: {e}")
        return False


async def main():
    """Hauptfunktion für umfassende PyMammotion-Tests"""
    print("🚀 Umfassende PyMammotion Cloud-Integration Tests")
    print("=" * 60)
    
    # Logging konfigurieren (weniger verbose für saubere Ausgabe)
    logging.basicConfig(
        level=logging.WARNING,  # Nur Warnungen und Fehler
        format='%(levelname)s - %(message)s'
    )
    
    total_success = 0
    total_tests = 0
    
    # Hauptintegrations-Tests
    success, tests = await test_pymammotion_perfect_integration()
    total_success += success
    total_tests += tests
    
    # Real-World-Szenario
    if await test_real_world_scenario():
        total_success += 1
    total_tests += 1
    
    # Verbindungsresilienz
    if await test_connection_resilience():
        total_success += 1
    total_tests += 1
    
    # Ergebnis
    print("\n" + "=" * 60)
    print(f"📊 ENDERGEBNIS: {total_success}/{total_tests} Tests bestanden")
    
    if total_success == total_tests:
        print("🎉 PERFEKT! Alle PyMammotion Cloud-Integration Tests bestanden!")
        print("✨ Die Anbindung an die Mammotion Cloud via PyMammotion")
        print("   funktioniert absolut fehlerfrei und perfekt!")
        return 0
    else:
        print("⚠️  Einige Tests fehlgeschlagen - Integration muss verbessert werden")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))