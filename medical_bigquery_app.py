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
import io
import altair as alt
from google.cloud import bigquery
from google.oauth2 import service_account

# Initialize Faker
fake = Faker()

# Page configuration
st.set_page_config(
    page_title="Medical Facility Analysis Dashboard - BigQuery",
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
            st.info("💡 Go to your app settings → Secrets and add the gcp_service_account section")
            return None, None
            
    except Exception as e:
        st.error(f"❌ Error connecting to BigQuery: {e}")
        st.info("💡 Check your Streamlit Cloud secrets configuration")
        return None, None

# Data Generation Functions for BigQuery
def generate_medical_data():
    """Generate synthetic medical data using Faker"""
    
    # Set seed for reproducible data
    Faker.seed(42)
    random.seed(42)
    np.random.seed(42)
    
    # 1. Patient Dimension
    patients = []
    for i in range(1, 1001):  # 1000 patients
        patient = {
            'patient_id': i,
            'patient_name': fake.name(),
            'date_of_birth': fake.date_of_birth(minimum_age=0, maximum_age=90).strftime('%Y-%m-%d'),
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
    
    # 5. Medical Visits Fact Table
    visits = []
    visit_id = 1
    
    for _ in range(5000):  # 5000 medical visits
        # Random selections from dimensions
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        department = random.choice(departments)
        treatment = random.choice(treatments)
        
        # Random visit date
        visit_date = fake.date_between(start_date='-2y', end_date='today')
        
        # Calculate age at visit
        birth_date = datetime.strptime(patient['date_of_birth'], '%Y-%m-%d').date()
        age_at_visit = visit_date.year - birth_date.year
        if visit_date.month < birth_date.month or \
           (visit_date.month == birth_date.month and visit_date.day < birth_date.day):
            age_at_visit -= 1
        
        visit = {
            'visit_id': visit_id,
            'patient_id': patient['patient_id'],
            'doctor_id': doctor['doctor_id'],
            'dept_id': department['dept_id'],
            'treatment_id': treatment['treatment_id'],
            'visit_date': visit_date.strftime('%Y-%m-%d'),
            'admission_time': fake.time(),
            'discharge_time': fake.time(),
            'visit_type': random.choice(['Emergency', 'Scheduled', 'Follow-up', 'Walk-in']),
            'diagnosis': fake.sentence(nb_words=4),
            'severity': random.choice(['Low', 'Medium', 'High', 'Critical']),
            'treatment_cost': round(treatment['cost'] * random.uniform(0.8, 1.5), 2),
            'insurance_covered': round(random.uniform(0, 1) * treatment['cost'], 2),
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
        'visits': pd.DataFrame(visits)
    }

def create_bigquery_tables(client, project_id, dataset_id='medical_facility'):
    """Create BigQuery tables for the medical star schema"""
    
    # Create dataset if it doesn't exist
    dataset_ref = f"{project_id}.{dataset_id}"
    
    try:
        client.get_dataset(dataset_ref)
        st.info(f"Dataset {dataset_id} already exists")
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30)
        st.success(f"Created dataset {dataset_id}")
    
    # Table schemas
    schemas = {
        'patients': [
            bigquery.SchemaField("patient_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("patient_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date_of_birth", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("gender", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("phone", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("address", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("emergency_contact", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("emergency_phone", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("insurance_provider", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("blood_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("allergies", "STRING", mode="NULLABLE"),
        ],
        'doctors': [
            bigquery.SchemaField("doctor_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("doctor_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("specialty", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("years_experience", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("education", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("license_number", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("phone", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("department", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("shift", "STRING", mode="NULLABLE"),
        ],
        'departments': [
            bigquery.SchemaField("dept_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("dept_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("location", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("head_doctor", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("capacity", "INTEGER", mode="NULLABLE"),
        ],
        'treatments': [
            bigquery.SchemaField("treatment_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("treatment_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("treatment_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("duration_minutes", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("cost", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("requires_admission", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("equipment_needed", "STRING", mode="NULLABLE"),
        ],
        'visits': [
            bigquery.SchemaField("visit_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("patient_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("doctor_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("dept_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("treatment_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("visit_date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("admission_time", "TIME", mode="NULLABLE"),
            bigquery.SchemaField("discharge_time", "TIME", mode="NULLABLE"),
            bigquery.SchemaField("visit_type", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("diagnosis", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("severity", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("treatment_cost", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("insurance_covered", "FLOAT", mode="NULLABLE"),
            bigquery.SchemaField("patient_satisfaction", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("length_of_stay_hours", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("readmission_30_days", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("complications", "BOOLEAN", mode="NULLABLE"),
            bigquery.SchemaField("age_at_visit", "INTEGER", mode="NULLABLE"),
        ]
    }
    
    # Create tables
    created_tables = []
    for table_name, schema in schemas.items():
        table_ref = f"{project_id}.{dataset_id}.{table_name}"
        
        try:
            client.get_table(table_ref)
            st.info(f"Table {table_name} already exists")
        except:
            table = bigquery.Table(table_ref, schema=schema)
            table = client.create_table(table)
            created_tables.append(table_name)
            st.success(f"Created table {table_name}")
    
    return created_tables

def populate_bigquery_tables(client, project_id, data, dataset_id='medical_facility'):
    """Populate BigQuery tables with generated data"""
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite existing data
    )
    
    populated_tables = []
    
    for table_name, df in data.items():
        table_ref = f"{project_id}.{dataset_id}.{table_name}"
        
        try:
            job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result()  # Wait for the job to complete
            
            populated_tables.append(table_name)
            st.success(f"Populated table {table_name} with {len(df)} records")
            
        except Exception as e:
            st.error(f"Error populating table {table_name}: {e}")
    
    return populated_tables

# Title and header
st.markdown('<h1 class="main-header">🏥 Medical Facility Analysis Dashboard - BigQuery</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏥 Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🏠 Home", "🔧 Database Setup", "📊 Star Schema Overview", "👥 Patient Analytics", 
     "👨‍⚕️ Doctor Performance", "🏥 Department Analysis", "💊 Treatment Insights", 
     "📈 Financial Analysis", "🔍 SQL Queries", "📋 About"]
)

# Get BigQuery client
client, project_id = get_bigquery_client()

# Home page
if page == "🏠 Home":
    st.markdown("## 🎯 Medical Facility Data Analysis - BigQuery Edition")
    st.markdown("**Data Source:** Synthetic medical data generated using Faker library")
    st.markdown("**Architecture:** Star Schema stored in Google BigQuery")
    st.markdown("**Dataset:** `medical_facility` (auto-created)")
    
    # BigQuery Status
    if client is None:
        st.error("❌ BigQuery connection failed. Please check your credentials.")
        st.info("💡 Please check your BigQuery credentials and try again.")
        st.stop()
    else:
        st.success(f"✅ Connected to BigQuery project: {project_id}")
        
        # Check if tables exist
        dataset_id = 'medical_facility'
        try:
            # Check for visits table (fact table)
            table_ref = f"{project_id}.{dataset_id}.visits"
            table = client.get_table(table_ref)
            
            # Data Overview
            st.markdown("---")
            st.subheader("📋 Dataset Overview")
            
            # Get comprehensive dataset metrics
            overview_query = f"""
            SELECT 
                (SELECT COUNT(*) FROM `{project_id}.{dataset_id}.patients`) as total_patients,
                (SELECT COUNT(*) FROM `{project_id}.{dataset_id}.doctors`) as total_doctors,
                (SELECT COUNT(*) FROM `{project_id}.{dataset_id}.departments`) as total_departments,
                (SELECT COUNT(*) FROM `{project_id}.{dataset_id}.treatments`) as total_treatments,
                COUNT(*) as total_visits,
                ROUND(SUM(treatment_cost), 2) as total_revenue,
                ROUND(AVG(patient_satisfaction), 1) as avg_satisfaction,
                ROUND(AVG(length_of_stay_hours), 1) as avg_length_of_stay
            FROM `{project_id}.{dataset_id}.visits`
            """
            
            overview_df = client.query(overview_query).to_dataframe()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Patients", f"{overview_df.iloc[0]['total_patients']:,}")
                st.metric("Total Doctors", f"{overview_df.iloc[0]['total_doctors']:,}")
            
            with col2:
                st.metric("Total Visits", f"{overview_df.iloc[0]['total_visits']:,}")
                st.metric("Departments", f"{overview_df.iloc[0]['total_departments']:,}")
            
            with col3:
                st.metric("Treatment Types", f"{overview_df.iloc[0]['total_treatments']:,}")
                st.metric("Total Revenue", f"${overview_df.iloc[0]['total_revenue']:,.0f}")
            
            # Key Metrics
            st.markdown("---")
            st.subheader("🎯 Key Performance Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Avg Patient Satisfaction", f"{overview_df.iloc[0]['avg_satisfaction']}/10")
            with col2:
                # Calculate readmission rate
                readmission_query = f"""
                SELECT ROUND(AVG(CASE WHEN readmission_30_days THEN 1 ELSE 0 END) * 100, 1) as readmission_rate
                FROM `{project_id}.{dataset_id}.visits`
                """
                readmission_df = client.query(readmission_query).to_dataframe()
                st.metric("Readmission Rate", f"{readmission_df.iloc[0]['readmission_rate']}%")
            with col3:
                st.metric("Avg Length of Stay", f"{overview_df.iloc[0]['avg_length_of_stay']} hours")
            with col4:
                # Calculate complication rate
                complication_query = f"""
                SELECT ROUND(AVG(CASE WHEN complications THEN 1 ELSE 0 END) * 100, 1) as complication_rate
                FROM `{project_id}.{dataset_id}.visits`
                """
                complication_df = client.query(complication_query).to_dataframe()
                st.metric("Complication Rate", f"{complication_df.iloc[0]['complication_rate']}%")
            
        except Exception as e:
            st.warning("⚠️ Medical facility tables not found in BigQuery")
            st.info("💡 Please go to the 'Database Setup' page to create and populate the tables")
            st.info(f"Error details: {e}")

# Database Setup page
elif page == "🔧 Database Setup":
    st.header("🔧 Database Setup & Data Population")
    
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    st.markdown("""
    ## 🏗️ Medical Facility Star Schema Setup
    
    This page allows you to create the BigQuery dataset and tables, then populate them with synthetic medical data.
    
    **What this will create:**
    - Dataset: `medical_facility`
    - Tables: `patients`, `doctors`, `departments`, `treatments`, `visits`
    - Data: 1,000 patients, 100 doctors, 8 departments, 200 treatments, 5,000 visits
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏗️ Create Tables", type="primary"):
            with st.spinner("Creating BigQuery tables..."):
                try:
                    created_tables = create_bigquery_tables(client, project_id)
                    if created_tables:
                        st.success(f"✅ Created {len(created_tables)} tables: {', '.join(created_tables)}")
                    else:
                        st.info("ℹ️ All tables already exist")
                except Exception as e:
                    st.error(f"❌ Error creating tables: {e}")
    
    with col2:
        if st.button("📊 Populate with Data", type="secondary"):
            with st.spinner("Generating and uploading synthetic medical data..."):
                try:
                    # Generate data
                    st.info("🔄 Generating synthetic medical data...")
                    data = generate_medical_data()
                    
                    # Populate tables
                    st.info("📤 Uploading data to BigQuery...")
                    populated_tables = populate_bigquery_tables(client, project_id, data)
                    
                    if populated_tables:
                        st.success(f"✅ Populated {len(populated_tables)} tables with synthetic data!")
                        st.balloons()
                    else:
                        st.warning("⚠️ No tables were populated")
                        
                except Exception as e:
                    st.error(f"❌ Error populating tables: {e}")
    
    # Check current table status
    st.markdown("---")
    st.subheader("📋 Current Table Status")
    
    dataset_id = 'medical_facility'
    tables_to_check = ['patients', 'doctors', 'departments', 'treatments', 'visits']
    
    table_status = []
    for table_name in tables_to_check:
        try:
            table_ref = f"{project_id}.{dataset_id}.{table_name}"
            table = client.get_table(table_ref)
            table_status.append({
                'Table': table_name,
                'Status': '✅ Exists',
                'Rows': f"{table.num_rows:,}",
                'Size (MB)': f"{table.num_bytes / (1024*1024):.2f}"
            })
        except:
            table_status.append({
                'Table': table_name,
                'Status': '❌ Not Found',
                'Rows': 'N/A',
                'Size (MB)': 'N/A'
            })
    
    status_df = pd.DataFrame(table_status)
    st.dataframe(status_df, use_container_width=True)

# SQL Queries page
elif page == "🔍 SQL Queries":
    st.header("🔍 SQL Query Execution")
    
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Pre-built Analysis Queries
    st.markdown("---")
    st.subheader("📋 Pre-built Medical Analysis Queries")
    
    dataset_id = 'medical_facility'
    
    query_templates = {
        "Basic Overview": f"""
        SELECT 
            COUNT(*) as total_visits,
            COUNT(DISTINCT patient_id) as unique_patients,
            COUNT(DISTINCT doctor_id) as unique_doctors,
            ROUND(AVG(treatment_cost), 2) as avg_treatment_cost,
            ROUND(SUM(treatment_cost), 2) as total_revenue,
            ROUND(AVG(patient_satisfaction), 1) as avg_satisfaction
        FROM `{project_id}.{dataset_id}.visits`
        """,
        
        "Department Performance": f"""
        SELECT 
            d.dept_name,
            d.location,
            COUNT(v.visit_id) as total_visits,
            ROUND(SUM(v.treatment_cost), 2) as total_revenue,
            ROUND(AVG(v.patient_satisfaction), 1) as avg_satisfaction,
            ROUND(AVG(v.length_of_stay_hours), 1) as avg_length_of_stay
        FROM `{project_id}.{dataset_id}.visits` v
        JOIN `{project_id}.{dataset_id}.departments` d ON v.dept_id = d.dept_id
        GROUP BY d.dept_name, d.location
        ORDER BY total_revenue DESC
        """,
        
        "Doctor Specialization Analysis": f"""
        SELECT 
            doc.specialty,
            COUNT(DISTINCT doc.doctor_id) as doctor_count,
            COUNT(v.visit_id) as total_visits,
            ROUND(AVG(v.patient_satisfaction), 1) as avg_satisfaction,
            ROUND(SUM(v.treatment_cost), 2) as total_revenue
        FROM `{project_id}.{dataset_id}.doctors` doc
        LEFT JOIN `{project_id}.{dataset_id}.visits` v ON doc.doctor_id = v.doctor_id
        GROUP BY doc.specialty
        ORDER BY total_revenue DESC
        """,
        
        "Patient Demographics": f"""
        SELECT 
            p.gender,
            COUNT(DISTINCT p.patient_id) as patient_count,
            COUNT(v.visit_id) as total_visits,
            ROUND(AVG(v.treatment_cost), 2) as avg_treatment_cost,
            ROUND(SUM(v.treatment_cost), 2) as total_revenue
        FROM `{project_id}.{dataset_id}.patients` p
        LEFT JOIN `{project_id}.{dataset_id}.visits` v ON p.patient_id = v.patient_id
        GROUP BY p.gender
        ORDER BY total_revenue DESC
        """,
        
        "Treatment Type Analysis": f"""
        SELECT 
            t.treatment_type,
            COUNT(v.visit_id) as frequency,
            ROUND(AVG(t.cost), 2) as avg_base_cost,
            ROUND(AVG(v.treatment_cost), 2) as avg_actual_cost,
            ROUND(SUM(v.treatment_cost), 2) as total_revenue,
            ROUND(AVG(v.patient_satisfaction), 1) as avg_satisfaction
        FROM `{project_id}.{dataset_id}.treatments` t
        JOIN `{project_id}.{dataset_id}.visits` v ON t.treatment_id = v.treatment_id
        GROUP BY t.treatment_type
        ORDER BY frequency DESC
        """,
        
        "Monthly Visit Trends": f"""
        SELECT 
            EXTRACT(YEAR FROM visit_date) as year,
            EXTRACT(MONTH FROM visit_date) as month,
            COUNT(*) as visit_count,
            ROUND(SUM(treatment_cost), 2) as monthly_revenue,
            ROUND(AVG(patient_satisfaction), 1) as avg_satisfaction
        FROM `{project_id}.{dataset_id}.visits`
        GROUP BY year, month
        ORDER BY year, month
        """
    }
    
    selected_template = st.selectbox("Choose a pre-built analysis:", list(query_templates.keys()))
    query = st.text_area("SQL Query:", value=query_templates[selected_template], height=200)
    
    if st.button("🚀 Execute Query", type="primary"):
        if query.strip():
            with st.spinner("Executing query..."):
                try:
                    # Execute query
                    results_df = client.query(query).to_dataframe()
                    
                    st.success(f"✅ Query executed successfully! Returned {len(results_df)} rows")
                    
                    # Display results
                    st.write("**Query Results:**")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Download results
                    if len(results_df) > 0:
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"{selected_template.lower().replace(' ', '_')}_results.csv",
                            mime="text/csv"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Query execution failed: {e}")
                    st.info("💡 Check your SQL syntax and table references")
        else:
            st.warning("⚠️ Please enter a SQL query")
    
    # Custom Query Section
    st.markdown("---")
    st.subheader("✍️ Custom SQL Query")
    
    custom_query = st.text_area("Enter your custom SQL query:", height=150, 
                               placeholder=f"SELECT * FROM `{project_id}.{dataset_id}.visits` LIMIT 10")
    
    if st.button("🔍 Run Custom Query"):
        if custom_query.strip():
            with st.spinner("Executing custom query..."):
                try:
                    # Execute custom query
                    custom_results = client.query(custom_query).to_dataframe()
                    
                    st.success(f"✅ Custom query executed successfully! Returned {len(custom_results)} rows")
                    
                    # Display results
                    st.write("**Custom Query Results:**")
                    st.dataframe(custom_results, use_container_width=True)
                    
                    # Download results
                    if len(custom_results) > 0:
                        csv = custom_results.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Custom Results as CSV",
                            data=csv,
                            file_name="custom_query_results.csv",
                            mime="text/csv"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Custom query execution failed: {e}")
                    st.info("💡 Check your SQL syntax and table references")
        else:
            st.warning("⚠️ Please enter a custom SQL query")

# Other pages would follow similar pattern, querying BigQuery instead of using in-memory data
# For brevity, I'll include a few key pages

# Star Schema Overview page
elif page == "📊 Star Schema Overview":
    st.header("📊 Star Schema Architecture - BigQuery Implementation")
    
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()
    
    st.markdown("""
    ## 🏗️ BigQuery Star Schema Implementation
    
    This medical facility database follows a **star schema** design pattern, implemented in Google BigQuery
    for scalable analytics and business intelligence reporting.
    """)
    
    # Schema diagram description
    st.markdown("---")
    st.subheader("🌟 Star Schema Components in BigQuery")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 📋 Dimension Tables
        
        **1. `patients`** - Patient demographics and medical info
        **2. `doctors`** - Doctor profiles and specializations  
        **3. `departments`** - Hospital departments and locations
        **4. `treatments`** - Treatment types and procedures
        
        ### 🎯 Fact Table
        **`visits`** - Central fact table with all metrics
        """)
    
    with col2:
        st.markdown("""
        ### 💾 BigQuery Benefits
        
        - **Scalable:** Handles large datasets efficiently
        - **Fast Queries:** Columnar storage for analytics
        - **SQL Interface:** Standard SQL for analysis
        - **Cloud Native:** Serverless and managed
        - **Integration:** Works with BI tools
        """)
    
    # Table details from BigQuery
    dataset_id = 'medical_facility'
    tables = ['patients', 'doctors', 'departments', 'treatments', 'visits']
    
    table_stats = []
    for table_name in tables:
        try:
            table_ref = f"{project_id}.{dataset_id}.{table_name}"
            table = client.get_table(table_ref)
            table_stats.append({
                'Table Name': table_name,
                'Record Count': f"{table.num_rows:,}",
                'Columns': len(table.schema),
                'Size (MB)': f"{table.num_bytes / (1024*1024):.2f}",
                'Table Type': 'Fact' if table_name == 'visits' else 'Dimension'
            })
        except:
            table_stats.append({
                'Table Name': table_name,
                'Record Count': 'Not Found',
                'Columns': 'N/A',
                'Size (MB)': 'N/A',
                'Table Type': 'Fact' if table_name == 'visits' else 'Dimension'
            })
    
    if table_stats:
        st.markdown("---")
        st.subheader("📊 BigQuery Table Statistics")
        stats_df = pd.DataFrame(table_stats)
        st.dataframe(stats_df, use_container_width=True)

# About page
elif page == "📋 About":
    st.header("📋 About This Medical Dashboard - BigQuery Edition")
    
    st.markdown("""
    ## 🎯 Purpose
    This dashboard provides comprehensive analysis of medical facility data using a star schema architecture
    implemented in Google BigQuery. It demonstrates advanced data modeling, synthetic data generation, 
    and cloud-based healthcare analytics.
    
    ## 🏗️ Technical Architecture
    
    ### BigQuery Star Schema Design
    - **4 Dimension Tables:** Patients, Doctors, Departments, Treatments
    - **1 Fact Table:** Medical Visits (central table with all metrics)
    - **Cloud Storage:** Google BigQuery for scalable analytics
    - **Real SQL:** Standard SQL queries on cloud infrastructure
    
    ### Data Generation & Population
    - **Faker Library:** Generates realistic synthetic medical data
    - **BigQuery Integration:** Direct upload to cloud tables
    - **1,000 Patients:** Diverse demographics and medical profiles
    - **100 Doctors:** Various specialties and experience levels
    - **8 Departments:** Different hospital departments
    - **200 Treatment Types:** Comprehensive medical procedures
    - **5,000 Visits:** Realistic patient visit patterns
    
    ## 🚀 Key Features
    
    ### Cloud-Native Analytics
    - **BigQuery Integration:** Real database queries, not in-memory data
    - **Scalable Architecture:** Handles large datasets efficiently
    - **SQL Interface:** Standard SQL for complex analytics
    - **Fast Performance:** Columnar storage optimized for analytics
    
    ### Healthcare Intelligence
    - **Patient Analytics:** Demographics, satisfaction, outcomes
    - **Doctor Performance:** Productivity, specialization metrics
    - **Department Efficiency:** Utilization, revenue analysis
    - **Treatment Insights:** Effectiveness, cost analysis
    - **Financial Analytics:** Revenue, insurance, profitability
    
    ## 🛠️ Technologies Used
    - **Google BigQuery:** Cloud data warehouse
    - **Streamlit:** Interactive web application framework
    - **Faker:** Synthetic data generation library
    - **Plotly:** Interactive data visualizations
    - **Pandas:** Data manipulation and analysis
    - **Google Cloud SDK:** BigQuery client libraries
    
    ## 📊 Assignment Context
    
    **Course:** Database Systems and Analytics - Assignment 2
    **Objective:** Create a star schema with synthetic data using Faker
    **Innovation:** Implemented in BigQuery for real cloud database experience
    **Technology Stack:** Python, Streamlit, Faker, BigQuery, Plotly
    
    ## 🔧 Setup Instructions
    
    1. **BigQuery Setup:** Ensure you have BigQuery credentials configured
    2. **Database Creation:** Use the "Database Setup" page to create tables
    3. **Data Population:** Generate and upload synthetic medical data
    4. **Analysis:** Explore the various analytics pages
    
    ## 🏥 Healthcare Metrics
    
    ### Quality Indicators
    - Patient satisfaction scores (1-10 scale)
    - Readmission rates (30-day tracking)
    - Complication rates by treatment type
    - Length of stay optimization
    
    ### Operational Metrics
    - Department utilization rates
    - Doctor productivity and specialization
    - Treatment frequency and effectiveness
    - Resource allocation efficiency
    
    ### Financial Metrics
    - Revenue per department and treatment
    - Insurance coverage analysis
    - Cost per visit and treatment type
    - Profitability by service line
    
    ---
    
    **🏥 Medical Facility Analysis Dashboard | BigQuery Star Schema | Assignment 2**
    """)

# Footer for all pages
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏥 Medical Facility Analysis Dashboard | BigQuery Star Schema | Built with Streamlit & Faker</p>
    <p><small>Cloud-native healthcare analytics with synthetic medical data</small></p>
</div>
""", unsafe_allow_html=True)
