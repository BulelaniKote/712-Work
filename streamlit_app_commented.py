# -*- coding: utf-8 -*-
"""
Retail Sales Analysis Dashboard
A comprehensive Streamlit application for analyzing retail sales data from BigQuery

This application provides:
- Interactive data visualizations
- SQL query execution capabilities
- Business intelligence insights
- Data quality analysis
- Export functionality

Author: BIA 712 Group 3
Date: 2024
"""

# =============================================================================
# IMPORT STATEMENTS
# =============================================================================

# Core web framework for creating the dashboard
import streamlit as st

# Data manipulation and analysis library
import pandas as pd

# High-level plotting library for interactive charts
import plotly.express as px

# Low-level plotting library for custom charts
import plotly.graph_objects as go

# For creating subplot layouts in Plotly
from plotly.subplots import make_subplots

# Numerical computing library
import numpy as np

# Date and time handling
from datetime import datetime

# Input/output operations for file handling
import io

# Declarative visualization library for interactive charts
import altair as alt

# Google BigQuery client library
from google.cloud import bigquery

# Google Cloud authentication
from google.oauth2 import service_account

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

# Configure Streamlit page settings
st.set_page_config(
    page_title="Retail Sales Analysis Dashboard",  # Browser tab title
    page_icon="��",  # Browser tab icon (emoji)
    layout="wide",  # Use full width layout instead of centered
    initial_sidebar_state="expanded"  # Show sidebar by default
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

# Define custom CSS styles for enhanced UI appearance
st.markdown("""
<style>
    /* Main header styling - large, blue, centered title */
    .main-header {
        font-size: 3rem;  /* Large font size */
        color: #1f77b4;  /* Blue color */
        text-align: center;  /* Center alignment */
        margin-bottom: 2rem;  /* Bottom margin */
        font-weight: bold;  /* Bold text */
    }
    /* Metric card styling - light background with blue left border */
    .metric-card {
        background-color: #f0f2f6;  /* Light gray background */
        padding: 1rem;  /* Internal spacing */
        border-radius: 0.5rem;  /* Rounded corners */
        border-left: 4px solid #1f77b4;  /* Blue left border */
        margin: 0.5rem 0;  /* Top and bottom margin */
    }
    /* Insight box styling - light blue background with red left border */
    .insight-box {
        background-color: #e8f4fd;  /* Light blue background */
        padding: 1rem;  /* Internal spacing */
        border-radius: 0.5rem;  /* Rounded corners */
        border-left: 4px solid #ff6b6b;  /* Red left border */
        margin: 1rem 0;  /* Top and bottom margin */
    }
    /* Success box styling - light green background with green left border */
    .success-box {
        background-color: #d4edda;  /* Light green background */
        padding: 1rem;  /* Internal spacing */
        border-radius: 0.5rem;  /* Rounded corners */
        border-left: 4px solid #28a745;  /* Green left border */
        margin: 1rem 0;  /* Top and bottom margin */
    }
</style>
""", unsafe_allow_html=True)  # Allow HTML rendering for custom styles

# =============================================================================
# UI LAYOUT SETUP
# =============================================================================

# Display the main dashboard title with custom styling
st.markdown('<h1 class="main-header">📊 Retail Sales Analysis Dashboard</h1>', unsafe_allow_html=True)

# Create sidebar navigation menu
st.sidebar.title("Navigation")  # Sidebar header
page = st.sidebar.selectbox(  # Dropdown selection widget
    "Choose a page:",  # Label for the dropdown
    ["🏠 Home", "📊 Dataset Analysis", "�� SQL Queries", "📈 Visualizations", "💡 Business Insights", "📋 About"]  # Available pages
)

# =============================================================================
# BIGQUERY CONNECTION FUNCTION
# =============================================================================

# BigQuery connection setup with caching for performance
@st.cache_resource  # Cache the client to avoid reconnection on every page load
def get_bigquery_client():
    """
    Initialize BigQuery client with service account credentials from Streamlit secrets
    
    This function:
    1. Checks for credentials in Streamlit secrets
    2. Creates service account credentials
    3. Initializes BigQuery client
    4. Returns client and project ID
    
    Returns:
        tuple: (client, project_id) if successful, (None, None) if failed
    """
    try:
        # Check if BigQuery credentials are available in Streamlit secrets
        if 'gcp_service_account' in st.secrets:
            try:
                # Create credentials object from service account info in secrets
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"],  # Service account JSON from secrets
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]  # Required API scopes
                )
                
                # Initialize BigQuery client with credentials
                client = bigquery.Client(
                    credentials=credentials,  # Use the created credentials
                    project=credentials.project_id  # Use project ID from credentials
                )
                
                # Return client and project ID for use in the application
                return client, credentials.project_id
                
            except Exception as e:
                # Handle credential creation errors
                st.error(f"❌ Error creating BigQuery client from secrets: {e}")
                st.info("💡 Please check your Streamlit Cloud secrets configuration")
                return None, None
                
        else:
            # Handle missing credentials
            st.error("❌ BigQuery credentials not found in Streamlit secrets")
            st.info("�� Please add your GCP service account credentials to Streamlit Cloud secrets")
            st.info("💡 Go to your app settings → Secrets and add the gcp_service_account section")
            return None, None
            
    except Exception as e:
        # Handle general connection errors
        st.error(f"❌ Error connecting to BigQuery: {e}")
        st.info("💡 Check your Streamlit Cloud secrets configuration")
        return None, None

# =============================================================================
# HOME PAGE
# =============================================================================

# Home page content
if page == "�� Home":
    # Display page header and dataset information
    st.markdown("## 🎯 Retail Sales Dataset Analysis")
    st.markdown("**Dataset:** `moonlit-autumn-468306-p6.assignment_one_1.retail_sales`")
    st.markdown("**Source:** Kaggle Retail Sales Dataset")
    
    # Initialize BigQuery connection
    client, project_id = get_bigquery_client()
    
    # Check if connection was successful
    if client is None:
        # Display error message if connection failed
        st.error("❌ BigQuery connection failed. Please check your credentials.")
        st.info("💡 Please check your BigQuery credentials and try again.")
    else:
        # Display success message with project ID
        st.success(f"✅ Connected to BigQuery project: {project_id}")
        
        # Dataset Overview Section
        st.markdown("---")  # Horizontal line separator
        st.subheader("📋 Dataset Overview")  # Section header
        
        try:
            # Get basic dataset information
            dataset_ref = f"{project_id}.assignment_one_1"  # Construct dataset reference
            dataset = client.get_dataset(dataset_ref)  # Retrieve dataset metadata
            
            # Get table information
            table_ref = f"{project_id}.assignment_one_1.retail_sales"  # Construct table reference
            table = client.get_table(table_ref)  # Retrieve table metadata
            
            # Create three columns for displaying metrics
            col1, col2, col3 = st.columns(3)
            
            # First column: Basic dataset information
            with col1:
                st.metric("Dataset", "assignment_one_1")  # Dataset name
                st.metric("Table", "retail_sales")  # Table name
                st.metric("Location", table.location)  # Geographic location of data
            
            # Second column: Data size and creation information
            with col2:
                st.metric("Total Rows", f"{table.num_rows:,}")  # Total number of rows (formatted with commas)
                st.metric("Table Size", f"{table.num_bytes / (1024*1024):.2f} MB")  # Table size in MB
                st.metric("Created", table.created.strftime("%Y-%m-%d"))  # Creation date
            
            # Third column: Project and schema information
            with col3:
                st.metric("Project ID", project_id)  # Google Cloud project ID
                st.metric("Columns", len(table.schema))  # Number of columns in the table
                try:
                    # Get the latest date from actual data (not table metadata)
                    latest_date_query = f"""
                    SELECT MAX(`Date`) as latest_data_date
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE `Date` IS NOT NULL
                    """
                    latest_date_result = client.query(latest_date_query).to_dataframe()  # Execute query
                    latest_data_date = latest_date_result.iloc[0]['latest_data_date']  # Extract latest date
                    st.metric("Last Modified", latest_data_date.strftime("%Y-%m-%d"))  # Display formatted date
                except Exception as e:
                    # Handle query errors
                    st.metric("Last Modified", "Error loading date")
            
        except Exception as e:
            # Handle dataset information retrieval errors
            st.error(f"❌ Error fetching dataset info: {e}")
        
        # Analysis Objectives Section
        st.markdown("---")  # Horizontal line separator
        st.subheader("🎯 Analysis Objectives")  # Section header
        
        # Create two columns for objectives
        col1, col2 = st.columns(2)
        
        # Left column: Data exploration and business analysis objectives
        with col1:
            st.markdown("""
            **📊 Data Exploration:**
            - Understand dataset structure and schema
            - Identify data quality issues
            - Explore key business metrics
            
            **🔍 Business Analysis:**
            - Sales performance by category
            - Store performance analysis
            - Customer behavior insights
            - Temporal trends and seasonality
            """)
        
        # Right column: Advanced analytics and actionable insights
        with col2:
            st.markdown("""
            **📈 Advanced Analytics:**
            - Revenue optimization opportunities
            - Customer segmentation
            - Product performance analysis
            - Payment method insights
            
            **💡 Actionable Insights:**
            - Data-driven recommendations
            - Performance improvement areas
            - Business growth opportunities
            """)

# =============================================================================
# DATASET ANALYSIS PAGE
# =============================================================================

# Dataset Analysis page
elif page == "📊 Dataset Analysis":
    st.header("📊 Comprehensive Dataset Analysis")  # Page header
    
    # Initialize BigQuery connection
    client, project_id = get_bigquery_client()
    
    # Check connection status
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()  # Stop execution if no connection
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Table Schema Analysis Section
    st.markdown("---")  # Horizontal line separator
    st.subheader("🏗️ Table Schema Analysis")  # Section header
    
    try:
        # Get table reference and metadata
        table_ref = f"{project_id}.assignment_one_1.retail_sales"
        table = client.get_table(table_ref)
        
        # Create DataFrame from table schema for display
        schema_df = pd.DataFrame([
            {
                'Column': field.name,  # Column name
                'Type': field.field_type,  # Data type
                'Mode': field.mode,  # NULLABLE, REQUIRED, or REPEATED
                'Description': field.description or 'No description'  # Column description
            }
            for field in table.schema  # Iterate through all fields in schema
        ])
        
        # Display schema table
        st.write("**Table Schema:**")
        st.dataframe(schema_df, use_container_width=True)
        
        # Data Types Summary Section
        st.markdown("---")  # Horizontal line separator
        st.subheader("📋 Data Types Summary")  # Section header
        
        # Count occurrences of each data type
        type_counts = schema_df['Type'].value_counts()
        
        # Create pie chart showing data type distribution
        fig = px.pie(values=type_counts.values, names=type_counts.index, title="Data Types Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        # Handle schema analysis errors
        st.error(f"❌ Error analyzing schema: {e}")
    
    # Data Quality Analysis Section
    st.markdown("---")  # Horizontal line separator
    st.subheader("🔍 Data Quality Analysis")  # Section header
    
    try:
        # Complex query to check for null values across all columns
        null_query = f"""
        SELECT 
            column_name,
            COUNT(*) as total_rows,
            COUNTIF(value IS NULL) as null_count,
            ROUND(COUNTIF(value IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
        FROM `{project_id}.assignment_one_1.retail_sales`,
        UNNEST([
            STRUCT('Date' as column_name, CAST(`Date` AS STRING) as value),
            STRUCT('Product Category' as column_name, `Product Category` as value),
            STRUCT('Customer ID' as column_name, CAST(`Customer ID` AS STRING) as value),
            STRUCT('Quantity' as column_name, CAST(`Quantity` AS STRING) as value),
            STRUCT('Total Amount' as column_name, CAST(`Total Amount` AS STRING) as value),
            STRUCT('Gender' as column_name, `Gender` as value),
            STRUCT('Age' as column_name, CAST(`Age` AS STRING) as value)
        ])
        GROUP BY column_name
        ORDER BY null_percentage DESC
        """
        
        # Execute null value analysis query
        null_df = client.query(null_query).to_dataframe()
        
        # Create two columns for displaying results
        col1, col2 = st.columns(2)
        
        # Left column: Data completeness table
        with col1:
            st.write("**Data Completeness Analysis:**")
            st.dataframe(null_df, use_container_width=True)
        
        # Right column: Data completeness chart
        with col2:
            # Create bar chart showing null percentages
            fig = px.bar(
                null_df, 
                x='column_name', 
                y='null_percentage',
                title="Data Completeness by Column (%)",
                color='null_percentage',  # Color bars by null percentage
                color_continuous_scale='RdYlGn_r'  # Red-Yellow-Green color scale (reversed)
            )
            fig.update_layout(xaxis_tickangle=-45)  # Rotate x-axis labels
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        # Handle data quality analysis errors
        st.error(f"❌ Error analyzing data quality: {e}")
    
    # Sample Data Display Section
    st.markdown("---")  # Horizontal line separator
    st.subheader("📋 Sample Data")  # Section header
    
    try:
        # Query to get sample data
        sample_query = f"SELECT * FROM `{project_id}.assignment_one_1.retail_sales` LIMIT 20"
        sample_df = client.query(sample_query).to_dataframe()
        
        # Display sample data
        st.write("**First 20 Records:**")
        st.dataframe(sample_df, use_container_width=True)
        
        # Create CSV download functionality
        csv = sample_df.to_csv(index=False)  # Convert DataFrame to CSV
        st.download_button(
            label="📥 Download Sample Data as CSV",  # Button label
            data=csv,  # CSV data
            file_name="retail_sales_sample.csv",  # Default filename
            mime="text/csv"  # MIME type
        )
        
    except Exception as e:
        # Handle sample data retrieval errors
        st.error(f"❌ Error fetching sample data: {e}")

# =============================================================================
# SQL QUERIES PAGE
# =============================================================================

# SQL Queries page
elif page == "🔍 SQL Queries":
    st.header("🔍 SQL Query Execution")  # Page header
    
    # Initialize BigQuery connection
    client, project_id = get_bigquery_client()
    
    # Check connection status
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()  # Stop execution if no connection
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Pre-built Analysis Queries Section
    st.markdown("---")  # Horizontal line separator
    st.subheader("📋 Pre-built Analysis Queries")  # Section header
    
    # Dictionary containing pre-built SQL queries for common analyses
    query_templates = {
        "Basic Overview": f"""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT `Customer ID`) as unique_customers,
            COUNT(DISTINCT `Product Category`) as unique_categories,
            COUNT(DISTINCT `Transaction ID`) as unique_transactions,
            ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value,
            ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue
        FROM `{project_id}.assignment_one_1.retail_sales`
        """,
        
        "Category Performance": f"""
        SELECT 
            `Product Category`,
            COUNT(*) as transaction_count,
            ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue,
            ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value,
            ROUND(SUM(CAST(`Quantity` AS INT64)), 0) as total_quantity_sold
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE `Product Category` IS NOT NULL
        GROUP BY `Product Category`
        ORDER BY total_revenue DESC
        """,
        
        "Customer Demographics": f"""
        SELECT 
            `Gender`,
            COUNT(*) as transaction_count,
            ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue,
            ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value,
            COUNT(DISTINCT `Customer ID`) as unique_customers
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE `Gender` IS NOT NULL
        GROUP BY `Gender`
        ORDER BY total_revenue DESC
        """,
        
        "Monthly Trends": f"""
        SELECT 
            EXTRACT(YEAR FROM `Date`) as year,
            EXTRACT(MONTH FROM `Date`) as month,
            COUNT(*) as transaction_count,
            ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as monthly_revenue,
            ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE `Date` IS NOT NULL
        GROUP BY year, month
        ORDER BY year, month
        """,
        
        "Customer Analysis": f"""
        SELECT 
            `Customer ID`,
            COUNT(*) as transaction_count,
            ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_spent,
            ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value,
            COUNT(DISTINCT `Product Category`) as categories_purchased,
            MIN(`Date`) as first_purchase,
            MAX(`Date`) as last_purchase
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE `Customer ID` IS NOT NULL
        GROUP BY `Customer ID`
        ORDER BY total_spent DESC
        LIMIT 20
        """,
        
        "Age Group Analysis": f"""
        SELECT 
            CASE
                WHEN CAST(`Age` AS INT64) < 18 THEN 'Under 18'
                WHEN CAST(`Age` AS INT64) BETWEEN 18 AND 25 THEN '18-25'
                WHEN CAST(`Age` AS INT64) BETWEEN 26 AND 35 THEN '26-35'
                WHEN CAST(`Age` AS INT64) BETWEEN 36 AND 45 THEN '36-45'
                WHEN CAST(`Age` AS INT64) BETWEEN 46 AND 55 THEN '46-55'
                ELSE '55+'
            END as age_group,
            COUNT(*) as transaction_count,
            ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue,
            ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE `Age` IS NOT NULL
        GROUP BY age_group
        ORDER BY total_revenue DESC
        """
    }
    
    # Create dropdown for selecting pre-built queries
    selected_template = st.selectbox("Choose a pre-built analysis:", list(query_templates.keys()))
    
    # Display selected query in text area
    query = st.text_area("SQL Query:", value=query_templates[selected_template], height=200)
    
    # Execute query button
    if st.button("🚀 Execute Query", type="primary"):
        if query.strip():  # Check if query is not empty
            with st.spinner("Executing query..."):  # Show loading spinner
                try:
                    # Execute the SQL query
                    results_df = client.query(query).to_dataframe()
                    
                    # Display success message with row count
                    st.success(f"✅ Query executed successfully! Returned {len(results_df)} rows")
                    
                    # Display query results
                    st.write("**Query Results:**")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Create download functionality for results
                    if len(results_df) > 0:
                        csv = results_df.to_csv(index=False)  # Convert to CSV
                        st.download_button(
                            label="�� Download Results as CSV",
                            data=csv,
                            file_name=f"{selected_template.lower().replace(' ', '_')}_results.csv",
                            mime="text/csv"
                        )
                    
                except Exception as e:
                    # Handle query execution errors
                    st.error(f"❌ Query execution failed: {e}")
                    st.info("💡 Check your SQL syntax and table references")
        else:
            # Handle empty query
            st.warning("⚠️ Please enter a SQL query")
    
    # Custom Query Section
    st.markdown("---")  # Horizontal line separator
    st.subheader("✍️ Custom SQL Query")  # Section header
    
    # Text area for custom SQL queries
    custom_query = st.text_area("Enter your custom SQL query:", height=150, 
                               placeholder=f"SELECT `Transaction ID`, `Customer ID`, `Product Category`, `Total Amount` FROM `{project_id}.assignment_one_1.retail_sales` LIMIT 10")
    
    # Execute custom query button
    if st.button("🔍 Run Custom Query"):
        if custom_query.strip():  # Check if query is not empty
            with st.spinner("Executing custom query..."):  # Show loading spinner
                try:
                    # Execute custom SQL query
                    custom_results = client.query(custom_query).to_dataframe()
                    
                    # Display success message with row count
                    st.success(f"✅ Custom query executed successfully! Returned {len(custom_results)} rows")
                    
                    # Display custom query results
                    st.write("**Custom Query Results:**")
                    st.dataframe(custom_results, use_container_width=True)
                    
                    # Create download functionality for custom results
                    if len(custom_results) > 0:
                        csv = custom_results.to_csv(index=False)  # Convert to CSV
                        st.download_button(
                            label="�� Download Custom Results as CSV",
                            data=csv,
                            file_name="custom_query_results.csv",
                            mime="text/csv"
                        )
                    
                except Exception as e:
                    # Handle custom query execution errors
                    st.error(f"❌ Custom query execution failed: {e}")
                    st.info("💡 Check your SQL syntax and table references")
        else:
            # Handle empty custom query
            st.warning("⚠️ Please enter a custom SQL query")

# =============================================================================
# VISUALIZATIONS PAGE
# =============================================================================

# Visualizations page
elif page == "📈 Visualizations":
    st.header("📈 Interactive Data Visualizations")  # Page header
    
    # Initialize BigQuery connection
    client, project_id = get_bigquery_client()
    
    # Check connection status
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()  # Stop execution if no connection
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Visualization Options Section
    st.markdown("---")  # Horizontal line separator
    st.subheader("📊 Choose Visualization Type")  # Section header
    
    # List of available visualization options
    viz_options = [
        "Revenue by Category",
        "Customer Demographics",
        "Monthly Trends",
        "Customer Spending",
        "Age Group Analysis",
        "Product Performance",
        "Interactive Sales Over Time"
    ]
    
    # Create dropdown for selecting visualization type
    selected_viz = st.selectbox("Select visualization:", viz_options)
    
    # Generate visualization button
    if st.button("�� Generate Visualization", type="primary"):
        with st.spinner("Generating visualization..."):  # Show loading spinner
            try:
                # Revenue by Category Visualization
                if selected_viz == "Revenue by Category":
                    # Query to get category revenue data
                    query = f"""
                    SELECT 
                        `Product Category`,
                        ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue,
                        COUNT(*) as transaction_count
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE `Product Category` IS NOT NULL
                    GROUP BY `Product Category`
                    ORDER BY total_revenue DESC
                    """
                    
                    # Execute query and get results
                    df = client.query(query).to_dataframe()
                    
                    # Create bar chart using Plotly
                    fig = px.bar(
                        df, 
                        x='Product Category', 
                        y='total_revenue',
                        title="Revenue by Product Category",
                        color='transaction_count',  # Color bars by transaction count
                        color_continuous_scale='Viridis'  # Color scale
                    )
                    fig.update_layout(xaxis_tickangle=-45)  # Rotate x-axis labels
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display underlying data
                    st.write("**Category Revenue Data:**")
                    st.dataframe(df, use_container_width=True)
                
                # Customer Demographics Visualization
                elif selected_viz == "Customer Demographics":
                    # Query to get gender-based revenue data
                    query = f"""
                    SELECT 
                        `Gender`,
                        ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue,
                        COUNT(*) as transaction_count,
                        ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE `Gender` IS NOT NULL
                    GROUP BY `Gender`
                    ORDER BY total_revenue DESC
                    """
                    
                    # Execute query and get results
                    df = client.query(query).to_dataframe()
                    
                    # Create pie chart using Plotly
                    fig = px.pie(
                        df,
                        values='total_revenue',
                        names='Gender',
                        title="Revenue Distribution by Gender"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display underlying data
                    st.write("**Customer Demographics Data:**")
                    st.dataframe(df, use_container_width=True)
                
                # Monthly Trends Visualization
                elif selected_viz == "Monthly Trends":
                    # Query to get monthly revenue trends
                    query = f"""
                    SELECT 
                        EXTRACT(YEAR FROM `Date`) as year,
                        EXTRACT(MONTH FROM `Date`) as month,
                        ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as monthly_revenue,
                        COUNT(*) as transaction_count
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE `Date` IS NOT NULL
                    GROUP BY year, month
                    ORDER BY year, month
                    """
                    
                    # Execute query and get results
                    df = client.query(query).to_dataframe()
                    
                    # Create line chart using Plotly
                    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))  # Create date column
                    fig = px.line(
                        df,
                        x='date',
                        y='monthly_revenue',
                        title="Monthly Revenue Trends",
                        markers=True  # Show markers on line
                    )
                    fig.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display underlying data
                    st.write("**Monthly Trends Data:**")
                    st.dataframe(df, use_container_width=True)
                
                # Customer Spending Visualization
                elif selected_viz == "Customer Spending":
                    # Query to get customer spending data
                    query = f"""
                    SELECT 
                        `Customer ID`,
                        ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_spent,
                        COUNT(*) as transaction_count,
                        ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE `Customer ID` IS NOT NULL
                    GROUP BY `Customer ID`
                    ORDER BY total_spent DESC
                    LIMIT 50
                    """
                    
                    # Execute query and get results
                    df = client.query(query).to_dataframe()
                    
                    # Create histogram using Plotly
                    fig = px.histogram(
                        df,
                        x='total_spent',
                        nbins=20,  # Number of bins
                        title="Customer Spending Distribution",
                        labels={'total_spent': 'Total Amount Spent ($)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display underlying data
                    st.write("**Customer Spending Data (Top 50):**")
                    st.dataframe(df, use_container_width=True)
                
                # Age Group Analysis Visualization
                elif selected_viz == "Age Group Analysis":
                    # Query to get age group revenue data
                    query = f"""
                    SELECT 
                        CASE
                            WHEN CAST(`Age` AS INT64) < 18 THEN 'Under 18'
                            WHEN CAST(`Age` AS INT64) BETWEEN 18 AND 25 THEN '18-25'
                            WHEN CAST(`Age` AS INT64) BETWEEN 26 AND 35 THEN '26-35'
                            WHEN CAST(`Age` AS INT64) BETWEEN 36 AND 45 THEN '36-45'
                            WHEN CAST(`Age` AS INT64) BETWEEN 46 AND 55 THEN '46-55'
                            ELSE '55+'
                        END as age_group,
                        COUNT(*) as transaction_count,
                        ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue,
                        ROUND(AVG(CAST(`Total Amount` AS FLOAT64)), 2) as avg_transaction_value
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE `Age` IS NOT NULL
                    GROUP BY age_group
                    ORDER BY total_revenue DESC
                    """
                    
                    # Execute query and get results
                    df = client.query(query).to_dataframe()
                    
                    # Create bar chart using Plotly
                    fig = px.bar(
                        df,
                        x='age_group',
                        y='total_revenue',
                        title="Revenue by Age Group",
                        color='transaction_count',  # Color bars by transaction count
                        color_continuous_scale='Viridis'  # Color scale
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display underlying data
                    st.write("**Age Group Analysis Data:**")
                    st.dataframe(df, use_container_width=True)
                
                # Product Performance Visualization
                elif selected_viz == "Product Performance":
                    # Query to get product performance data
                    query = f"""
                    SELECT 
                        `Product Category`,
                        COUNT(*) as times_purchased,
                        ROUND(SUM(CAST(`Total Amount` AS FLOAT64)), 2) as total_revenue,
                        ROUND(SUM(CAST(`Quantity` AS INT64)), 0) as total_quantity_sold
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE `Product Category` IS NOT NULL
                    GROUP BY `Product Category`
                    ORDER BY total_revenue DESC
                    LIMIT 20
                    """
                    
                    # Execute query and get results
                    df = client.query(query).to_dataframe()
                    
                    # Create horizontal bar chart using Plotly
                    fig = px.bar(
                        df,
                        y='Product Category',
                        x='total_revenue',
                        orientation='h',  # Horizontal orientation
                        title="Top 20 Product Categories by Revenue",
                        color='times_purchased',  # Color bars by purchase count
                        color_continuous_scale='Plasma'  # Color scale
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display underlying data
                    st.write("**Product Performance Data (Top 20):**")
                    st.dataframe(df, use_container_width=True)
                
                # Interactive Sales Over Time Visualization
                elif selected_viz == "Interactive Sales Over Time":
                    # Interactive sales over time with date filtering
                    st.markdown("### 📅 Interactive Sales Over Time")
                    
                    # Load data with caching for performance
                    @st.cache_data  # Cache data to avoid re-querying
                    def load_sales_data():
                        query = f"""
                        SELECT 
                            `Date`,
                            `Total Amount`,
                            `Product Category`,
                            `Customer ID`
                        FROM `{project_id}.assignment_one_1.retail_sales`
                        WHERE `Date` IS NOT NULL
                        ORDER BY `Date`
                        """
                        return client.query(query).to_dataframe()
                    
                    # Load and process data
                    df = load_sales_data()
                    df['Date'] = pd.to_datetime(df['Date'])  # Convert to datetime
                    
                    # Get date range for filtering
                    min_date = df['Date'].min().date()
                    max_date = df['Date'].max().date()
                    
                    # Create two-column layout
                    col1, col2 = st.columns([1, 2])
                    
                    # Left column: Filter controls
                    with col1:
                        st.markdown("**📅 Filter Options:**")
                        # Date range picker
                        start_date, end_date = st.date_input(
                            "Select date range", 
                            [min_date, max_date],
                            min_value=min_date,
                            max_value=max_date
                        )
                        
                        # Category filter dropdown
                        categories = ['All'] + sorted(df['Product Category'].unique().tolist())
                        selected_category = st.selectbox("Filter by Category:", categories)
                        
                        # Customer breakdown toggle
                        show_customer_breakdown = st.checkbox("Show customer breakdown")
                    
                    # Apply filters to data
                    df_filtered = df[
                        (df['Date'] >= pd.to_datetime(start_date)) & 
                        (df['Date'] <= pd.to_datetime(end_date))
                    ]
                    
                    # Apply category filter if not 'All'
                    if selected_category != 'All':
                        df_filtered = df_filtered[df_filtered['Product Category'] == selected_category]
                    
                    # Aggregate sales by date
                    if show_customer_breakdown:
                        # Group by date and customer for breakdown view
                        sales_over_time = df_filtered.groupby(['Date', 'Customer ID'])['Total Amount'].sum().reset_index()
                        
                        # Create interactive line chart with customer breakdown using Altair
                        line_chart = alt.Chart(sales_over_time).mark_line(point=True).encode(
                            x='Date:T',  # Time axis
                            y='Total Amount:Q',  # Quantitative axis
                            color='Customer ID:N',  # Nominal color encoding
                            tooltip=['Date:T', 'Customer ID:N', 'Total Amount:Q']  # Tooltip information
                        ).properties(
                            width=800,
                            height=400,
                            title=f"Sales Over Time by Customer ({selected_category})"
                        ).interactive()  # Make chart interactive
                    else:
                        # Group by date only for aggregate view
                        sales_over_time = df_filtered.groupby('Date')['Total Amount'].sum().reset_index()
                        
                        # Create interactive line chart using Altair
                        line_chart = alt.Chart(sales_over_time).mark_line(
                            color='green',  # Line color
                            point=True,  # Show points
                            strokeWidth=3  # Line width
                        ).encode(
                            x='Date:T',  # Time axis
                            y='Total Amount:Q',  # Quantitative axis
                            tooltip=['Date:T', 'Total Amount:Q']  # Tooltip information
                        ).properties(
                            width=800,
                            height=400,
                            title=f"Sales Over Time ({selected_category})"
                        ).interactive()  # Make chart interactive
                    
                    # Right column: Chart display
                    with col2:
                        st.altair_chart(line_chart, use_container_width=True)
                    
                    # Display summary statistics in four columns
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Sales", f"${sales_over_time['Total Amount'].sum():,.2f}")
                    with col2:
                        st.metric("Average Daily Sales", f"${sales_over_time['Total Amount'].mean():,.2f}")
                    with col3:
                        st.metric("Peak Sales Day", f"${sales_over_time['Total Amount'].max():,.2f}")
                    with col4:
                        st.metric("Days in Range", len(sales_over_time))
                    
                    # Display filtered data table
                    st.markdown("**📊 Filtered Data:**")
                    st.dataframe(sales_over_time, use_container_width=True)
                
            except Exception as e:
                # Handle visualization generation errors
                st.error(f"❌ Error generating visualization: {e}")
                st.info("�� This might be due to data type issues or missing columns")

# =============================================================================
# BUSINESS INSIGHTS PAGE
# =============================================================================

# Business Insights page
elif page == "💡 Business Insights":
    st.header("💡 Business Intelligence Insights")  # Page header
    
    # Initialize BigQuery connection
    client, project_id = get_bigquery_client()
    
    # Check connection status
    if client is None 