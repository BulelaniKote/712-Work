import streamlit as st
from streamlit_option_menu import option_menu
from modules.utilis import is_logged_in, logout, is_admin

# --- PAGE CONFIG ---
st.set_page_config(page_title="Medical Booking System", layout="wide")

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# --- SIDEBAR MENU ---
with st.sidebar:
    # Check if user is logged in
    if is_logged_in():
        # User info section
        st.markdown(f"**Welcome, {st.session_state.username}!**")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.divider()
        
        # Navigation menu for logged in users
        # Determine default index based on current page
        if is_admin():
            menu_items = ["🏠 Home", "👨‍⚕️ Specialists", "🗓️ Book Appointment", "📑 My Appointments", "👨‍💼 Admin Dashboard", "📊 Upload Data"]
        else:
            menu_items = ["🏠 Home", "👨‍⚕️ Specialists", "🗓️ Book Appointment", "📑 My Appointments"]
        
        current_page = st.session_state.get('current_page', "🏠 Home")
        default_index = menu_items.index(current_page) if current_page in menu_items else 0
        
        # Set icons based on menu items
        if is_admin():
            icons = ["house", "person-badge", "calendar-plus", "journal-text", "gear", "cloud-upload"]
    else:
            icons = ["house", "person-badge", "calendar-plus", "journal-text"]
        
        selected = option_menu(
            "📋 Navigation",
            menu_items,
            icons=icons,
            menu_icon="cast",
            default_index=default_index,
            key="main_navigation"
        )
        
        # Update current page when selection changes
        if selected != st.session_state.get('current_page', "🏠 Home"):
            st.session_state.current_page = selected
        else:
        # Navigation menu for non-logged in users
        selected = option_menu(
            "📋 Navigation",
            ["🔐 Login"],
            icons=["box-arrow-in-right"],
            menu_icon="cast",
            default_index=0,
            key="main_navigation"
        )

# --- PAGE ROUTING ---
# Use a container to prevent duplicates
with st.container():
    if selected == "🔐 Login":
        from modules.login import app as login_app
        login_app()
    elif selected == "🏠 Home" and is_logged_in():
        from modules.home import app as home_app
        home_app()
    elif selected == "👨‍⚕️ Specialists" and is_logged_in():
        from modules.specialists import app as specialists_app
        specialists_app()
    elif selected == "🗓️ Book Appointment" and is_logged_in():
        from modules.book_appointment import app as book_app
        book_app()
    elif selected == "📑 My Appointments" and is_logged_in():
        from modules.my_appointments import app as my_appointments_app
        my_appointments_app()
    elif selected == "👨‍💼 Admin Dashboard" and is_admin():
        from modules.admin_dashboard import app as admin_app
        admin_app()
    elif selected == "📊 Upload Data" and is_admin():
        from modules.data_upload import app as upload_app
        upload_app()
        else:
        # If user tries to access protected pages without login, show login
        from modules.login import app as login_app
        login_app()