#!/usr/bin/env python3
"""
Test script to verify BigQuery connection after fixing credentials
"""

import streamlit as st
from modules.utilis import get_bigquery_client

def test_bigquery_connection():
    """Test the BigQuery connection"""
    st.title("BigQuery Connection Test")
    
    st.info("Testing BigQuery connection with updated credentials...")
    
    # Test the connection
    client, project_id = get_bigquery_client()
    
    if client and project_id:
        st.success(f"✅ BigQuery connection successful!")
        st.info(f"Project ID: {project_id}")
        
        # Test a simple query
        try:
            query = f"""
            SELECT 1 as test_value
            """
            result = client.query(query).to_dataframe()
            st.success("✅ Test query executed successfully!")
            st.dataframe(result)
            
        except Exception as e:
            st.error(f"❌ Test query failed: {e}")
            
    else:
        st.error("❌ BigQuery connection failed!")
        st.info("Please check your credentials and try again.")

if __name__ == "__main__":
    test_bigquery_connection()
