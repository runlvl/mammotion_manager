#!/usr/bin/env python3
"""Test different parameter combinations for CloudIOTGateway.login_by_oauth()"""

import asyncio
import logging
import aiohttp
from pymammotion.aliyun.cloud_gateway import CloudIOTGateway

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def test_login_parameters():
    """Test different parameter combinations for login_by_oauth."""
    print("🔍 Testing CloudIOTGateway.login_by_oauth() parameter combinations...")
    
    session = aiohttp.ClientSession()
    
    try:
        gateway = CloudIOTGateway(session)
        print("✅ CloudIOTGateway initialized")
        
        test_email = "test@example.com"
        test_password = "testpassword"
        
        # Test 1: Dictionary with credentials
        print("\n--- Test 1: Dictionary parameter ---")
        try:
            credentials = {
                'email': test_email,
                'password': test_password,
                'username': test_email,
                'user': test_email,
                'account': test_email
            }
            result = await gateway.login_by_oauth(credentials)
            print(f"✅ Dict parameter works: {result}")
        except Exception as e:
            print(f"❌ Dict parameter failed: {e}")
        
        # Test 2: Single email string
        print("\n--- Test 2: Single email string ---")
        try:
            result = await gateway.login_by_oauth(test_email)
            print(f"✅ Single email works: {result}")
        except Exception as e:
            print(f"❌ Single email failed: {e}")
        
        # Test 3: Tuple with email and password
        print("\n--- Test 3: Tuple parameter ---")
        try:
            credentials_tuple = (test_email, test_password)
            result = await gateway.login_by_oauth(credentials_tuple)
            print(f"✅ Tuple parameter works: {result}")
        except Exception as e:
            print(f"❌ Tuple parameter failed: {e}")
        
        # Test 4: Different dict structures
        print("\n--- Test 4: Different dict structures ---")
        dict_variations = [
            {'username': test_email, 'password': test_password},
            {'user': test_email, 'pass': test_password},
            {'account': test_email, 'password': test_password},
            {'login': test_email, 'password': test_password},
            {'email': test_email, 'pwd': test_password},
        ]
        
        for i, creds in enumerate(dict_variations):
            try:
                result = await gateway.login_by_oauth(creds)
                print(f"✅ Dict variation {i+1} works: {creds} -> {result}")
            except Exception as e:
                print(f"❌ Dict variation {i+1} failed: {creds} -> {e}")
        
        # Test 5: OAuth-style parameters
        print("\n--- Test 5: OAuth-style parameters ---")
        try:
            oauth_params = {
                'grant_type': 'password',
                'username': test_email,
                'password': test_password,
                'client_id': 'mammotion',
                'scope': 'read write'
            }
            result = await gateway.login_by_oauth(oauth_params)
            print(f"✅ OAuth params work: {result}")
        except Exception as e:
            print(f"❌ OAuth params failed: {e}")
        
        # Test 6: No parameters (maybe it uses stored credentials?)
        print("\n--- Test 6: No parameters ---")
        try:
            result = await gateway.login_by_oauth()
            print(f"✅ No parameters works: {result}")
        except Exception as e:
            print(f"❌ No parameters failed: {e}")
            
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_login_parameters())
