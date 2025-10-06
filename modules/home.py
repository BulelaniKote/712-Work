import streamlit as st
import pandas as pd
import plotly.express as px
from modules.utilis import get_current_user_data
from datetime import datetime

def app():
    st.title("🏥 Medical Booking System")
    
    # Get user data
    user_data = get_current_user_data()
    username = st.session_state.username
    
    st.markdown(f"Welcome back, **{username}**! 👋")
    st.markdown("Your one-stop platform for booking medical specialists!")

    # --- USER METRICS ---
    user_appointments = user_data.get('appointments', []) if user_data else []
    upcoming_appointments = [a for a in user_appointments 
                           if pd.to_datetime(a.get('date', '1900-01-01'), errors='coerce').date() >= datetime.now().date()]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👨‍⚕️ Specialists", "50+", delta="Available")
    with col2:
        st.metric("📅 Your Appointments", len(user_appointments), delta=f"{len(upcoming_appointments)} upcoming")
    with col3:
        st.metric("🗓️ System Total", "200+", delta="This Month")
    with col4:
        st.metric("😊 Active Users", "100+", delta="Online")
    
    st.divider()

    # --- QUICK ACTIONS ---
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📅 Book New Appointment", use_container_width=True):
            st.info("👆 Use the navigation menu on the left to access 'Book Appointment'")
    
    with col2:
        if st.button("👨‍⚕️ Browse Specialists", use_container_width=True):
            st.info("👆 Use the navigation menu on the left to access 'Specialists'")
    
    with col3:
        if st.button("📑 View My Appointments", use_container_width=True):
            st.info("👆 Use the navigation menu on the left to access 'My Appointments'")

    # --- UPCOMING APPOINTMENTS ---
    if upcoming_appointments:
        st.subheader("📋 Your Upcoming Appointments")
        upcoming_df_data = []
        for appointment in upcoming_appointments[:3]:  # Show next 3
            upcoming_df_data.append({
                "Date": appointment.get('date', 'N/A'),
                "Time": appointment.get('time', 'N/A'),
                "Specialty": appointment.get('specialty', 'N/A'),
                "Status": appointment.get('status', 'N/A').title()
            })
        
        if upcoming_df_data:
            upcoming_df = pd.DataFrame(upcoming_df_data)
            st.dataframe(upcoming_df, use_container_width=True)
    
    st.divider()

    # --- APPOINTMENTS TREND CHART ---
    df = pd.DataFrame({
        "Date": pd.date_range(start="2025-10-01", periods=7),
        "Appointments": [5, 10, 8, 12, 15, 7, 9]
    })

    st.subheader("📈 System Appointments Trend")
    fig = px.line(df, x="Date", y="Appointments", markers=True, 
                  title="Weekly Appointments Trend", 
                  color_discrete_sequence=["#2E86DE"])
    st.plotly_chart(fig, use_container_width=True)




