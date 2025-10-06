#!/usr/bin/env python3
"""
Setup Medical Booking System BigQuery Tables
This script creates the necessary tables for the medical booking system
"""

import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

def setup_bigquery_tables():
    """Create BigQuery tables for medical booking system"""
    
    # Configuration
    project_id = "moonlit-autumn-468306-p6"  # Same project as retail sales
    dataset_id = "medical_booking_system"
    
    try:
        # Initialize BigQuery client
        print("Initializing BigQuery client...")
        
        # Use Streamlit secrets
        if 'gcp_service_account' in st.secrets:
            credentials = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            client = bigquery.Client(
                credentials=credentials,
                project=credentials.project_id
            )
            project_id = credentials.project_id
            print("Using Streamlit secrets for authentication")
        else:
            print("No Streamlit secrets found")
            return False
        
        # Create dataset if it doesn't exist
        print(f"Creating dataset: {dataset_id}")
        dataset_ref = client.dataset(dataset_id)
        try:
            dataset = client.get_dataset(dataset_ref)
            print(f"Dataset {dataset_id} already exists")
        except:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset = client.create_dataset(dataset, timeout=30)
            print(f"Created dataset: {dataset_id}")
        
        # Create users table
        print("Creating users table...")
        users_table_id = f"{project_id}.{dataset_id}.users"
        users_schema = [
            bigquery.SchemaField("username", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("password", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("role", "STRING", mode="REQUIRED")
        ]
        
        users_table = bigquery.Table(users_table_id, schema=users_schema)
        users_table = client.create_table(users_table, exists_ok=True)
        print(f"Created users table: {users_table_id}")
        
        # Create appointments table
        print("Creating appointments table...")
        appointments_table_id = f"{project_id}.{dataset_id}.appointments"
        appointments_schema = [
            bigquery.SchemaField("username", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("specialty", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
            bigquery.SchemaField("time", "TIME", mode="REQUIRED"),
            bigquery.SchemaField("reason", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED")
        ]
        
        appointments_table = bigquery.Table(appointments_table_id, schema=appointments_schema)
        appointments_table = client.create_table(appointments_table, exists_ok=True)
        print(f"Created appointments table: {appointments_table_id}")
        
        print("Medical booking system tables setup completed!")
        return True
        
    except Exception as e:
        print(f"Error in setup process: {e}")
        return False

if __name__ == "__main__":
    print("Medical Booking System BigQuery Tables Setup")
    print("=" * 50)
    success = setup_bigquery_tables()
    
    if success:
        print("\nSetup completed successfully!")
        print("You can now use the medical booking system with BigQuery")
    else:
        print("\nSetup failed. Please check the error messages above.")
