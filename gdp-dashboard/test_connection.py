#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test BigQuery Connection
"""

from google.cloud import bigquery
from google.oauth2 import service_account
import json

def test_bigquery_connection():
    """Test BigQuery connection with service account"""
    
    try:
        print("🔍 Testing BigQuery connection...")
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            "istanbul_sales_analysis/API.JSON",
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        print(f"✅ Credentials loaded successfully")
        print(f"   Project ID: {credentials.project_id}")
        print(f"   Service Account: {credentials.service_account_email}")
        
        # Create client
        client = bigquery.Client(
            credentials=credentials,
            project=credentials.project_id
        )
        
        print(f"✅ BigQuery client created successfully")
        
        # Test connection by getting project info
        try:
            project = client.get_project(credentials.project_id)
            print(f"✅ Project info retrieved: {project.project_id}")
        except Exception as e:
            print(f"⚠️ Could not get project info: {e}")
        
        # Test dataset access
        try:
            dataset_ref = f"{credentials.project_id}.assignment_one_1"
            dataset = client.get_dataset(dataset_ref)
            print(f"✅ Dataset accessed: {dataset.dataset_id}")
        except Exception as e:
            print(f"❌ Could not access dataset: {e}")
            return False
        
        # Test table access
        try:
            table_ref = f"{credentials.project_id}.assignment_one_1.retail_sales"
            table = client.get_table(table_ref)
            print(f"✅ Table accessed: {table.table_id}")
            print(f"   Rows: {table.num_rows:,}")
            print(f"   Size: {table.num_bytes / (1024*1024):.2f} MB")
        except Exception as e:
            print(f"❌ Could not access table: {e}")
            return False
        
        # Test simple query
        try:
            query = f"SELECT COUNT(*) as total_records FROM `{table_ref}`"
            results = client.query(query).to_dataframe()
            print(f"✅ Query executed successfully: {results.iloc[0]['total_records']:,} records")
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            return False
        
        print("\n🎉 All connection tests passed! BigQuery is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_bigquery_connection()
