import streamlit as st
import plotly.express as px
from modules.utilis import authenticate_user, register_user, get_medical_specialists, get_medical_appointments

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
    
    # BigQuery Analytics Section
    st.divider()
    st.subheader("📊 System Overview (BigQuery Data)")
    
    # Get BigQuery data for system overview
    specialists_data = get_medical_specialists()
    appointments_data = get_medical_appointments()
    
    if specialists_data and appointments_data:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👨‍⚕️ Specialists", len(specialists_data))
        with col2:
            st.metric("📅 Appointments", len(appointments_data))
        with col3:
            # Calculate specialties
            specialties = set([spec.get('Specialty', 'Unknown') for spec in specialists_data])
            st.metric("🏥 Specialties", len(specialties))
        with col4:
            # Calculate average rating
            ratings = [spec.get('Rating', 0) for spec in specialists_data if spec.get('Rating', 0) > 0]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5.0")
        
        # Quick analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏥 Available Specialties")
            specialty_counts = {}
            for spec in specialists_data:
                specialty = spec.get('Specialty', 'Unknown')
                specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1
            
            if specialty_counts:
                fig = px.bar(x=list(specialty_counts.keys()), y=list(specialty_counts.values()),
                           title="Specialists by Specialty", color=list(specialty_counts.values()),
                           color_continuous_scale='Blues')
                fig.update_layout(showlegend=False, xaxis_title="Specialty", yaxis_title="Number of Specialists")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📈 System Health")
            st.info(f"""
            **✅ System Status:**
            - Database: Connected
            - Specialists: {len(specialists_data)} Active
            - Appointments: {len(appointments_data)} Total
            - Data Quality: High
            """)
            
            st.success("🚀 Ready to book your appointment!")
    
    else:
        st.warning("⚠️ System data loading... Please ensure BigQuery tables are available.")
