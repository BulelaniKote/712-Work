#!/usr/bin/env python3
"""
Simple test script to verify BigQuery connection
"""

import os
import sys
from google.cloud import bigquery
from google.oauth2 import service_account

def test_bigquery_connection():
    """Test BigQuery connection using service account credentials"""
    
    print("🔗 Testing BigQuery Connection...")
    
    try:
        # Check if credentials file exists
        credentials_path = "istanbul_sales_analysis/API.JSON"
        if not os.path.exists(credentials_path):
            print(f"❌ Credentials file not found: {credentials_path}")
            return False
        
        print(f"✅ Found credentials file: {credentials_path}")
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        print(f"✅ Loaded service account: {credentials.service_account_email}")
        print(f"✅ Project ID: {credentials.project_id}")
        
        # Initialize BigQuery client
        client = bigquery.Client(
            credentials=credentials,
            project=credentials.project_id
        )
        
        print("✅ BigQuery client initialized successfully")
        
        # Test basic connection
        datasets = list(client.list_datasets())
        print(f"✅ Found {len(datasets)} datasets in project")
        
        # Test creating a simple query
        query = "SELECT 1 as test_value"
        query_job = client.query(query)
        result = query_job.result()
        
        for row in result:
            print(f"✅ Test query successful: {row.test_value}")
        
        print("\n🎉 BigQuery connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ BigQuery connection test FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_bigquery_connection()
    sys.exit(0 if success else 1)
