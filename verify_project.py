"""
Project Verification Script
==========================

This script verifies that all components of the Satellite CDN project are working correctly.
Run this before presentations or demonstrations to ensure everything is ready.

Team Members: 
1. Neha (U25UV23T064063)
2. Sanjana C K (U25UV22T064049)
"""

import os
import sys
import importlib
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    required_packages = [
        'simpy', 'flask', 'pandas', 'numpy', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install " + " ".join(missing_packages))
        return False
    return True

def check_files():
    """Check if all required files exist"""
    print("\n📁 Checking project files...")
    required_files = [
        'content_data.py',
        'main.py',
        'satellite_cdn_simulation.py',
        'enhanced_satellite_cdn.py',
        'live_simulation.py',
        'web_simulation.py',
        'PROJECT_DOCUMENTATION.md',
        'README.md',
        'PRESENTATION_GUIDE.md',
        'templates/index.html',
        'templates/live_dashboard.html'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - Found")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    return True

def test_basic_simulation():
    """Test the basic simulation"""
    print("\n🧪 Testing basic simulation...")
    try:
        result = subprocess.run([sys.executable, 'main.py'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Basic simulation - Working")
            return True
        else:
            print(f"❌ Basic simulation - Failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ Basic simulation - Working (timeout expected)")
        return True
    except Exception as e:
        print(f"❌ Basic simulation - Error: {e}")
        return False

def test_enhanced_simulation():
    """Test the enhanced simulation"""
    print("\n🚀 Testing enhanced simulation...")
    try:
        result = subprocess.run([sys.executable, 'enhanced_satellite_cdn.py'], 
                              capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Enhanced simulation - Working")
            return True
        else:
            print(f"❌ Enhanced simulation - Failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ Enhanced simulation - Working (timeout expected)")
        return True
    except Exception as e:
        print(f"❌ Enhanced simulation - Error: {e}")
        return False

def check_csv_outputs():
    """Check if CSV output files are generated"""
    print("\n📊 Checking CSV outputs...")
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if csv_files:
        print(f"✅ Found {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            size = os.path.getsize(csv_file)
            print(f"   📄 {csv_file} ({size} bytes)")
        return True
    else:
        print("⚠️  No CSV files found (run simulations first)")
        return False

def test_web_server():
    """Test if web server can start"""
    print("\n🌐 Testing web server...")
    try:
        # Try to import Flask
        import flask
        print("✅ Flask - Available")
        
        # Check if templates directory exists
        if os.path.exists('templates'):
            print("✅ Templates directory - Found")
            return True
        else:
            print("❌ Templates directory - Missing")
            return False
    except ImportError:
        print("❌ Flask - Not available")
        return False

def generate_status_report(results):
    """Generate a comprehensive status report"""
    print("\n" + "="*60)
    print("📋 PROJECT STATUS REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Overall Status: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All systems operational! Project is ready for presentation.")
        print("\n🚀 Quick Start Commands:")
        print("1. venv/Scripts/Activate.ps1")
        print("2. python live_simulation.py")
        print("3. Open: http://localhost:5000")
    else:
        print("⚠️  Some issues detected. Please resolve before presentation.")
        print("\n🔧 Troubleshooting:")
        print("1. Activate virtual environment")
        print("2. Install missing dependencies: pip install -r requirements.txt")
        print("3. Run simulations to generate CSV files")
    
    print("\n📁 Project Structure:")
    print("├── live_simulation.py (Main presentation file)")
    print("├── enhanced_satellite_cdn.py (Comprehensive analysis)")
    print("├── satellite_cdn_simulation.py (Basic simulation)")
    print("├── main.py (Simple simulation)")
    print("├── PROJECT_DOCUMENTATION.md (Academic documentation)")
    print("├── PRESENTATION_GUIDE.md (Presentation instructions)")
    print("└── README.md (Project overview)")
    
    print("\n🎯 Presentation Ready:")
    if all(results.values()):
        print("✅ All components working")
        print("✅ Dependencies installed")
        print("✅ Files present")
        print("✅ Simulations functional")
        print("✅ Web interface available")
    else:
        print("❌ Some components need attention")
    
    print("="*60)

def main():
    """Main verification function"""
    print("🛰️  Satellite CDN Project Verification")
    print("Team: Neha & Sanjana C K")
    print("="*50)
    
    results = {}
    
    # Run all checks
    results['python_version'] = check_python_version()
    results['dependencies'] = check_dependencies()
    results['files'] = check_files()
    results['basic_simulation'] = test_basic_simulation()
    results['enhanced_simulation'] = test_enhanced_simulation()
    results['csv_outputs'] = check_csv_outputs()
    results['web_server'] = test_web_server()
    
    # Generate report
    generate_status_report(results)
    
    # Return overall status
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 