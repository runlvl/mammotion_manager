#!/usr/bin/env python3
"""Investigate MammotionHTTP class and its authentication methods."""

import asyncio
import logging
import inspect
from pymammotion.http.http import MammotionHTTP

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def investigate_mammotion_http():
    """Investigate MammotionHTTP class and authentication methods."""
    print("🔍 Investigating MammotionHTTP class...")
    
    try:
        # Initialize MammotionHTTP
        mammotion_http = MammotionHTTP()
        print("✅ MammotionHTTP initialized")
        
        # 1. Inspect MammotionHTTP class
        print("\n=== MammotionHTTP Class Inspection ===")
        print(f"Class: {MammotionHTTP}")
        print(f"Module: {MammotionHTTP.__module__}")
        
        # Get all methods
        methods = [method for method in dir(mammotion_http) if not method.startswith('_')]
        print(f"Available methods: {methods}")
        
        # 2. Look for authentication methods
        print("\n=== Authentication Methods ===")
        auth_methods = [method for method in methods if 'login' in method.lower() or 'auth' in method.lower() or 'credential' in method.lower()]
        print(f"Auth-related methods: {auth_methods}")
        
        for method_name in auth_methods:
            method = getattr(mammotion_http, method_name)
            try:
                sig = inspect.signature(method)
                print(f"{method_name}: {sig}")
                
                # Get docstring
                docstring = inspect.getdoc(method)
                if docstring:
                    print(f"  Docstring: {docstring}")
                    
            except Exception as e:
                print(f"{method_name}: signature unavailable - {e}")
        
        # 3. Check initialization parameters
        print("\n=== MammotionHTTP Initialization ===")
        try:
            init_sig = inspect.signature(MammotionHTTP.__init__)
            print(f"__init__ signature: {init_sig}")
        except Exception as e:
            print(f"Could not get __init__ signature: {e}")
        
        # 4. Check attributes after initialization
        print("\n=== MammotionHTTP Attributes ===")
        attrs = [attr for attr in dir(mammotion_http) if not attr.startswith('_') and not callable(getattr(mammotion_http, attr))]
        for attr in attrs:
            try:
                value = getattr(mammotion_http, attr)
                print(f"{attr}: {type(value)} = {value}")
            except Exception as e:
                print(f"{attr}: Error getting value - {e}")
        
        # 5. Check for login_info attribute specifically
        print("\n=== login_info Attribute Investigation ===")
        if hasattr(mammotion_http, 'login_info'):
            login_info = mammotion_http.login_info
            print(f"login_info: {type(login_info)} = {login_info}")
            
            if login_info:
                # Check login_info attributes
                login_info_attrs = [attr for attr in dir(login_info) if not attr.startswith('_')]
                print(f"login_info attributes: {login_info_attrs}")
                
                for attr in login_info_attrs:
                    try:
                        value = getattr(login_info, attr)
                        if not callable(value):
                            print(f"  login_info.{attr}: {type(value)} = {value}")
                    except Exception as e:
                        print(f"  login_info.{attr}: Error - {e}")
            else:
                print("login_info is None - needs to be initialized")
        else:
            print("❌ No login_info attribute found")
        
        # 6. Try to find source code
        print("\n=== Source Code Location ===")
        try:
            import pymammotion.http.http
            source_file = inspect.getfile(pymammotion.http.http)
            print(f"Source file: {source_file}")
            
            # Try to read the source for login methods
            try:
                with open(source_file, 'r') as f:
                    source_lines = f.readlines()
                
                # Look for login-related method definitions
                login_keywords = ['def login', 'def authenticate', 'def set_credential', 'login_info']
                
                for keyword in login_keywords:
                    for i, line in enumerate(source_lines):
                        if keyword in line:
                            print(f"\nFound '{keyword}' at line {i+1}:")
                            # Print the line and a few lines after
                            for j in range(max(0, i-1), min(len(source_lines), i+5)):
                                prefix = ">>> " if j == i else "    "
                                print(f"{prefix}{j+1:3d}: {source_lines[j].rstrip()}")
                            break
                        
            except Exception as e:
                print(f"Could not read source file: {e}")
                
        except Exception as e:
            print(f"Could not get source file: {e}")
        
        # 7. Test different ways to set credentials
        print("\n=== Testing Credential Setting Methods ===")
        
        test_email = "test@example.com"
        test_password = "testpassword"
        
        # Method 1: Direct attribute setting
        try:
            print("Testing direct attribute setting...")
            if hasattr(mammotion_http, 'username'):
                mammotion_http.username = test_email
                print(f"✅ Set username: {mammotion_http.username}")
            if hasattr(mammotion_http, 'password'):
                mammotion_http.password = test_password
                print(f"✅ Set password: {'*' * len(test_password)}")
            if hasattr(mammotion_http, 'email'):
                mammotion_http.email = test_email
                print(f"✅ Set email: {mammotion_http.email}")
        except Exception as e:
            print(f"❌ Direct attribute setting failed: {e}")
        
        # Method 2: Check for set_credentials method
        if hasattr(mammotion_http, 'set_credentials'):
            try:
                print("Testing set_credentials method...")
                result = await mammotion_http.set_credentials(test_email, test_password)
                print(f"✅ set_credentials result: {result}")
            except Exception as e:
                print(f"❌ set_credentials failed: {e}")
        
        # Method 3: Check for login method
        if hasattr(mammotion_http, 'login'):
            try:
                print("Testing login method...")
                result = await mammotion_http.login(test_email, test_password)
                print(f"✅ login result: {result}")
            except Exception as e:
                print(f"❌ login failed: {e}")
        
        # Method 4: Check for authenticate method
        if hasattr(mammotion_http, 'authenticate'):
            try:
                print("Testing authenticate method...")
                result = await mammotion_http.authenticate(test_email, test_password)
                print(f"✅ authenticate result: {result}")
            except Exception as e:
                print(f"❌ authenticate failed: {e}")
        
        # 8. Check login_info after credential attempts
        print("\n=== login_info After Credential Setting ===")
        if hasattr(mammotion_http, 'login_info'):
            login_info = mammotion_http.login_info
            print(f"login_info after credential setting: {type(login_info)} = {login_info}")
            
            if login_info and hasattr(login_info, 'authorization_code'):
                auth_code = login_info.authorization_code
                print(f"authorization_code: {auth_code}")
            else:
                print("❌ Still no authorization_code available")
        
    except Exception as e:
        print(f"❌ Error investigating MammotionHTTP: {e}")

if __name__ == "__main__":
    asyncio.run(investigate_mammotion_http())
