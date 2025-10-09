#!/usr/bin/env python3
"""
Test script to verify BigQuery synchronization functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utilis import (
    get_bigquery_client, 
    ensure_dataset_exists, 
    add_appointment_to_bigquery,
    add_user_to_bigquery,
    sync_existing_data_to_bigquery
)

def test_bigquery_connection():
    """Test BigQuery connection"""
    print("Testing BigQuery connection...")
    client, project_id = get_bigquery_client()
    
    if client and project_id:
        print(f"✅ BigQuery connection successful!")
        print(f"   Project ID: {project_id}")
        return True
    else:
        print("❌ BigQuery connection failed!")
        return False

def test_dataset_creation():
    """Test dataset creation"""
    print("\nTesting dataset creation...")
    success = ensure_dataset_exists()
    
    if success:
        print("✅ Dataset creation/verification successful!")
        return True
    else:
        print("❌ Dataset creation failed!")
        return False

def test_user_sync():
    """Test user synchronization"""
    print("\nTesting user synchronization...")
    
    test_user = {
        'username': 'test_user_sync',
        'email': 'test@example.com',
        'password': 'hashed_password_123',
        'role': 'patient'
    }
    
    success = add_user_to_bigquery(test_user)
    
    if success:
        print("✅ User synchronization successful!")
        return True
    else:
        print("❌ User synchronization failed!")
        return False

def test_appointment_sync():
    """Test appointment synchronization"""
    print("\nTesting appointment synchronization...")
    
    test_appointment = {
        'name': 'Test Patient',
        'email': 'test@example.com',
        'specialty': 'Cardiology',
        'date': '2024-01-15',
        'time': '09:00:00',
        'reason': 'Test appointment',
        'status': 'confirmed',
        'created_at': '2024-01-01T10:00:00'
    }
    
    # Mock session state for testing
    import streamlit as st
    if not hasattr(st, 'session_state'):
        st.session_state = type('obj', (object,), {})()
    st.session_state.username = 'test_user_sync'
    
    success = add_appointment_to_bigquery(test_appointment)
    
    if success:
        print("✅ Appointment synchronization successful!")
        return True
    else:
        print("❌ Appointment synchronization failed!")
        return False

def main():
    """Run all tests"""
    print("BigQuery Synchronization Test Suite")
    print("=" * 50)
    
    tests = [
        test_bigquery_connection,
        test_dataset_creation,
        test_user_sync,
        test_appointment_sync
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! BigQuery synchronization is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check your BigQuery configuration.")

if __name__ == "__main__":
    main()
