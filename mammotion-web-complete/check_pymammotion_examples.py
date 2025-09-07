#!/usr/bin/env python3
"""Check for pymammotion usage examples and documentation."""

import os
import sys
import importlib.util
from pathlib import Path

def find_pymammotion_examples():
    """Find pymammotion installation and look for examples."""
    print("🔍 Looking for pymammotion examples and documentation...")
    
    try:
        import pymammotion
        pymammotion_path = Path(pymammotion.__file__).parent
        print(f"pymammotion installed at: {pymammotion_path}")
        
        # Look for example files
        example_patterns = ['example', 'demo', 'test', 'sample']
        
        for root, dirs, files in os.walk(pymammotion_path):
            for file in files:
                if file.endswith('.py'):
                    file_lower = file.lower()
                    if any(pattern in file_lower for pattern in example_patterns):
                        file_path = Path(root) / file
                        print(f"\nFound potential example: {file_path}")
                        
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                
                            # Look for login_by_oauth usage
                            if 'login_by_oauth' in content:
                                print("  Contains login_by_oauth usage!")
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if 'login_by_oauth' in line:
                                        print(f"    Line {i+1}: {line.strip()}")
                                        # Print context
                                        for j in range(max(0, i-2), min(len(lines), i+3)):
                                            if j != i:
                                                print(f"    Line {j+1}: {lines[j].strip()}")
                                        print()
                                        
                        except Exception as e:
                            print(f"  Could not read file: {e}")
        
        # Look for README or documentation files
        doc_patterns = ['README', 'readme', 'USAGE', 'usage', 'doc', 'DOC']
        
        for root, dirs, files in os.walk(pymammotion_path.parent):
            for file in files:
                file_lower = file.lower()
                if any(pattern in file_lower for pattern in doc_patterns):
                    file_path = Path(root) / file
                    if file_path.suffix in ['.md', '.txt', '.rst', '']:
                        print(f"\nFound documentation: {file_path}")
                        
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                
                            if 'login' in content.lower() or 'auth' in content.lower():
                                print("  Contains authentication information!")
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if 'login' in line.lower() or 'auth' in line.lower():
                                        print(f"    Line {i+1}: {line.strip()}")
                                        
                        except Exception as e:
                            print(f"  Could not read file: {e}")
                            
    except ImportError:
        print("❌ pymammotion not found")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_pip_info():
    """Check pip information for pymammotion."""
    print("\n🔍 Checking pip information for pymammotion...")
    
    try:
        import subprocess
        result = subprocess.run(['pip', 'show', 'pymammotion'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Pip show output:")
            print(result.stdout)
            
            # Look for homepage or repository
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Home-page:' in line or 'Project-URL:' in line:
                    print(f"  {line}")
        else:
            print("❌ pip show failed")
            
    except Exception as e:
        print(f"❌ Error running pip show: {e}")

if __name__ == "__main__":
    find_pymammotion_examples()
    check_pip_info()
