import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import json

st.title("🔍 BigQuery Connection Test")

st.markdown("Testing your BigQuery credentials...")

try:
    # Check if secrets are available
    if 'gcp_service_account' in st.secrets:
        st.success("✅ GCP service account found in secrets")
        
        # Display credential info
        creds = st.secrets["gcp_service_account"]
        st.write("**Project ID:**", creds.get('project_id', 'Not found'))
        st.write("**Client Email:**", creds.get('client_email', 'Not found'))
        
        # Test the connection
        st.markdown("---")
        st.subheader("Testing BigQuery Connection...")
        
        try:
            # Create credentials
            credentials = service_account.Credentials.from_service_account_info(
                creds,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            # Create client
            client = bigquery.Client(
                credentials=credentials,
                project=credentials.project_id
            )
            
            st.success("✅ BigQuery client created successfully!")
            st.write("**Connected to project:**", credentials.project_id)
            
            # Test a simple query
            st.markdown("---")
            st.subheader("Testing Query...")
            
            query = "SELECT 1 as test_value"
            result = client.query(query).result()
            
            for row in result:
                st.success(f"✅ Query successful! Result: {row.test_value}")
            
            # Test listing tables
            st.markdown("---")
            st.subheader("Available Tables:")
            
            dataset_id = "assignment_one_1"
            tables = list(client.list_tables(dataset_id))
            
            if tables:
                st.success(f"✅ Found {len(tables)} tables in dataset {dataset_id}")
                for table in tables:
                    st.write(f"- {table.table_id}")
            else:
                st.warning(f"⚠️ No tables found in dataset {dataset_id}")
                
        except Exception as e:
            st.error(f"❌ BigQuery connection failed: {e}")
            
            if "Incorrect padding" in str(e):
                st.markdown("""
                ### 🔧 "Incorrect padding" Error Fix:
                
                This error usually means the private key is corrupted. Try:
                
                1. **Download a fresh JSON key** from Google Cloud Console
                2. **Replace the private_key in your secrets.toml**
                3. **Make sure the private key has proper line breaks (\\n)**
                
                **Current private key format check:**
                """)
                
                private_key = creds.get('private_key', '')
                if private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                    st.success("✅ Private key format looks correct")
                else:
                    st.error("❌ Private key format looks incorrect")
                    
                st.code(private_key[:100] + "...", language="text")
                
    else:
        st.error("❌ GCP service account not found in secrets")
        st.info("Make sure your secrets.toml file has the [gcp_service_account] section")
        
except Exception as e:
    st.error(f"❌ Error reading secrets: {e}")

st.markdown("---")
st.subheader("Your Current Secrets Structure:")
st.code("""
[gcp_service_account]
type = "service_account"
project_id = "moonlit-autumn-468306-p6"
private_key_id = "783a4505ed2c8f63fe6048194ad4eea580f361d8"
private_key = "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
client_email = "bulelani-kote@moonlit-autumn-468306-p6.iam.gserviceaccount.com"
client_id = "116228650630636664819"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/bulelani-kote%40moonlit-autumn-468306-p6.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
""", language="toml")
