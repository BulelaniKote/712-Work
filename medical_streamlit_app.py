# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import sqlite3
import io
import altair as alt

# Initialize Faker
fake = Faker()

# Page configuration
st.set_page_config(
    page_title="Medical Facility Analysis Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f8f0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .medical-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.8rem;
        border: 2px solid #2E8B57;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Star Schema Data Generation Functions
@st.cache_data
def create_star_schema_data():
    """Create a comprehensive star schema for medical facility data"""
    
    # Set seed for reproducible data
    Faker.seed(42)
    random.seed(42)
    np.random.seed(42)
    
    # Dimension Tables
    
    # 1. Patient Dimension
    patients = []
    for i in range(1, 1001):  # 1000 patients
        patient = {
            'patient_id': i,
            'patient_name': fake.name(),
            'date_of_birth': fake.date_of_birth(minimum_age=0, maximum_age=90),
            'gender': random.choice(['Male', 'Female', 'Other']),
            'phone': fake.phone_number(),
            'email': fake.email(),
            'address': fake.address().replace('\n', ', '),
            'emergency_contact': fake.name(),
            'emergency_phone': fake.phone_number(),
            'insurance_provider': random.choice(['HealthCare Plus', 'MediCare', 'BlueCross', 'Aetna', 'Cigna', 'Uninsured']),
            'blood_type': random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
            'allergies': random.choice(['None', 'Penicillin', 'Peanuts', 'Shellfish', 'Latex', 'Multiple'])
        }
        patients.append(patient)
    
    # 2. Doctor Dimension
    doctors = []
    specialties = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology', 
                  'Psychiatry', 'Oncology', 'Radiology', 'Emergency Medicine', 'Internal Medicine',
                  'Surgery', 'Anesthesiology', 'Pathology', 'Gynecology', 'Urology']
    
    for i in range(1, 101):  # 100 doctors
        doctor = {
            'doctor_id': i,
            'doctor_name': f"Dr. {fake.name()}",
            'specialty': random.choice(specialties),
            'years_experience': random.randint(1, 35),
            'education': f"{fake.company()} Medical School",
            'license_number': f"MD{random.randint(100000, 999999)}",
            'phone': fake.phone_number(),
            'email': fake.email(),
            'department': random.choice(['Emergency', 'ICU', 'Surgery', 'Outpatient', 'Pediatrics', 'Maternity']),
            'shift': random.choice(['Day', 'Night', 'Rotating'])
        }
        doctors.append(doctor)
    
    # 3. Department Dimension
    departments = [
        {'dept_id': 1, 'dept_name': 'Emergency', 'location': 'Ground Floor', 'head_doctor': 'Dr. Smith', 'capacity': 50},
        {'dept_id': 2, 'dept_name': 'ICU', 'location': '3rd Floor', 'head_doctor': 'Dr. Johnson', 'capacity': 30},
        {'dept_id': 3, 'dept_name': 'Surgery', 'location': '2nd Floor', 'head_doctor': 'Dr. Williams', 'capacity': 20},
        {'dept_id': 4, 'dept_name': 'Outpatient', 'location': '1st Floor', 'head_doctor': 'Dr. Brown', 'capacity': 100},
        {'dept_id': 5, 'dept_name': 'Pediatrics', 'location': '4th Floor', 'head_doctor': 'Dr. Davis', 'capacity': 40},
        {'dept_id': 6, 'dept_name': 'Maternity', 'location': '5th Floor', 'head_doctor': 'Dr. Miller', 'capacity': 25},
        {'dept_id': 7, 'dept_name': 'Radiology', 'location': 'Basement', 'head_doctor': 'Dr. Wilson', 'capacity': 15},
        {'dept_id': 8, 'dept_name': 'Laboratory', 'location': 'Basement', 'head_doctor': 'Dr. Moore', 'capacity': 10}
    ]
    
    # 4. Treatment Dimension
    treatments = []
    treatment_types = ['Consultation', 'Surgery', 'Diagnostic Test', 'Therapy', 'Vaccination', 
                      'Emergency Care', 'Preventive Care', 'Rehabilitation', 'Medication', 'Monitoring']
    
    for i in range(1, 201):  # 200 treatment types
        treatment = {
            'treatment_id': i,
            'treatment_name': f"{random.choice(treatment_types)} - {fake.word().title()}",
            'treatment_type': random.choice(treatment_types),
            'duration_minutes': random.randint(15, 480),
            'cost': round(random.uniform(50, 5000), 2),
            'requires_admission': random.choice([True, False]),
            'equipment_needed': random.choice(['None', 'X-Ray', 'MRI', 'CT Scan', 'Ultrasound', 'ECG', 'Blood Test'])
        }
        treatments.append(treatment)
    
    # 5. Date Dimension
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = []
    
    current_date = start_date
    date_id = 1
    while current_date <= end_date:
        date_record = {
            'date_id': date_id,
            'full_date': current_date,
            'year': current_date.year,
            'month': current_date.month,
            'day': current_date.day,
            'quarter': (current_date.month - 1) // 3 + 1,
            'day_of_week': current_date.strftime('%A'),
            'month_name': current_date.strftime('%B'),
            'is_weekend': current_date.weekday() >= 5,
            'is_holiday': random.choice([True, False]) if random.random() < 0.05 else False
        }
        dates.append(date_record)
        current_date += timedelta(days=1)
        date_id += 1
    
    # Fact Table - Medical Visits
    visits = []
    visit_id = 1
    
    for _ in range(5000):  # 5000 medical visits
        # Random selections from dimensions
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        department = random.choice(departments)
        treatment = random.choice(treatments)
        date_record = random.choice(dates)
        
        # Calculate age at visit
        age_at_visit = date_record['full_date'].year - patient['date_of_birth'].year
        if date_record['full_date'].month < patient['date_of_birth'].month or \
           (date_record['full_date'].month == patient['date_of_birth'].month and 
            date_record['full_date'].day < patient['date_of_birth'].day):
            age_at_visit -= 1
        
        visit = {
            'visit_id': visit_id,
            'patient_id': patient['patient_id'],
            'doctor_id': doctor['doctor_id'],
            'dept_id': department['dept_id'],
            'treatment_id': treatment['treatment_id'],
            'date_id': date_record['date_id'],
            'visit_date': date_record['full_date'],
            'admission_time': fake.time(),
            'discharge_time': fake.time(),
            'visit_type': random.choice(['Emergency', 'Scheduled', 'Follow-up', 'Walk-in']),
            'diagnosis': fake.sentence(nb_words=4),
            'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
            'treatment_cost': treatment['cost'] * random.uniform(0.8, 1.5),
            'insurance_covered': random.uniform(0, 1) * treatment['cost'],
            'patient_satisfaction': random.randint(1, 10),
            'length_of_stay_hours': random.randint(1, 168) if treatment['requires_admission'] else random.randint(1, 8),
            'readmission_30_days': random.choice([True, False]) if random.random() < 0.1 else False,
            'complications': random.choice([True, False]) if random.random() < 0.05 else False,
            'age_at_visit': age_at_visit
        }
        visits.append(visit)
        visit_id += 1
    
    return {
        'patients': pd.DataFrame(patients),
        'doctors': pd.DataFrame(doctors),
        'departments': pd.DataFrame(departments),
        'treatments': pd.DataFrame(treatments),
        'dates': pd.DataFrame(dates),
        'visits': pd.DataFrame(visits)
    }

# Load data
@st.cache_data
def load_medical_data():
    """Load and cache the medical data"""
    return create_star_schema_data()

# Title and header
st.markdown('<h1 class="main-header">🏥 Medical Facility Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏥 Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🏠 Home", "📊 Star Schema Overview", "👥 Patient Analytics", "👨‍⚕️ Doctor Performance", 
     "🏥 Department Analysis", "💊 Treatment Insights", "📈 Financial Analysis", "📋 About"]
)

# Load data
data = load_medical_data()

# Home page
if page == "🏠 Home":
    st.markdown("## 🎯 Medical Facility Data Analysis")
    st.markdown("**Data Source:** Synthetic medical data generated using Faker library")
    st.markdown("**Architecture:** Star Schema with dimension and fact tables")
    
    # Data Overview
    st.markdown("---")
    st.subheader("📋 Dataset Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Patients", f"{len(data['patients']):,}")
        st.metric("Total Doctors", f"{len(data['doctors']):,}")
    
    with col2:
        st.metric("Total Visits", f"{len(data['visits']):,}")
        st.metric("Departments", f"{len(data['departments']):,}")
    
    with col3:
        st.metric("Treatment Types", f"{len(data['treatments']):,}")
        st.metric("Date Range", f"{len(data['dates']):,} days")
    
    # Key Metrics
    st.markdown("---")
    st.subheader("🎯 Key Performance Metrics")
    
    # Calculate key metrics
    total_revenue = data['visits']['treatment_cost'].sum()
    avg_satisfaction = data['visits']['patient_satisfaction'].mean()
    readmission_rate = (data['visits']['readmission_30_days'].sum() / len(data['visits'])) * 100
    avg_los = data['visits']['length_of_stay_hours'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Avg Patient Satisfaction", f"{avg_satisfaction:.1f}/10")
    with col3:
        st.metric("Readmission Rate", f"{readmission_rate:.1f}%")
    with col4:
        st.metric("Avg Length of Stay", f"{avg_los:.1f} hours")
    
    # Analysis Objectives
    st.markdown("---")
    st.subheader("🎯 Analysis Objectives")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Data Architecture:**
        - Star schema with 5 dimension tables
        - 1 central fact table (medical visits)
        - Comprehensive patient journey tracking
        - Financial and operational metrics
        
        **🔍 Patient Analytics:**
        - Demographics and health patterns
        - Visit frequency and trends
        - Satisfaction and outcomes analysis
        - Insurance and payment patterns
        """)
    
    with col2:
        st.markdown("""
        **👨‍⚕️ Healthcare Operations:**
        - Doctor performance and specialization
        - Department efficiency analysis
        - Treatment effectiveness tracking
        - Resource utilization optimization
        
        **💡 Business Intelligence:**
        - Revenue optimization opportunities
        - Quality improvement insights
        - Operational efficiency metrics
        - Predictive healthcare analytics
        """)

# Star Schema Overview page
elif page == "📊 Star Schema Overview":
    st.header("📊 Star Schema Architecture")
    
    st.markdown("""
    ## 🏗️ Data Architecture Overview
    
    This medical facility database follows a **star schema** design pattern, optimized for analytical queries 
    and business intelligence reporting. The schema consists of dimension tables surrounding a central fact table.
    """)
    
    # Schema diagram description
    st.markdown("---")
    st.subheader("🌟 Star Schema Components")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 📋 Dimension Tables
        
        **1. Patient Dimension**
        - Patient demographics and personal info
        - Insurance and contact details
        - Medical history indicators
        
        **2. Doctor Dimension**
        - Doctor profiles and specializations
        - Experience and credentials
        - Department assignments
        
        **3. Department Dimension**
        - Hospital departments and locations
        - Capacity and management info
        - Operational details
        
        **4. Treatment Dimension**
        - Treatment types and procedures
        - Costs and duration
        - Equipment requirements
        
        **5. Date Dimension**
        - Time-based attributes
        - Calendar hierarchies
        - Holiday and weekend flags
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 Fact Table
        
        **Medical Visits Fact Table**
        - Central table connecting all dimensions
        - Contains measurable business metrics
        - Tracks patient visits and outcomes
        
        **Key Metrics:**
        - Treatment costs and insurance coverage
        - Patient satisfaction scores
        - Length of stay and readmission rates
        - Visit types and severity levels
        - Complications and outcomes
        
        **Benefits:**
        - Fast analytical queries
        - Easy to understand structure
        - Optimized for reporting
        - Scalable design
        """)
    
    # Table details
    st.markdown("---")
    st.subheader("📊 Table Statistics")
    
    # Create table statistics
    table_stats = pd.DataFrame({
        'Table Name': ['Patients', 'Doctors', 'Departments', 'Treatments', 'Dates', 'Visits (Fact)'],
        'Record Count': [len(data['patients']), len(data['doctors']), len(data['departments']), 
                        len(data['treatments']), len(data['dates']), len(data['visits'])],
        'Columns': [len(data['patients'].columns), len(data['doctors'].columns), 
                   len(data['departments'].columns), len(data['treatments'].columns),
                   len(data['dates'].columns), len(data['visits'].columns)],
        'Table Type': ['Dimension', 'Dimension', 'Dimension', 'Dimension', 'Dimension', 'Fact']
    })
    
    st.dataframe(table_stats, use_container_width=True)
    
    # Sample data from each table
    st.markdown("---")
    st.subheader("📋 Sample Data Preview")
    
    table_choice = st.selectbox("Select table to preview:", 
                               ['Patients', 'Doctors', 'Departments', 'Treatments', 'Dates', 'Visits'])
    
    if table_choice == 'Patients':
        st.write("**Patient Dimension Sample:**")
        st.dataframe(data['patients'].head(10), use_container_width=True)
    elif table_choice == 'Doctors':
        st.write("**Doctor Dimension Sample:**")
        st.dataframe(data['doctors'].head(10), use_container_width=True)
    elif table_choice == 'Departments':
        st.write("**Department Dimension Sample:**")
        st.dataframe(data['departments'], use_container_width=True)
    elif table_choice == 'Treatments':
        st.write("**Treatment Dimension Sample:**")
        st.dataframe(data['treatments'].head(10), use_container_width=True)
    elif table_choice == 'Dates':
        st.write("**Date Dimension Sample:**")
        st.dataframe(data['dates'].head(10), use_container_width=True)
    elif table_choice == 'Visits':
        st.write("**Visits Fact Table Sample:**")
        st.dataframe(data['visits'].head(10), use_container_width=True)

# Patient Analytics page
elif page == "👥 Patient Analytics":
    st.header("👥 Patient Analytics Dashboard")
    
    # Patient Demographics
    st.markdown("---")
    st.subheader("📊 Patient Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gender distribution
        gender_dist = data['patients']['gender'].value_counts()
        fig = px.pie(values=gender_dist.values, names=gender_dist.index, 
                    title="Patient Gender Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Age distribution
        data['patients']['age'] = (datetime.now() - pd.to_datetime(data['patients']['date_of_birth'])).dt.days // 365
        fig = px.histogram(data['patients'], x='age', nbins=20, 
                          title="Patient Age Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Insurance and Blood Type Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Insurance distribution
        insurance_dist = data['patients']['insurance_provider'].value_counts()
        fig = px.bar(x=insurance_dist.index, y=insurance_dist.values,
                    title="Insurance Provider Distribution")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Blood type distribution
        blood_dist = data['patients']['blood_type'].value_counts()
        fig = px.bar(x=blood_dist.index, y=blood_dist.values,
                    title="Blood Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Patient Visit Patterns
    st.markdown("---")
    st.subheader("🏥 Patient Visit Patterns")
    
    # Merge visits with patient data for analysis
    patient_visits = data['visits'].merge(data['patients'], on='patient_id')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Visit frequency by age group
        patient_visits['age_group'] = pd.cut(patient_visits['age_at_visit'], 
                                           bins=[0, 18, 35, 50, 65, 100], 
                                           labels=['0-18', '19-35', '36-50', '51-65', '65+'])
        age_visits = patient_visits['age_group'].value_counts().sort_index()
        fig = px.bar(x=age_visits.index, y=age_visits.values,
                    title="Visits by Age Group")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Visit type distribution
        visit_type_dist = patient_visits['visit_type'].value_counts()
        fig = px.pie(values=visit_type_dist.values, names=visit_type_dist.index,
                    title="Visit Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Patient Satisfaction Analysis
    st.markdown("---")
    st.subheader("😊 Patient Satisfaction Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_satisfaction = patient_visits['patient_satisfaction'].mean()
        st.metric("Average Satisfaction", f"{avg_satisfaction:.1f}/10")
    
    with col2:
        high_satisfaction = (patient_visits['patient_satisfaction'] >= 8).sum()
        satisfaction_rate = (high_satisfaction / len(patient_visits)) * 100
        st.metric("High Satisfaction Rate", f"{satisfaction_rate:.1f}%")
    
    with col3:
        low_satisfaction = (patient_visits['patient_satisfaction'] <= 5).sum()
        dissatisfaction_rate = (low_satisfaction / len(patient_visits)) * 100
        st.metric("Dissatisfaction Rate", f"{dissatisfaction_rate:.1f}%")
    
    # Satisfaction by demographics
    col1, col2 = st.columns(2)
    
    with col1:
        # Satisfaction by gender
        satisfaction_gender = patient_visits.groupby('gender')['patient_satisfaction'].mean()
        fig = px.bar(x=satisfaction_gender.index, y=satisfaction_gender.values,
                    title="Average Satisfaction by Gender")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Satisfaction by age group
        satisfaction_age = patient_visits.groupby('age_group')['patient_satisfaction'].mean()
        fig = px.bar(x=satisfaction_age.index, y=satisfaction_age.values,
                    title="Average Satisfaction by Age Group")
        st.plotly_chart(fig, use_container_width=True)

# Doctor Performance page
elif page == "👨‍⚕️ Doctor Performance":
    st.header("👨‍⚕️ Doctor Performance Analysis")
    
    # Doctor Overview
    st.markdown("---")
    st.subheader("📊 Doctor Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Doctors", len(data['doctors']))
    with col2:
        avg_experience = data['doctors']['years_experience'].mean()
        st.metric("Avg Experience", f"{avg_experience:.1f} years")
    with col3:
        specialties_count = data['doctors']['specialty'].nunique()
        st.metric("Specialties", specialties_count)
    with col4:
        departments_count = data['doctors']['department'].nunique()
        st.metric("Departments", departments_count)
    
    # Doctor Specialization Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Specialty distribution
        specialty_dist = data['doctors']['specialty'].value_counts()
        fig = px.bar(x=specialty_dist.values, y=specialty_dist.index, orientation='h',
                    title="Doctors by Specialty")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Experience distribution
        fig = px.histogram(data['doctors'], x='years_experience', nbins=15,
                          title="Doctor Experience Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    # Doctor Performance Metrics
    st.markdown("---")
    st.subheader("📈 Doctor Performance Metrics")
    
    # Merge visits with doctor data
    doctor_visits = data['visits'].merge(data['doctors'], on='doctor_id')
    
    # Calculate performance metrics per doctor
    doctor_performance = doctor_visits.groupby(['doctor_id', 'doctor_name', 'specialty']).agg({
        'visit_id': 'count',
        'patient_satisfaction': 'mean',
        'treatment_cost': 'sum',
        'readmission_30_days': 'sum',
        'complications': 'sum',
        'length_of_stay_hours': 'mean'
    }).reset_index()
    
    doctor_performance.columns = ['doctor_id', 'doctor_name', 'specialty', 'total_visits', 
                                 'avg_satisfaction', 'total_revenue', 'readmissions', 
                                 'complications', 'avg_los']
    
    # Calculate rates
    doctor_performance['readmission_rate'] = (doctor_performance['readmissions'] / 
                                             doctor_performance['total_visits'] * 100)
    doctor_performance['complication_rate'] = (doctor_performance['complications'] / 
                                              doctor_performance['total_visits'] * 100)
    
    # Top performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top 10 Doctors by Patient Volume:**")
        top_volume = doctor_performance.nlargest(10, 'total_visits')[
            ['doctor_name', 'specialty', 'total_visits', 'avg_satisfaction']
        ]
        st.dataframe(top_volume, use_container_width=True)
    
    with col2:
        st.write("**Top 10 Doctors by Patient Satisfaction:**")
        top_satisfaction = doctor_performance.nlargest(10, 'avg_satisfaction')[
            ['doctor_name', 'specialty', 'avg_satisfaction', 'total_visits']
        ]
        st.dataframe(top_satisfaction, use_container_width=True)
    
    # Performance visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Satisfaction vs Volume scatter plot
        fig = px.scatter(doctor_performance, x='total_visits', y='avg_satisfaction',
                        color='specialty', size='total_revenue',
                        title="Doctor Performance: Satisfaction vs Volume",
                        hover_data=['doctor_name'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Readmission rates by specialty
        specialty_readmission = doctor_performance.groupby('specialty')['readmission_rate'].mean()
        fig = px.bar(x=specialty_readmission.values, y=specialty_readmission.index, 
                    orientation='h', title="Average Readmission Rate by Specialty")
        st.plotly_chart(fig, use_container_width=True)

# Department Analysis page
elif page == "🏥 Department Analysis":
    st.header("🏥 Department Analysis Dashboard")
    
    # Department Overview
    st.markdown("---")
    st.subheader("📊 Department Overview")
    
    # Merge visits with department data
    dept_visits = data['visits'].merge(data['departments'], on='dept_id')
    
    # Department performance metrics
    dept_performance = dept_visits.groupby(['dept_id', 'dept_name', 'location', 'capacity']).agg({
        'visit_id': 'count',
        'patient_satisfaction': 'mean',
        'treatment_cost': 'sum',
        'length_of_stay_hours': 'mean',
        'readmission_30_days': 'sum',
        'complications': 'sum'
    }).reset_index()
    
    dept_performance.columns = ['dept_id', 'dept_name', 'location', 'capacity', 'total_visits',
                               'avg_satisfaction', 'total_revenue', 'avg_los', 'readmissions', 'complications']
    
    # Calculate utilization and rates
    dept_performance['utilization_rate'] = (dept_performance['total_visits'] / 
                                           dept_performance['capacity'] * 100)
    dept_performance['readmission_rate'] = (dept_performance['readmissions'] / 
                                           dept_performance['total_visits'] * 100)
    
    # Display department metrics
    st.dataframe(dept_performance, use_container_width=True)
    
    # Department visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Department utilization
        fig = px.bar(dept_performance, x='dept_name', y='utilization_rate',
                    title="Department Utilization Rate (%)",
                    color='utilization_rate', color_continuous_scale='RdYlGn')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by department
        fig = px.pie(dept_performance, values='total_revenue', names='dept_name',
                    title="Revenue Distribution by Department")
        st.plotly_chart(fig, use_container_width=True)
    
    # Department efficiency analysis
    st.markdown("---")
    st.subheader("⚡ Department Efficiency Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Satisfaction vs Utilization
        fig = px.scatter(dept_performance, x='utilization_rate', y='avg_satisfaction',
                        size='total_revenue', color='dept_name',
                        title="Department Efficiency: Satisfaction vs Utilization")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average length of stay by department
        fig = px.bar(dept_performance, x='dept_name', y='avg_los',
                    title="Average Length of Stay by Department (hours)",
                    color='avg_los', color_continuous_scale='Viridis')
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Time-based analysis
    st.markdown("---")
    st.subheader("📅 Department Activity Over Time")
    
    # Monthly visits by department
    dept_visits['visit_month'] = pd.to_datetime(dept_visits['visit_date']).dt.to_period('M')
    monthly_dept = dept_visits.groupby(['visit_month', 'dept_name']).size().reset_index(name='visits')
    monthly_dept['visit_month'] = monthly_dept['visit_month'].astype(str)
    
    fig = px.line(monthly_dept, x='visit_month', y='visits', color='dept_name',
                 title="Monthly Visits by Department")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# Treatment Insights page
elif page == "💊 Treatment Insights":
    st.header("💊 Treatment Analysis Dashboard")
    
    # Treatment Overview
    st.markdown("---")
    st.subheader("📊 Treatment Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Treatments", len(data['treatments']))
    with col2:
        avg_cost = data['treatments']['cost'].mean()
        st.metric("Avg Treatment Cost", f"${avg_cost:.0f}")
    with col3:
        avg_duration = data['treatments']['duration_minutes'].mean()
        st.metric("Avg Duration", f"{avg_duration:.0f} min")
    with col4:
        admission_rate = (data['treatments']['requires_admission'].sum() / 
                         len(data['treatments']) * 100)
        st.metric("Admission Rate", f"{admission_rate:.1f}%")
    
    # Treatment Type Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Treatment type distribution
        treatment_type_dist = data['treatments']['treatment_type'].value_counts()
        fig = px.pie(values=treatment_type_dist.values, names=treatment_type_dist.index,
                    title="Treatment Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cost distribution by treatment type
        fig = px.box(data['treatments'], x='treatment_type', y='cost',
                    title="Cost Distribution by Treatment Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Treatment Performance Analysis
    st.markdown("---")
    st.subheader("📈 Treatment Performance Analysis")
    
    # Merge visits with treatment data
    treatment_visits = data['visits'].merge(data['treatments'], on='treatment_id')
    
    # Treatment performance metrics
    treatment_performance = treatment_visits.groupby(['treatment_id', 'treatment_name', 'treatment_type']).agg({
        'visit_id': 'count',
        'patient_satisfaction': 'mean',
        'treatment_cost': 'sum',
        'complications': 'sum',
        'readmission_30_days': 'sum'
    }).reset_index()
    
    treatment_performance.columns = ['treatment_id', 'treatment_name', 'treatment_type', 
                                   'frequency', 'avg_satisfaction', 'total_revenue', 
                                   'complications', 'readmissions']
    
    # Calculate rates
    treatment_performance['complication_rate'] = (treatment_performance['complications'] / 
                                                 treatment_performance['frequency'] * 100)
    treatment_performance['readmission_rate'] = (treatment_performance['readmissions'] / 
                                                treatment_performance['frequency'] * 100)
    
    # Top treatments
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Most Frequent Treatments:**")
        top_frequent = treatment_performance.nlargest(10, 'frequency')[
            ['treatment_name', 'treatment_type', 'frequency', 'avg_satisfaction']
        ]
        st.dataframe(top_frequent, use_container_width=True)
    
    with col2:
        st.write("**Highest Revenue Treatments:**")
        top_revenue = treatment_performance.nlargest(10, 'total_revenue')[
            ['treatment_name', 'treatment_type', 'total_revenue', 'frequency']
        ]
        st.dataframe(top_revenue, use_container_width=True)
    
    # Treatment effectiveness analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Satisfaction vs Frequency
        fig = px.scatter(treatment_performance, x='frequency', y='avg_satisfaction',
                        color='treatment_type', size='total_revenue',
                        title="Treatment Effectiveness: Satisfaction vs Frequency")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Complication rates by treatment type
        type_complications = treatment_performance.groupby('treatment_type')['complication_rate'].mean()
        fig = px.bar(x=type_complications.index, y=type_complications.values,
                    title="Average Complication Rate by Treatment Type")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

# Financial Analysis page
elif page == "📈 Financial Analysis":
    st.header("📈 Financial Analysis Dashboard")
    
    # Financial Overview
    st.markdown("---")
    st.subheader("💰 Financial Overview")
    
    total_revenue = data['visits']['treatment_cost'].sum()
    total_insurance = data['visits']['insurance_covered'].sum()
    out_of_pocket = total_revenue - total_insurance
    avg_visit_cost = data['visits']['treatment_cost'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Insurance Covered", f"${total_insurance:,.0f}")
    with col3:
        st.metric("Out of Pocket", f"${out_of_pocket:,.0f}")
    with col4:
        st.metric("Avg Visit Cost", f"${avg_visit_cost:.0f}")
    
    # Revenue Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by department
        dept_revenue = data['visits'].merge(data['departments'], on='dept_id')
        dept_revenue_summary = dept_revenue.groupby('dept_name')['treatment_cost'].sum().sort_values(ascending=False)
        fig = px.bar(x=dept_revenue_summary.values, y=dept_revenue_summary.index, 
                    orientation='h', title="Revenue by Department")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly revenue trend
        data['visits']['visit_month'] = pd.to_datetime(data['visits']['visit_date']).dt.to_period('M')
        monthly_revenue = data['visits'].groupby('visit_month')['treatment_cost'].sum()
        monthly_revenue.index = monthly_revenue.index.astype(str)
        fig = px.line(x=monthly_revenue.index, y=monthly_revenue.values,
                     title="Monthly Revenue Trend")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Insurance Analysis
    st.markdown("---")
    st.subheader("🏥 Insurance Analysis")
    
    # Merge with patient data for insurance analysis
    insurance_analysis = data['visits'].merge(data['patients'], on='patient_id')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue by insurance provider
        insurance_revenue = insurance_analysis.groupby('insurance_provider')['treatment_cost'].sum().sort_values(ascending=False)
        fig = px.bar(x=insurance_revenue.index, y=insurance_revenue.values,
                    title="Revenue by Insurance Provider")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Insurance coverage rates
        insurance_coverage = insurance_analysis.groupby('insurance_provider').agg({
            'treatment_cost': 'sum',
            'insurance_covered': 'sum'
        })
        insurance_coverage['coverage_rate'] = (insurance_coverage['insurance_covered'] / 
                                              insurance_coverage['treatment_cost'] * 100)
        fig = px.bar(x=insurance_coverage.index, y=insurance_coverage['coverage_rate'],
                    title="Insurance Coverage Rate by Provider (%)")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Cost Analysis
    st.markdown("---")
    st.subheader("💊 Cost Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost by visit type
        cost_by_type = data['visits'].groupby('visit_type')['treatment_cost'].mean()
        fig = px.bar(x=cost_by_type.index, y=cost_by_type.values,
                    title="Average Cost by Visit Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cost by severity
        cost_by_severity = data['visits'].groupby('severity')['treatment_cost'].mean()
        fig = px.bar(x=cost_by_severity.index, y=cost_by_severity.values,
                    title="Average Cost by Severity Level",
                    color=cost_by_severity.values, color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

# About page
elif page == "📋 About":
    st.header("📋 About This Medical Dashboard")
    
    st.markdown("""
    ## 🎯 Purpose
    This dashboard provides comprehensive analysis of medical facility data using a star schema architecture.
    It demonstrates advanced data modeling, synthetic data generation, and healthcare analytics.
    
    ## 🏗️ Technical Architecture
    
    ### Star Schema Design
    - **5 Dimension Tables:** Patients, Doctors, Departments, Treatments, Dates
    - **1 Fact Table:** Medical Visits (central table with all metrics)
    - **Optimized for:** Fast analytical queries and business intelligence
    
    ### Data Generation
    - **Faker Library:** Used to generate realistic synthetic medical data
    - **1,000 Patients:** Diverse demographics and medical profiles
    - **100 Doctors:** Various specialties and experience levels
    - **8 Departments:** Different hospital departments and capacities
    - **200 Treatment Types:** Comprehensive medical procedures and costs
    - **5,000 Visits:** Realistic patient visit patterns and outcomes
    
    ## 📊 Analytics Capabilities
    
    ### Patient Analytics
    - Demographics and health patterns
    - Visit frequency and satisfaction analysis
    - Insurance and payment pattern insights
    - Age-based health trend analysis
    
    ### Healthcare Operations
    - Doctor performance and specialization metrics
    - Department efficiency and utilization rates
    - Treatment effectiveness and safety analysis
    - Resource allocation optimization
    
    ### Financial Intelligence
    - Revenue analysis by department and treatment
    - Insurance coverage and reimbursement patterns
    - Cost optimization opportunities
    - Profitability analysis
    
    ## 🛠️ Technologies Used
    - **Streamlit:** Interactive web application framework
    - **Faker:** Synthetic data generation library
    - **Pandas:** Data manipulation and analysis
    - **Plotly:** Interactive data visualizations
    - **NumPy:** Numerical computing
    - **Python:** Core programming language
    
    ## 🏥 Healthcare Metrics
    
    ### Quality Indicators
    - Patient satisfaction scores (1-10 scale)
    - Readmission rates (30-day tracking)
    - Complication rates by treatment type
    - Length of stay optimization
    
    ### Operational Metrics
    - Department utilization rates
    - Doctor productivity and patient volume
    - Treatment frequency and effectiveness
    - Resource allocation efficiency
    
    ### Financial Metrics
    - Revenue per department and treatment
    - Insurance coverage and reimbursement rates
    - Cost per visit and treatment type
    - Profitability analysis
    
    ## 📈 Business Intelligence Features
    
    ### Interactive Dashboards
    - Real-time data filtering and exploration
    - Multi-dimensional analysis capabilities
    - Drill-down functionality for detailed insights
    - Export capabilities for further analysis
    
    ### Predictive Analytics Ready
    - Historical trend analysis
    - Pattern recognition in patient data
    - Resource demand forecasting
    - Quality improvement opportunities
    
    ## 👥 Assignment Information
    
    **Course:** Database Systems and Analytics
    **Assignment:** Medical Facility Star Schema Analysis
    **Technology Stack:** Python, Streamlit, Faker, Plotly
    **Data Architecture:** Star Schema with Fact and Dimension Tables
    
    ---
    
    **🏥 Medical Facility Analysis Dashboard | Powered by Star Schema & Faker**
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")

# Footer for all pages
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏥 Medical Facility Analysis Dashboard | Star Schema Architecture | Built with Streamlit & Faker</p>
    <p><small>Comprehensive healthcare analytics with synthetic medical data</small></p>
</div>
""", unsafe_allow_html=True)

# Update TODO status
if page == "🏠 Home":
    # Mark first todo as completed
    st.sidebar.success("✅ Star schema structure created successfully!")
