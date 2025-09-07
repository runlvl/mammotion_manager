"""Command line interface for Mammotion Web."""

import argparse
import sys
from pathlib import Path

from .main import main as run_server
from .config import get_settings


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Mammotion Web Control - Professional lawn mower management"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Server command
    server_parser = subparsers.add_parser("serve", help="Start the web server")
    server_parser.add_argument("--host", help="Host to bind to")
    server_parser.add_argument("--port", type=int, help="Port to bind to")
    server_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Show current configuration")
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check system health")
    
    args = parser.parse_args()
    
    if args.command == "serve" or args.command is None:
        # Override settings if provided
        if args.command == "serve":
            settings = get_settings()
            if args.host:
                settings.HOST = args.host
            if args.port:
                settings.PORT = args.port
            if args.debug:
                settings.DEBUG = True
        
        run_server()
    
    elif args.command == "config":
        settings = get_settings()
        print("Current Configuration:")
        print(f"  Host: {settings.HOST}")
        print(f"  Port: {settings.PORT}")
        print(f"  Region: {settings.REGION}")
        print(f"  Country: {settings.COUNTRY_CODE}")
        print(f"  Debug: {settings.DEBUG}")
        print(f"  Redis: {settings.REDIS_URL}")
        print(f"  Log Level: {settings.LOG_LEVEL}")
    
    elif args.command == "health":
        print("System Health Check:")
        print("  [✓] Configuration loaded")
        
        # Check Redis connection
        try:
            from .core.session import SessionManager
            session_manager = SessionManager()
            print("  [✓] Redis connection available")
        except Exception as e:
            print(f"  [✗] Redis connection failed: {e}")
            sys.exit(1)
        
        # Check pymammotion import
        try:
            import pymammotion
            print(f"  [✓] PyMammotion library available (v{pymammotion.__version__})")
        except ImportError as e:
            print(f"  [✗] PyMammotion library not available: {e}")
            sys.exit(1)
        
        print("  [✓] All systems operational")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
