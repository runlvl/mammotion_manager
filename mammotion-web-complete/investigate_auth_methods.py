#!/usr/bin/env python3
"""Investigate pymammotion authentication methods and CloudIOTGateway usage."""

import asyncio
import logging
import inspect
import aiohttp
from pymammotion.aliyun.cloud_gateway import CloudIOTGateway

# Set up logging
logging.basicConfig(level=logging.DEBUG)

async def investigate_auth_methods():
    """Investigate all available authentication methods."""
    print("🔍 Investigating pymammotion authentication methods...")
    
    session = aiohttp.ClientSession()
    
    try:
        gateway = CloudIOTGateway(session)
        print("✅ CloudIOTGateway initialized")
        
        # 1. Inspect CloudIOTGateway class
        print("\n=== CloudIOTGateway Class Inspection ===")
        print(f"Class: {CloudIOTGateway}")
        print(f"Module: {CloudIOTGateway.__module__}")
        
        # Get all methods
        methods = [method for method in dir(gateway) if not method.startswith('_')]
        print(f"Available methods: {methods}")
        
        # 2. Inspect login_by_oauth method specifically
        print("\n=== login_by_oauth Method Inspection ===")
        if hasattr(gateway, 'login_by_oauth'):
            method = getattr(gateway, 'login_by_oauth')
            print(f"Method: {method}")
            
            # Get method signature
            try:
                sig = inspect.signature(method)
                print(f"Signature: {sig}")
                print(f"Parameters: {list(sig.parameters.keys())}")
                
                for param_name, param in sig.parameters.items():
                    print(f"  - {param_name}: {param.annotation} (default: {param.default})")
                    
            except Exception as e:
                print(f"Could not get signature: {e}")
            
            # Get docstring
            docstring = inspect.getdoc(method)
            if docstring:
                print(f"Docstring:\n{docstring}")
            else:
                print("No docstring available")
        else:
            print("❌ login_by_oauth method not found")
        
        # 3. Look for other authentication methods
        print("\n=== Other Authentication Methods ===")
        auth_methods = [method for method in methods if 'login' in method.lower() or 'auth' in method.lower()]
        print(f"Auth-related methods: {auth_methods}")
        
        for method_name in auth_methods:
            method = getattr(gateway, method_name)
            try:
                sig = inspect.signature(method)
                print(f"{method_name}: {sig}")
            except:
                print(f"{method_name}: signature unavailable")
        
        # 4. Check for initialization parameters
        print("\n=== CloudIOTGateway Initialization ===")
        try:
            init_sig = inspect.signature(CloudIOTGateway.__init__)
            print(f"__init__ signature: {init_sig}")
        except Exception as e:
            print(f"Could not get __init__ signature: {e}")
        
        # 5. Check gateway attributes after initialization
        print("\n=== Gateway Attributes ===")
        attrs = [attr for attr in dir(gateway) if not attr.startswith('_') and not callable(getattr(gateway, attr))]
        for attr in attrs:
            try:
                value = getattr(gateway, attr)
                print(f"{attr}: {type(value)} = {value}")
            except Exception as e:
                print(f"{attr}: Error getting value - {e}")
        
        # 6. Try to find example usage in the source
        print("\n=== Source Code Location ===")
        try:
            import pymammotion.aliyun.cloud_gateway
            source_file = inspect.getfile(pymammotion.aliyun.cloud_gateway)
            print(f"Source file: {source_file}")
            
            # Try to read the source
            try:
                with open(source_file, 'r') as f:
                    source_lines = f.readlines()
                
                # Look for login_by_oauth definition
                for i, line in enumerate(source_lines):
                    if 'def login_by_oauth' in line:
                        print(f"\nFound login_by_oauth definition at line {i+1}:")
                        # Print the method definition and a few lines after
                        for j in range(max(0, i-2), min(len(source_lines), i+10)):
                            prefix = ">>> " if j == i else "    "
                            print(f"{prefix}{j+1:3d}: {source_lines[j].rstrip()}")
                        break
                        
            except Exception as e:
                print(f"Could not read source file: {e}")
                
        except Exception as e:
            print(f"Could not get source file: {e}")
        
        # 7. Test actual method call with different approaches
        print("\n=== Testing Method Calls ===")
        
        # Test with no parameters first to see the actual error
        try:
            print("Testing login_by_oauth() with no parameters...")
            result = await gateway.login_by_oauth()
            print(f"✅ No parameters worked: {result}")
        except Exception as e:
            print(f"❌ No parameters failed: {e}")
            print(f"Error type: {type(e)}")
        
        # Test with single parameter
        try:
            print("Testing login_by_oauth('test') with single string...")
            result = await gateway.login_by_oauth('test')
            print(f"✅ Single string worked: {result}")
        except Exception as e:
            print(f"❌ Single string failed: {e}")
            print(f"Error type: {type(e)}")
        
        # Test with dict parameter
        try:
            print("Testing login_by_oauth({'test': 'value'}) with dict...")
            result = await gateway.login_by_oauth({'test': 'value'})
            print(f"✅ Dict worked: {result}")
        except Exception as e:
            print(f"❌ Dict failed: {e}")
            print(f"Error type: {type(e)}")
            
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(investigate_auth_methods())
