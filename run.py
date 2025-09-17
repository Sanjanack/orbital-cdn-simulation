#!/usr/bin/env python3
"""
Orbital CDN Simulation - Startup Script
========================================

This script provides an easy way to start the Orbital CDN simulation application.
It handles environment setup and provides helpful information for users.

Team Members: 
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)

Usage:
    python run.py
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print the application banner"""
    print("=" * 80)
    print("🛰️  ORBITAL CDN SIMULATION - ADVANCED SATELLITE CONTENT DELIVERY NETWORK")
    print("=" * 80)
    print("Team Members:")
    print("1. Neha (U25UV23T064063) - Lead Developer & Simulation Engineer")
    print("2. Sanjana C K (U25UV22T064049) - System Architect & UI/UX Designer")
    print("=" * 80)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        print("Please upgrade Python and try again.")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'simpy', 
        'pandas', 'numpy', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please install missing dependencies using:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def setup_environment():
    """Set up environment variables"""
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = '1'
    
    if 'SECRET_KEY' not in os.environ:
        os.environ['SECRET_KEY'] = 'orbital-cdn-secret-key-2025'
    
    print("✅ Environment variables configured")

def start_application():
    """Start the Flask application"""
    try:
        print("\n🚀 Starting Orbital CDN Simulation Application...")
        print("📱 Web interface will be available at: http://localhost:5000")
        print("🔑 Default admin credentials: admin / admin123")
        print("⏹️  Press Ctrl+C to stop the application")
        print("=" * 80)
        
        # Import and initialize the Flask app and database
        from app import app, db, ensure_schema_migrations, create_default_admin
        
        with app.app_context():
            db.create_all()
            ensure_schema_migrations()
            create_default_admin()
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        print("👋 Thank you for using Orbital CDN Simulation!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("Please check the error message and try again.")

def main():
    """Main function"""
    print_banner()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    print("\n🔍 Checking dependencies...")
    if not check_dependencies():
        print("\n💡 To install dependencies, run:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n⚙️  Setting up environment...")
    setup_environment()
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main() 