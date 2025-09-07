#!/usr/bin/env python3
"""Debug script to inspect actual pymammotion library structure."""

import sys
import importlib
import inspect
from pathlib import Path

def inspect_module(module_name):
    """Inspect a module and show its contents."""
    try:
        module = importlib.import_module(module_name)
        print(f"\n=== Module: {module_name} ===")
        print(f"File: {getattr(module, '__file__', 'Built-in')}")
        
        # Get all attributes
        attrs = dir(module)
        
        # Separate different types
        classes = []
        functions = []
        constants = []
        
        for attr in attrs:
            if not attr.startswith('_'):
                obj = getattr(module, attr)
                if inspect.isclass(obj):
                    classes.append(attr)
                elif inspect.isfunction(obj):
                    functions.append(attr)
                else:
                    constants.append(attr)
        
        if classes:
            print(f"\nClasses: {', '.join(classes)}")
        if functions:
            print(f"Functions: {', '.join(functions)}")
        if constants:
            print(f"Constants: {', '.join(constants)}")
            
        return module
        
    except ImportError as e:
        print(f"Cannot import {module_name}: {e}")
        return None
    except Exception as e:
        print(f"Error inspecting {module_name}: {e}")
        return None

def main():
    print("🔍 Inspecting pymammotion library structure...")
    
    # Check main pymammotion module
    inspect_module("pymammotion")
    
    # Check specific submodules
    modules_to_check = [
        "pymammotion.mammotion",
        "pymammotion.mammotion.devices",
        "pymammotion.mammotion.devices.mammotion",
        "pymammotion.mammotion.commands",
        "pymammotion.mammotion.commands.mammotion_command",
        "pymammotion.aliyun",
        "pymammotion.aliyun.cloud_gateway",
        "pymammotion.bluetooth",
        "pymammotion.http",
        "pymammotion.mqtt"
    ]
    
    for module_name in modules_to_check:
        inspect_module(module_name)
    
    # Try to find device-related classes
    print("\n🔍 Looking for device classes...")
    try:
        import pymammotion
        
        # Check if there are any device classes in the main module
        for attr_name in dir(pymammotion):
            attr = getattr(pymammotion, attr_name)
            if inspect.isclass(attr) and 'device' in attr_name.lower():
                print(f"Found device class: {attr_name}")
                
    except Exception as e:
        print(f"Error searching for device classes: {e}")
    
    # Check for cloud gateway
    print("\n🔍 Looking for cloud gateway...")
    try:
        from pymammotion.aliyun.cloud_gateway import CloudIOTGateway
        print("✅ CloudIOTGateway found")
        
        # Inspect CloudIOTGateway methods
        methods = [method for method in dir(CloudIOTGateway) if not method.startswith('_')]
        print(f"CloudIOTGateway methods: {', '.join(methods)}")
        
    except ImportError as e:
        print(f"❌ CloudIOTGateway not found: {e}")
    
    # Check for command classes
    print("\n🔍 Looking for command classes...")
    try:
        from pymammotion.mammotion.commands.mammotion_command import MammotionCommand
        print("✅ MammotionCommand found")
        
        # Inspect MammotionCommand methods
        methods = [method for method in dir(MammotionCommand) if not method.startswith('_')]
        print(f"MammotionCommand methods: {', '.join(methods)}")
        
    except ImportError as e:
        print(f"❌ MammotionCommand not found: {e}")

if __name__ == "__main__":
    main()
