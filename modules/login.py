import streamlit as st
from modules.utilis import authenticate_user, register_user

def login_form():
    """Login form component"""
    st.title("🔐 Login")
    st.markdown("Welcome back! Please sign in to access your medical booking account.")
    
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
                    st.session_state.current_page = "🏠 Home"  # Set to Home page
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    # Link to sign up
    st.markdown("---")
    st.markdown("Don't have an account?")
    if st.button("Sign Up", use_container_width=True):
        st.session_state.auth_page = "signup"
        st.rerun()

def signup_form():
    """Sign up form component"""
    st.title("📝 Create Account")
    st.markdown("Join our medical booking platform today!")
    
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email")
        
        with col2:
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # Password requirements
        st.markdown("**Password Requirements:**")
        st.markdown("• At least 6 characters long")
        st.markdown("• Mix of letters and numbers recommended")
        
        signup_button = st.form_submit_button("Create Account", use_container_width=True)
        
        if signup_button:
            # Validation
            errors = []
            
            if not all([username, email, password, confirm_password]):
                errors.append("Please fill in all fields")
            
            if username and len(username) < 3:
                errors.append("Username must be at least 3 characters long")
            
            if email and "@" not in email:
                errors.append("Please enter a valid email address")
            
            if password and len(password) < 6:
                errors.append("Password must be at least 6 characters long")
            
            if password != confirm_password:
                errors.append("Passwords do not match")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                success, message = register_user(username, email, password)
                if success:
                    st.success(message)
                    # Auto-login after successful registration
                    st.session_state.username = username
                    st.session_state.current_page = "🏠 Home"  # Set to Home page
                    st.rerun()
                else:
                    st.error(message)
    
    # Link to login
    st.markdown("---")
    st.markdown("Already have an account?")
    if st.button("Login", use_container_width=True):
        st.session_state.auth_page = "login"
        st.rerun()

def app():
    """Main authentication app"""
    # Initialize auth page if not set
    if 'auth_page' not in st.session_state:
        st.session_state.auth_page = "login"
    
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.session_state.auth_page == "login":
            login_form()
        else:
            signup_form()
    
    # Add some styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
