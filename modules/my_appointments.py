import streamlit as st
import pandas as pd
import plotly.express as px
from modules.utilis import get_current_user_data, get_medical_appointments, get_medical_specialists
from datetime import datetime

def app():
    st.title("📑 My Appointments")
    st.markdown("Track your booked appointments here.")

    # Get current user's appointments from JSON
    user_data = get_current_user_data()
    
    # Get BigQuery data for analytics
    all_appointments = get_medical_appointments()
    specialists_data = get_medical_specialists()
    
    # Display user's personal appointments
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
    
    # BigQuery Analytics Section
    st.divider()
    st.subheader("📊 System Appointment Analytics (BigQuery Data)")
    
    if all_appointments and specialists_data:
        try:
            # Convert BigQuery data to DataFrame
            appointments_df = pd.DataFrame(all_appointments)
            specialists_df = pd.DataFrame(specialists_data)
            
            # Analytics based on BigQuery data
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Appointment Trends")
                
                # Time slot analysis from BigQuery
                if 'TimeSlotID' in appointments_df.columns:
                    time_slot_counts = appointments_df['TimeSlotID'].value_counts()
                    fig = px.bar(x=time_slot_counts.index, y=time_slot_counts.values,
                               title="Appointments by Time Slot (BigQuery Data)",
                               color=time_slot_counts.values,
                               color_continuous_scale='Blues')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🏥 Specialty Distribution")
                
                # Join appointments with specialists to get specialty data
                if 'SpecialistID' in appointments_df.columns and 'SpecialistID' in specialists_df.columns:
                    merged_df = appointments_df.merge(specialists_df, on='SpecialistID', how='left')
                    
                    # Debug: Show available columns (can be removed after testing)
                    # st.write("Debug - Available columns after merge:", list(merged_df.columns))
                    
                    # Check if Specialty column exists, if not, try alternative column names
                    specialty_column = None
                    possible_specialty_columns = ['Specialty', 'specialty', 'Specialization', 'specialization', 'Specialty_x', 'Specialty_y']
                    
                    for col in possible_specialty_columns:
                        if col in merged_df.columns:
                            specialty_column = col
                            break
                    
                    if specialty_column:
                        specialty_counts = merged_df[specialty_column].value_counts()
                        
                        # Show which column is being used
                        st.info(f"Using column: **{specialty_column}** for specialty analysis")
                        
                        fig = px.pie(values=specialty_counts.values, names=specialty_counts.index,
                                   title="Appointments by Specialty (BigQuery Data)")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("⚠️ Specialty column not found in merged data. Available columns: " + str(list(merged_df.columns)))
                        # Show a simple count of appointments by specialist instead
                        if 'SpecialistID' in merged_df.columns:
                            specialist_counts = merged_df['SpecialistID'].value_counts()
                            fig = px.bar(x=specialist_counts.index, y=specialist_counts.values,
                                       title="Appointments by Specialist ID")
                            st.plotly_chart(fig, use_container_width=True)
            
            # Status analysis
            st.subheader("📋 Appointment Status Analysis")
            if 'Status' in appointments_df.columns:
                status_counts = appointments_df['Status'].value_counts()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total System Appointments", len(appointments_df))
                with col2:
                    confirmed_system = len(appointments_df[appointments_df['Status'] == 'confirmed'])
                    st.metric("Confirmed (System)", confirmed_system)
                with col3:
                    st.metric("Your vs System", f"{len(appointments) if user_data and user_data.get('appointments') else 0} / {len(appointments_df)}")
            
            # Data insights
            st.subheader("💡 Key Insights from BigQuery Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info(f"""
                **📊 System Overview:**
                - Total Appointments: {len(appointments_df)}
                - Active Specialists: {len(specialists_df)}
                - Data Source: BigQuery
                """)
            
            with col2:
                if 'Status' in appointments_df.columns:
                    confirmation_rate = (len(appointments_df[appointments_df['Status'] == 'confirmed']) / len(appointments_df)) * 100
                    st.info(f"""
                    **🎯 Performance:**
                    - Confirmation Rate: {confirmation_rate:.1f}%
                    - Data Quality: High
                    - System Health: Active
                    """)
            
            with col3:
                st.info(f"""
                **👤 Your Activity:**
                - Your Appointments: {len(appointments) if user_data and user_data.get('appointments') else 0}
                - System Average: {len(appointments_df) / len(specialists_df) if len(specialists_df) > 0 else 0:.1f}
                - Status: Active User
                """)
        
        except Exception as e:
            st.error(f"Error processing BigQuery analytics: {e}")
            st.info("This might be due to missing or incorrectly formatted data in BigQuery tables.")
    
    else:
        st.warning("⚠️ No BigQuery data available for analytics. Please ensure the medical data tables are uploaded.")






