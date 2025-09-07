#!/usr/bin/env python3
"""Test authentication with country code parameter."""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mammotion_web.services.auth_service import AuthService
from mammotion_web.core.exceptions import AuthenticationError

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_auth_with_country():
    """Test authentication with country code."""
    print("🔍 Testing authentication service with country code...")
    
    auth_service = AuthService()
    
    # Test with dummy credentials and different country codes
    test_email = "test@example.com"
    test_password = "testpassword"
    
    country_codes = ["DE", "US", "CN", "GB", "FR"]
    
    for country_code in country_codes:
        try:
            print(f"\nAttempting login with: {test_email} (country: {country_code})")
            user_data = await auth_service.authenticate(test_email, test_password, country_code)
            print(f"✅ Login successful for {country_code}: {user_data}")
            
            # Clean up session
            await auth_service.cleanup_session(user_data)
            
        except AuthenticationError as e:
            print(f"❌ Authentication error for {country_code}: {e.message}")
            
        except Exception as e:
            print(f"❌ Unexpected error for {country_code}: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth_with_country())
