import streamlit as st
import pandas as pd
from modules.utilis import get_current_user_data, add_appointment, get_medical_specialists, get_medical_timeslots
from datetime import datetime, timedelta

def app():
    st.title("🗓️ Book Appointment")
    st.markdown("Schedule a visit with a specialist.")

    # Get current user data
    user_data = get_current_user_data()
    
    # Get specialists and timeslots from BigQuery
    specialists_data = get_medical_specialists()
    timeslots_data = get_medical_timeslots()
    
    if not specialists_data:
        st.warning("⚠️ No specialists available. Please ensure the specialists table is uploaded to BigQuery.")
        return
    
    # Extract unique specialties from BigQuery data
    specialties = list(set([spec.get('Specialty', 'Unknown') for spec in specialists_data]))
    specialties.sort()
    
    # --- Booking Form ---
    with st.form("appointment_form"):
        # Pre-fill with user data
        name = st.text_input("Your Name", value=st.session_state.username)
        email = st.text_input("Email", value=user_data.get('email', '') if user_data else '')
        
        # Dynamic specialty selection from BigQuery data
        specialty = st.selectbox("Select Specialty", specialties)
        
        # Show available specialists for selected specialty
        available_specialists = [spec for spec in specialists_data if spec.get('Specialty') == specialty]
        if available_specialists:
            st.subheader(f"👨‍⚕️ Available {specialty} Specialists")
            specialist_options = []
            for spec in available_specialists:
                specialist_name = f"Dr. {spec.get('FirstName', '')} {spec.get('LastName', '')}"
                specialist_info = f"{specialist_name} (Rating: {spec.get('Rating', 'N/A')}/5.0)"
                specialist_options.append(specialist_info)
            
            selected_specialist = st.selectbox("Choose Specialist", specialist_options)
            
            # Extract specialist details
            selected_spec = None
            for spec in available_specialists:
                specialist_name = f"Dr. {spec.get('FirstName', '')} {spec.get('LastName', '')}"
                if selected_specialist.startswith(specialist_name):
                    selected_spec = spec
                    break
        
        col1, col2 = st.columns(2)
        with col1:
            # Date selection with business days only
            min_date = datetime.now().date() + timedelta(days=1)
            max_date = min_date + timedelta(days=30)
            date = st.date_input("Choose Date", min_value=min_date, max_value=max_date)
        with col2:
            # Time selection from BigQuery timeslots
            if timeslots_data:
                time_options = []
                for slot in timeslots_data:
                    start_time = slot.get('StartTime', '')
                    end_time = slot.get('EndTime', '')
                    label = slot.get('Label', '')
                    if start_time and end_time:
                        time_options.append(f"{start_time} - {end_time} ({label})")
                
                if time_options:
                    selected_time = st.selectbox("Choose Time Slot", time_options)
                else:
                    selected_time = st.time_input("Choose Time")
            else:
                selected_time = st.time_input("Choose Time")
        
        # Additional appointment details
        reason = st.text_area("Reason for Visit (Optional)", placeholder="Brief description of your symptoms or concerns")
        
        # Emergency contact
        emergency_contact = st.text_input("Emergency Contact (Optional)", placeholder="Name and phone number")
        
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
                    'specialist_name': selected_specialist if 'selected_specialist' in locals() else f"{specialty} Specialist",
                    'date': str(date),
                    'time': str(selected_time),
                    'reason': reason,
                    'emergency_contact': emergency_contact,
                    'status': 'confirmed'
                }
                
                # Save appointment
                if add_appointment(appointment_data):
                    st.success(f"✅ Appointment booked successfully!")
                    st.success(f"**Details:** {specialty} appointment on {date} at {selected_time}")
                    st.success(f"**Specialist:** {selected_specialist if 'selected_specialist' in locals() else 'Assigned'}")
                    st.info("You can view your appointments in the 'My Appointments' section.")
                    
                    # Show next steps
                    st.subheader("📋 Next Steps")
                    st.info("""
                    1. **Confirmation Email**: You'll receive a confirmation email shortly
                    2. **Reminder**: We'll send you a reminder 24 hours before your appointment
                    3. **Preparation**: Please arrive 15 minutes early for check-in
                    4. **Cancellation**: You can cancel or reschedule up to 24 hours in advance
                    """)
                else:
                    st.error("❌ Failed to book appointment. Please try again.")
    
    # Show specialist information
    if available_specialists:
        st.divider()
        st.subheader("👨‍⚕️ Specialist Information")
        
        for spec in available_specialists:
            with st.expander(f"Dr. {spec.get('FirstName', '')} {spec.get('LastName', '')} - {spec.get('Specialty', '')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📞 Contact:** {spec.get('Contact', 'N/A')}")
                    st.write(f"**📧 Email:** {spec.get('Email', 'N/A')}")
                
                with col2:
                    rating = spec.get('Rating', 0)
                    st.write(f"**⭐ Rating:** {rating}/5.0")
                    if rating > 0:
                        st.progress(rating / 5.0)
                        st.caption(f"Patient satisfaction: {(rating/5.0)*100:.0f}%")


