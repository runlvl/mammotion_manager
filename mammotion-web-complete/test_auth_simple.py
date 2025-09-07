#!/usr/bin/env python3
"""Simple authentication test to debug the login issue."""

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

async def test_auth():
    """Test authentication with dummy credentials."""
    print("🔍 Testing authentication service...")
    
    auth_service = AuthService()
    
    # Test with dummy credentials
    test_email = "test@example.com"
    test_password = "testpassword"
    
    try:
        print(f"Attempting login with: {test_email}")
        user_data = await auth_service.authenticate(test_email, test_password)
        print(f"✅ Login successful: {user_data}")
        
    except AuthenticationError as e:
        print(f"❌ Authentication error: {e.message}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth())
