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
    """Register a new user using both JSON file and BigQuery"""
    try:
        users_file_path = "users.json"
        
        # Load existing users
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as f:
                users_data = json.load(f)
        else:
            users_data = {}
        
        # Check if user already exists
        if username in users_data:
            return False, "Username already exists"
        
        # Check if email already exists
        for user_info in users_data.values():
            if user_info.get('email') == email:
                return False, "Email already exists"
        
        # Add new user to JSON
        users_data[username] = {
            "email": email,
            "password": hash_password(password),
            "created_at": datetime.now().isoformat(),
            "appointments": []
        }
        
        # Save back to JSON file
        with open(users_file_path, 'w') as f:
            json.dump(users_data, f, indent=2)
        
        # Also save to BigQuery
        user_data_for_bigquery = {
            'username': username,
            'email': email,
            'password': hash_password(password),
            'role': 'patient'
        }
        
        bigquery_success = add_user_to_bigquery(user_data_for_bigquery)
        
        if bigquery_success:
            return True, "User registered successfully in both local storage and BigQuery"
        else:
            return True, "User registered locally, but BigQuery sync failed"
        
    except Exception as e:
        return False, f"Registration failed: {str(e)}"

def authenticate_user(username, password):
    """Authenticate user login from JSON file"""
    try:
        users_file_path = "users.json"
        
        # Load users data
        if not os.path.exists(users_file_path):
            return False, "No users found"
        
        with open(users_file_path, 'r') as f:
            users_data = json.load(f)
        
        # Check if user exists
        if username not in users_data:
            return False, "Invalid username or password"
        
        user_info = users_data[username]
        stored_password = user_info.get('password', '')
        
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
    """Get current user's data from JSON file"""
    if not is_logged_in():
        return None
    
    try:
        users_file_path = "users.json"
        
        # Load users data
        if not os.path.exists(users_file_path):
            return None
        
        with open(users_file_path, 'r') as f:
            users_data = json.load(f)
        
        # Get current user data
        username = st.session_state.username
        if username not in users_data:
            return None
        
        user_info = users_data[username]
        user_data = {
            'username': username,
            'email': user_info.get('email', ''),
            'created_at': user_info.get('created_at', ''),
            'role': 'patient',  # Default role
            'appointments': user_info.get('appointments', [])
        }
        
        return user_data
        
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        return None

def add_appointment(appointment_data):
    """Add appointment to both JSON file and BigQuery"""
    if not is_logged_in():
        return False
    
    try:
        users_file_path = "users.json"
        
        # Load existing users
        if os.path.exists(users_file_path):
            with open(users_file_path, 'r') as f:
                users_data = json.load(f)
        else:
            users_data = {}
        
        username = st.session_state.username
        if username not in users_data:
            return False
        
        # Add appointment to user's data
        appointment = {
            'name': appointment_data.get('name', username),
            'email': appointment_data.get('email', users_data[username].get('email', '')),
            'specialty': appointment_data.get('specialty', ''),
            'date': appointment_data.get('date', ''),
            'time': appointment_data.get('time', ''),
            'reason': appointment_data.get('reason', ''),
            'status': appointment_data.get('status', 'confirmed'),
            'created_at': datetime.now().isoformat()
        }
        
        if 'appointments' not in users_data[username]:
            users_data[username]['appointments'] = []
        
        users_data[username]['appointments'].append(appointment)
        
        # Save back to JSON file
        with open(users_file_path, 'w') as f:
            json.dump(users_data, f, indent=2)
        
        # Also save to BigQuery
        bigquery_success = add_appointment_to_bigquery(appointment)
        
        if bigquery_success:
            st.success("✅ Appointment saved to both local storage and BigQuery")
        else:
            st.warning("⚠️ Appointment saved locally, but BigQuery sync failed")
        
        return True
        
    except Exception as e:
        st.error(f"Error adding appointment: {e}")
        return False

def is_admin():
    """Check if current user is an admin"""
    if not is_logged_in():
        return False
    
    # Check if username is 'admin' or if user has admin role
    username = st.session_state.username
    if username == 'admin':
        return True
    
    user_data = get_current_user_data()
    return user_data and user_data.get('role') == 'admin'

def get_all_users():
    """Get all users data for admin purposes from JSON file"""
    try:
        users_file_path = "users.json"
        
        # Load users data
        if not os.path.exists(users_file_path):
            return {}
        
        with open(users_file_path, 'r') as f:
            users_data = json.load(f)
        
        # Transform to expected format
        users = {}
        for username, user_info in users_data.items():
            users[username] = {
                'email': user_info.get('email', ''),
                'created_at': user_info.get('created_at', ''),
                'role': 'admin' if username == 'admin' else 'patient',
                'appointments': user_info.get('appointments', [])
            }
        
        return users
        
    except Exception as e:
        st.error(f"Error fetching all users: {e}")
        return {}

def get_all_appointments():
    """Get all appointments from all users for admin analytics from JSON file"""
    try:
        users_file_path = "users.json"
        
        # Load users data
        if not os.path.exists(users_file_path):
            return []
        
        with open(users_file_path, 'r') as f:
            users_data = json.load(f)
        
        appointments = []
        for username, user_info in users_data.items():
            user_appointments = user_info.get('appointments', [])
            for appointment in user_appointments:
                appointments.append({
                    'username': username,
                    'user_email': user_info.get('email', ''),
                    'name': appointment.get('name', ''),
                    'email': appointment.get('email', ''),
                    'specialty': appointment.get('specialty', ''),
                    'date': appointment.get('date', ''),
                    'time': appointment.get('time', ''),
                    'reason': appointment.get('reason', ''),
                    'status': appointment.get('status', ''),
                    'created_at': appointment.get('created_at', '')
                })
        
        # Sort by created_at descending
        appointments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
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
    """Ensure the assignment_one_1 dataset exists in BigQuery"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        dataset_id = "assignment_one_1"
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
        dataset_id = "assignment_one_1"
        
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
        SELECT username FROM `{project_id}.assignment_one_1.users`
        WHERE username = 'admin'
        """
        
        result = client.query(query).to_dataframe()
        
        if not result.empty:
            return False  # Admin already exists
        
        # Create admin user
        query = f"""
        INSERT INTO `{project_id}.assignment_one_1.users`
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

def get_medical_specialists():
    """Get specialists data from the uploaded medical data tables"""
    client, project_id = get_bigquery_client()
    if not client:
        return []
    
    try:
        # Try with trailing space first (like appointments table)
        try:
            query = f"""
            SELECT * FROM `{project_id}.assignment_one_1.specialists `
            ORDER BY FirstName, LastName
            """
            result = client.query(query).to_dataframe()
            # Debug: Show column names
            print(f"Specialists columns (with space): {list(result.columns)}")
            return result.to_dict('records')
        except:
            # If that fails, try without trailing space
            query = f"""
            SELECT * FROM `{project_id}.assignment_one_1.specialists`
            ORDER BY FirstName, LastName
            """
            result = client.query(query).to_dataframe()
            # Debug: Show column names
            print(f"Specialists columns (no space): {list(result.columns)}")
            return result.to_dict('records')
        
    except Exception as e:
        st.error(f"Error fetching specialists: {e}")
        return []

def get_medical_patients():
    """Get patients data from the uploaded medical data tables"""
    client, project_id = get_bigquery_client()
    if not client:
        return []
    
    try:
        query = f"""
        SELECT * FROM `{project_id}.assignment_one_1.patients`
        ORDER BY FirstName, LastName
        """
        
        result = client.query(query).to_dataframe()
        return result.to_dict('records')
        
    except Exception as e:
        st.error(f"Error fetching patients: {e}")
        return []

def get_medical_appointments():
    """Get appointments data from the uploaded medical data tables"""
    client, project_id = get_bigquery_client()
    if not client:
        return []
    
    try:
        # First, let's try a simple query to check if the table exists
        # Note: table name has trailing space
        simple_query = f"""
        SELECT * FROM `{project_id}.assignment_one_1.appointments `
        LIMIT 5
        """
        
        st.info(f"Querying: {project_id}.assignment_one_1.appointments")
        result = client.query(simple_query).to_dataframe()
        
        if result.empty:
            st.warning("Appointments table exists but is empty")
            return []
        
        st.success(f"Found {len(result)} appointments in BigQuery")
        
        # Now try the full query with joins
        full_query = f"""
        SELECT 
            a.*,
            p.FirstName as PatientFirstName,
            p.LastName as PatientLastName,
            s.FirstName as SpecialistFirstName,
            s.LastName as SpecialistLastName,
            s.Specialty,
            d.Year,
            d.Month,
            d.Day,
            d.Weekday,
            t.StartTime,
            t.EndTime,
            t.Label as TimeLabel
        FROM `{project_id}.assignment_one_1.appointments ` a
        LEFT JOIN `{project_id}.assignment_one_1.patients` p ON a.PatientID = p.PatientID
        LEFT JOIN `{project_id}.assignment_one_1.specialists` s ON a.SpecialistID = s.SpecialistID
        LEFT JOIN `{project_id}.assignment_one_1.dates` d ON a.DateKey = d.DateKey
        LEFT JOIN `{project_id}.assignment_one_1.timeslots ` t ON a.TimeSlotID = t.TimeSlotID
        ORDER BY a.DateKey, t.StartTime
        """
        
        full_result = client.query(full_query).to_dataframe()
        return full_result.to_dict('records')
        
    except Exception as e:
        st.error(f"Error fetching medical appointments: {e}")
        st.info("Trying to list available tables...")
        
        # Try to list tables to debug
        try:
            dataset_ref = client.dataset("assignment_one_1")
            tables = list(client.list_tables(dataset_ref))
            table_names = [table.table_id for table in tables]
            st.info(f"Available tables in assignment_one_1: {table_names}")
        except Exception as list_error:
            st.error(f"Could not list tables: {list_error}")
        
        return []

def get_medical_clients():
    """Get clients data from the uploaded medical data tables"""
    client, project_id = get_bigquery_client()
    if not client:
        return []
    
    try:
        query = f"""
        SELECT * FROM `{project_id}.assignment_one_1.clients`
        ORDER BY FirstName, LastName
        """
        
        result = client.query(query).to_dataframe()
        return result.to_dict('records')
        
    except Exception as e:
        st.error(f"Error fetching clients: {e}")
        return []

def get_medical_dates():
    """Get dates data from the uploaded medical data tables"""
    client, project_id = get_bigquery_client()
    if not client:
        return []
    
    try:
        query = f"""
        SELECT * FROM `{project_id}.assignment_one_1.dates`
        ORDER BY DateKey
        """
        
        result = client.query(query).to_dataframe()
        return result.to_dict('records')
        
    except Exception as e:
        st.error(f"Error fetching dates: {e}")
        return []

def get_medical_timeslots():
    """Get timeslots data from the uploaded medical data tables"""
    client, project_id = get_bigquery_client()
    if not client:
        return []
    
    try:
        query = f"""
        SELECT * FROM `{project_id}.assignment_one_1.timeslots `
        ORDER BY StartTime
        """
        
        result = client.query(query).to_dataframe()
        return result.to_dict('records')
        
    except Exception as e:
        st.error(f"Error fetching timeslots: {e}")
        return []

def create_admin_user():
    """Create default admin user if it doesn't exist in BigQuery"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        # Check if admin user exists
        query = f"""
        SELECT username FROM `{project_id}.assignment_one_1.users`
        WHERE username = 'admin'
        """
        
        result = client.query(query).to_dataframe()
        
        if not result.empty:
            return False  # Admin already exists
        
        # Create admin user
        query = f"""
        INSERT INTO `{project_id}.assignment_one_1.users`
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

def add_appointment_to_bigquery(appointment_data):
    """Add appointment to BigQuery appointments table"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        # Ensure dataset and tables exist
        ensure_dataset_exists()
        
        # Prepare appointment data for BigQuery
        username = st.session_state.username
        appointment_date = datetime.strptime(appointment_data['date'], '%Y-%m-%d').date()
        
        # Handle different time formats
        time_str = appointment_data['time']
        try:
            # Try parsing as time object first
            if isinstance(time_str, str):
                if ':' in time_str:
                    # Handle formats like "09:00:00" or "09:00 - 10:00 (Morning)"
                    time_part = time_str.split(' - ')[0]  # Get first part if range
                    time_part = time_part.split(' (')[0]  # Remove label if present
                    appointment_time = datetime.strptime(time_part, '%H:%M:%S').time()
                else:
                    appointment_time = datetime.strptime(time_str, '%H:%M:%S').time()
            else:
                appointment_time = time_str
        except:
            # Fallback to current time if parsing fails
            appointment_time = datetime.now().time()
        
        # Insert appointment into BigQuery
        query = f"""
        INSERT INTO `{project_id}.assignment_one_1.appointments`
        (username, name, email, specialty, date, time, reason, status, created_at)
        VALUES (@username, @name, @email, @specialty, @date, @time, @reason, @status, @created_at)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", username),
                bigquery.ScalarQueryParameter("name", "STRING", appointment_data['name']),
                bigquery.ScalarQueryParameter("email", "STRING", appointment_data['email']),
                bigquery.ScalarQueryParameter("specialty", "STRING", appointment_data['specialty']),
                bigquery.ScalarQueryParameter("date", "DATE", appointment_date),
                bigquery.ScalarQueryParameter("time", "TIME", appointment_time),
                bigquery.ScalarQueryParameter("reason", "STRING", appointment_data.get('reason', '')),
                bigquery.ScalarQueryParameter("status", "STRING", appointment_data['status']),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now())
            ]
        )
        
        client.query(query, job_config=job_config)
        return True
        
    except Exception as e:
        st.error(f"Error adding appointment to BigQuery: {e}")
        return False

def add_user_to_bigquery(user_data):
    """Add user to BigQuery users table"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        # Ensure dataset and tables exist
        ensure_dataset_exists()
        
        # Check if user already exists
        query = f"""
        SELECT username FROM `{project_id}.assignment_one_1.users`
        WHERE username = @username
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", user_data['username'])
            ]
        )
        
        result = client.query(query, job_config=job_config).to_dataframe()
        
        if not result.empty:
            return True  # User already exists
        
        # Insert user into BigQuery
        query = f"""
        INSERT INTO `{project_id}.assignment_one_1.users`
        (username, email, password, created_at, role)
        VALUES (@username, @email, @password, @created_at, @role)
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("username", "STRING", user_data['username']),
                bigquery.ScalarQueryParameter("email", "STRING", user_data['email']),
                bigquery.ScalarQueryParameter("password", "STRING", user_data['password']),
                bigquery.ScalarQueryParameter("created_at", "TIMESTAMP", datetime.now()),
                bigquery.ScalarQueryParameter("role", "STRING", user_data.get('role', 'patient'))
            ]
        )
        
        client.query(query, job_config=job_config)
        return True
        
    except Exception as e:
        st.error(f"Error adding user to BigQuery: {e}")
        return False

def sync_existing_data_to_bigquery():
    """Sync existing JSON data to BigQuery (one-time migration)"""
    client, project_id = get_bigquery_client()
    if not client:
        return False
    
    try:
        # Ensure dataset and tables exist
        ensure_dataset_exists()
        
        users_file_path = "users.json"
        if not os.path.exists(users_file_path):
            return True  # No data to sync
        
        with open(users_file_path, 'r') as f:
            users_data = json.load(f)
        
        synced_users = 0
        synced_appointments = 0
        
        # Sync users
        for username, user_info in users_data.items():
            user_data_for_bigquery = {
                'username': username,
                'email': user_info.get('email', ''),
                'password': user_info.get('password', ''),
                'role': 'admin' if username == 'admin' else 'patient'
            }
            
            if add_user_to_bigquery(user_data_for_bigquery):
                synced_users += 1
            
            # Sync appointments for this user
            appointments = user_info.get('appointments', [])
            for appointment in appointments:
                if add_appointment_to_bigquery(appointment):
                    synced_appointments += 1
        
        st.success(f"✅ Data sync completed: {synced_users} users, {synced_appointments} appointments synced to BigQuery")
        return True
        
    except Exception as e:
        st.error(f"Error syncing data to BigQuery: {e}")
        return False