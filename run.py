#!/usr/bin/env python3
"""
HTTP Version for ngrok testing
"""

from app import create_app, socketio
from config import config
import os
import sys

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                                    🔓 WEAK SSL CHAT - HTTP MODE                                                                ║
    ║                                                                                                                                  ║
    ║  WARNING: This is a VULNERABLE application designed for penetration testing demonstrations.                                     ║
    ║  ⚠️  DO NOT use in production environments!                                                                                     ║
    ║                                                                                                                                  ║
    ║  🎯 Purpose: Demonstrate SSL/TLS vulnerabilities and traffic interception                                                       ║
    ║  📍 Running on: HTTP (no SSL for ngrok compatibility)                                                                           ║
    ║                                                                                                                                  ║
    ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)
    
    app = create_app()
    
    try:
        # Run HTTP version (no SSL certificates)
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=app.config['DEBUG'],
            allow_unsafe_werkzeug=True
        )
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
