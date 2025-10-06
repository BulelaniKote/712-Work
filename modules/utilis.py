import streamlit as st
import hashlib
import json
import os
from datetime import datetime
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

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
                st.error(f"Error creating BigQuery client from secrets: {e}")
                st.info("Please check your Streamlit Cloud secrets configuration")
                return None, None
                
        else:
            st.error("BigQuery credentials not found in Streamlit secrets")
            st.info("Please add your GCP service account credentials to Streamlit Cloud secrets")
            st.info("Go to your app settings → Secrets and add the gcp_service_account section")
            return None, None
            
    except Exception as e:
        st.error(f"Error connecting to BigQuery: {e}")
        st.info("Check your Streamlit Cloud secrets configuration")
        return None, None

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def register_user(username, email, password):
    """Register a new user in BigQuery"""
    # Ensure dataset exists first
    ensure_dataset_exists()
    
    client, project_id = get_bigquery_client()
    if not client:
        return False, "Database connection failed"
    
    try:
        # Check if user already exists
        query = f"""
        SELECT username FROM `{project_id}.medical_booking_system.users`
        WHERE username = @username
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", username)
            ]
        )
        
        result = client.query(query, job_config=job_config).to_dataframe()
        
        if not result.empty:
            return False, "Username already exists"
        
        # Check if email already exists
        query = f"""
        SELECT email FROM `{project_id}.medical_booking_system.users`
        WHERE email = @email
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("email", "STRING", email)
            ]
        )
        
        result = client.query(query, job_config=job_config).to_dataframe()
        
        if not result.empty:
            return False, "Email already registered"
        
        # Insert new user
        query = f"""
        INSERT INTO `{project_id}.medical_booking_system.users`
        (username, email, password, created_at, role)
        VALUES (@username, @email, @password, @created_at, @role)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", username),
                bigquery.ScalarQueryParameter("email", "STRING", email),
                bigquery.ScalarQueryParameter("password", "STRING", hash_password(password)),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now()),
                bigquery.ScalarQueryParameter("role", "STRING", "patient")
            ]
        )
        
        client.query(query, job_config=job_config)
        
        return True, "User registered successfully"
        
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def authenticate_user(username, password):
    """Authenticate user login from BigQuery"""
    # Ensure dataset exists first
    ensure_dataset_exists()
    
    client, project_id = get_bigquery_client()
    if not client:
        return False, "Database connection failed"
    
    try:
        query = f"""
        SELECT username, password FROM `{project_id}.medical_booking_system.users`
        WHERE username = @username
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", username)
            ]
        )
        
        result = client.query(query, job_config=job_config).to_dataframe()
        
        if result.empty:
            return False, "Invalid username or password"
        
        stored_password = result.iloc[0]['password']
        
        if verify_password(password, stored_password):
            return True, "Login successful"
        else:
            return False, "Invalid username or password"
            
    except Exception as e:
        return False, f"Authentication failed: {str(e)}"

def is_logged_in():
    """Check if user is logged in"""
    return 'username' in st.session_state and st.session_state.username is not None

def logout():
    """Logout user"""
    if 'username' in st.session_state:
        del st.session_state.username
    st.rerun()

def get_current_user_data():
    """Get current user's data from BigQuery"""
    if not is_logged_in():
        return None
    
    # Ensure dataset exists first
    ensure_dataset_exists()
    
    client, project_id = get_bigquery_client()
    if not client:
        return None
    
    try:
        query = f"""
        SELECT username, email, created_at, role FROM `{project_id}.medical_booking_system.users`
        WHERE username = @username
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", st.session_state.username)
            ]
        )
        
        result = client.query(query, job_config=job_config).to_dataframe()
        
        if result.empty:
            return None
        
        user_data = result.iloc[0].to_dict()
        
        # Get user's appointments
        appointments_query = f"""
        SELECT * FROM `{project_id}.medical_booking_system.appointments`
        WHERE username = @username
        ORDER BY created_at DESC
        """
        
        appointments_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", st.session_state.username)
            ]
        )
        
        appointments_result = client.query(appointments_query, appointments_job_config).to_dataframe()
        
        if not appointments_result.empty:
            user_data['appointments'] = appointments_result.to_dict('records')
        else:
            user_data['appointments'] = []
        
        return user_data
        
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return None

def add_appointment(appointment_data):
    """Add appointment to BigQuery"""
    if not is_logged_in():
        return False
    
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        query = f"""
        INSERT INTO `{project_id}.medical_booking_system.appointments`
        (username, name, email, specialty, date, time, reason, status, created_at)
        VALUES (@username, @name, @email, @specialty, @date, @time, @reason, @status, @created_at)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", st.session_state.username),
                bigquery.ScalarQueryParameter("name", "STRING", appointment_data.get('name', '')),
                bigquery.ScalarQueryParameter("email", "STRING", appointment_data.get('email', '')),
                bigquery.ScalarQueryParameter("specialty", "STRING", appointment_data.get('specialty', '')),
                bigquery.ScalarQueryParameter("date", "DATE", appointment_data.get('date', '')),
                bigquery.ScalarQueryParameter("time", "TIME", appointment_data.get('time', '')),
                bigquery.ScalarQueryParameter("reason", "STRING", appointment_data.get('reason', '')),
                bigquery.ScalarQueryParameter("status", "STRING", appointment_data.get('status', 'confirmed')),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now())
            ]
        )
        
        client.query(query, job_config=job_config)
        return True
        
    except Exception as e:
        st.error(f"Error adding appointment: {e}")
        return False

def is_admin():
    """Check if current user is an admin"""
    if not is_logged_in():
        return False
    
    user_data = get_current_user_data()
    return user_data and user_data.get('role') == 'admin'

def get_all_users():
    """Get all users data for admin purposes from BigQuery"""
    client, project_id = get_bigquery_client()
    if not client:
        return {}
    
    try:
        query = f"""
        SELECT username, email, created_at, role FROM `{project_id}.medical_booking_system.users`
        ORDER BY created_at DESC
        """
        
        result = client.query(query).to_dataframe()
        
        if result.empty:
            return {}
        
        users = {}
        for _, row in result.iterrows():
            users[row['username']] = {
                'email': row['email'],
                'created_at': row['created_at'].isoformat() if pd.notna(row['created_at']) else '',
                'role': row['role'],
                'appointments': []
            }
        
        # Get appointments for each user
        appointments_query = f"""
        SELECT username, name, email, specialty, date, time, reason, status, created_at
        FROM `{project_id}.medical_booking_system.appointments`
        ORDER BY created_at DESC
        """
        
        appointments_result = client.query(appointments_query).to_dataframe()
        
        if not appointments_result.empty:
            for _, appointment in appointments_result.iterrows():
                username = appointment['username']
                if username in users:
                    if 'appointments' not in users[username]:
                        users[username]['appointments'] = []
                    
                    users[username]['appointments'].append({
                        'name': appointment['name'],
                        'email': appointment['email'],
                        'specialty': appointment['specialty'],
                        'date': str(appointment['date']) if pd.notna(appointment['date']) else '',
                        'time': str(appointment['time']) if pd.notna(appointment['time']) else '',
                        'reason': appointment['reason'],
                        'status': appointment['status'],
                        'created_at': appointment['created_at'].isoformat() if pd.notna(appointment['created_at']) else ''
                    })
        
        return users
        
    except Exception as e:
        st.error(f"Error fetching all users: {e}")
        return {}

def get_all_appointments():
    """Get all appointments from all users for admin analytics from BigQuery"""
    client, project_id = get_bigquery_client()
    if not client:
        return []
    
    try:
        query = f"""
        SELECT a.*, u.email as user_email
        FROM `{project_id}.medical_booking_system.appointments` a
        JOIN `{project_id}.medical_booking_system.users` u ON a.username = u.username
        ORDER BY a.created_at DESC
        """
        
        result = client.query(query).to_dataframe()
        
        if result.empty:
            return []
        
        appointments = []
        for _, row in result.iterrows():
            appointments.append({
                'username': row['username'],
                'user_email': row['user_email'],
                'name': row['name'],
                'email': row['email'],
                'specialty': row['specialty'],
                'date': str(row['date']) if pd.notna(row['date']) else '',
                'time': str(row['time']) if pd.notna(row['time']) else '',
                'reason': row['reason'],
                'status': row['status'],
                'created_at': row['created_at'].isoformat() if pd.notna(row['created_at']) else ''
            })
        
        return appointments
        
    except Exception as e:
        st.error(f"Error fetching all appointments: {e}")
        return []

def get_specialist_performance():
    """Get specialist performance data from BigQuery"""
    appointments = get_all_appointments()
    specialist_stats = {}
    
    for appointment in appointments:
        specialty = appointment.get('specialty', 'Unknown')
        if specialty not in specialist_stats:
            specialist_stats[specialty] = {
                'total_appointments': 0,
                'confirmed_appointments': 0,
                'cancelled_appointments': 0,
                'unique_patients': set(),
                'monthly_appointments': {}
            }
        
        stats = specialist_stats[specialty]
        stats['total_appointments'] += 1
        
        status = appointment.get('status', 'unknown').lower()
        if status == 'confirmed':
            stats['confirmed_appointments'] += 1
        elif status == 'cancelled':
            stats['cancelled_appointments'] += 1
        
        stats['unique_patients'].add(appointment.get('username', ''))
        
        # Monthly stats
        date_str = appointment.get('date', '')
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                month_key = f"{date_obj.year}-{date_obj.month:02d}"
                stats['monthly_appointments'][month_key] = stats['monthly_appointments'].get(month_key, 0) + 1
            except:
                pass
    
    # Convert sets to counts and format data
    for specialty, stats in specialist_stats.items():
        stats['unique_patients'] = len(stats['unique_patients'])
        stats['confirmation_rate'] = (stats['confirmed_appointments'] / stats['total_appointments'] * 100) if stats['total_appointments'] > 0 else 0
    
    return specialist_stats

def ensure_dataset_exists():
    """Ensure the medical_booking_system dataset exists in BigQuery"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        dataset_id = "medical_booking_system"
        dataset_ref = client.dataset(dataset_id)
        
        # Check if dataset exists
        try:
            client.get_dataset(dataset_ref)
            return True  # Dataset exists
        except:
            # Dataset doesn't exist, create it
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset = client.create_dataset(dataset, timeout=30)
            st.success(f"Created dataset: {dataset_id}")
            
            # Create tables after dataset is created
            create_tables()
            return True
            
    except Exception as e:
        st.error(f"Error ensuring dataset exists: {e}")
        return False

def create_tables():
    """Create the users and appointments tables in BigQuery"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        dataset_id = "medical_booking_system"
        
        # Create users table
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
        
        # Create appointments table
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
        
        # Create admin user
        create_admin_user_auto()
        
        return True
        
    except Exception as e:
        st.error(f"Error creating tables: {e}")
        return False

def create_admin_user_auto():
    """Create default admin user automatically"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        # Check if admin user exists
        query = f"""
        SELECT username FROM `{project_id}.medical_booking_system.users`
        WHERE username = 'admin'
        """
        
        result = client.query(query).to_dataframe()
        
        if not result.empty:
            return False  # Admin already exists
        
        # Create admin user
        query = f"""
        INSERT INTO `{project_id}.medical_booking_system.users`
        (username, email, password, created_at, role)
        VALUES (@username, @email, @password, @created_at, @role)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", "admin"),
                bigquery.ScalarQueryParameter("email", "STRING", "admin@medicalcenter.com"),
                bigquery.ScalarQueryParameter("password", "STRING", hash_password("admin123")),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now()),
                bigquery.ScalarQueryParameter("role", "STRING", "admin")
            ]
        )
        
        client.query(query, job_config=job_config)
        return True
        
    except Exception as e:
        st.error(f"Error creating admin user: {e}")
        return False

def create_admin_user():
    """Create default admin user if it doesn't exist in BigQuery"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        # Check if admin user exists
        query = f"""
        SELECT username FROM `{project_id}.medical_booking_system.users`
        WHERE username = 'admin'
        """
        
        result = client.query(query).to_dataframe()
        
        if not result.empty:
            return False  # Admin already exists
        
        # Create admin user
        query = f"""
        INSERT INTO `{project_id}.medical_booking_system.users`
        (username, email, password, created_at, role)
        VALUES (@username, @email, @password, @created_at, @role)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", "admin"),
                bigquery.ScalarQueryParameter("email", "STRING", "admin@medicalcenter.com"),
                bigquery.ScalarQueryParameter("password", "STRING", hash_password("admin123")),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now()),
                bigquery.ScalarQueryParameter("role", "STRING", "admin")
            ]
        )
        
        client.query(query, job_config=job_config)
        return True
        
    except Exception as e:
        st.error(f"Error creating admin user: {e}")
        return False