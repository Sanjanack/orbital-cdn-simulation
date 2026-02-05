"""
Setup Verification Script
=========================
Run this script before your presentation to ensure everything is working.
"""

import sys
import os

def check_python_version():
    """Check if Python version is 3.8+"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    required_packages = [
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_socketio',
        'simpy',
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'werkzeug',
        'eventlet'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

def check_files():
    """Check if required files exist"""
    print("\n🔍 Checking project files...")
    required_files = [
        'app.py',
        'realistic_content_catalog.py',
        'advanced_caching.py',
        'satellite_constellation.py',
        'realtime_collaboration.py',
        'ntn_network_simulation.py',
        'requirements.txt'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            missing.append(file)
    
    if missing:
        print(f"\n⚠️  Missing files: {', '.join(missing)}")
        return False
    return True

def check_database():
    """Check if database directory exists"""
    print("\n🔍 Checking database setup...")
    instance_dir = 'instance'
    if os.path.exists(instance_dir):
        print(f"✅ {instance_dir}/ directory - Found")
        return True
    else:
        print(f"⚠️  {instance_dir}/ directory - Will be created on first run")
        return True  # This is OK, will be created automatically

def check_port():
    """Check if port 5000 is available"""
    print("\n🔍 Checking port 5000...")
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("⚠️  Port 5000 is in use - Application may already be running")
        print("   If not, you may need to change the port in app.py")
        return False
    else:
        print("✅ Port 5000 - Available")
        return True

def main():
    """Run all checks"""
    print("=" * 50)
    print("🚀 Orbital CDN Simulation - Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Files", check_files),
        ("Database Setup", check_database),
        ("Port Availability", check_port),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Verification Summary")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! You're ready to run the application!")
        print("\nNext steps:")
        print("1. Activate virtual environment: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)")
        print("2. Run: python app.py")
        print("3. Open browser: http://localhost:5000")
        print("4. Login: admin / admin123")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Check Python version: python --version (need 3.8+)")
        print("- If port 5000 in use, change port in app.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
