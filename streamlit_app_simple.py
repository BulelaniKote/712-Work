import streamlit as st
import hashlib
import json
import os
from datetime import datetime
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Medical Booking System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

# User data file path
USERS_FILE = "data/users.json"

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

def is_logged_in():
    """Check if user is logged in"""
    return 'username' in st.session_state

def logout():
    """Logout user"""
    if 'username' in st.session_state:
        del st.session_state.username
    st.session_state.current_page = "🔐 Login"
    st.rerun()

def is_admin():
    """Check if current user is admin"""
    return st.session_state.get('username') == 'admin'

def authenticate_user(username, password):
    """Authenticate user"""
    init_users_file()
    
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
        
        if username in users:
            if verify_password(password, users[username]['password']):
                return True, "Login successful!"
            else:
                return False, "Invalid password"
        else:
            return False, "User not found"
    except Exception as e:
        return False, f"Error: {str(e)}"

def register_user(username, email, password):
    """Register a new user"""
    init_users_file()
    
    try:
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
        
        return True, "Registration successful!"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# --- SIDEBAR MENU ---
with st.sidebar:
    st.markdown("## 🏥 Medical Booking System")
    st.markdown("---")
    
    # Check if user is logged in
    if is_logged_in():
        # User info section
        st.markdown(f"**Welcome, {st.session_state.username}!**")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.divider()
        
        # Navigation menu for logged in users
        if is_admin():
            menu_items = ["🏠 Home", "👨‍⚕️ Specialists", "🗓️ Book Appointment", "📑 My Appointments", "👨‍💼 Admin Dashboard"]
        else:
            menu_items = ["🏠 Home", "👨‍⚕️ Specialists", "🗓️ Book Appointment", "📑 My Appointments"]
        
        current_page = st.session_state.get('current_page', "🏠 Home")
        default_index = menu_items.index(current_page) if current_page in menu_items else 0
        
        selected = st.selectbox(
            "📋 Navigation",
            menu_items,
            index=default_index,
            key="main_navigation"
        )
        
        # Update current page when selection changes
        if selected != st.session_state.get('current_page', "🏠 Home"):
            st.session_state.current_page = selected
    else:
        # Navigation menu for non-logged in users
        selected = st.selectbox(
            "📋 Navigation",
            ["🔐 Login"],
            key="main_navigation"
        )

# --- MAIN CONTENT ---
st.markdown('<h1 class="main-header">🏥 Medical Booking System</h1>', unsafe_allow_html=True)

# --- PAGE ROUTING ---
with st.container():
    if selected == "🔐 Login":
        st.title("🔐 Login")
        st.markdown("Welcome to the Medical Booking System! Please sign in to access your account.")
        
        # Create tabs for Login and Register
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                login_button = st.form_submit_button("Login", use_container_width=True)
                
                if login_button:
                    if not username or not password:
                        st.error("Please fill in all fields")
                    else:
                        success, message = authenticate_user(username, password)
                        if success:
                            st.session_state.username = username
                            st.session_state.current_page = "🏠 Home"
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email", placeholder="Enter your email")
                new_password = st.text_input("Password", type="password", placeholder="Choose a password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                register_button = st.form_submit_button("Register", use_container_width=True)
                
                if register_button:
                    if not all([new_username, new_email, new_password, confirm_password]):
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = register_user(new_username, new_email, new_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
    
    elif selected == "🏠 Home" and is_logged_in():
        st.title("🏠 Home Dashboard")
        st.markdown("Welcome to your Medical Booking System dashboard!")
        
        # Display some basic stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Appointments", "15", "3")
        
        with col2:
            st.metric("Available Specialists", "5", "1")
        
        with col3:
            st.metric("Active Patients", "10", "2")
        
        with col4:
            st.metric("System Status", "Online", "✅")
        
        st.markdown("### Recent Activity")
        st.info("Your medical booking system is running smoothly!")
    
    elif selected == "👨‍⚕️ Specialists" and is_logged_in():
        st.title("👨‍⚕️ Medical Specialists")
        st.markdown("Browse our available medical specialists.")
        
        # Sample specialists data
        specialists_data = {
            "Dr. Nathan Nelson": {"Specialty": "Pediatrician", "Rating": "4.1", "Contact": "856-841-7195"},
            "Dr. Christine Jones": {"Specialty": "Dermatologist", "Rating": "3.1", "Contact": "231.942.5129"},
            "Dr. Heather Brooks": {"Specialty": "Cardiologist", "Rating": "4.5", "Contact": "555-123-4567"},
            "Dr. Logan Willis": {"Specialty": "Neurologist", "Rating": "4.2", "Contact": "555-987-6543"},
            "Dr. Sarah Johnson": {"Specialty": "Orthopedist", "Rating": "4.0", "Contact": "555-456-7890"}
        }
        
        for name, info in specialists_data.items():
            with st.expander(f"👨‍⚕️ {name}"):
                st.write(f"**Specialty:** {info['Specialty']}")
                st.write(f"**Rating:** {info['Rating']}/5.0")
                st.write(f"**Contact:** {info['Contact']}")
                if st.button(f"Book Appointment with {name}", key=f"book_{name}"):
                    st.success(f"Appointment booking feature coming soon!")
    
    elif selected == "🗓️ Book Appointment" and is_logged_in():
        st.title("🗓️ Book Appointment")
        st.markdown("Schedule your medical appointment.")
        
        with st.form("appointment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                specialty = st.selectbox("Specialty", ["Pediatrician", "Dermatologist", "Cardiologist", "Neurologist", "Orthopedist"])
                date = st.date_input("Preferred Date")
            
            with col2:
                time = st.selectbox("Preferred Time", ["09:00", "11:00", "13:00", "15:00"])
                reason = st.text_area("Reason for Visit", placeholder="Brief description of your symptoms or concerns")
            
            if st.form_submit_button("Book Appointment", use_container_width=True):
                st.success("Appointment booked successfully! You will receive a confirmation email.")
    
    elif selected == "📑 My Appointments" and is_logged_in():
        st.title("📑 My Appointments")
        st.markdown("View and manage your scheduled appointments.")
        
        # Sample appointments data
        appointments_data = [
            {"Date": "2025-10-10", "Time": "09:00", "Specialist": "Dr. Nathan Nelson", "Specialty": "Pediatrician", "Status": "Confirmed"},
            {"Date": "2025-10-15", "Time": "11:00", "Specialist": "Dr. Christine Jones", "Specialty": "Dermatologist", "Status": "Pending"}
        ]
        
        if appointments_data:
            for i, appointment in enumerate(appointments_data):
                with st.expander(f"Appointment {i+1} - {appointment['Date']}"):
                    st.write(f"**Date:** {appointment['Date']}")
                    st.write(f"**Time:** {appointment['Time']}")
                    st.write(f"**Specialist:** {appointment['Specialist']}")
                    st.write(f"**Specialty:** {appointment['Specialty']}")
                    st.write(f"**Status:** {appointment['Status']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Reschedule", key=f"reschedule_{i}"):
                            st.info("Reschedule feature coming soon!")
                    with col2:
                        if st.button(f"Cancel", key=f"cancel_{i}"):
                            st.warning("Cancel feature coming soon!")
        else:
            st.info("No appointments scheduled.")
    
    elif selected == "👨‍💼 Admin Dashboard" and is_admin():
        st.title("👨‍💼 Admin Dashboard")
        st.markdown("Administrative panel for system management.")
        
        # Admin features
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("User Management")
            st.info("User management features coming soon!")
        
        with col2:
            st.subheader("System Statistics")
            st.metric("Total Users", "25")
            st.metric("Total Appointments", "150")
            st.metric("System Uptime", "99.9%")
    
    else:
        # If user tries to access protected pages without login, show login
        st.title("🔐 Login Required")
        st.info("Please log in to access this page.")
        st.markdown("Use the sidebar to navigate to the login page.")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🏥 Medical Booking System | Built with Streamlit | BIA 712 Group 3</p>
    <p>Secure • Reliable • User-Friendly</p>
</div>
""", unsafe_allow_html=True)
