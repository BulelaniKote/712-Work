#!/usr/bin/env python3
"""
Simple Medical Data Population Script
====================================

This script creates and populates BigQuery tables with synthetic medical data.
It uses the same project as your retail sales app.

Since your retail app works, this should work with the same credentials.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
from google.cloud import bigquery

# Initialize Faker
fake = Faker()

def get_bigquery_client():
    """Initialize BigQuery client - uses same setup as your retail app"""
    try:
        # This should work if your retail app works
        client = bigquery.Client()
        return client, client.project
    except Exception as e:
        print(f"❌ Error connecting to BigQuery: {e}")
        print("💡 Make sure you're using the same credentials as your retail app")
        return None, None

def generate_medical_data():
    """Generate synthetic medical data using Faker"""
    print("🔄 Generating synthetic medical data...")
    
    # Set seed for reproducible data
    Faker.seed(42)
    random.seed(42)
    np.random.seed(42)
    
    # 1. Patient Dimension (1000 patients)
    print("   👥 Generating 1,000 patients...")
    patients = []
    for i in range(1, 1001):
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
    
    # 2. Doctor Dimension (100 doctors)
    print("   👨‍⚕️ Generating 100 doctors...")
    doctors = []
    specialties = ['Cardiology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Dermatology', 
                  'Psychiatry', 'Oncology', 'Radiology', 'Emergency Medicine', 'Internal Medicine']
    
    for i in range(1, 101):
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
    
    # 3. Department Dimension (8 departments)
    print("   🏥 Generating 8 departments...")
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
    
    # 4. Treatment Dimension (200 treatments)
    print("   💊 Generating 200 treatments...")
    treatments = []
    treatment_types = ['Consultation', 'Surgery', 'Diagnostic Test', 'Therapy', 'Vaccination', 
                      'Emergency Care', 'Preventive Care', 'Rehabilitation', 'Medication', 'Monitoring']
    
    for i in range(1, 201):
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
    
    # 5. Medical Visits Fact Table (5000 visits)
    print("   🏥 Generating 5,000 medical visits...")
    visits = []
    visit_id = 1
    
    for _ in range(5000):
        # Random selections from dimensions
        patient = random.choice(patients)
        doctor = random.choice(doctors)
        department = random.choice(departments)
        treatment = random.choice(treatments)
        
        # Random visit date in last 2 years
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

def create_and_populate_tables(client, project_id):
    """Create and populate all tables in one go"""
    dataset_id = 'medical_facility'
    dataset_ref = f"{project_id}.{dataset_id}"
    
    print(f"🏗️ Setting up medical facility database...")
    
    # Create dataset
    try:
        client.get_dataset(dataset_ref)
        print(f"   ✅ Dataset {dataset_id} exists")
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"   ✅ Created dataset {dataset_id}")
    
    # Generate data
    data = generate_medical_data()
    
    # Upload each table
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    
    for table_name, df in data.items():
        table_ref = f"{project_id}.{dataset_id}.{table_name}"
        print(f"   📤 Uploading {table_name} ({len(df):,} records)...")
        
        try:
            job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            job.result()  # Wait for completion
            print(f"   ✅ {table_name} uploaded successfully")
        except Exception as e:
            print(f"   ❌ Error uploading {table_name}: {e}")
    
    return True

def main():
    """Main function"""
    print("🏥 Medical Facility Database Setup")
    print("=" * 50)
    
    # Connect to BigQuery
    client, project_id = get_bigquery_client()
    if client is None:
        return
    
    print(f"✅ Connected to BigQuery project: {project_id}")
    
    # Create and populate everything
    if create_and_populate_tables(client, project_id):
        print("\n🎉 Medical Database Setup Complete!")
        print(f"📊 Dataset: {project_id}.medical_facility")
        print("📋 Tables created:")
        print("   • patients (1,000 records)")
        print("   • doctors (100 records)")
        print("   • departments (8 records)")
        print("   • treatments (200 records)")
        print("   • visits (5,000 records)")
        print("\n🚀 Ready to run: streamlit run medical_web_app.py")
    else:
        print("❌ Setup failed")

if __name__ == "__main__":
    main()
