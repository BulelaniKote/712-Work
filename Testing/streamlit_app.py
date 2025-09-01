import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Data Analysis Dashboard",
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
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Title and header
st.markdown('<h1 class="main-header">📊 Data Analysis Dashboard</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["🏠 Home", "📈 College Student Analysis", "🛍️ Retail Sales Analysis", "🏙️ Istanbul Sales Analysis", "📊 Data Explorer", "📋 About"]
)

# Load data functions
@st.cache_data
def load_college_data():
    try:
        df = pd.read_csv("College Student Analysis.csv")
        return df
    except Exception as e:
        st.error(f"Error loading college data: {e}")
        return None

@st.cache_data
def load_retail_data():
    try:
        df = pd.read_csv("retail_sales_dataset.csv")
        return df
    except Exception as e:
        st.error(f"Error loading retail data: {e}")
        return None

@st.cache_data
def load_istanbul_data():
    try:
        df = pd.read_csv("istanbul_sales_data.csv")
        return df
    except Exception as e:
        st.error(f"Error loading Istanbul data: {e}")
        return None

# Home page
if page == "🏠 Home":
    st.markdown("## Welcome to the Data Analysis Dashboard!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📚 College Students</h3>
            <p>Analyze student performance, demographics, and academic trends</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🛍️ Retail Sales</h3>
            <p>Explore sales patterns, product performance, and market trends</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🏙️ Istanbul Sales</h3>
            <p>Discover regional sales insights and business performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats
    st.subheader("📊 Quick Statistics")
    
    college_df = load_college_data()
    retail_df = load_retail_data()
    istanbul_df = load_istanbul_data()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if college_df is not None:
            st.metric("College Students", f"{len(college_df):,}")
        else:
            st.metric("College Students", "N/A")
    
    with col2:
        if retail_df is not None:
            st.metric("Retail Records", f"{len(retail_df):,}")
        else:
            st.metric("Retail Records", "N/A")
    
    with col3:
        if istanbul_df is not None:
            st.metric("Istanbul Records", f"{len(istanbul_df):,}")
        else:
            st.metric("Istanbul Records", "N/A")
    
    with col4:
        total_records = sum([
            len(college_df) if college_df is not None else 0,
            len(retail_df) if retail_df is not None else 0,
            len(istanbul_df) if istanbul_df is not None else 0
        ])
        st.metric("Total Records", f"{total_records:,}")

# College Student Analysis page
elif page == "📈 College Student Analysis":
    st.header("📈 College Student Analysis")
    
    college_df = load_college_data()
    
    if college_df is not None:
        st.success(f"✅ Loaded {len(college_df)} records with {len(college_df.columns)} columns")
        
        # Data overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Data Overview")
            st.dataframe(college_df.head(10))
        
        with col2:
            st.subheader("📊 Data Info")
            buffer = io.StringIO()
            college_df.info(buf=buffer)
            st.text(buffer.getvalue())
        
        # Basic statistics
        st.subheader("📈 Statistical Summary")
        st.dataframe(college_df.describe())
        
        # Interactive visualizations
        st.subheader("📊 Interactive Visualizations")
        
        # Column selection for analysis
        numeric_cols = college_df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = college_df.select_dtypes(include=['object']).columns.tolist()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if numeric_cols:
                selected_numeric = st.selectbox("Select numeric column for histogram:", numeric_cols)
                fig = px.histogram(college_df, x=selected_numeric, title=f"Distribution of {selected_numeric}")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if categorical_cols:
                selected_categorical = st.selectbox("Select categorical column for bar chart:", categorical_cols)
                value_counts = college_df[selected_categorical].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, 
                           title=f"Top 10 values in {selected_categorical}")
                st.plotly_chart(fig, use_container_width=True)
        
        # Correlation matrix for numeric columns
        if len(numeric_cols) > 1:
            st.subheader("🔗 Correlation Matrix")
            correlation_matrix = college_df[numeric_cols].corr()
            fig = px.imshow(correlation_matrix, 
                          title="Correlation Matrix",
                          color_continuous_scale='RdBu',
                          aspect="auto")
            st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot
        if len(numeric_cols) >= 2:
            st.subheader("📈 Scatter Plot")
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("Select X-axis:", numeric_cols, index=0)
            with col2:
                y_col = st.selectbox("Select Y-axis:", numeric_cols, index=1)
            
            fig = px.scatter(college_df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("❌ Could not load college student data")

# Retail Sales Analysis page
elif page == "🛍️ Retail Sales Analysis":
    st.header("🛍️ Retail Sales Analysis")
    
    retail_df = load_retail_data()
    
    if retail_df is not None:
        st.success(f"✅ Loaded {len(retail_df)} records with {len(retail_df.columns)} columns")
        
        # Data overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Data Overview")
            st.dataframe(retail_df.head(10))
        
        with col2:
            st.subheader("📊 Data Info")
            buffer = io.StringIO()
            retail_df.info(buf=buffer)
            st.text(buffer.getvalue())
        
        # Sales analysis
        st.subheader("💰 Sales Analysis")
        
        # Convert date columns if they exist
        date_columns = [col for col in retail_df.columns if 'date' in col.lower() or 'time' in col.lower()]
        
        if date_columns:
            selected_date_col = st.selectbox("Select date column:", date_columns)
            try:
                retail_df[selected_date_col] = pd.to_datetime(retail_df[selected_date_col])
                retail_df['Year'] = retail_df[selected_date_col].dt.year
                retail_df['Month'] = retail_df[selected_date_col].dt.month
                retail_df['Day'] = retail_df[selected_date_col].dt.day
                
                # Time series analysis
                st.subheader("📅 Time Series Analysis")
                
                # Sales over time
                if 'sales' in retail_df.columns.str.lower() or 'amount' in retail_df.columns.str.lower():
                    sales_col = [col for col in retail_df.columns if 'sales' in col.lower() or 'amount' in col.lower()][0]
                    
                    monthly_sales = retail_df.groupby(['Year', 'Month'])[sales_col].sum().reset_index()
                    monthly_sales['Date'] = pd.to_datetime(monthly_sales[['Year', 'Month']].assign(day=1))
                    
                    fig = px.line(monthly_sales, x='Date', y=sales_col, title="Monthly Sales Trend")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Yearly comparison
                yearly_sales = retail_df.groupby('Year')[sales_col].sum().reset_index()
                fig = px.bar(yearly_sales, x='Year', y=sales_col, title="Yearly Sales Comparison")
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.warning(f"Could not process date column: {e}")
        
        # Product analysis
        product_cols = [col for col in retail_df.columns if 'product' in col.lower() or 'item' in col.lower()]
        if product_cols:
            st.subheader("📦 Product Analysis")
            selected_product_col = st.selectbox("Select product column:", product_cols)
            
            product_sales = retail_df.groupby(selected_product_col).size().sort_values(ascending=False).head(10)
            fig = px.bar(x=product_sales.index, y=product_sales.values, title="Top 10 Products by Sales Count")
            st.plotly_chart(fig, use_container_width=True)
        
        # Statistical summary
        st.subheader("📊 Statistical Summary")
        st.dataframe(retail_df.describe())
    
    else:
        st.error("❌ Could not load retail sales data")

# Istanbul Sales Analysis page
elif page == "🏙️ Istanbul Sales Analysis":
    st.header("🏙️ Istanbul Sales Analysis")
    
    istanbul_df = load_istanbul_data()
    
    if istanbul_df is not None:
        st.success(f"✅ Loaded {len(istanbul_df)} records with {len(istanbul_df.columns)} columns")
        
        # Data cleaning and preprocessing
        st.subheader("🔧 Data Preprocessing")
        
        # Clean the data
        df_clean = istanbul_df.copy()
        df_clean = df_clean.dropna()
        
        # Convert date column if it exists
        date_columns = [col for col in df_clean.columns if 'date' in col.lower()]
        if date_columns:
            try:
                df_clean['invoice_date'] = pd.to_datetime(df_clean[date_columns[0]])
                df_clean['month'] = df_clean['invoice_date'].dt.month
                df_clean['year'] = df_clean['invoice_date'].dt.year
                df_clean['day_of_week'] = df_clean['invoice_date'].dt.day_name()
                df_clean['quarter'] = df_clean['invoice_date'].dt.quarter
                st.success("✅ Date columns processed successfully")
            except Exception as e:
                st.warning(f"Could not process date column: {e}")
        
        # Calculate total amount if quantity and price exist
        quantity_cols = [col for col in df_clean.columns if 'quantity' in col.lower()]
        price_cols = [col for col in df_clean.columns if 'price' in col.lower()]
        
        if quantity_cols and price_cols:
            df_clean['total_amount'] = df_clean[quantity_cols[0]] * df_clean[price_cols[0]]
            st.success("✅ Total amount calculated")
        
        # Data overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📋 Data Overview")
            st.dataframe(df_clean.head(10))
        
        with col2:
            st.subheader("📊 Data Info")
            buffer = io.StringIO()
            df_clean.info(buf=buffer)
            st.text(buffer.getvalue())
        
        # Key Metrics Dashboard
        st.subheader("📊 Key Performance Metrics")
        
        if 'total_amount' in df_clean.columns:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_revenue = df_clean['total_amount'].sum()
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            
            with col2:
                avg_transaction = df_clean['total_amount'].mean()
                st.metric("Avg Transaction", f"${avg_transaction:.2f}")
            
            with col3:
                total_transactions = len(df_clean)
                st.metric("Total Transactions", f"{total_transactions:,}")
            
            with col4:
                unique_customers = df_clean['customer_id'].nunique() if 'customer_id' in df_clean.columns else "N/A"
                st.metric("Unique Customers", f"{unique_customers:,}" if isinstance(unique_customers, int) else unique_customers)
        
        # Category Analysis
        if 'category' in df_clean.columns:
            st.subheader("📦 Category Performance Analysis")
            
            category_sales = df_clean.groupby('category')['total_amount'].sum().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top categories by revenue
                fig = px.bar(
                    x=category_sales.head(10).values,
                    y=category_sales.head(10).index,
                    orientation='h',
                    title="Top 10 Categories by Revenue",
                    labels={'x': 'Total Revenue ($)', 'y': 'Category'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Category statistics
                category_stats = df_clean.groupby('category').agg({
                    'total_amount': ['sum', 'mean', 'count'],
                    'quantity': ['sum', 'mean'] if 'quantity' in df_clean.columns else 'count'
                }).round(2)
                
                # Flatten column names
                category_stats.columns = ['_'.join(col).strip() for col in category_stats.columns]
                st.dataframe(category_stats.head(10))
        
        # Shopping Mall Analysis
        if 'shopping_mall' in df_clean.columns:
            st.subheader("🏬 Shopping Mall Performance")
            
            mall_sales = df_clean.groupby('shopping_mall')['total_amount'].sum().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    x=mall_sales.values,
                    y=mall_sales.index,
                    orientation='h',
                    title="Revenue by Shopping Mall",
                    labels={'x': 'Total Revenue ($)', 'y': 'Shopping Mall'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                mall_stats = df_clean.groupby('shopping_mall').agg({
                    'total_amount': ['sum', 'mean', 'count'],
                    'customer_id': 'nunique' if 'customer_id' in df_clean.columns else 'count'
                }).round(2)
                
                mall_stats.columns = ['_'.join(col).strip() for col in mall_stats.columns]
                st.dataframe(mall_stats)
        
        # Payment Method Analysis
        if 'payment_method' in df_clean.columns:
            st.subheader("💳 Payment Method Analysis")
            
            payment_analysis = df_clean.groupby('payment_method').agg({
                'total_amount': ['sum', 'mean', 'count'],
                'quantity': ['sum', 'mean'] if 'quantity' in df_clean.columns else 'count'
            }).round(2)
            
            payment_analysis.columns = ['_'.join(col).strip() for col in payment_analysis.columns]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Payment method distribution
                payment_counts = df_clean['payment_method'].value_counts()
                fig = px.pie(
                    values=payment_counts.values,
                    names=payment_counts.index,
                    title="Payment Method Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.dataframe(payment_analysis)
        
        # Temporal Analysis
        if 'month' in df_clean.columns and 'year' in df_clean.columns:
            st.subheader("📅 Temporal Patterns Analysis")
            
            # Monthly trends
            monthly_sales = df_clean.groupby(['year', 'month'])['total_amount'].sum().reset_index()
            monthly_sales['date'] = pd.to_datetime(monthly_sales[['year', 'month']].assign(day=1))
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(
                    monthly_sales,
                    x='date',
                    y='total_amount',
                    title="Monthly Sales Trend",
                    labels={'total_amount': 'Total Revenue ($)', 'date': 'Month'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Day of week analysis
                if 'day_of_week' in df_clean.columns:
                    dow_sales = df_clean.groupby('day_of_week')['total_amount'].sum()
                    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    dow_sales = dow_sales.reindex(dow_order)
                    
                    fig = px.bar(
                        x=dow_sales.index,
                        y=dow_sales.values,
                        title="Sales by Day of Week",
                        labels={'x': 'Day of Week', 'y': 'Total Revenue ($)'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Customer Demographics
        if 'age' in df_clean.columns:
            st.subheader("👥 Customer Demographics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Age distribution
                fig = px.histogram(
                    df_clean,
                    x='age',
                    nbins=20,
                    title="Customer Age Distribution",
                    labels={'age': 'Age', 'count': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Age group analysis
                df_clean['age_group'] = pd.cut(
                    df_clean['age'],
                    bins=[0, 25, 35, 45, 55, 100],
                    labels=['18-25', '26-35', '36-45', '46-55', '55+']
                )
                
                age_group_sales = df_clean.groupby('age_group')['total_amount'].sum()
                fig = px.bar(
                    x=age_group_sales.index,
                    y=age_group_sales.values,
                    title="Revenue by Age Group",
                    labels={'x': 'Age Group', 'y': 'Total Revenue ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Gender Analysis
        if 'gender' in df_clean.columns:
            st.subheader("👫 Gender-based Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gender distribution
                gender_counts = df_clean['gender'].value_counts()
                fig = px.pie(
                    values=gender_counts.values,
                    names=gender_counts.index,
                    title="Gender Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Gender vs transaction value
                gender_avg = df_clean.groupby('gender')['total_amount'].mean()
                fig = px.bar(
                    x=gender_avg.index,
                    y=gender_avg.values,
                    title="Average Transaction Value by Gender",
                    labels={'x': 'Gender', 'y': 'Average Transaction Value ($)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Correlation Analysis
        st.subheader("🔗 Correlation Analysis")
        
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_columns) > 1:
            correlation_matrix = df_clean[numeric_columns].corr()
            
            fig = px.imshow(
                correlation_matrix,
                title="Correlation Matrix",
                color_continuous_scale='RdBu',
                aspect="auto",
                labels=dict(x="Variables", y="Variables", color="Correlation")
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Price vs Quantity Analysis
        if 'price' in df_clean.columns and 'quantity' in df_clean.columns:
            st.subheader("💰 Price vs Quantity Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot
                fig = px.scatter(
                    df_clean,
                    x='price',
                    y='quantity',
                    title="Price vs Quantity Relationship",
                    labels={'price': 'Price ($)', 'quantity': 'Quantity'},
                    opacity=0.6
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Price distribution by category
                if 'category' in df_clean.columns:
                    category_price = df_clean.groupby('category')['price'].mean().sort_values(ascending=False)
                    fig = px.bar(
                        x=category_price.values,
                        y=category_price.index,
                        orientation='h',
                        title="Average Price by Category",
                        labels={'x': 'Average Price ($)', 'y': 'Category'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Statistical Summary
        st.subheader("📊 Comprehensive Statistical Summary")
        st.dataframe(df_clean.describe())
        
        # Download processed data
        st.subheader("💾 Download Processed Data")
        
        csv = df_clean.to_csv(index=False)
        st.download_button(
            label="📥 Download Processed Data as CSV",
            data=csv,
            file_name="istanbul_sales_processed.csv",
            mime="text/csv"
        )
        
        # Export visualizations
        st.subheader("📊 Export Visualizations")
        
        # Create a comprehensive visualization
        if 'total_amount' in df_clean.columns and 'category' in df_clean.columns:
            # Create subplot with multiple charts
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Top Categories by Revenue', 'Revenue by Shopping Mall', 
                              'Monthly Sales Trend', 'Payment Method Distribution'),
                specs=[[{"type": "bar"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "pie"}]]
            )
            
            # Top categories
            top_categories = df_clean.groupby('category')['total_amount'].sum().sort_values(ascending=False).head(8)
            fig.add_trace(
                go.Bar(x=top_categories.values, y=top_categories.index, orientation='h', name="Categories"),
                row=1, col=1
            )
            
            # Top malls
            if 'shopping_mall' in df_clean.columns:
                top_malls = df_clean.groupby('shopping_mall')['total_amount'].sum().sort_values(ascending=False).head(8)
                fig.add_trace(
                    go.Bar(x=top_malls.values, y=top_malls.index, orientation='h', name="Malls"),
                    row=1, col=2
                )
            
            # Monthly trend
            if 'month' in df_clean.columns and 'year' in df_clean.columns:
                monthly_trend = df_clean.groupby(['year', 'month'])['total_amount'].sum().reset_index()
                monthly_trend['date'] = pd.to_datetime(monthly_trend[['year', 'month']].assign(day=1))
                fig.add_trace(
                    go.Scatter(x=monthly_trend['date'], y=monthly_trend['total_amount'], mode='lines+markers', name="Monthly Trend"),
                    row=2, col=1
                )
            
            # Payment methods
            if 'payment_method' in df_clean.columns:
                payment_counts = df_clean['payment_method'].value_counts()
                fig.add_trace(
                    go.Pie(labels=payment_counts.index, values=payment_counts.values, name="Payment Methods"),
                    row=2, col=2
                )
            
            fig.update_layout(height=800, title_text="Istanbul Sales Analysis Dashboard")
            st.plotly_chart(fig, use_container_width=True)
            
            # Download visualization
            img_bytes = fig.to_image(format="png")
            st.download_button(
                label="📥 Download Dashboard as PNG",
                data=img_bytes,
                file_name="istanbul_sales_dashboard.png",
                mime="image/png"
            )
    
    else:
        st.error("❌ Could not load Istanbul sales data")

# Data Explorer page
elif page == "📊 Data Explorer":
    st.header("📊 Interactive Data Explorer")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file to explore:", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Successfully loaded {len(df)} rows and {len(df.columns)} columns")
            
            # Data overview
            st.subheader("📋 Data Overview")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("First 10 rows:")
                st.dataframe(df.head(10))
            
            with col2:
                st.write("Data types:")
                st.dataframe(df.dtypes.to_frame('Data Type'))
            
            # Column analysis
            st.subheader("📊 Column Analysis")
            selected_column = st.selectbox("Select a column to analyze:", df.columns)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Column: {selected_column}**")
                st.write(f"Data type: {df[selected_column].dtype}")
                st.write(f"Missing values: {df[selected_column].isnull().sum()}")
                st.write(f"Unique values: {df[selected_column].nunique()}")
            
            with col2:
                if df[selected_column].dtype in ['int64', 'float64']:
                    st.write("**Numeric Statistics:**")
                    st.write(df[selected_column].describe())
                else:
                    st.write("**Categorical Statistics:**")
                    st.write(df[selected_column].value_counts().head(10))
            
            # Visualization
            st.subheader("📈 Visualization")
            
            if df[selected_column].dtype in ['int64', 'float64']:
                fig = px.histogram(df, x=selected_column, title=f"Distribution of {selected_column}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                value_counts = df[selected_column].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values, title=f"Top 10 values in {selected_column}")
                st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    else:
        st.info("👆 Upload a CSV file to start exploring!")

# About page
elif page == "📋 About":
    st.header("📋 About This Dashboard")
    
    st.markdown("""
    ## 🎯 Purpose
    This interactive data analysis dashboard provides comprehensive insights into various datasets including:
    
    - **College Student Analysis**: Academic performance and demographic analysis
    - **Retail Sales Analysis**: Sales patterns and product performance
    - **Istanbul Sales Analysis**: Regional business insights
    
    ## 🛠️ Features
    - **Interactive Visualizations**: Dynamic charts and graphs using Plotly
    - **Data Exploration**: Comprehensive data analysis tools
    - **Real-time Filtering**: Customizable data views
    - **Statistical Analysis**: Descriptive statistics and correlations
    - **File Upload**: Upload and analyze your own CSV files
    
    ## 📊 Technologies Used
    - **Streamlit**: Web application framework
    - **Pandas**: Data manipulation and analysis
    - **Plotly**: Interactive visualizations
    - **NumPy**: Numerical computing
    - **Seaborn**: Statistical data visualization
    
    ## 🚀 Getting Started
    1. Navigate through the sidebar to explore different datasets
    2. Use the interactive controls to customize your analysis
    3. Upload your own CSV files in the Data Explorer section
    4. Export visualizations and insights as needed
    
    ## 📈 Data Sources
    - College Student Analysis: Academic performance dataset
    - Retail Sales Dataset: Sales and product data
    - Istanbul Sales Data: Regional business performance
    
    ---
    
    **Created with ❤️ using Streamlit**
    """)
    
    # Footer
    st.markdown("---")
    st.markdown("*Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "*")

# Footer for all pages
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>📊 Data Analysis Dashboard | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
