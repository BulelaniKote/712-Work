#!/usr/bin/env python3
"""
Medical System Runner
====================

This script runs the complete medical facility system:
1. Populates BigQuery with synthetic medical data
2. Launches the Streamlit web application

Usage:
    python run_medical_system.py
"""

import subprocess
import sys
import time

def run_population_script():
    """Run the BigQuery population script"""
    print("🏥 Step 1: Populating BigQuery with Medical Data")
    print("=" * 60)
    
    try:
        result = subprocess.run([sys.executable, "populate_medical_bigquery.py"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running population script: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ populate_medical_bigquery.py not found in current directory")
        return False

def run_web_app():
    """Run the Streamlit web application"""
    print("\n🌐 Step 2: Launching Medical Web Application")
    print("=" * 60)
    print("🚀 Starting Streamlit server...")
    print("📱 Your web app will open at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "medical_web_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Medical web application stopped by user")
    except FileNotFoundError:
        print("❌ medical_web_app.py not found in current directory")
    except Exception as e:
        print(f"❌ Error running web application: {e}")

def main():
    """Main function"""
    print("🏥 Medical Facility System Launcher")
    print("=" * 60)
    print("This will:")
    print("1. 📊 Create and populate BigQuery medical database")
    print("2. 🌐 Launch the medical analytics web application")
    print()
    
    # Ask user if they want to proceed
    response = input("Continue? (y/n): ").lower().strip()
    if response not in ['y', 'yes']:
        print("👋 Goodbye!")
        return
    
    # Step 1: Populate database
    if run_population_script():
        print("\n✅ Database population completed successfully!")
        print("⏳ Waiting 3 seconds before launching web app...")
        time.sleep(3)
        
        # Step 2: Launch web app
        run_web_app()
    else:
        print("\n❌ Database population failed. Cannot launch web app.")
        print("\n💡 Please check:")
        print("   • BigQuery credentials are configured")
        print("   • populate_medical_bigquery.py exists")
        print("   • Required packages are installed")

if __name__ == "__main__":
    main()
