#!/usr/bin/env python3
"""
Medical Data BigQuery Population Script
======================================

This script creates and populates BigQuery tables with synthetic medical data
using the Faker library. Run this FIRST before running the web application.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
from google.cloud import bigquery
from google.oauth2 import service_account
import json
import os

# Initialize Faker
fake = Faker()

def get_bigquery_client():
    """Initialize BigQuery client with service account credentials"""
    try:
        # Try environment variable first
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            client = bigquery.Client()
            return client, client.project
        
        # Try to use the same credentials as your retail app
        # You'll need to create a service account JSON file or use Streamlit secrets
        print("💡 Using the same BigQuery credentials as your retail app...")
        print("📋 Please ensure you have one of these set up:")
        print("   1. GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("   2. Service account JSON file")
        print("   3. Default Google Cloud credentials")
        
        # Try default credentials
        try:
            client = bigquery.Client()
            return client, client.project
        except Exception as default_error:
            print(f"❌ Default credentials failed: {default_error}")
            
            # Provide instructions for manual setup
            print("\n🔧 Manual Setup Options:")
            print("Option 1 - Use your service account JSON:")
            print('   set GOOGLE_APPLICATION_CREDENTIALS=path\\to\\your\\service-account.json')
            print("\nOption 2 - Use gcloud CLI:")
            print('   gcloud auth application-default login')
            print("\nOption 3 - Modify this script with your project ID:")
            print('   client = bigquery.Client(project="your-project-id")')
            
            return None, None
            
    except Exception as e:
        print(f"❌ Error connecting to BigQuery: {e}")
        return None, None

def generate_medical_data():
    """Generate synthetic medical data using Faker"""
    print("🔄 Generating synthetic medical data...")
    
    # Set seed for reproducible data
    Faker.seed(42)
    random.seed(42)
    np.random.seed(42)
    
    # 1. Patient Dimension
    print("   👥 Generating patients...")
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
    print("   👨‍⚕️ Generating doctors...")
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
    print("   🏥 Generating departments...")
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
    print("   💊 Generating treatments...")
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
    print("   🏥 Generating medical visits...")
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
    
    print("✅ Data generation complete!")
    return {
        'patients': pd.DataFrame(patients),
        'doctors': pd.DataFrame(doctors),
        'departments': pd.DataFrame(departments),
        'treatments': pd.DataFrame(treatments),
        'visits': pd.DataFrame(visits)
    }

def create_bigquery_tables(client, project_id, dataset_id='medical_facility'):
    """Create BigQuery tables for the medical star schema"""
    print(f"🏗️  Creating BigQuery dataset and tables...")
    
    # Create dataset if it doesn't exist
    dataset_ref = f"{project_id}.{dataset_id}"
    
    try:
        client.get_dataset(dataset_ref)
        print(f"   ℹ️  Dataset {dataset_id} already exists")
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"   ✅ Created dataset {dataset_id}")
    
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
            print(f"   ℹ️  Table {table_name} already exists")
        except:
            table = bigquery.Table(table_ref, schema=schema)
            table = client.create_table(table)
            created_tables.append(table_name)
            print(f"   ✅ Created table {table_name}")
    
    return created_tables

def populate_bigquery_tables(client, project_id, data, dataset_id='medical_facility'):
    """Populate BigQuery tables with generated data"""
    print("📤 Uploading data to BigQuery...")
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrite existing data
    )
    
    populated_tables = []
    
    for table_name, df in data.items():
        table_ref = f"{project_id}.{dataset_id}.{table_name}"
        
        try:
            print(f"   📊 Uploading {table_name} ({len(df)} records)...")
            job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result()  # Wait for the job to complete
            
            populated_tables.append(table_name)
            print(f"   ✅ Populated table {table_name}")
            
        except Exception as e:
            print(f"   ❌ Error populating table {table_name}: {e}")
    
    return populated_tables

def main():
    """Main function to create and populate medical database"""
    print("🏥 Medical Facility BigQuery Population Script")
    print("=" * 50)
    
    # Get BigQuery client
    client, project_id = get_bigquery_client()
    if client is None:
        print("❌ Failed to connect to BigQuery. Please check your credentials.")
        return
    
    print(f"✅ Connected to BigQuery project: {project_id}")
    
    # Generate synthetic data
    data = generate_medical_data()
    
    # Create tables
    created_tables = create_bigquery_tables(client, project_id)
    
    # Populate tables
    populated_tables = populate_bigquery_tables(client, project_id, data)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Medical Database Population Complete!")
    print(f"📊 Dataset: {project_id}.medical_facility")
    print(f"📋 Tables populated: {len(populated_tables)}")
    
    for table_name, df in data.items():
        print(f"   • {table_name}: {len(df):,} records")
    
    print("\n💡 Next steps:")
    print("   1. Run the Streamlit web application")
    print("   2. Explore the medical data analytics")
    print("   3. Execute custom SQL queries")
    
    print("\n🚀 Ready to run: streamlit run medical_web_app.py")

if __name__ == "__main__":
    main()
