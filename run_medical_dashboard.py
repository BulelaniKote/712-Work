#!/usr/bin/env python3
"""
Medical Dashboard Runner Script
===============================

This script helps you run the Medical Facility Analysis Dashboard.
It checks for required dependencies and provides installation instructions.
"""

import sys
import subprocess
import importlib.util

def check_package(package_name):
    """Check if a package is installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "medical_requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages. Please install manually:")
        print("pip install streamlit pandas plotly numpy faker altair")
        return False

def run_dashboard():
    """Run the Streamlit dashboard"""
    print("🏥 Starting Medical Facility Analysis Dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "medical_streamlit_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

def main():
    """Main function"""
    print("🏥 Medical Facility Analysis Dashboard")
    print("=" * 50)
    
    # Check required packages
    required_packages = ['streamlit', 'pandas', 'plotly', 'numpy', 'faker', 'altair']
    missing_packages = []
    
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\nWould you like to install them automatically? (y/n): ", end="")
        
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                if install_requirements():
                    print("\n🚀 Starting dashboard...")
                    run_dashboard()
                else:
                    print("\n❌ Please install packages manually and try again")
            else:
                print("\n💡 Please install required packages:")
                print("pip install -r medical_requirements.txt")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("✅ All required packages are installed!")
        run_dashboard()

if __name__ == "__main__":
    main()
