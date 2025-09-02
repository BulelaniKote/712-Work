import os
import json
import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class BigQueryIntegration:
    def __init__(self, credentials_path="istanbul_sales_analysis/API.JSON"):
        """
        Initialize BigQuery connection using service account credentials
        """
        try:
            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            
            # Initialize BigQuery client
            self.client = bigquery.Client(
                credentials=credentials,
                project=credentials.project_id
            )
            
            self.project_id = credentials.project_id
            self.dataset_id = "sales_analysis"
            self.dataset_ref = f"{self.project_id}.{self.dataset_id}"
            
            # Create dataset if it doesn't exist
            self._create_dataset_if_not_exists()
            
            st.success(f"✅ Connected to BigQuery project: {self.project_id}")
            
        except Exception as e:
            st.error(f"❌ Error connecting to BigQuery: {e}")
            self.client = None
    
    def _create_dataset_if_not_exists(self):
        """Create the sales_analysis dataset if it doesn't exist"""
        try:
            dataset = bigquery.Dataset(self.dataset_ref)
            dataset.location = "US"  # Set your preferred location
            
            # Create dataset if it doesn't exist
            try:
                self.client.get_dataset(self.dataset_ref)
                st.info(f"📊 Dataset {self.dataset_id} already exists")
            except:
                dataset = self.client.create_dataset(dataset, timeout=30)
                st.success(f"✅ Created dataset: {self.dataset_id}")
                
        except Exception as e:
            st.warning(f"⚠️ Could not create dataset: {e}")
    
    def create_tables(self):
        """Create all necessary tables for the analysis"""
        try:
            # Istanbul Sales Table
            istanbul_schema = [
                bigquery.SchemaField("invoice_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("invoice_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_age", "INTEGER"),
                bigquery.SchemaField("customer_gender", "STRING"),
                bigquery.SchemaField("product_category", "STRING"),
                bigquery.SchemaField("product_name", "STRING"),
                bigquery.SchemaField("quantity", "INTEGER"),
                bigquery.SchemaField("unit_price", "FLOAT64"),
                bigquery.SchemaField("total_amount", "FLOAT64"),
                bigquery.SchemaField("payment_method", "STRING"),
                bigquery.SchemaField("shopping_mall", "STRING"),
                bigquery.SchemaField("city", "STRING"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED")
            ]
            
            # College Students Table
            college_schema = [
                bigquery.SchemaField("student_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("student_name", "STRING"),
                bigquery.SchemaField("age", "INTEGER"),
                bigquery.SchemaField("gpa", "FLOAT64"),
                bigquery.SchemaField("major", "STRING"),
                bigquery.SchemaField("year", "STRING"),
                bigquery.SchemaField("enrollment_date", "DATE"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED")
            ]
            
            # Retail Sales Table
            retail_schema = [
                bigquery.SchemaField("transaction_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("transaction_date", "DATE", mode="REQUIRED"),
                bigquery.SchemaField("product_id", "STRING"),
                bigquery.SchemaField("product_name", "STRING"),
                bigquery.SchemaField("category", "STRING"),
                bigquery.SchemaField("quantity", "INTEGER"),
                bigquery.SchemaField("unit_price", "FLOAT64"),
                bigquery.SchemaField("total_amount", "FLOAT64"),
                bigquery.SchemaField("store_id", "STRING"),
                bigquery.SchemaField("store_name", "STRING"),
                bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED")
            ]
            
            tables_config = [
                ("istanbul_sales", istanbul_schema),
                ("college_students", college_schema),
                ("retail_sales", retail_schema)
            ]
            
            for table_name, schema in tables_config:
                table_ref = f"{self.dataset_ref}.{table_name}"
                try:
                    self.client.get_table(table_ref)
                    st.info(f"📋 Table {table_name} already exists")
                except:
                    table = bigquery.Table(table_ref, schema=schema)
                    table = self.client.create_table(table)
                    st.success(f"✅ Created table: {table_name}")
                    
        except Exception as e:
            st.error(f"❌ Error creating tables: {e}")
    
    def upload_data_to_bigquery(self, df, table_name, write_disposition="WRITE_TRUNCATE"):
        """
        Upload pandas DataFrame to BigQuery table
        
        Args:
            df: Pandas DataFrame
            table_name: Name of the table in BigQuery
            write_disposition: How to handle existing data
        """
        try:
            if self.client is None:
                st.error("❌ BigQuery client not initialized")
                return False
            
            table_ref = f"{self.dataset_ref}.{table_name}"
            
            # Configure the load job
            job_config = bigquery.LoadJobConfig(
                write_disposition=write_disposition,
                autodetect=True
            )
            
            # Load the data
            job = self.client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            
            # Wait for the job to complete
            job.result()
            
            st.success(f"✅ Successfully uploaded {len(df)} rows to {table_name}")
            return True
            
        except Exception as e:
            st.error(f"❌ Error uploading data to {table_name}: {e}")
            return False
    
    def run_analysis_queries(self):
        """Run comprehensive analysis queries and return results"""
        if self.client is None:
            st.error("❌ BigQuery client not initialized")
            return {}
        
        try:
            results = {}
            
            # 1. Istanbul Sales Analysis Queries
            istanbul_queries = {
                "total_revenue": """
                    SELECT 
                        SUM(total_amount) as total_revenue,
                        COUNT(*) as total_transactions,
                        AVG(total_amount) as avg_transaction_value
                    FROM `{}.{}.istanbul_sales`
                    WHERE total_amount > 0
                """,
                
                "revenue_by_category": """
                    SELECT 
                        product_category,
                        SUM(total_amount) as total_revenue,
                        COUNT(*) as transaction_count,
                        AVG(total_amount) as avg_transaction_value
                    FROM `{}.{}.istanbul_sales`
                    WHERE product_category IS NOT NULL
                    GROUP BY product_category
                    ORDER BY total_revenue DESC
                    LIMIT 10
                """,
                
                "revenue_by_mall": """
                    SELECT 
                        shopping_mall,
                        SUM(total_amount) as total_revenue,
                        COUNT(*) as transaction_count,
                        COUNT(DISTINCT customer_id) as unique_customers
                    FROM `{}.{}.istanbul_sales`
                    WHERE shopping_mall IS NOT NULL
                    GROUP BY shopping_mall
                    ORDER BY total_revenue DESC
                """,
                
                "monthly_trends": """
                    SELECT 
                        EXTRACT(YEAR FROM invoice_date) as year,
                        EXTRACT(MONTH FROM invoice_date) as month,
                        SUM(total_amount) as monthly_revenue,
                        COUNT(*) as transaction_count
                    FROM `{}.{}.istanbul_sales`
                    WHERE invoice_date IS NOT NULL
                    GROUP BY year, month
                    ORDER BY year, month
                """,
                
                "customer_demographics": """
                    SELECT 
                        customer_age,
                        customer_gender,
                        COUNT(*) as transaction_count,
                        AVG(total_amount) as avg_transaction_value,
                        SUM(total_amount) as total_spent
                    FROM `{}.{}.istanbul_sales`
                    WHERE customer_age IS NOT NULL AND customer_gender IS NOT NULL
                    GROUP BY customer_age, customer_gender
                    ORDER BY customer_age
                """,
                
                "payment_method_analysis": """
                    SELECT 
                        payment_method,
                        COUNT(*) as transaction_count,
                        SUM(total_amount) as total_revenue,
                        AVG(total_amount) as avg_transaction_value
                    FROM `{}.{}.istanbul_sales`
                    WHERE payment_method IS NOT NULL
                    GROUP BY payment_method
                    ORDER BY total_revenue DESC
                """
            }
            
            # Execute Istanbul queries
            for query_name, query in istanbul_queries.items():
                try:
                    formatted_query = query.format(self.project_id, self.dataset_id)
                    query_job = self.client.query(formatted_query)
                    results[f"istanbul_{query_name}"] = query_job.to_dataframe()
                except Exception as e:
                    st.warning(f"⚠️ Error executing {query_name}: {e}")
            
            # 2. College Students Analysis Queries
            college_queries = {
                "gpa_distribution": """
                    SELECT 
                        major,
                        AVG(gpa) as avg_gpa,
                        COUNT(*) as student_count,
                        MIN(gpa) as min_gpa,
                        MAX(gpa) as max_gpa
                    FROM `{}.{}.college_students`
                    WHERE gpa IS NOT NULL
                    GROUP BY major
                    ORDER BY avg_gpa DESC
                """,
                
                "age_analysis": """
                    SELECT 
                        age,
                        COUNT(*) as student_count,
                        AVG(gpa) as avg_gpa
                    FROM `{}.{}.college_students`
                    WHERE age IS NOT NULL
                    GROUP BY age
                    ORDER BY age
                """,
                
                "year_enrollment": """
                    SELECT 
                        year,
                        COUNT(*) as student_count,
                        AVG(gpa) as avg_gpa
                    FROM `{}.{}.college_students`
                    WHERE year IS NOT NULL
                    GROUP BY year
                    ORDER BY year
                """
            }
            
            # Execute College queries
            for query_name, query in college_queries.items():
                try:
                    formatted_query = query.format(self.project_id, self.dataset_id)
                    query_job = self.client.query(formatted_query)
                    results[f"college_{query_name}"] = query_job.to_dataframe()
                except Exception as e:
                    st.warning(f"⚠️ Error executing {query_name}: {e}")
            
            # 3. Retail Sales Analysis Queries
            retail_queries = {
                "sales_trends": """
                    SELECT 
                        EXTRACT(YEAR FROM transaction_date) as year,
                        EXTRACT(MONTH FROM transaction_date) as month,
                        SUM(total_amount) as monthly_sales,
                        COUNT(*) as transaction_count
                    FROM `{}.{}.retail_sales`
                    WHERE transaction_date IS NOT NULL
                    GROUP BY year, month
                    ORDER BY year, month
                """,
                
                "product_performance": """
                    SELECT 
                        product_name,
                        category,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count,
                        AVG(unit_price) as avg_price
                    FROM `{}.{}.retail_sales`
                    WHERE product_name IS NOT NULL
                    GROUP BY product_name, category
                    ORDER BY total_sales DESC
                    LIMIT 20
                """,
                
                "store_performance": """
                    SELECT 
                        store_name,
                        SUM(total_amount) as total_sales,
                        COUNT(*) as transaction_count,
                        AVG(total_amount) as avg_transaction_value
                    FROM `{}.{}.retail_sales`
                    WHERE store_name IS NOT NULL
                    GROUP BY store_name
                    ORDER BY total_sales DESC
                """
            }
            
            # Execute Retail queries
            for query_name, query in retail_queries.items():
                try:
                    formatted_query = query.format(self.project_id, self.dataset_id)
                    query_job = self.client.query(formatted_query)
                    results[f"retail_{query_name}"] = query_job.to_dataframe()
                except Exception as e:
                    st.warning(f"⚠️ Error executing {query_name}: {e}")
            
            st.success(f"✅ Executed {len(results)} analysis queries successfully")
            return results
            
        except Exception as e:
            st.error(f"❌ Error running analysis queries: {e}")
            return {}
    
    def create_advanced_queries(self):
        """Create and execute advanced analytical queries"""
        if self.client is None:
            st.error("❌ BigQuery client not initialized")
            return {}
        
        try:
            advanced_results = {}
            
            # Advanced Istanbul Sales Analysis
            advanced_queries = {
                "customer_segmentation": """
                    WITH customer_metrics AS (
                        SELECT 
                            customer_id,
                            COUNT(*) as transaction_count,
                            SUM(total_amount) as total_spent,
                            AVG(total_amount) as avg_transaction_value,
                            MAX(invoice_date) as last_purchase_date
                        FROM `{}.{}.istanbul_sales`
                        GROUP BY customer_id
                    )
                    SELECT 
                        CASE 
                            WHEN total_spent >= 1000 THEN 'High Value'
                            WHEN total_spent >= 500 THEN 'Medium Value'
                            ELSE 'Low Value'
                        END as customer_segment,
                        COUNT(*) as customer_count,
                        AVG(total_spent) as avg_total_spent,
                        AVG(transaction_count) as avg_transactions
                    FROM customer_metrics
                    GROUP BY customer_segment
                    ORDER BY avg_total_spent DESC
                """,
                
                "seasonal_analysis": """
                    SELECT 
                        EXTRACT(MONTH FROM invoice_date) as month,
                        EXTRACT(DAYOFWEEK FROM invoice_date) as day_of_week,
                        SUM(total_amount) as daily_revenue,
                        COUNT(*) as transaction_count,
                        AVG(total_amount) as avg_transaction_value
                    FROM `{}.{}.istanbul_sales`
                    WHERE invoice_date IS NOT NULL
                    GROUP BY month, day_of_week
                    ORDER BY month, day_of_week
                """,
                
                "product_category_correlation": """
                    SELECT 
                        p1.product_category as category1,
                        p2.product_category as category2,
                        CORR(p1.total_amount, p2.total_amount) as correlation
                    FROM `{}.{}.istanbul_sales` p1
                    JOIN `{}.{}.istanbul_sales` p2
                    ON p1.customer_id = p2.customer_id
                    AND p1.invoice_date = p2.invoice_date
                    WHERE p1.product_category < p2.product_category
                    AND CORR(p1.total_amount, p2.total_amount) IS NOT NULL
                    ORDER BY ABS(correlation) DESC
                    LIMIT 10
                """,
                
                "mall_performance_ranking": """
                    WITH mall_stats AS (
                        SELECT 
                            shopping_mall,
                            SUM(total_amount) as total_revenue,
                            COUNT(*) as transaction_count,
                            COUNT(DISTINCT customer_id) as unique_customers,
                            AVG(total_amount) as avg_transaction_value
                        FROM `{}.{}.istanbul_sales`
                        WHERE shopping_mall IS NOT NULL
                        GROUP BY shopping_mall
                    )
                    SELECT 
                        shopping_mall,
                        total_revenue,
                        transaction_count,
                        unique_customers,
                        avg_transaction_value,
                        RANK() OVER (ORDER BY total_revenue DESC) as revenue_rank,
                        RANK() OVER (ORDER BY unique_customers DESC) as customer_rank
                    FROM mall_stats
                    ORDER BY revenue_rank
                """
            }
            
            # Execute advanced queries
            for query_name, query in advanced_queries.items():
                try:
                    formatted_query = query.format(self.project_id, self.dataset_id, self.project_id, self.dataset_id)
                    query_job = self.client.query(formatted_query)
                    advanced_results[f"advanced_{query_name}"] = query_job.to_dataframe()
                except Exception as e:
                    st.warning(f"⚠️ Error executing advanced query {query_name}: {e}")
            
            st.success(f"✅ Executed {len(advanced_results)} advanced queries successfully")
            return advanced_results
            
        except Exception as e:
            st.error(f"❌ Error running advanced queries: {e}")
            return {}
    
    def export_query_results(self, results, format_type="csv"):
        """Export query results to various formats"""
        try:
            if format_type == "csv":
                for query_name, df in results.items():
                    if not df.empty:
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label=f"📥 Download {query_name} as CSV",
                            data=csv,
                            file_name=f"{query_name}.csv",
                            mime="text/csv"
                        )
            elif format_type == "excel":
                # Create Excel file with multiple sheets
                with pd.ExcelWriter("bigquery_analysis_results.xlsx", engine="openpyxl") as writer:
                    for query_name, df in results.items():
                        if not df.empty:
                            df.to_excel(writer, sheet_name=query_name[:31], index=False)
                
                # Read the Excel file and provide download
                with open("bigquery_analysis_results.xlsx", "rb") as f:
                    st.download_button(
                        label="📥 Download All Results as Excel",
                        data=f.read(),
                        file_name="bigquery_analysis_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Clean up the file
                os.remove("bigquery_analysis_results.xlsx")
                
        except Exception as e:
            st.error(f"❌ Error exporting results: {e}")

# Streamlit Integration Functions
def bigquery_streamlit_integration():
    """Main function to integrate BigQuery with Streamlit"""
    st.header("🔗 BigQuery Integration")
    
    # Initialize BigQuery connection
    if 'bq_client' not in st.session_state:
        st.session_state.bq_client = BigQueryIntegration()
    
    bq_client = st.session_state.bq_client
    
    if bq_client.client is None:
        st.error("❌ BigQuery connection failed. Please check your credentials.")
        return
    
    # Sidebar controls
    st.sidebar.subheader("🔧 BigQuery Operations")
    
    # Create tables
    if st.sidebar.button("🏗️ Create Tables"):
        with st.spinner("Creating BigQuery tables..."):
            bq_client.create_tables()
    
    # Upload data options
    st.sidebar.subheader("📤 Upload Data")
    upload_option = st.sidebar.selectbox(
        "Select data to upload:",
        ["None", "Istanbul Sales", "College Students", "Retail Sales"]
    )
    
    if upload_option != "None":
        if upload_option == "Istanbul Sales":
            # Load Istanbul data
            istanbul_df = pd.read_csv("data/istanbul_sales_data.csv")
            if st.sidebar.button("📤 Upload Istanbul Data"):
                with st.spinner("Uploading Istanbul sales data..."):
                    bq_client.upload_data_to_bigquery(istanbul_df, "istanbul_sales")
        
        elif upload_option == "College Students":
            # Load College data
            college_df = pd.read_csv("data/College Student Analysis.csv")
            if st.sidebar.button("📤 Upload College Data"):
                with st.spinner("Uploading college student data..."):
                    bq_client.upload_data_to_bigquery(college_df, "college_students")
        
        elif upload_option == "Retail Sales":
            # Load Retail data
            retail_df = pd.read_csv("retail_sales_analysis/retail_sales_dataset.csv")
            if st.sidebar.button("📤 Upload Retail Data"):
                with st.spinner("Uploading retail sales data..."):
                    bq_client.upload_data_to_bigquery(retail_df, "retail_sales")
    
    # Analysis queries
    st.sidebar.subheader("📊 Run Analysis")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔍 Basic Analysis"):
            with st.spinner("Running basic analysis queries..."):
                results = bq_client.run_analysis_queries()
                st.session_state.bq_results = results
    
    with col2:
        if st.button("🚀 Advanced Analysis"):
            with st.spinner("Running advanced analysis queries..."):
                advanced_results = bq_client.create_advanced_queries()
                st.session_state.bq_advanced_results = advanced_results
    
    # Display results
    if 'bq_results' in st.session_state and st.session_state.bq_results:
        st.subheader("📊 Basic Analysis Results")
        
        # Display Istanbul results
        if any(k.startswith('istanbul_') for k in st.session_state.bq_results.keys()):
            st.write("**🏙️ Istanbul Sales Analysis**")
            for key, df in st.session_state.bq_results.items():
                if key.startswith('istanbul_') and not df.empty:
                    st.write(f"**{key.replace('istanbul_', '').replace('_', ' ').title()}**")
                    st.dataframe(df)
                    
                    # Create visualizations
                    if 'revenue' in key:
                        if 'category' in key:
                            fig = px.bar(df, x='product_category', y='total_revenue', 
                                       title="Revenue by Product Category")
                            st.plotly_chart(fig, use_container_width=True)
                        elif 'mall' in key:
                            fig = px.bar(df, x='shopping_mall', y='total_revenue', 
                                       title="Revenue by Shopping Mall")
                            st.plotly_chart(fig, use_container_width=True)
        
        # Display College results
        if any(k.startswith('college_') for k in st.session_state.bq_results.keys()):
            st.write("**📚 College Students Analysis**")
            for key, df in st.session_state.bq_results.items():
                if key.startswith('college_') and not df.empty:
                    st.write(f"**{key.replace('college_', '').replace('_', ' ').title()}**")
                    st.dataframe(df)
        
        # Display Retail results
        if any(k.startswith('retail_') for k in st.session_state.bq_results.keys()):
            st.write("**🛍️ Retail Sales Analysis**")
            for key, df in st.session_state.bq_results.items():
                if key.startswith('retail_') and not df.empty:
                    st.write(f"**{key.replace('retail_', '').replace('_', ' ').title()}**")
                    st.dataframe(df)
    
    # Display advanced results
    if 'bq_advanced_results' in st.session_state and st.session_state.bq_advanced_results:
        st.subheader("🚀 Advanced Analysis Results")
        
        for key, df in st.session_state.bq_advanced_results.items():
            if not df.empty:
                st.write(f"**{key.replace('advanced_', '').replace('_', ' ').title()}**")
                st.dataframe(df)
    
    # Export options
    if st.sidebar.button("📥 Export Results"):
        if 'bq_results' in st.session_state and st.session_state.bq_results:
            bq_client.export_query_results(st.session_state.bq_results, "csv")
        if 'bq_advanced_results' in st.session_state and st.session_state.bq_advanced_results:
            bq_client.export_query_results(st.session_state.bq_advanced_results, "csv")

# Example usage and testing
if __name__ == "__main__":
    # Test the BigQuery integration
    st.title("🔗 BigQuery Integration Test")
    
    # Initialize connection
    bq_client = BigQueryIntegration()
    
    if bq_client.client:
        st.success("✅ BigQuery connection successful!")
        
        # Create tables
        if st.button("Create Tables"):
            bq_client.create_tables()
        
        # Test queries
        if st.button("Test Queries"):
            results = bq_client.run_analysis_queries()
            st.write(f"Executed {len(results)} queries successfully")
    
    else:
        st.error("❌ BigQuery connection failed!")
