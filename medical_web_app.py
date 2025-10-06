# -*- coding: utf-8 -*-
"""
Medical Facility Web Application
================================

A professional web application that reads medical data from BigQuery
and presents comprehensive healthcare analytics and insights.

Run populate_medical_bigquery.py FIRST to create and populate the database.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import altair as alt
from google.cloud import bigquery
from google.oauth2 import service_account

# Page configuration
st.set_page_config(
    page_title="Medical Facility Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional medical theme
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 2rem;
        color: #228B22;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #f0f8f0 0%, #e8f5e8 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #2E8B57;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .insight-box {
        background: linear-gradient(135deg, #e8f4fd 0%, #d1ecf1 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #17a2b8;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .medical-card {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #2E8B57;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f0f8f0 0%, #e8f5e8 100%);
    }
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# BigQuery connection setup
@st.cache_resource
def get_bigquery_client():
    """Initialize BigQuery client with service account credentials from Streamlit secrets"""
    try:
        # Always use Streamlit secrets (both local and deployed)
        if 'gcp_service_account' in st.secrets:
            try:
                # Create credentials from secrets
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                
                client = bigquery.Client(
                    credentials=credentials,
                    project=credentials.project_id
                )
                
                return client, credentials.project_id
                
            except Exception as e:
                st.error(f"❌ Error creating BigQuery client from secrets: {e}")
                st.info("💡 Please check your Streamlit Cloud secrets configuration")
                return None, None
                
        else:
            st.error("❌ BigQuery credentials not found in Streamlit secrets")
            st.info("💡 Please add your GCP service account credentials to Streamlit Cloud secrets")
            return None, None
            
    except Exception as e:
        st.error(f"❌ Error connecting to BigQuery: {e}")
        return None, None

# Data loading functions
@st.cache_data
def load_overview_data(client, project_id):
    """Load overview metrics from BigQuery"""
    query = f"""
    SELECT 
        (SELECT COUNT(*) FROM `{project_id}.medical_facility.patients`) as total_patients,
        (SELECT COUNT(*) FROM `{project_id}.medical_facility.doctors`) as total_doctors,
        (SELECT COUNT(*) FROM `{project_id}.medical_facility.departments`) as total_departments,
        (SELECT COUNT(*) FROM `{project_id}.medical_facility.treatments`) as total_treatments,
        COUNT(*) as total_visits,
        ROUND(SUM(treatment_cost), 2) as total_revenue,
        ROUND(AVG(patient_satisfaction), 1) as avg_satisfaction,
        ROUND(AVG(length_of_stay_hours), 1) as avg_length_of_stay,
        ROUND(AVG(CASE WHEN readmission_30_days THEN 1 ELSE 0 END) * 100, 1) as readmission_rate,
        ROUND(AVG(CASE WHEN complications THEN 1 ELSE 0 END) * 100, 1) as complication_rate
    FROM `{project_id}.medical_facility.visits`
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_department_performance(client, project_id):
    """Load department performance data"""
    query = f"""
    SELECT 
        d.dept_name,
        d.location,
        d.capacity,
        COUNT(v.visit_id) as total_visits,
        ROUND(SUM(v.treatment_cost), 2) as total_revenue,
        ROUND(AVG(v.patient_satisfaction), 1) as avg_satisfaction,
        ROUND(AVG(v.length_of_stay_hours), 1) as avg_length_of_stay,
        ROUND(COUNT(v.visit_id) * 100.0 / d.capacity, 1) as utilization_rate
    FROM `{project_id}.medical_facility.departments` d
    LEFT JOIN `{project_id}.medical_facility.visits` v ON d.dept_id = v.dept_id
    GROUP BY d.dept_name, d.location, d.capacity
    ORDER BY total_revenue DESC
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_doctor_performance(client, project_id):
    """Load doctor performance data"""
    query = f"""
    SELECT 
        doc.doctor_name,
        doc.specialty,
        doc.years_experience,
        COUNT(v.visit_id) as total_visits,
        ROUND(AVG(v.patient_satisfaction), 1) as avg_satisfaction,
        ROUND(SUM(v.treatment_cost), 2) as total_revenue,
        ROUND(AVG(CASE WHEN v.readmission_30_days THEN 1 ELSE 0 END) * 100, 1) as readmission_rate
    FROM `{project_id}.medical_facility.doctors` doc
    LEFT JOIN `{project_id}.medical_facility.visits` v ON doc.doctor_id = v.doctor_id
    GROUP BY doc.doctor_name, doc.specialty, doc.years_experience
    HAVING total_visits > 0
    ORDER BY total_visits DESC
    LIMIT 20
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_patient_demographics(client, project_id):
    """Load patient demographics data"""
    query = f"""
    SELECT 
        p.gender,
        p.insurance_provider,
        COUNT(DISTINCT p.patient_id) as patient_count,
        COUNT(v.visit_id) as total_visits,
        ROUND(AVG(v.treatment_cost), 2) as avg_treatment_cost,
        ROUND(SUM(v.treatment_cost), 2) as total_revenue
    FROM `{project_id}.medical_facility.patients` p
    LEFT JOIN `{project_id}.medical_facility.visits` v ON p.patient_id = v.patient_id
    GROUP BY p.gender, p.insurance_provider
    ORDER BY total_revenue DESC
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_treatment_analysis(client, project_id):
    """Load treatment analysis data"""
    query = f"""
    SELECT 
        t.treatment_type,
        COUNT(v.visit_id) as frequency,
        ROUND(AVG(t.cost), 2) as avg_base_cost,
        ROUND(AVG(v.treatment_cost), 2) as avg_actual_cost,
        ROUND(SUM(v.treatment_cost), 2) as total_revenue,
        ROUND(AVG(v.patient_satisfaction), 1) as avg_satisfaction,
        ROUND(AVG(CASE WHEN v.complications THEN 1 ELSE 0 END) * 100, 1) as complication_rate
    FROM `{project_id}.medical_facility.treatments` t
    JOIN `{project_id}.medical_facility.visits` v ON t.treatment_id = v.treatment_id
    GROUP BY t.treatment_type
    ORDER BY frequency DESC
    """
    return client.query(query).to_dataframe()

@st.cache_data
def load_monthly_trends(client, project_id):
    """Load monthly trends data"""
    query = f"""
    SELECT 
        EXTRACT(YEAR FROM visit_date) as year,
        EXTRACT(MONTH FROM visit_date) as month,
        COUNT(*) as visit_count,
        ROUND(SUM(treatment_cost), 2) as monthly_revenue,
        ROUND(AVG(patient_satisfaction), 1) as avg_satisfaction
    FROM `{project_id}.medical_facility.visits`
    GROUP BY year, month
    ORDER BY year, month
    """
    return client.query(query).to_dataframe()

# Main application
def main():
    # Title and header
    st.markdown('<h1 class="main-header">🏥 Medical Facility Analytics Portal</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏥 Navigation")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Choose Analytics Page:",
        ["🏠 Executive Dashboard", "🏥 Department Performance", "👨‍⚕️ Doctor Analytics", 
         "👥 Patient Insights", "💊 Treatment Analysis", "📈 Financial Overview", 
         "📊 Operational Metrics", "🔍 Custom Queries"]
    )
    
    # Get BigQuery client
    client, project_id = get_bigquery_client()
    
    if client is None:
        st.markdown('<div class="warning-box">⚠️ <strong>Database Connection Required</strong><br>Please configure your BigQuery credentials to access the medical facility data.</div>', unsafe_allow_html=True)
        st.stop()
    
    # Check if medical facility data exists
    try:
        table_ref = f"{project_id}.medical_facility.visits"
        table = client.get_table(table_ref)
        st.sidebar.success(f"✅ Connected to Medical DB")
        st.sidebar.info(f"📊 {table.num_rows:,} visits recorded")
    except Exception as e:
        st.markdown('<div class="warning-box">⚠️ <strong>Medical Database Not Found</strong><br>Please run <code>populate_medical_bigquery.py</code> first to create and populate the medical facility database.</div>', unsafe_allow_html=True)
        st.code("python populate_medical_bigquery.py", language="bash")
        st.stop()
    
    # Executive Dashboard
    if page == "🏠 Executive Dashboard":
        st.markdown('<h2 class="sub-header">📊 Executive Dashboard</h2>', unsafe_allow_html=True)
        
        # Load overview data
        overview_data = load_overview_data(client, project_id)
        overview = overview_data.iloc[0]
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Patients", f"{overview['total_patients']:,}")
            st.metric("Total Visits", f"{overview['total_visits']:,}")
        
        with col2:
            st.metric("Total Revenue", f"${overview['total_revenue']:,.0f}")
            st.metric("Avg Satisfaction", f"{overview['avg_satisfaction']}/10")
        
        with col3:
            st.metric("Readmission Rate", f"{overview['readmission_rate']}%")
            st.metric("Complication Rate", f"{overview['complication_rate']}%")
        
        with col4:
            st.metric("Total Doctors", f"{overview['total_doctors']:,}")
            st.metric("Avg Length of Stay", f"{overview['avg_length_of_stay']:.1f} hrs")
        
        # Department overview
        st.markdown("---")
        st.markdown('<h3 class="sub-header">🏥 Department Performance Overview</h3>', unsafe_allow_html=True)
        
        dept_data = load_department_performance(client, project_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by department
            fig = px.bar(dept_data, x='dept_name', y='total_revenue',
                        title="Revenue by Department",
                        color='avg_satisfaction',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Department utilization
            fig = px.bar(dept_data, x='dept_name', y='utilization_rate',
                        title="Department Utilization Rate (%)",
                        color='utilization_rate',
                        color_continuous_scale='Viridis')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Monthly trends
        st.markdown("---")
        st.markdown('<h3 class="sub-header">📈 Monthly Trends</h3>', unsafe_allow_html=True)
        
        monthly_data = load_monthly_trends(client, project_id)
        monthly_data['date'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))
        
        fig = px.line(monthly_data, x='date', y='monthly_revenue',
                     title="Monthly Revenue Trends", markers=True)
        fig.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Department Performance
    elif page == "🏥 Department Performance":
        st.markdown('<h2 class="sub-header">🏥 Department Performance Analysis</h2>', unsafe_allow_html=True)
        
        dept_data = load_department_performance(client, project_id)
        
        # Department metrics table
        st.markdown("### 📊 Department Metrics")
        st.dataframe(dept_data, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Satisfaction vs Utilization scatter
            fig = px.scatter(dept_data, x='utilization_rate', y='avg_satisfaction',
                           size='total_revenue', color='dept_name',
                           title="Department Efficiency: Satisfaction vs Utilization")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue distribution pie chart
            fig = px.pie(dept_data, values='total_revenue', names='dept_name',
                        title="Revenue Distribution by Department")
            st.plotly_chart(fig, use_container_width=True)
    
    # Doctor Analytics
    elif page == "👨‍⚕️ Doctor Analytics":
        st.markdown('<h2 class="sub-header">👨‍⚕️ Doctor Performance Analytics</h2>', unsafe_allow_html=True)
        
        doctor_data = load_doctor_performance(client, project_id)
        
        # Top performers
        st.markdown("### 🏆 Top 20 Doctors by Patient Volume")
        st.dataframe(doctor_data, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Experience vs Satisfaction
            fig = px.scatter(doctor_data, x='years_experience', y='avg_satisfaction',
                           size='total_visits', color='specialty',
                           title="Doctor Performance: Experience vs Satisfaction")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Specialty performance
            specialty_data = doctor_data.groupby('specialty').agg({
                'total_visits': 'sum',
                'avg_satisfaction': 'mean',
                'total_revenue': 'sum'
            }).reset_index()
            
            fig = px.bar(specialty_data, x='specialty', y='total_visits',
                        title="Visits by Medical Specialty",
                        color='avg_satisfaction',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Patient Insights
    elif page == "👥 Patient Insights":
        st.markdown('<h2 class="sub-header">👥 Patient Demographics & Insights</h2>', unsafe_allow_html=True)
        
        patient_data = load_patient_demographics(client, project_id)
        
        # Demographics analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Gender analysis
            gender_data = patient_data.groupby('gender').agg({
                'patient_count': 'sum',
                'total_visits': 'sum',
                'total_revenue': 'sum'
            }).reset_index()
            
            fig = px.pie(gender_data, values='total_revenue', names='gender',
                        title="Revenue Distribution by Gender")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Insurance analysis
            insurance_data = patient_data.groupby('insurance_provider').agg({
                'patient_count': 'sum',
                'total_revenue': 'sum'
            }).reset_index().sort_values('total_revenue', ascending=False)
            
            fig = px.bar(insurance_data, x='insurance_provider', y='total_revenue',
                        title="Revenue by Insurance Provider")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed patient data
        st.markdown("### 📊 Patient Demographics Data")
        st.dataframe(patient_data, use_container_width=True)
    
    # Treatment Analysis
    elif page == "💊 Treatment Analysis":
        st.markdown('<h2 class="sub-header">💊 Treatment Analysis & Outcomes</h2>', unsafe_allow_html=True)
        
        treatment_data = load_treatment_analysis(client, project_id)
        
        # Treatment metrics
        st.markdown("### 📊 Treatment Performance Metrics")
        st.dataframe(treatment_data, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Treatment frequency
            fig = px.bar(treatment_data, x='treatment_type', y='frequency',
                        title="Treatment Frequency by Type",
                        color='avg_satisfaction',
                        color_continuous_scale='RdYlGn')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cost vs Satisfaction
            fig = px.scatter(treatment_data, x='avg_actual_cost', y='avg_satisfaction',
                           size='frequency', color='treatment_type',
                           title="Treatment Cost vs Patient Satisfaction")
            st.plotly_chart(fig, use_container_width=True)
    
    # Custom Queries
    elif page == "🔍 Custom Queries":
        st.markdown('<h2 class="sub-header">🔍 Custom SQL Queries</h2>', unsafe_allow_html=True)
        
        st.markdown("### 💡 Write your own SQL queries against the medical facility database")
        
        # Sample queries
        sample_queries = {
            "Patient Age Analysis": f"""
            SELECT 
                CASE 
                    WHEN age_at_visit < 18 THEN 'Pediatric'
                    WHEN age_at_visit BETWEEN 18 AND 65 THEN 'Adult'
                    ELSE 'Senior'
                END as age_group,
                COUNT(*) as visit_count,
                ROUND(AVG(patient_satisfaction), 1) as avg_satisfaction,
                ROUND(SUM(treatment_cost), 2) as total_revenue
            FROM `{project_id}.medical_facility.visits`
            GROUP BY age_group
            ORDER BY visit_count DESC
            """,
            
            "High-Risk Patients": f"""
            SELECT 
                p.patient_name,
                p.insurance_provider,
                COUNT(v.visit_id) as visit_count,
                SUM(CASE WHEN v.complications THEN 1 ELSE 0 END) as complications,
                SUM(CASE WHEN v.readmission_30_days THEN 1 ELSE 0 END) as readmissions
            FROM `{project_id}.medical_facility.patients` p
            JOIN `{project_id}.medical_facility.visits` v ON p.patient_id = v.patient_id
            GROUP BY p.patient_name, p.insurance_provider
            HAVING visit_count > 5 OR complications > 0 OR readmissions > 0
            ORDER BY visit_count DESC, complications DESC
            """,
            
            "Department Efficiency": f"""
            SELECT 
                d.dept_name,
                COUNT(v.visit_id) as total_visits,
                ROUND(AVG(v.length_of_stay_hours), 1) as avg_stay_hours,
                ROUND(AVG(v.treatment_cost), 2) as avg_cost,
                ROUND(COUNT(v.visit_id) * 100.0 / d.capacity, 1) as utilization_rate
            FROM `{project_id}.medical_facility.departments` d
            LEFT JOIN `{project_id}.medical_facility.visits` v ON d.dept_id = v.dept_id
            GROUP BY d.dept_name, d.capacity
            ORDER BY utilization_rate DESC
            """
        }
        
        selected_query = st.selectbox("Choose a sample query:", list(sample_queries.keys()))
        
        query = st.text_area("SQL Query:", value=sample_queries[selected_query], height=200)
        
        if st.button("🚀 Execute Query", type="primary"):
            if query.strip():
                with st.spinner("Executing query..."):
                    try:
                        results_df = client.query(query).to_dataframe()
                        
                        st.success(f"✅ Query executed successfully! Returned {len(results_df)} rows")
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Download option
                        if len(results_df) > 0:
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results as CSV",
                                data=csv,
                                file_name="query_results.csv",
                                mime="text/csv"
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Query execution failed: {e}")
            else:
                st.warning("⚠️ Please enter a SQL query")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><strong>🏥 Medical Facility Analytics Portal</strong></p>
        <p>Powered by BigQuery Star Schema | Built with Streamlit & Faker</p>
        <p><small>Professional healthcare analytics with synthetic medical data</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
