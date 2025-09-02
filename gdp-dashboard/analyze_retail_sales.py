#!/usr/bin/env python3
"""
Enhanced Analysis of retail_sales table in assignment_one_1 dataset
Creates comprehensive views, stored procedures, and provides frontend insights
"""

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

def create_analysis_views_and_procedures(client, project_id, dataset_id):
    """Create comprehensive business intelligence views for data insights"""
    
    st.subheader("🏗️ Creating Business Intelligence Views")
    
    # Define the table reference
    table_ref = f"{project_id}.{dataset_id}.retail_sales"
    
    # 1. Executive Summary Dashboard View
    st.write("**1️⃣ Executive Summary Dashboard**")
    executive_summary_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_executive_summary` AS
    SELECT 
        'Executive Summary' as dashboard_type,
        COUNT(*) as total_transactions,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT store_name) as total_stores,
        COUNT(DISTINCT product_category) as product_categories,
        SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
        AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
        SUM(CAST(quantity AS INT64)) as total_items_sold,
        AVG(CAST(quantity AS FLOAT64)) as avg_items_per_transaction,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(DISTINCT store_name), 2) as revenue_per_store
    FROM `{table_ref}`
    """
    
    try:
        client.query(executive_summary_query)
        st.success("✅ Created Executive Summary Dashboard")
    except Exception as e:
        st.error(f"❌ Error creating Executive Summary: {e}")
    
    # 2. Sales Performance Insights View
    st.write("**2️⃣ Sales Performance Insights**")
    sales_insights_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_performance_insights` AS
    SELECT 
        product_category,
        COUNT(*) as transaction_count,
        SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
        AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
        SUM(CAST(quantity AS INT64)) as total_quantity_sold,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT store_name) as stores_involved,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) * 100.0 / SUM(SUM(CAST(total_amount AS FLOAT64))) OVER(), 2) as revenue_percentage,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as transaction_percentage
    FROM `{table_ref}`
    WHERE product_category IS NOT NULL
    GROUP BY product_category
    ORDER BY total_revenue DESC
    """
    
    try:
        client.query(sales_insights_query)
        st.success("✅ Created Sales Performance Insights")
    except Exception as e:
        st.error(f"❌ Error creating Sales Insights: {e}")
    
    # 3. Store Performance Analysis View
    st.write("**3️⃣ Store Performance Analysis**")
    store_insights_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_store_insights` AS
    SELECT 
        store_name,
        COUNT(*) as transaction_count,
        SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
        AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT product_category) as product_categories,
        SUM(CAST(quantity AS INT64)) as total_quantity_sold,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer,
        ROUND(COUNT(*) / COUNT(DISTINCT customer_id), 2) as transactions_per_customer,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(*), 2) as revenue_per_transaction
    FROM `{table_ref}`
    WHERE store_name IS NOT NULL
    GROUP BY store_name
    ORDER BY total_revenue DESC
    """
    
    try:
        client.query(store_insights_query)
        st.success("✅ Created Store Performance Insights")
    except Exception as e:
        st.error(f"❌ Error creating Store Insights: {e}")
    
    # 4. Customer Segmentation View
    st.write("**4️⃣ Customer Segmentation Analysis**")
    customer_segmentation_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_customer_segmentation` AS
    SELECT 
        CASE 
            WHEN total_spent >= 1000 THEN 'High Value (≥$1000)'
            WHEN total_spent >= 500 THEN 'Medium Value ($500-$999)'
            WHEN total_spent >= 100 THEN 'Low Value ($100-$499)'
            ELSE 'Minimal Value (<$100)'
        END as customer_segment,
        COUNT(*) as customer_count,
        ROUND(AVG(total_spent), 2) as avg_spending,
        ROUND(SUM(total_spent), 2) as total_segment_revenue,
        ROUND(AVG(transaction_count), 2) as avg_transactions,
        ROUND(AVG(stores_visited), 2) as avg_stores_visited,
        ROUND(AVG(product_categories_purchased), 2) as avg_categories
    FROM (
        SELECT 
            customer_id,
            COUNT(*) as transaction_count,
            SUM(CAST(total_amount AS FLOAT64)) as total_spent,
            COUNT(DISTINCT store_name) as stores_visited,
            COUNT(DISTINCT product_category) as product_categories_purchased
        FROM `{table_ref}`
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
    )
    GROUP BY customer_segment
    ORDER BY avg_spending DESC
    """
    
    try:
        client.query(customer_segmentation_query)
        st.success("✅ Created Customer Segmentation")
    except Exception as e:
        st.error(f"❌ Error creating Customer Segmentation: {e}")
    
    # 5. Product Performance Insights View
    st.write("**5️⃣ Product Performance Insights**")
    product_insights_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_product_insights` AS
    SELECT 
        product_name,
        product_category,
        COUNT(*) as times_purchased,
        SUM(CAST(quantity AS INT64)) as total_quantity_sold,
        SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
        AVG(CAST(total_amount AS FLOAT64)) as avg_sale_price,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT store_name) as stores_selling,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / SUM(CAST(quantity AS INT64)), 2) as effective_unit_price,
        ROUND(COUNT(DISTINCT customer_id) * 100.0 / COUNT(*), 2) as customer_diversity_score
    FROM `{table_ref}`
    WHERE product_name IS NOT NULL
    GROUP BY product_name, product_category
    ORDER BY total_revenue DESC
    """
    
    try:
        client.query(product_insights_query)
        st.success("✅ Created Product Performance Insights")
    except Exception as e:
        st.error(f"❌ Error creating Product Insights: {e}")
    
    # 6. Temporal Trends & Seasonality View
    st.write("**6️⃣ Temporal Trends & Seasonality**")
    temporal_insights_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_temporal_insights` AS
    SELECT 
        EXTRACT(YEAR FROM transaction_date) as year,
        EXTRACT(MONTH FROM transaction_date) as month,
        EXTRACT(DAYOFWEEK FROM transaction_date) as day_of_week,
        CASE EXTRACT(MONTH FROM transaction_date)
            WHEN 12 OR 1 OR 2 THEN 'Winter'
            WHEN 3 OR 4 OR 5 THEN 'Spring'
            WHEN 6 OR 7 OR 8 THEN 'Summer'
            WHEN 9 OR 10 OR 11 THEN 'Fall'
        END as season,
        COUNT(*) as transaction_count,
        SUM(CAST(total_amount AS FLOAT64)) as monthly_revenue,
        AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT store_name) as active_stores,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer
    FROM `{table_ref}`
    WHERE transaction_date IS NOT NULL
    GROUP BY year, month, day_of_week, season
    ORDER BY year, month, day_of_week
    """
    
    try:
        client.query(temporal_insights_query)
        st.success("✅ Created Temporal Trends & Seasonality")
    except Exception as e:
        st.error(f"❌ Error creating Temporal Insights: {e}")
    
    # 7. Payment & Financial Insights View
    st.write("**7️⃣ Payment & Financial Insights**")
    payment_insights_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_payment_insights` AS
    SELECT 
        payment_method,
        COUNT(*) as transaction_count,
        SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
        AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT store_name) as stores_used,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) * 100.0 / SUM(SUM(CAST(total_amount AS FLOAT64))) OVER(), 2) as revenue_percentage,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as transaction_percentage,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer
    FROM `{table_ref}`
    WHERE payment_method IS NOT NULL
    GROUP BY payment_method
    ORDER BY total_revenue DESC
    """
    
    try:
        client.query(payment_insights_query)
        st.success("✅ Created Payment & Financial Insights")
    except Exception as e:
        st.error(f"❌ Error creating Payment Insights: {e}")
    
    # 8. Data Quality & Completeness View
    st.write("**8️⃣ Data Quality & Completeness**")
    data_quality_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_data_quality` AS
    SELECT 
        'Data Completeness Assessment' as metric_type,
        COUNT(*) as total_records,
        COUNTIF(transaction_date IS NOT NULL) as records_with_date,
        COUNTIF(product_name IS NOT NULL) as records_with_product,
        COUNTIF(store_name IS NOT NULL) as records_with_store,
        COUNTIF(customer_id IS NOT NULL) as records_with_customer,
        COUNTIF(quantity IS NOT NULL) as records_with_quantity,
        COUNTIF(total_amount IS NOT NULL) as records_with_amount,
        ROUND(COUNTIF(transaction_date IS NOT NULL) * 100.0 / COUNT(*), 2) as date_completeness_pct,
        ROUND(COUNTIF(product_name IS NOT NULL) * 100.0 / COUNT(*), 2) as product_completeness_pct,
        ROUND(COUNTIF(store_name IS NOT NULL) * 100.0 / COUNT(*), 2) as store_completeness_pct,
        ROUND(COUNTIF(customer_id IS NOT NULL) * 100.0 / COUNT(*), 2) as customer_completeness_pct,
        ROUND(COUNTIF(quantity IS NOT NULL) * 100.0 / COUNT(*), 2) as quantity_completeness_pct,
        ROUND(COUNTIF(total_amount IS NOT NULL) * 100.0 / COUNT(*), 2) as amount_completeness_pct
    FROM `{table_ref}`
    """
    
    try:
        client.query(data_quality_query)
        st.success("✅ Created Data Quality Assessment")
    except Exception as e:
        st.error(f"❌ Error creating Data Quality: {e}")
    
    # 9. Business Intelligence KPIs View
    st.write("**9️⃣ Business Intelligence KPIs**")
    kpi_insights_query = f"""
    CREATE OR REPLACE VIEW `{project_id}.{dataset_id}.retail_sales_kpi_insights` AS
    SELECT 
        'Key Performance Indicators' as kpi_type,
        COUNT(*) as total_transactions,
        COUNT(DISTINCT customer_id) as unique_customers,
        COUNT(DISTINCT store_name) as total_stores,
        SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
        AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
        SUM(CAST(quantity AS INT64)) as total_items_sold,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(DISTINCT customer_id), 2) as customer_lifetime_value,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(DISTINCT store_name), 2) as store_performance,
        ROUND(COUNT(*) / COUNT(DISTINCT customer_id), 2) as customer_engagement_rate,
        ROUND(SUM(CAST(total_amount AS FLOAT64)) / COUNT(*), 2) as revenue_per_transaction,
        ROUND(SUM(CAST(quantity AS INT64)) / COUNT(*), 2) as items_per_transaction
    FROM `{table_ref}`
    """
    
    try:
        client.query(kpi_insights_query)
        st.success("✅ Created Business Intelligence KPIs")
    except Exception as e:
        st.error(f"❌ Error creating KPI Insights: {e}")
    
    st.success("🎉 All Business Intelligence views created successfully!")

def display_frontend_insights(client, project_id, dataset_id):
    """Display comprehensive business intelligence insights in the frontend"""
    
    st.subheader("📊 Business Intelligence Dashboard")
    
    try:
        # 1. Executive Summary KPIs
        st.write("**🎯 Executive Summary - Key Performance Indicators**")
        executive_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_executive_summary`"
        executive_data = client.query(executive_query).to_dataframe()
        
        if not executive_data.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Revenue", f"${executive_data.iloc[0]['total_revenue']:,.2f}")
            with col2:
                st.metric("Total Transactions", f"{executive_data.iloc[0]['total_transactions']:,}")
            with col3:
                st.metric("Unique Customers", f"{executive_data.iloc[0]['unique_customers']:,}")
            with col4:
                st.metric("Total Stores", f"{executive_data.iloc[0]['total_stores']:,}")
            
            # Second row of KPIs
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Transaction Value", f"${executive_data.iloc[0]['avg_transaction_value']:.2f}")
            with col2:
                st.metric("Revenue per Customer", f"${executive_data.iloc[0]['revenue_per_customer']:.2f}")
            with col3:
                st.metric("Revenue per Store", f"${executive_data.iloc[0]['revenue_per_store']:.2f}")
            with col4:
                st.metric("Total Items Sold", f"{executive_data.iloc[0]['total_items_sold']:,}")
        
        # 2. Sales Performance Insights
        st.write("**📈 Sales Performance by Product Category**")
        sales_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_performance_insights` LIMIT 10"
        sales_data = client.query(sales_query).to_dataframe()
        
        if not sales_data.empty:
            # Create a comprehensive chart
            fig = px.bar(
                sales_data, 
                x='product_category', 
                y='total_revenue',
                title="Revenue by Product Category with Transaction Count",
                color='transaction_count',
                color_continuous_scale='viridis',
                hover_data=['unique_customers', 'revenue_percentage', 'transaction_percentage']
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show insights table
            st.write("**📊 Category Performance Insights:**")
            insights_table = sales_data[['product_category', 'total_revenue', 'transaction_count', 'unique_customers', 'revenue_percentage', 'transaction_percentage']].copy()
            insights_table['total_revenue'] = insights_table['total_revenue'].round(2)
            insights_table['revenue_percentage'] = insights_table['revenue_percentage'].round(2)
            insights_table['transaction_percentage'] = insights_table['transaction_percentage'].round(2)
            st.dataframe(insights_table, use_container_width=True)
        
        # 3. Store Performance Analysis
        st.write("**🏪 Store Performance & Efficiency Analysis**")
        store_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_store_insights` LIMIT 10"
        store_data = client.query(store_query).to_dataframe()
        
        if not store_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Store performance scatter plot
                fig = px.scatter(
                    store_data,
                    x='transaction_count',
                    y='total_revenue',
                    size='unique_customers',
                    color='avg_transaction_value',
                    hover_name='store_name',
                    title="Store Performance: Revenue vs Transactions",
                    labels={'transaction_count': 'Number of Transactions', 'total_revenue': 'Total Revenue ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Revenue per customer by store
                fig = px.bar(
                    store_data.head(8),
                    x='store_name',
                    y='revenue_per_customer',
                    title="Revenue per Customer by Store",
                    color='total_revenue'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Store insights table
            st.write("**📊 Store Performance Metrics:**")
            store_metrics = store_data[['store_name', 'total_revenue', 'transaction_count', 'unique_customers', 'revenue_per_customer', 'transactions_per_customer']].copy()
            store_metrics['total_revenue'] = store_metrics['total_revenue'].round(2)
            store_metrics['revenue_per_customer'] = store_metrics['revenue_per_customer'].round(2)
            store_metrics['transactions_per_customer'] = store_metrics['transactions_per_customer'].round(2)
            st.dataframe(store_metrics, use_container_width=True)
        
        # 4. Customer Segmentation Insights
        st.write("**👥 Customer Segmentation & Value Analysis**")
        customer_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_customer_segmentation`"
        customer_data = client.query(customer_query).to_dataframe()
        
        if not customer_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Customer segment distribution
                fig = px.pie(
                    customer_data,
                    values='customer_count',
                    names='customer_segment',
                    title="Customer Distribution by Value Segment"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Average spending by segment
                fig = px.bar(
                    customer_data,
                    x='customer_segment',
                    y='avg_spending',
                    title="Average Spending by Customer Segment",
                    color='customer_count'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Customer insights table
            st.write("**📊 Customer Segment Analysis:**")
            customer_metrics = customer_data[['customer_segment', 'customer_count', 'avg_spending', 'total_segment_revenue', 'avg_transactions', 'avg_stores_visited']].copy()
            customer_metrics['avg_spending'] = customer_metrics['avg_spending'].round(2)
            customer_metrics['total_segment_revenue'] = customer_metrics['total_segment_revenue'].round(2)
            customer_metrics['avg_transactions'] = customer_metrics['avg_transactions'].round(2)
            customer_metrics['avg_stores_visited'] = customer_metrics['avg_stores_visited'].round(2)
            st.dataframe(customer_metrics, use_container_width=True)
        
        # 5. Product Performance Insights
        st.write("**🛍️ Product Performance & Market Analysis**")
        product_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_product_insights` ORDER BY total_revenue DESC LIMIT 15"
        product_data = client.query(product_query).to_dataframe()
        
        if not product_data.empty:
            # Top products by revenue
            fig = px.bar(
                product_data,
                x='product_name',
                y='total_revenue',
                color='product_category',
                title="Top 15 Products by Revenue",
                height=500
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Product insights table
            st.write("**📊 Product Performance Metrics:**")
            product_metrics = product_data[['product_name', 'product_category', 'total_revenue', 'times_purchased', 'unique_customers', 'effective_unit_price', 'customer_diversity_score']].copy()
            product_metrics['total_revenue'] = product_metrics['total_revenue'].round(2)
            product_metrics['effective_unit_price'] = product_metrics['effective_unit_price'].round(2)
            product_metrics['customer_diversity_score'] = product_metrics['customer_diversity_score'].round(2)
            st.dataframe(product_metrics, use_container_width=True)
        
        # 6. Temporal Trends & Seasonality
        st.write("**📅 Sales Trends & Seasonal Patterns**")
        temporal_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_temporal_insights` ORDER BY year, month"
        temporal_data = client.query(temporal_query).to_dataframe()
        
        if not temporal_data.empty:
            # Create date column for plotting
            temporal_data['date'] = pd.to_datetime(temporal_data[['year', 'month']].assign(day=1))
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Monthly revenue trends
                fig = px.line(
                    temporal_data,
                    x='date',
                    y='monthly_revenue',
                    title="Monthly Revenue Trends",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Seasonal analysis
                seasonal_data = temporal_data.groupby('season').agg({
                    'monthly_revenue': 'sum',
                    'transaction_count': 'sum',
                    'unique_customers': 'sum'
                }).reset_index()
                
                fig = px.bar(
                    seasonal_data,
                    x='season',
                    y='monthly_revenue',
                    title="Revenue by Season",
                    color='transaction_count'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 7. Payment & Financial Insights
        st.write("**💳 Payment Methods & Financial Analysis**")
        payment_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_payment_insights`"
        payment_data = client.query(payment_query).to_dataframe()
        
        if not payment_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Revenue by payment method
                fig = px.pie(
                    payment_data,
                    values='total_revenue',
                    names='payment_method',
                    title="Revenue Distribution by Payment Method"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Transaction value by payment method
                fig = px.bar(
                    payment_data,
                    x='payment_method',
                    y='avg_transaction_value',
                    title="Average Transaction Value by Payment Method",
                    color='transaction_count'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Payment insights table
            st.write("**📊 Payment Method Analysis:**")
            payment_metrics = payment_data[['payment_method', 'total_revenue', 'transaction_count', 'avg_transaction_value', 'revenue_percentage', 'transaction_percentage']].copy()
            payment_metrics['total_revenue'] = payment_metrics['total_revenue'].round(2)
            payment_metrics['avg_transaction_value'] = payment_metrics['avg_transaction_value'].round(2)
            payment_metrics['revenue_percentage'] = payment_metrics['revenue_percentage'].round(2)
            payment_metrics['transaction_percentage'] = payment_metrics['transaction_percentage'].round(2)
            st.dataframe(payment_metrics, use_container_width=True)
        
        # 8. Data Quality Assessment
        st.write("**🔍 Data Quality & Completeness Metrics**")
        quality_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_data_quality`"
        quality_data = client.query(quality_query).to_dataframe()
        
        if not quality_data.empty:
            st.info("📊 Data Quality Assessment:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Date Completeness", f"{quality_data.iloc[0]['date_completeness_pct']}%")
                st.metric("Product Completeness", f"{quality_data.iloc[0]['product_completeness_pct']}%")
            with col2:
                st.metric("Store Completeness", f"{quality_data.iloc[0]['store_completeness_pct']}%")
                st.metric("Customer Completeness", f"{quality_data.iloc[0]['customer_completeness_pct']}%")
            with col3:
                st.metric("Quantity Completeness", f"{quality_data.iloc[0]['quantity_completeness_pct']}%")
                st.metric("Amount Completeness", f"{quality_data.iloc[0]['amount_completeness_pct']}%")
        
        # 9. Business Intelligence Summary
        st.write("**🎯 Business Intelligence Summary**")
        kpi_query = f"SELECT * FROM `{project_id}.{dataset_id}.retail_sales_kpi_insights`"
        kpi_data = client.query(kpi_query).to_dataframe()
        
        if not kpi_data.empty:
            st.success("📊 **Key Business Insights:**")
            
            insights = [
                f"💰 **Revenue Performance**: Total revenue of ${kpi_data.iloc[0]['total_revenue']:,.2f} from {kpi_data.iloc[0]['total_transactions']:,} transactions",
                f"👥 **Customer Metrics**: {kpi_data.iloc[0]['unique_customers']:,} unique customers with average lifetime value of ${kpi_data.iloc[0]['customer_lifetime_value']:.2f}",
                f"🏪 **Store Performance**: {kpi_data.iloc[0]['total_stores']:,} stores with average performance of ${kpi_data.iloc[0]['store_performance']:.2f}",
                f"📈 **Engagement**: Customer engagement rate of {kpi_data.iloc[0]['customer_engagement_rate']:.2f} transactions per customer",
                f"🛒 **Transaction Quality**: Average transaction value of ${kpi_data.iloc[0]['revenue_per_transaction']:.2f} with {kpi_data.iloc[0]['items_per_transaction']:.1f} items per transaction"
            ]
            
            for insight in insights:
                st.write(insight)
    
    except Exception as e:
        st.error(f"❌ Error displaying insights: {e}")
        st.info("💡 Make sure all analysis views have been created first")

def display_direct_insights(client, project_id, dataset_id):
    """Display insights directly from the source table without requiring views"""
    
    st.subheader("📊 Direct Insights from Source Table")
    
    table_ref = f"{project_id}.{dataset_id}.retail_sales"
    
    try:
        # 1. Basic KPIs
        st.write("**🎯 Key Performance Indicators (KPIs)**")
        
        basic_query = f"""
        SELECT 
            COUNT(*) as total_records,
            AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
            SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
            AVG(CAST(quantity AS FLOAT64)) as avg_quantity,
            COUNT(DISTINCT customer_id) as unique_customers,
            COUNT(DISTINCT store_name) as unique_stores,
            COUNT(DISTINCT product_category) as product_categories
        FROM `{table_ref}`
        """
        
        basic_stats = client.query(basic_query).to_dataframe()
        
        if not basic_stats.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", f"{basic_stats.iloc[0]['total_records']:,}")
            with col2:
                st.metric("Avg Transaction Value", f"${basic_stats.iloc[0]['avg_transaction_value']:.2f}")
            with col3:
                st.metric("Total Revenue", f"${basic_stats.iloc[0]['total_revenue']:,.2f}")
            with col4:
                st.metric("Unique Customers", f"{basic_stats.iloc[0]['unique_customers']:,}")
        
        # 2. Category Performance
        st.write("**📈 Product Category Performance**")
        
        category_query = f"""
        SELECT 
            product_category,
            COUNT(*) as transaction_count,
            SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
            AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM `{table_ref}`
        WHERE product_category IS NOT NULL
        GROUP BY product_category
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        
        category_data = client.query(category_query).to_dataframe()
        
        if not category_data.empty:
            fig = px.bar(
                category_data, 
                x='product_category', 
                y='total_revenue',
                title="Revenue by Product Category",
                color='transaction_count',
                color_continuous_scale='viridis'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show top categories table
            st.write("**Top Revenue Categories:**")
            st.dataframe(category_data, use_container_width=True)
        
        # 3. Store Performance
        st.write("**🏪 Store Performance Analysis**")
        
        store_query = f"""
        SELECT 
            store_name,
            COUNT(*) as transaction_count,
            SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
            AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM `{table_ref}`
        WHERE store_name IS NOT NULL
        GROUP BY store_name
        ORDER BY total_revenue DESC
        LIMIT 10
        """
        
        store_data = client.query(store_query).to_dataframe()
        
        if not store_data.empty:
            fig = px.scatter(
                store_data,
                x='transaction_count',
                y='total_revenue',
                size='unique_customers',
                color='avg_transaction_value',
                hover_name='store_name',
                title="Store Performance: Revenue vs Transactions"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 4. Temporal Trends
        st.write("**📅 Sales Trends Over Time**")
        
        temporal_query = f"""
        SELECT 
            EXTRACT(YEAR FROM transaction_date) as year,
            EXTRACT(MONTH FROM transaction_date) as month,
            COUNT(*) as transaction_count,
            SUM(CAST(total_amount AS FLOAT64)) as monthly_revenue
        FROM `{table_ref}`
        WHERE transaction_date IS NOT NULL
        GROUP BY year, month
        ORDER BY year, month
        """
        
        temporal_data = client.query(temporal_query).to_dataframe()
        
        if not temporal_data.empty:
            # Create date column for plotting
            temporal_data['date'] = pd.to_datetime(temporal_data[['year', 'month']].assign(day=1))
            
            fig = px.line(
                temporal_data,
                x='date',
                y='monthly_revenue',
                title="Monthly Revenue Trends",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # 5. Customer Behavior
        st.write("**👥 Customer Behavior Insights**")
        
        customer_query = f"""
        SELECT 
            customer_id,
            COUNT(*) as total_transactions,
            SUM(CAST(total_amount AS FLOAT64)) as total_spent,
            AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value,
            COUNT(DISTINCT store_name) as stores_visited,
            COUNT(DISTINCT product_category) as product_categories_purchased
        FROM `{table_ref}`
        WHERE customer_id IS NOT NULL
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT 20
        """
        
        customer_data = client.query(customer_query).to_dataframe()
        
        if not customer_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.histogram(
                    customer_data,
                    x='total_spent',
                    nbins=20,
                    title="Customer Spending Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.scatter(
                    customer_data,
                    x='total_transactions',
                    y='total_spent',
                    size='product_categories_purchased',
                    color='stores_visited',
                    title="Customer Value Analysis"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 6. Product Performance
        st.write("**🛍️ Top Performing Products**")
        
        product_query = f"""
        SELECT 
            product_name,
            product_category,
            COUNT(*) as times_purchased,
            SUM(CAST(quantity AS INT64)) as total_quantity_sold,
            SUM(CAST(total_amount AS FLOAT64)) as total_revenue
        FROM `{table_ref}`
        WHERE product_name IS NOT NULL
        GROUP BY product_name, product_category
        ORDER BY total_revenue DESC
        LIMIT 15
        """
        
        product_data = client.query(product_query).to_dataframe()
        
        if not product_data.empty:
            fig = px.bar(
                product_data,
                x='product_name',
                y='total_revenue',
                color='product_category',
                title="Top Products by Revenue",
                height=500
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        # 7. Payment Method Analysis
        st.write("**💳 Payment Method Preferences**")
        
        payment_query = f"""
        SELECT 
            payment_method,
            COUNT(*) as transaction_count,
            SUM(CAST(total_amount AS FLOAT64)) as total_revenue,
            AVG(CAST(total_amount AS FLOAT64)) as avg_transaction_value
        FROM `{table_ref}`
        WHERE payment_method IS NOT NULL
        GROUP BY payment_method
        ORDER BY total_revenue DESC
        """
        
        payment_data = client.query(payment_query).to_dataframe()
        
        if not payment_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    payment_data,
                    values='total_revenue',
                    names='payment_method',
                    title="Revenue by Payment Method"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    payment_data,
                    x='payment_method',
                    y='avg_transaction_value',
                    title="Average Transaction Value by Payment Method"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # 8. Data Quality Assessment
        st.write("**🔍 Data Quality Assessment**")
        
        quality_query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNTIF(transaction_date IS NOT NULL) as records_with_date,
            COUNTIF(product_name IS NOT NULL) as records_with_product,
            COUNTIF(store_name IS NOT NULL) as records_with_store,
            COUNTIF(customer_id IS NOT NULL) as records_with_customer,
            ROUND(COUNTIF(transaction_date IS NOT NULL) * 100.0 / COUNT(*), 2) as date_completeness_pct,
            ROUND(COUNTIF(product_name IS NOT NULL) * 100.0 / COUNT(*), 2) as product_completeness_pct,
            ROUND(COUNTIF(store_name IS NOT NULL) * 100.0 / COUNT(*), 2) as store_completeness_pct,
            ROUND(COUNTIF(customer_id IS NOT NULL) * 100.0 / COUNT(*), 2) as customer_completeness_pct
        FROM `{table_ref}`
        """
        
        quality_data = client.query(quality_query).to_dataframe()
        
        if not quality_data.empty:
            st.info("📊 Data Quality Metrics:")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Date Completeness", f"{quality_data.iloc[0]['date_completeness_pct']}%")
            with col2:
                st.metric("Product Completeness", f"{quality_data.iloc[0]['product_completeness_pct']}%")
            with col3:
                st.metric("Store Completeness", f"{quality_data.iloc[0]['store_completeness_pct']}%")
            with col4:
                st.metric("Customer Completeness", f"{quality_data.iloc[0]['customer_completeness_pct']}%")
    
    except Exception as e:
        st.error(f"❌ Error displaying direct insights: {e}")
        st.info("💡 This analysis works directly from the source table")

def analyze_retail_sales_table():
    """Main function to analyze the retail_sales table and create comprehensive analysis views"""
    
    st.title("🔍 Enhanced Retail Sales Table Analysis")
    st.write("Analyzing `moonlit-autumn-468306-p6.assignment_one_1.retail_sales`")
    
    try:
        # Initialize BigQuery client with your credentials
        credentials = service_account.Credentials.from_service_account_file(
            "istanbul_sales_analysis/API.JSON",
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        client = bigquery.Client(
            credentials=credentials,
            project=credentials.project_id
        )
        
        st.success(f"✅ Connected to BigQuery project: {credentials.project_id}")
        
        # Define the table reference
        table_ref = f"{credentials.project_id}.assignment_one_1.retail_sales"
        
        # Get table information
        st.subheader("📊 Table Information")
        with st.spinner("Fetching table information..."):
            table = client.get_table(table_ref)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", f"{table.num_rows:,}")
            with col2:
                st.metric("Size", f"{table.num_bytes / (1024*1024):.2f} MB")
            with col3:
                st.metric("Columns", len(table.schema))
        
        # Display schema
        st.subheader("📋 Table Schema")
        schema_data = []
        for field in table.schema:
            schema_data.append({
                'Column': field.name,
                'Type': field.field_type,
                'Mode': field.mode,
                'Description': field.description or 'No description'
            })
        
        schema_df = pd.DataFrame(schema_data)
        st.dataframe(schema_df, use_container_width=True)
        
        # Categorize columns
        numeric_columns = [col['Column'] for col in schema_data if col['Type'] in ['INT64', 'FLOAT64', 'NUMERIC']]
        categorical_columns = [col['Column'] for col in schema_data if col['Type'] in ['STRING', 'BOOL']]
        date_columns = [col['Column'] for col in schema_data if col['Type'] in ['DATE', 'DATETIME', 'TIMESTAMP']]
        
        st.info(f"📊 Found {len(numeric_columns)} numeric, {len(categorical_columns)} categorical, and {len(date_columns)} date columns")
        
        # Sample data
        st.subheader("📋 Sample Data")
        with st.spinner("Fetching sample data..."):
            sample_query = f"SELECT * FROM `{table_ref}` LIMIT 10"
            sample_df = client.query(sample_query).to_dataframe()
            st.dataframe(sample_df, use_container_width=True)
        
        # Create analysis views and procedures
        create_analysis_views_and_procedures(client, credentials.project_id, "assignment_one_1")
        
        # Display frontend insights
        display_frontend_insights(client, credentials.project_id, "assignment_one_1")
        
    except Exception as e:
        st.error(f"❌ Error in analysis: {e}")
        st.info("💡 Please check your BigQuery credentials and table access")

if __name__ == "__main__":
    analyze_retail_sales_table()
