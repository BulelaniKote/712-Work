import streamlit as st
from modules.utilis import get_current_user_data, add_appointment
from datetime import datetime

def app():
    st.title("🗓️ Book Appointment")
    st.markdown("Schedule a visit with a specialist.")

    # Get current user data
    user_data = get_current_user_data()
    
    # --- Booking Form ---
    with st.form("appointment_form"):
        # Pre-fill with user data
        name = st.text_input("Your Name", value=st.session_state.username)
        email = st.text_input("Email", value=user_data.get('email', '') if user_data else '')
        specialty = st.selectbox("Select Specialty", ["Cardiology", "Dermatology", "Neurology", "Pediatrics", "Orthopedics"])
        
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Choose Date", min_value=datetime.now().date())
        with col2:
            time = st.time_input("Choose Time")
        
        # Additional appointment details
        reason = st.text_area("Reason for Visit (Optional)", placeholder="Brief description of your symptoms or concerns")
        submit = st.form_submit_button("Book Appointment", use_container_width=True)

        if submit:
            if not name or not email:
                st.error("Please fill in your name and email")
            elif date < datetime.now().date():
                st.error("Please select a future date")
            else:
                # Prepare appointment data
                appointment_data = {
                    'name': name,
                    'email': email,
                    'specialty': specialty,
                    'date': str(date),
                    'time': str(time),
                    'reason': reason,
                    'status': 'confirmed'
                }
                
                # Save appointment
                if add_appointment(appointment_data):
                    st.success(f"✅ Appointment booked successfully!")
                    st.success(f"**Details:** {specialty} appointment on {date} at {time}")
                    st.info("You can view your appointments in the 'My Appointments' section.")
                else:
                    st.error("❌ Failed to book appointment. Please try again.")


