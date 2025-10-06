import streamlit as st
import pandas as pd
from modules.utilis import get_current_user_data
from datetime import datetime

def app():
    st.title("📑 My Appointments")
    st.markdown("Track your booked appointments here.")

    # Get current user's appointments
    user_data = get_current_user_data()
    
    if user_data and user_data.get('appointments'):
        appointments = user_data['appointments']
        
        if appointments:
            # Convert appointments to DataFrame
            df_data = []
            for appointment in appointments:
                df_data.append({
                    "Date": appointment.get('date', 'N/A'),
                    "Time": appointment.get('time', 'N/A'),
                    "Specialty": appointment.get('specialty', 'N/A'),
                    "Status": appointment.get('status', 'N/A').title(),
                    "Reason": appointment.get('reason', 'N/A')[:50] + "..." if len(appointment.get('reason', '')) > 50 else appointment.get('reason', 'N/A'),
                    "Booked On": appointment.get('created_at', 'N/A')[:10] if appointment.get('created_at') else 'N/A'
                })
            
            df = pd.DataFrame(df_data)
            
            # Sort by date
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.sort_values('Date', ascending=True)
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            # Display appointments
            st.dataframe(df, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Appointments", len(appointments))
            with col2:
                confirmed_count = len([a for a in appointments if a.get('status') == 'confirmed'])
                st.metric("Confirmed", confirmed_count)
            with col3:
                upcoming_count = len([a for a in appointments 
                                     if pd.to_datetime(a.get('date', '1900-01-01'), errors='coerce').date() >= datetime.now().date()])
                st.metric("Upcoming", upcoming_count)
        else:
            st.info("📅 You haven't booked any appointments yet.")
            st.markdown("Visit the [Book Appointment](/Book_Appointment) page to schedule your first visit!")
    else:
        st.info("📅 You haven't booked any appointments yet.")
        st.markdown("Visit the [Book Appointment](/Book_Appointment) page to schedule your first visit!")






