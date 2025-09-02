# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import io
from google.cloud import bigquery
from google.oauth2 import service_account

# Page configuration
st.set_page_config(
    page_title="Retail Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff6b6b;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.markdown('<h1 class="main-header">📊 Retail Sales Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🏠 Home", "📊 Dataset Analysis", "🔍 SQL Queries", "📈 Visualizations", "💡 Business Insights", "📋 About"]
)

# BigQuery connection setup
@st.cache_resource
def get_bigquery_client():
    """Initialize BigQuery client with service account credentials"""
    try:
        import os
        
        # Get the current file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Construct the absolute path to the credentials file
        credentials_path = os.path.join(current_dir, "istanbul_sales_analysis", "API.JSON")
        
        # Check if file exists
        if not os.path.exists(credentials_path):
            st.error(f"❌ Credentials file not found at: {credentials_path}")
            st.info(f"💡 Current working directory: {os.getcwd()}")
            st.info(f"💡 Looking for file in: {current_dir}")
            return None, None
        
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        client = bigquery.Client(
            credentials=credentials,
            project=credentials.project_id
        )
        
        return client, credentials.project_id
    except Exception as e:
        st.error(f"❌ Error connecting to BigQuery: {e}")
        st.info(f"💡 Please check if the credentials file exists at: istanbul_sales_analysis/API.JSON")
        return None, None

# Home page
if page == "🏠 Home":
    st.markdown("## 🎯 Retail Sales Dataset Analysis")
    st.markdown("**Dataset:** `moonlit-autumn-468306-p6.assignment_one_1.retail_sales`")
    st.markdown("**Source:** Kaggle Retail Sales Dataset")
    
    # BigQuery Status
    client, project_id = get_bigquery_client()
    if client is None:
        st.error("❌ BigQuery connection failed. Please check your credentials.")
        st.info("💡 Please check your BigQuery credentials and try again.")
    else:
        st.success(f"✅ Connected to BigQuery project: {project_id}")
        
        # Dataset Overview
        st.markdown("---")
        st.subheader("📋 Dataset Overview")
        
        try:
            # Get basic dataset info
            dataset_ref = f"{project_id}.assignment_one_1"
            dataset = client.get_dataset(dataset_ref)
            
            # Get table info
            table_ref = f"{project_id}.assignment_one_1.retail_sales"
            table = client.get_table(table_ref)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Dataset", "assignment_one_1")
                st.metric("Table", "retail_sales")
                st.metric("Location", table.location)
            
            with col2:
                st.metric("Total Rows", f"{table.num_rows:,}")
                st.metric("Table Size", f"{table.num_bytes / (1024*1024):.2f} MB")
                st.metric("Created", table.created.strftime("%Y-%m-%d"))
            
            with col3:
                st.metric("Project ID", project_id)
                st.metric("Columns", len(table.schema))
                st.metric("Last Modified", table.modified.strftime("%Y-%m-%d"))
            
        except Exception as e:
            st.error(f"❌ Error fetching dataset info: {e}")
        
        # Analysis Objectives
        st.markdown("---")
        st.subheader("🎯 Analysis Objectives")
        
        col1, col2 = st.columns(2)
        
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

# Dataset Analysis page
elif page == "📊 Dataset Analysis":
    st.header("📊 Comprehensive Dataset Analysis")
    
    client, project_id = get_bigquery_client()
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Table Schema Analysis
    st.markdown("---")
    st.subheader("🏗️ Table Schema Analysis")
    
    try:
        table_ref = f"{project_id}.assignment_one_1.retail_sales"
        table = client.get_table(table_ref)
        
        # Display schema
        schema_df = pd.DataFrame([
            {
                'Column': field.name,
                'Type': field.field_type,
                'Mode': field.mode,
                'Description': field.description or 'No description'
            }
            for field in table.schema
        ])
        
        st.write("**Table Schema:**")
        st.dataframe(schema_df, use_container_width=True)
        
        # Data types summary
        st.markdown("---")
        st.subheader("📋 Data Types Summary")
        
        type_counts = schema_df['Type'].value_counts()
        fig = px.pie(values=type_counts.values, names=type_counts.index, title="Data Types Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error analyzing schema: {e}")
    
    # Data Quality Analysis
    st.markdown("---")
    st.subheader("🔍 Data Quality Analysis")
    
    try:
        # Check for null values
        null_query = f"""
        SELECT 
            column_name,
            COUNT(*) as total_rows,
            COUNTIF(value IS NULL) as null_count,
            ROUND(COUNTIF(value IS NULL) * 100.0 / COUNT(*), 2) as null_percentage
        FROM `{project_id}.assignment_one_1.retail_sales`,
        UNNEST([
            STRUCT('transaction_date' as column_name, CAST(transaction_date AS STRING) as value),
            STRUCT('product_name' as column_name, product_name as value),
            STRUCT('store_name' as column_name, store_name as value),
            STRUCT('customer_id' as column_name, CAST(customer_id AS STRING) as value),
            STRUCT('quantity' as column_name, CAST(quantity AS STRING) as value),
            STRUCT('total_amount' as column_name, CAST(total_amount AS STRING) as value),
            STRUCT('payment_method' as column_name, payment_method as value)
        ])
        GROUP BY column_name
        ORDER BY null_percentage DESC
        """
        
        null_df = client.query(null_query).to_dataframe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Completeness Analysis:**")
            st.dataframe(null_df, use_container_width=True)
        
        with col2:
            # Create completeness chart
            fig = px.bar(
                null_df, 
                x='column_name', 
                y='null_percentage',
                title="Data Completeness by Column (%)",
                color='null_percentage',
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error analyzing data quality: {e}")
    
    # Sample Data Display
    st.markdown("---")
    st.subheader("📋 Sample Data")
    
    try:
        sample_query = f"SELECT * FROM `{project_id}.assignment_one_1.retail_sales` LIMIT 20"
        sample_df = client.query(sample_query).to_dataframe()
        
        st.write("**First 20 Records:**")
        st.dataframe(sample_df, use_container_width=True)
        
        # Download sample data
        csv = sample_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Sample Data as CSV",
            data=csv,
            file_name="retail_sales_sample.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"❌ Error fetching sample data: {e}")

# SQL Queries page
elif page == "🔍 SQL Queries":
    st.header("🔍 SQL Query Execution")
    
    client, project_id = get_bigquery_client()
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Pre-built Analysis Queries
    st.markdown("---")
    st.subheader("📋 Pre-built Analysis Queries")
    
    query_templates = {
        "Basic Overview": f"""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(DISTINCT store_name) as unique_stores,
            COUNT(DISTINCT product_name) as unique_products,
            ROUND(AVG(total_amount), 2) as avg_transaction_value,
            ROUND(SUM(total_amount), 2) as total_revenue
        FROM `{project_id}.assignment_one_1.retail_sales`
        """,
        
        "Category Performance": f"""
        SELECT 
            product_category,
            COUNT(*) as transaction_count,
            ROUND(SUM(total_amount), 2) as total_revenue,
            ROUND(AVG(total_amount), 2) as avg_transaction_value,
            ROUND(SUM(quantity), 0) as total_quantity_sold
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE product_category IS NOT NULL
        GROUP BY product_category
        ORDER BY total_revenue DESC
        """,
        
        "Store Performance": f"""
        SELECT 
            store_name,
            COUNT(*) as transaction_count,
            ROUND(SUM(total_amount), 2) as total_revenue,
            ROUND(AVG(total_amount), 2) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE store_name IS NOT NULL
        GROUP BY store_name
        ORDER BY total_revenue DESC
        LIMIT 15
        """,
        
        "Monthly Trends": f"""
        SELECT 
            EXTRACT(YEAR FROM transaction_date) as year,
            EXTRACT(MONTH FROM transaction_date) as month,
            COUNT(*) as transaction_count,
            ROUND(SUM(total_amount), 2) as monthly_revenue,
            ROUND(AVG(total_amount), 2) as avg_transaction_value
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE transaction_date IS NOT NULL
        GROUP BY year, month
        ORDER BY year, month
        """,
        
        "Customer Analysis": f"""
        SELECT 
            customer_id,
            COUNT(*) as transaction_count,
            ROUND(SUM(total_amount), 2) as total_spent,
            ROUND(AVG(total_amount), 2) as avg_transaction_value,
            COUNT(DISTINCT store_name) as stores_visited,
            MIN(transaction_date) as first_purchase,
            MAX(transaction_date) as last_purchase
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT 20
        """,
        
        "Payment Method Analysis": f"""
        SELECT 
            payment_method,
            COUNT(*) as transaction_count,
            ROUND(SUM(total_amount), 2) as total_revenue,
            ROUND(AVG(total_amount), 2) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE payment_method IS NOT NULL
        GROUP BY payment_method
        ORDER BY total_revenue DESC
        """
    }
    
    selected_template = st.selectbox("Choose a pre-built analysis:", list(query_templates.keys()))
    query = st.text_area("SQL Query:", value=query_templates[selected_template], height=200)
    
    if st.button("🚀 Execute Query", type="primary"):
        if query.strip():
            with st.spinner("Executing query..."):
                try:
                    # Execute query
                    results_df = client.query(query).to_dataframe()
                    
                    st.success(f"✅ Query executed successfully! Returned {len(results_df)} rows")
                    
                    # Display results
                    st.write("**Query Results:**")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Download results
                    if len(results_df) > 0:
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name=f"{selected_template.lower().replace(' ', '_')}_results.csv",
                            mime="text/csv"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Query execution failed: {e}")
                    st.info("💡 Check your SQL syntax and table references")
        else:
            st.warning("⚠️ Please enter a SQL query")
    
    # Custom Query Section
    st.markdown("---")
    st.subheader("✍️ Custom SQL Query")
    
    custom_query = st.text_area("Enter your custom SQL query:", height=150, 
                               placeholder=f"SELECT * FROM `{project_id}.assignment_one_1.retail_sales` LIMIT 10")
    
    if st.button("🔍 Run Custom Query"):
        if custom_query.strip():
            with st.spinner("Executing custom query..."):
                try:
                    # Execute custom query
                    custom_results = client.query(custom_query).to_dataframe()
                    
                    st.success(f"✅ Custom query executed successfully! Returned {len(custom_results)} rows")
                    
                    # Display results
                    st.write("**Custom Query Results:**")
                    st.dataframe(custom_results, use_container_width=True)
                    
                    # Download results
                    if len(custom_results) > 0:
                        csv = custom_results.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Custom Results as CSV",
                            data=csv,
                            file_name="custom_query_results.csv",
                            mime="text/csv"
                        )
                    
                except Exception as e:
                    st.error(f"❌ Custom query execution failed: {e}")
                    st.info("💡 Check your SQL syntax and table references")
        else:
            st.warning("⚠️ Please enter a custom SQL query")

# Visualizations page
elif page == "📈 Visualizations":
    st.header("📈 Interactive Data Visualizations")
    
    client, project_id = get_bigquery_client()
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Visualization Options
    st.markdown("---")
    st.subheader("📊 Choose Visualization Type")
    
    viz_options = [
        "Revenue by Category",
        "Store Performance",
        "Monthly Trends",
        "Customer Spending",
        "Payment Methods",
        "Product Performance"
    ]
    
    selected_viz = st.selectbox("Select visualization:", viz_options)
    
    if st.button("🎨 Generate Visualization", type="primary"):
        with st.spinner("Generating visualization..."):
            try:
                if selected_viz == "Revenue by Category":
                    # Category revenue analysis
                    query = f"""
                    SELECT 
                        product_category,
                        ROUND(SUM(total_amount), 2) as total_revenue,
                        COUNT(*) as transaction_count
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE product_category IS NOT NULL
                    GROUP BY product_category
                    ORDER BY total_revenue DESC
                    """
                    
                    df = client.query(query).to_dataframe()
                    
                    # Create bar chart
                    fig = px.bar(
                        df, 
                        x='product_category', 
                        y='total_revenue',
                        title="Revenue by Product Category",
                        color='transaction_count',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display data
                    st.write("**Category Revenue Data:**")
                    st.dataframe(df, use_container_width=True)
                
                elif selected_viz == "Store Performance":
                    # Store performance analysis
                    query = f"""
                    SELECT 
                        store_name,
                        ROUND(SUM(total_amount), 2) as total_revenue,
                        COUNT(*) as transaction_count,
                        ROUND(AVG(total_amount), 2) as avg_transaction_value
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE store_name IS NOT NULL
                    GROUP BY store_name
                    ORDER BY total_revenue DESC
                    LIMIT 15
                    """
                    
                    df = client.query(query).to_dataframe()
                    
                    # Create scatter plot
                    fig = px.scatter(
                        df,
                        x='transaction_count',
                        y='total_revenue',
                        size='avg_transaction_value',
                        color='total_revenue',
                        hover_data=['store_name'],
                        title="Store Performance: Revenue vs Transactions"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display data
                    st.write("**Store Performance Data:**")
                    st.dataframe(df, use_container_width=True)
                
                elif selected_viz == "Monthly Trends":
                    # Monthly trends analysis
                    query = f"""
                    SELECT 
                        EXTRACT(YEAR FROM transaction_date) as year,
                        EXTRACT(MONTH FROM transaction_date) as month,
                        ROUND(SUM(total_amount), 2) as monthly_revenue,
                        COUNT(*) as transaction_count
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE transaction_date IS NOT NULL
                    GROUP BY year, month
                    ORDER BY year, month
                    """
                    
                    df = client.query(query).to_dataframe()
                    
                    # Create line chart
                    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
                    fig = px.line(
                        df,
                        x='date',
                        y='monthly_revenue',
                        title="Monthly Revenue Trends",
                        markers=True
                    )
                    fig.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display data
                    st.write("**Monthly Trends Data:**")
                    st.dataframe(df, use_container_width=True)
                
                elif selected_viz == "Customer Spending":
                    # Customer spending analysis
                    query = f"""
                    SELECT 
                        customer_id,
                        ROUND(SUM(total_amount), 2) as total_spent,
                        COUNT(*) as transaction_count,
                        ROUND(AVG(total_amount), 2) as avg_transaction_value
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE customer_id IS NOT NULL
                    GROUP BY customer_id
                    ORDER BY total_spent DESC
                    LIMIT 50
                    """
                    
                    df = client.query(query).to_dataframe()
                    
                    # Create histogram
                    fig = px.histogram(
                        df,
                        x='total_spent',
                        nbins=20,
                        title="Customer Spending Distribution",
                        labels={'total_spent': 'Total Amount Spent ($)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display data
                    st.write("**Customer Spending Data (Top 50):**")
                    st.dataframe(df, use_container_width=True)
                
                elif selected_viz == "Payment Methods":
                    # Payment method analysis
                    query = f"""
                    SELECT 
                        payment_method,
                        COUNT(*) as transaction_count,
                        ROUND(SUM(total_amount), 2) as total_revenue,
                        ROUND(AVG(total_amount), 2) as avg_transaction_value
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE payment_method IS NOT NULL
                    GROUP BY payment_method
                    ORDER BY total_revenue DESC
                    """
                    
                    df = client.query(query).to_dataframe()
                    
                    # Create pie chart
                    fig = px.pie(
                        df,
                        values='total_revenue',
                        names='payment_method',
                        title="Revenue Distribution by Payment Method"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display data
                    st.write("**Payment Method Data:**")
                    st.dataframe(df, use_container_width=True)
                
                elif selected_viz == "Product Performance":
                    # Product performance analysis
                    query = f"""
                    SELECT 
                        product_name,
                        COUNT(*) as times_purchased,
                        ROUND(SUM(total_amount), 2) as total_revenue,
                        ROUND(SUM(quantity), 0) as total_quantity_sold
                    FROM `{project_id}.assignment_one_1.retail_sales`
                    WHERE product_name IS NOT NULL
                    GROUP BY product_name
                    ORDER BY total_revenue DESC
                    LIMIT 20
                    """
                    
                    df = client.query(query).to_dataframe()
                    
                    # Create horizontal bar chart
                    fig = px.bar(
                        df,
                        y='product_name',
                        x='total_revenue',
                        orientation='h',
                        title="Top 20 Products by Revenue",
                        color='times_purchased',
                        color_continuous_scale='Plasma'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display data
                    st.write("**Product Performance Data (Top 20):**")
                    st.dataframe(df, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error generating visualization: {e}")
                st.info("💡 This might be due to data type issues or missing columns")

# Business Insights page
elif page == "💡 Business Insights":
    st.header("💡 Business Intelligence Insights")
    
    client, project_id = get_bigquery_client()
    if client is None:
        st.error("❌ BigQuery connection failed.")
        st.stop()
    
    st.success(f"✅ Connected to BigQuery project: {project_id}")
    
    # Key Performance Indicators
    st.markdown("---")
    st.subheader("🎯 Key Performance Indicators (KPIs)")
    
    try:
        # Calculate KPIs
        kpi_query = f"""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(DISTINCT store_name) as unique_stores,
            COUNT(DISTINCT product_name) as unique_products,
            ROUND(SUM(total_amount), 2) as total_revenue,
            ROUND(AVG(total_amount), 2) as avg_transaction_value,
            ROUND(SUM(quantity), 0) as total_items_sold,
            ROUND(AVG(quantity), 2) as avg_items_per_transaction
        FROM `{project_id}.assignment_one_1.retail_sales`
        """
        
        kpi_df = client.query(kpi_query).to_dataframe()
        
        # Display KPIs in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transactions", f"{kpi_df.iloc[0]['total_transactions']:,}")
            st.metric("Total Revenue", f"${kpi_df.iloc[0]['total_revenue']:,.2f}")
        
        with col2:
            st.metric("Unique Customers", f"{kpi_df.iloc[0]['unique_customers']:,}")
            st.metric("Avg Transaction Value", f"${kpi_df.iloc[0]['avg_transaction_value']:.2f}")
        
        with col3:
            st.metric("Unique Stores", f"{kpi_df.iloc[0]['unique_stores']:,}")
            st.metric("Total Items Sold", f"{kpi_df.iloc[0]['total_items_sold']:,}")
        
        with col4:
            st.metric("Unique Products", f"{kpi_df.iloc[0]['unique_products']:,}")
            st.metric("Avg Items/Transaction", f"{kpi_df.iloc[0]['avg_items_per_transaction']:.2f}")
        
    except Exception as e:
        st.error(f"❌ Error calculating KPIs: {e}")
    
    # Business Insights Analysis
    st.markdown("---")
    st.subheader("💡 Business Insights Analysis")
    
    try:
        # Revenue by category insights
        category_query = f"""
        SELECT 
            product_category,
            ROUND(SUM(total_amount), 2) as total_revenue,
            COUNT(*) as transaction_count,
            ROUND(SUM(total_amount) * 100.0 / SUM(SUM(total_amount)) OVER(), 2) as revenue_percentage
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE product_category IS NOT NULL
        GROUP BY product_category
        ORDER BY total_revenue DESC
        """
        
        category_df = client.query(category_query).to_dataframe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Revenue by Category:**")
            st.dataframe(category_df, use_container_width=True)
        
        with col2:
            # Create pie chart
            fig = px.pie(
                category_df,
                values='total_revenue',
                names='product_category',
                title="Revenue Distribution by Category"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top performing stores
        st.markdown("---")
        st.subheader("🏪 Top Performing Stores")
        
        store_query = f"""
        SELECT 
            store_name,
            ROUND(SUM(total_amount), 2) as total_revenue,
            COUNT(*) as transaction_count,
            ROUND(AVG(total_amount), 2) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM `{project_id}.assignment_one_1.retail_sales`
        WHERE store_name IS NOT NULL
        GROUP BY store_name
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        
        store_df = client.query(store_query).to_dataframe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Top 10 Stores by Revenue:**")
            st.dataframe(store_df, use_container_width=True)
        
        with col2:
            # Create bar chart
            fig = px.bar(
                store_df,
                x='store_name',
                y='total_revenue',
                title="Top 10 Stores by Revenue",
                color='transaction_count',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Customer insights
        st.markdown("---")
        st.subheader("👥 Customer Insights")
        
        customer_query = f"""
        SELECT 
            CASE 
                WHEN total_spent >= 1000 THEN 'High Value'
                WHEN total_spent >= 500 THEN 'Medium Value'
                ELSE 'Low Value'
            END as customer_segment,
            COUNT(*) as customer_count,
            ROUND(AVG(total_spent), 2) as avg_spent,
            ROUND(SUM(total_spent), 2) as total_spent
        FROM (
            SELECT 
                customer_id,
                SUM(total_amount) as total_spent
            FROM `{project_id}.assignment_one_1.retail_sales`
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
        )
        GROUP BY customer_segment
        ORDER BY total_spent DESC
        """
        
        customer_df = client.query(customer_query).to_dataframe()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Customer Segmentation by Spending:**")
            st.dataframe(customer_df, use_container_width=True)
        
        with col2:
            # Create pie chart
            fig = px.pie(
                customer_df,
                values='customer_count',
                names='customer_segment',
                title="Customer Distribution by Value Segment"
            )
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error generating business insights: {e}")
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Business Recommendations")
    
    try:
        # Generate recommendations based on data
        st.markdown("""
        **🎯 Based on the analysis, here are key business recommendations:**
        
        **📈 Revenue Optimization:**
        - Focus on high-performing product categories
        - Optimize store performance in top locations
        - Develop customer loyalty programs for high-value customers
        
        **🏪 Store Performance:**
        - Analyze successful store strategies
        - Implement best practices across all locations
        - Consider expansion in high-performing areas
        
        **👥 Customer Strategy:**
        - Target high-value customer segments
        - Develop retention strategies for medium-value customers
        - Create engagement programs for low-value customers
        
        **📊 Data Quality:**
        - Monitor data completeness regularly
        - Implement data validation processes
        - Ensure consistent data entry across stores
        """)
        
    except Exception as e:
        st.error(f"❌ Error generating recommendations: {e}")

# About page
elif page == "📋 About":
    st.header("📋 About This Dashboard")
    
    st.markdown("""
    ## 🎯 Purpose
    This dashboard provides comprehensive analysis of the retail sales dataset from BigQuery, 
    offering business intelligence insights and data-driven recommendations.
    
    ## 🔗 Data Source
    - **Dataset:** `moonlit-autumn-468306-p6.assignment_one_1.retail_sales`
    - **Source:** Kaggle Retail Sales Dataset
    - **Platform:** Google BigQuery
    
    ## 🛠️ Features
    - **Data Exploration:** Comprehensive dataset analysis and schema review
    - **SQL Queries:** Pre-built and custom SQL query execution
    - **Visualizations:** Interactive charts and graphs
    - **Business Insights:** KPI analysis and business recommendations
    - **Data Export:** Download results and insights
    
    ## 📊 Analysis Capabilities
    - Revenue analysis by category and store
    - Customer segmentation and behavior analysis
    - Temporal trends and seasonality
    - Payment method performance
    - Product performance insights
    
    ## 🚀 Technologies Used
    - **Streamlit:** Web application framework
    - **BigQuery:** Cloud data warehouse
    - **Plotly:** Interactive visualizations
    - **Pandas:** Data manipulation
    - **Python:** Programming language
    
    ---
    
    **📊 Retail Sales Analysis Dashboard | Powered by BigQuery & Streamlit**
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")

# Footer for all pages
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 Retail Sales Analysis Dashboard | BigQuery Integration | Built with Streamlit</p>
    <p><small>Comprehensive analysis of retail sales data with business intelligence insights</small></p>
</div>
""", unsafe_allow_html=True)
