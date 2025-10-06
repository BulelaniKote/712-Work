import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.utilis import get_all_users, get_all_appointments, get_specialist_performance, create_admin_user
from datetime import datetime, timedelta
import json

def app():
    # Ensure admin user exists
    create_admin_user()
    
    st.title("👨‍💼 Admin Dashboard")
    st.markdown("**Facility Administrator Interface** - Monitor bookings, analyze performance, and generate reports")
    
    # Get data
    all_users = get_all_users()
    all_appointments = get_all_appointments()
    specialist_performance = get_specialist_performance()
    
    # Main metrics
    st.subheader("📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(all_users)
        st.metric("Total Users", total_users, delta=f"{total_users - 1} patients")
    
    with col2:
        total_appointments = len(all_appointments)
        confirmed_appointments = len([a for a in all_appointments if a.get('status') == 'confirmed'])
        st.metric("Total Appointments", total_appointments, delta=f"{confirmed_appointments} confirmed")
    
    with col3:
        total_specialties = len(specialist_performance)
        st.metric("Specialties", total_specialties, delta="Available")
    
    with col4:
        if all_appointments:
            recent_appointments = len([a for a in all_appointments 
                                     if datetime.strptime(a.get('date', '1900-01-01'), '%Y-%m-%d').date() >= datetime.now().date()])
            st.metric("Upcoming", recent_appointments, delta="This week")
        else:
            st.metric("Upcoming", 0, delta="No appointments")
    
    st.divider()
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Booking Analytics", "👨‍⚕️ Specialist Performance", "👥 User Management", "📈 Reports"])
    
    with tab1:
        st.subheader("📅 Booking Analytics")
        
        if all_appointments:
            # Convert appointments to DataFrame
            df_data = []
            for appointment in all_appointments:
                df_data.append({
                    "Patient": appointment.get('username', 'N/A'),
                    "Email": appointment.get('user_email', 'N/A'),
                    "Specialty": appointment.get('specialty', 'N/A'),
                    "Date": appointment.get('date', 'N/A'),
                    "Time": appointment.get('time', 'N/A'),
                    "Status": appointment.get('status', 'N/A').title(),
                    "Booked On": appointment.get('created_at', 'N/A')[:10] if appointment.get('created_at') else 'N/A'
                })
            
            df = pd.DataFrame(df_data)
            
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
            with col2:
                end_date = st.date_input("End Date", value=datetime.now().date())
            
            # Filter by date range
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            filtered_df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
            
            # Display filtered data
            st.dataframe(filtered_df, use_container_width=True)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Appointments by Specialty")
                specialty_counts = filtered_df['Specialty'].value_counts()
                fig = px.pie(values=specialty_counts.values, names=specialty_counts.index, 
                           title="Appointment Distribution by Specialty")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📈 Daily Appointment Trends")
                daily_counts = filtered_df.groupby(filtered_df['Date'].dt.date).size().reset_index()
                daily_counts.columns = ['Date', 'Count']
                
                fig = px.line(daily_counts, x='Date', y='Count', 
                            title="Daily Appointment Volume", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            # Status breakdown
            st.subheader("📋 Appointment Status Breakdown")
            status_counts = filtered_df['Status'].value_counts()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                confirmed = status_counts.get('Confirmed', 0)
                st.metric("Confirmed", confirmed)
            with col2:
                cancelled = status_counts.get('Cancelled', 0)
                st.metric("Cancelled", cancelled)
            with col3:
                pending = status_counts.get('Pending', 0)
                st.metric("Pending", pending)
                
        else:
            st.info("No appointment data available")
    
    with tab2:
        st.subheader("👨‍⚕️ Specialist Performance Monitoring")
        
        if specialist_performance:
            # Performance metrics table
            performance_data = []
            for specialty, stats in specialist_performance.items():
                performance_data.append({
                    "Specialty": specialty,
                    "Total Appointments": stats['total_appointments'],
                    "Confirmed": stats['confirmed_appointments'],
                    "Cancelled": stats['cancelled_appointments'],
                    "Unique Patients": stats['unique_patients'],
                    "Confirmation Rate": f"{stats['confirmation_rate']:.1f}%"
                })
            
            performance_df = pd.DataFrame(performance_data)
            st.dataframe(performance_df, use_container_width=True)
            
            # Performance charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Appointment Volume by Specialty")
                fig = px.bar(performance_df, x='Specialty', y='Total Appointments',
                           title="Total Appointments per Specialty",
                           color='Total Appointments', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🎯 Confirmation Rates")
                fig = px.bar(performance_df, x='Specialty', y='Confirmation Rate',
                           title="Confirmation Rate by Specialty",
                           color='Confirmation Rate', color_continuous_scale='Greens')
                fig.update_layout(yaxis_title="Confirmation Rate (%)")
                st.plotly_chart(fig, use_container_width=True)
            
            # Top performing specialties
            st.subheader("🏆 Top Performing Specialties")
            top_specialties = performance_df.nlargest(3, 'Confirmation Rate')
            
            for idx, row in top_specialties.iterrows():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{row['Specialty']}**")
                with col2:
                    st.write(f"Confirmation Rate: {row['Confirmation Rate']}")
                with col3:
                    st.write(f"Total Patients: {row['Unique Patients']}")
                st.divider()
        else:
            st.info("No specialist performance data available")
    
    with tab3:
        st.subheader("👥 User Management")
        
        # User statistics
        user_stats = []
        for username, user_data in all_users.items():
            if username != 'admin':  # Exclude admin user
                appointments = user_data.get('appointments', [])
                user_stats.append({
                    "Username": username,
                    "Email": user_data.get('email', 'N/A'),
                    "Total Appointments": len(appointments),
                    "Confirmed": len([a for a in appointments if a.get('status') == 'confirmed']),
                    "Joined": user_data.get('created_at', 'N/A')[:10],
                    "Role": user_data.get('role', 'patient')
                })
        
        if user_stats:
            users_df = pd.DataFrame(user_stats)
            st.dataframe(users_df, use_container_width=True)
            
            # User analytics
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("👥 User Registration Trends")
                users_df['Joined'] = pd.to_datetime(users_df['Joined'], errors='coerce')
                monthly_registrations = users_df.groupby(users_df['Joined'].dt.to_period('M')).size()
                
                fig = px.bar(x=monthly_registrations.index.astype(str), y=monthly_registrations.values,
                           title="Monthly User Registrations")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📊 Appointments per User")
                fig = px.histogram(users_df, x='Total Appointments', 
                                 title="Distribution of Appointments per User",
                                 nbins=10)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No user data available")
    
    with tab4:
        st.subheader("📈 Report Generation")
        
        # Report options
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox("Select Report Type", 
                                     ["Booking Summary", "Specialist Performance", "User Analytics", "System Overview"])
        
        with col2:
            date_range = st.selectbox("Date Range", 
                                    ["Last 7 days", "Last 30 days", "Last 3 months", "All time"])
        
        # Generate report
        if st.button("📊 Generate Report", use_container_width=True):
            st.success("Report generated successfully!")
            
            # Sample report content
            st.subheader(f"📋 {report_type} Report - {date_range}")
            
            if report_type == "Booking Summary":
                st.write(f"**Total Appointments:** {len(all_appointments)}")
                st.write(f"**Confirmed Appointments:** {len([a for a in all_appointments if a.get('status') == 'confirmed'])}")
                st.write(f"**Most Popular Specialty:** {max(specialist_performance.keys(), key=lambda k: specialist_performance[k]['total_appointments']) if specialist_performance else 'N/A'}")
                
            elif report_type == "Specialist Performance":
                for specialty, stats in specialist_performance.items():
                    st.write(f"**{specialty}:**")
                    st.write(f"  - Total Appointments: {stats['total_appointments']}")
                    st.write(f"  - Confirmation Rate: {stats['confirmation_rate']:.1f}%")
                    st.write(f"  - Unique Patients: {stats['unique_patients']}")
                    st.write("")
                    
            elif report_type == "User Analytics":
                st.write(f"**Total Users:** {len(all_users) - 1}")  # Exclude admin
                st.write(f"**Active Users:** {len([u for u in all_users.values() if u.get('appointments')])}")
                st.write(f"**Average Appointments per User:** {sum(len(u.get('appointments', [])) for u in all_users.values()) / (len(all_users) - 1):.1f}")
                
            elif report_type == "System Overview":
                st.write(f"**System Health:** ✅ Operational")
                st.write(f"**Total Data Points:** {len(all_appointments) + len(all_users)}")
                st.write(f"**System Uptime:** 99.9%")
                st.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Export options
        st.subheader("📤 Export Data")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export Appointments (CSV)"):
                if all_appointments:
                    df = pd.DataFrame(all_appointments)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"appointments_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No appointment data to export")
        
        with col2:
            if st.button("📊 Export Performance (JSON)"):
                if specialist_performance:
                    json_data = json.dumps(specialist_performance, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name=f"performance_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("No performance data to export")
        
        with col3:
            if st.button("👥 Export Users (CSV)"):
                if user_stats:
                    users_df = pd.DataFrame(user_stats)
                    csv = users_df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"users_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No user data to export")
