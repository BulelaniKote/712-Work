import streamlit as st
import hashlib
import json
import os
from datetime import datetime
import pandas as pd

# User data file path - using the existing data folder
USERS_FILE = "MedicalBookingApp/med/MedicalBookingApp/data/users.json"

def init_users_file():
    """Initialize users file if it doesn't exist"""
    if not os.path.exists(USERS_FILE):
        os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def register_user(username, email, password):
    """Register a new user"""
    init_users_file()
    
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    # Check if user already exists
    if username in users:
        return False, "Username already exists"
    
    # Check if email already exists
    for user_data in users.values():
        if user_data.get('email') == email:
            return False, "Email already registered"
    
    # Add new user
    users[username] = {
        'email': email,
        'password': hash_password(password),
        'created_at': datetime.now().isoformat(),
        'appointments': []
    }
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    
    return True, "User registered successfully"

def authenticate_user(username, password):
    """Authenticate user login"""
    init_users_file()
    
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        
        if username in users and verify_password(password, users[username]['password']):
            return True, "Login successful"
        else:
            return False, "Invalid username or password"
    except FileNotFoundError:
        return False, "No users found. Please sign up first."

def is_logged_in():
    """Check if user is logged in"""
    return 'username' in st.session_state and st.session_state.username is not None

def logout():
    """Logout user"""
    if 'username' in st.session_state:
        del st.session_state.username
    st.rerun()

def get_current_user_data():
    """Get current user's data"""
    if not is_logged_in():
        return None
    
    init_users_file()
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        return users.get(st.session_state.username, None)
    except FileNotFoundError:
        return None

def save_user_data(user_data):
    """Save updated user data"""
    if not is_logged_in():
        return False
    
    init_users_file()
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        
        users[st.session_state.username] = user_data
        
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving user data: {e}")
        return False

def add_appointment(appointment_data):
    """Add appointment to current user's data"""
    user_data = get_current_user_data()
    if user_data:
        if 'appointments' not in user_data:
            user_data['appointments'] = []
        
        user_data['appointments'].append({
            **appointment_data,
            'created_at': datetime.now().isoformat()
        })
        
        return save_user_data(user_data)
    return False

def is_admin():
    """Check if current user is an admin"""
    return is_logged_in() and st.session_state.get('username') == 'admin'

def get_all_users():
    """Get all users data for admin purposes"""
    init_users_file()
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        return users
    except FileNotFoundError:
        return {}

def get_all_appointments():
    """Get all appointments from all users for admin analytics"""
    users = get_all_users()
    all_appointments = []
    
    for username, user_data in users.items():
        if 'appointments' in user_data:
            for appointment in user_data['appointments']:
                appointment_with_user = appointment.copy()
                appointment_with_user['username'] = username
                appointment_with_user['user_email'] = user_data.get('email', 'N/A')
                all_appointments.append(appointment_with_user)
    
    return all_appointments

def get_specialist_performance():
    """Get specialist performance data"""
    appointments = get_all_appointments()
    specialist_stats = {}
    
    for appointment in appointments:
        specialty = appointment.get('specialty', 'Unknown')
        if specialty not in specialist_stats:
            specialist_stats[specialty] = {
                'total_appointments': 0,
                'confirmed_appointments': 0,
                'cancelled_appointments': 0,
                'unique_patients': set(),
                'monthly_appointments': {}
            }
        
        stats = specialist_stats[specialty]
        stats['total_appointments'] += 1
        
        status = appointment.get('status', 'unknown').lower()
        if status == 'confirmed':
            stats['confirmed_appointments'] += 1
        elif status == 'cancelled':
            stats['cancelled_appointments'] += 1
        
        stats['unique_patients'].add(appointment.get('username', ''))
        
        # Monthly stats
        date_str = appointment.get('date', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                stats['monthly_appointments'][month_key] = stats['monthly_appointments'].get(month_key, 0) + 1
            except:
                pass
    
    # Convert sets to counts and format data
    for specialty, stats in specialist_stats.items():
        stats['unique_patients'] = len(stats['unique_patients'])
        stats['confirmation_rate'] = (stats['confirmed_appointments'] / stats['total_appointments'] * 100) if stats['total_appointments'] > 0 else 0
    
    return specialist_stats

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    init_users_file()
    
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if 'admin' not in users:
        users['admin'] = {
            'email': 'admin@medicalcenter.com',
            'password': hash_password('admin123'),
            'created_at': datetime.now().isoformat(),
            'appointments': [],
            'role': 'admin'
        }
        
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        
        return True
    return False