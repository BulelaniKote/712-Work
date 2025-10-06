#!/usr/bin/env python3
"""
Upload Medical Booking Data to BigQuery
This script uploads the medical booking Excel files to BigQuery
"""

import pandas as pd
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import json

def upload_medical_data():
    """Upload medical booking data to BigQuery"""
    
    # Configuration
    project_id = "moonlit-autumn-468306-p6"  # Same project as retail sales
    dataset_id = "medical_booking_system"
    
    # Data directory
    data_dir = "MedicalBookingApp/med/MedicalBookingApp/data"
    
    # File mappings
    files_to_upload = {
        "appointments": "Appointments (1).xls",
        "clients": "Clients (1).xls", 
        "dates": "Dates (1).xls",
        "patients": "Patients (1).xls",
        "specialists": "Specialists (1).xls",
        "timeslots": "TimeSlots (1).xls"
    }
    
    try:
        # Initialize BigQuery client
        print("Initializing BigQuery client...")
        
        # Use the same approach as the sales app - try Streamlit secrets first
        try:
            import streamlit as st
            if 'gcp_service_account' in st.secrets:
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                client = bigquery.Client(
                    credentials=credentials,
                    project=credentials.project_id
                )
                project_id = credentials.project_id  # Use project from credentials
                print("Using Streamlit secrets for authentication")
            else:
                raise Exception("No Streamlit secrets found")
        except:
            # For local development, try to use the same credentials as the sales app
            # Check if there's a .streamlit/secrets.toml file
            secrets_path = ".streamlit/secrets.toml"
            if os.path.exists(secrets_path):
                print("Found .streamlit/secrets.toml file")
                # Read secrets file
                with open(secrets_path, 'r') as f:
                    secrets_content = f.read()
                    print("Secrets file content preview:", secrets_content[:200] + "...")
                
                # Try to parse and use the secrets
                try:
                    import toml
                    secrets = toml.load(secrets_path)
                    if 'gcp_service_account' in secrets:
                        credentials = service_account.Credentials.from_service_account_info(
                            secrets["gcp_service_account"],
                            scopes=["https://www.googleapis.com/auth/cloud-platform"]
                        )
                        client = bigquery.Client(
                            credentials=credentials,
                            project=credentials.project_id
                        )
                        project_id = credentials.project_id
                        print("Using local secrets.toml for authentication")
                    else:
                        raise Exception("No gcp_service_account in secrets.toml")
                except Exception as e:
                    print(f"Error reading secrets.toml: {e}")
                    raise Exception("Could not use secrets.toml")
            else:
                print("No authentication method found")
                print("Please ensure you have either:")
                print("1. Streamlit secrets configured in Streamlit Cloud")
                print("2. A .streamlit/secrets.toml file with gcp_service_account")
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
        
        # Upload each file
        for table_name, filename in files_to_upload.items():
            file_path = os.path.join(data_dir, filename)
            
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
                
            print(f"Processing {filename}...")
            
            try:
                # Read Excel file (these are actually CSV files with .xls extension)
                df = pd.read_csv(file_path)
                print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")
                
                # Clean column names (remove spaces and special characters)
                df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('-', '_')
                
                # Display first few rows
                print(f"   Columns: {list(df.columns)}")
                print(f"   Sample data:")
                print(df.head(2).to_string())
                
                # Upload to BigQuery
                table_id = f"{project_id}.{dataset_id}.{table_name}"
                table_ref = client.dataset(dataset_id).table(table_name)
                
                # Configure job
                job_config = bigquery.LoadJobConfig(
                    write_disposition="WRITE_TRUNCATE",  # Overwrite existing data
                    autodetect=True,  # Auto-detect schema
                    source_format=bigquery.SourceFormat.CSV
                )
                
                # Upload data
                job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
                job.result()  # Wait for job to complete
                
                # Verify upload
                table = client.get_table(table_ref)
                print(f"   Uploaded {table.num_rows} rows to {table_id}")
                
            except Exception as e:
                print(f"   Error uploading {filename}: {e}")
                continue
        
        print("Medical data upload completed!")
        return True
        
    except Exception as e:
        print(f"Error in upload process: {e}")
        return False

if __name__ == "__main__":
    print("Medical Booking Data Upload to BigQuery")
    print("=" * 50)
    success = upload_medical_data()
    
    if success:
        print("\nUpload completed successfully!")
        print("You can now use the medical data in your Streamlit app")
    else:
        print("\nUpload failed. Please check the error messages above.")
