import streamlit as st
import pandas as pd
import os
from google.cloud import bigquery
from google.oauth2 import service_account
import json

def upload_data_to_bigquery():
    """Upload medical data to BigQuery"""
    
    st.title("📊 Upload Medical Data to BigQuery")
    st.markdown("Upload the medical booking system data to BigQuery")
    
    # Configuration
    project_id = "moonlit-autumn-468306-p6"
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
    
    if st.button("🚀 Upload All Medical Data to BigQuery", type="primary"):
        try:
            # Initialize BigQuery client
            st.info("Initializing BigQuery client...")
            
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
                st.success(f"✅ Connected to BigQuery project: {project_id}")
            else:
                st.error("❌ BigQuery credentials not found in Streamlit secrets")
                return
            
            # Create dataset if it doesn't exist
            st.info(f"Creating dataset: {dataset_id}")
            dataset_ref = client.dataset(dataset_id)
            try:
                dataset = client.get_dataset(dataset_ref)
                st.info(f"Dataset {dataset_id} already exists")
            except:
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"
                dataset = client.create_dataset(dataset, timeout=30)
                st.success(f"✅ Created dataset: {dataset_id}")
            
            # Upload each file
            progress_bar = st.progress(0)
            total_files = len(files_to_upload)
            
            for i, (table_name, filename) in enumerate(files_to_upload.items()):
                file_path = os.path.join(data_dir, filename)
                
                if not os.path.exists(file_path):
                    st.warning(f"⚠️ File not found: {file_path}")
                    continue
                
                st.info(f"Processing {filename}...")
                
                try:
                    # Read Excel file (these are actually CSV files with .xls extension)
                    df = pd.read_csv(file_path)
                    st.write(f"   📋 Loaded {len(df)} rows, {len(df.columns)} columns")
                    
                    # Clean column names (remove spaces and special characters)
                    df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('-', '_')
                    
                    # Display sample data
                    with st.expander(f"Sample data from {filename}"):
                        st.dataframe(df.head())
                    
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
                    st.success(f"   ✅ Uploaded {table.num_rows} rows to {table_id}")
                    
                except Exception as e:
                    st.error(f"   ❌ Error uploading {filename}: {e}")
                    continue
                
                # Update progress
                progress_bar.progress((i + 1) / total_files)
            
            # Upload users.json data
            st.info("Processing users.json...")
            users_file_path = os.path.join(data_dir, "users.json")
            if os.path.exists(users_file_path):
                try:
                    with open(users_file_path, 'r') as f:
                        users_data = json.load(f)
                    
                    # Convert to DataFrame
                    users_list = []
                    for username, user_data in users_data.items():
                        user_row = {
                            'username': username,
                            'email': user_data.get('email', ''),
                            'password': user_data.get('password', ''),
                            'created_at': user_data.get('created_at', ''),
                            'role': user_data.get('role', 'patient')
                        }
                        users_list.append(user_row)
                    
                    users_df = pd.DataFrame(users_list)
                    st.write(f"   📋 Loaded {len(users_df)} users")
                    
                    # Upload users table
                    table_id = f"{project_id}.{dataset_id}.users"
                    table_ref = client.dataset(dataset_id).table("users")
                    
                    job_config = bigquery.LoadJobConfig(
                        write_disposition="WRITE_TRUNCATE",
                        autodetect=True,
                        source_format=bigquery.SourceFormat.CSV
                    )
                    
                    job = client.load_table_from_dataframe(users_df, table_ref, job_config=job_config)
                    job.result()
                    
                    table = client.get_table(table_ref)
                    st.success(f"   ✅ Uploaded {table.num_rows} users to {table_id}")
                    
                    # Upload appointments from users.json
                    appointments_list = []
                    for username, user_data in users_data.items():
                        if 'appointments' in user_data:
                            for appointment in user_data['appointments']:
                                appointment_row = {
                                    'username': username,
                                    'name': appointment.get('name', ''),
                                    'email': appointment.get('email', ''),
                                    'specialty': appointment.get('specialty', ''),
                                    'date': appointment.get('date', ''),
                                    'time': appointment.get('time', ''),
                                    'reason': appointment.get('reason', ''),
                                    'status': appointment.get('status', ''),
                                    'created_at': appointment.get('created_at', '')
                                }
                                appointments_list.append(appointment_row)
                    
                    if appointments_list:
                        appointments_df = pd.DataFrame(appointments_list)
                        st.write(f"   📋 Loaded {len(appointments_df)} appointments from users.json")
                        
                        # Upload appointments table
                        table_id = f"{project_id}.{dataset_id}.appointments"
                        table_ref = client.dataset(dataset_id).table("appointments")
                        
                        job_config = bigquery.LoadJobConfig(
                            write_disposition="WRITE_TRUNCATE",
                            autodetect=True,
                            source_format=bigquery.SourceFormat.CSV
                        )
                        
                        job = client.load_table_from_dataframe(appointments_df, table_ref, job_config=job_config)
                        job.result()
                        
                        table = client.get_table(table_ref)
                        st.success(f"   ✅ Uploaded {table.num_rows} appointments to {table_id}")
                    
                except Exception as e:
                    st.error(f"   ❌ Error uploading users.json: {e}")
            
            st.success("🎉 Medical data upload completed successfully!")
            st.info("You can now use the medical booking system with BigQuery data!")
            
        except Exception as e:
            st.error(f"❌ Error in upload process: {e}")

def app():
    """Main data upload app"""
    upload_data_to_bigquery()
