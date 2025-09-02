#!/usr/bin/env python3
"""
Comprehensive Table Analysis Script
Analyzes a BigQuery table and creates views for different analysis perspectives
"""

import os
import sys
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime

class TableAnalyzer:
    def __init__(self, credentials_path="istanbul_sales_analysis/API.JSON"):
        """Initialize BigQuery connection and table analyzer"""
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
            print(f"✅ Connected to BigQuery project: {self.project_id}")
            
        except Exception as e:
            print(f"❌ Error connecting to BigQuery: {e}")
            self.client = None
    
    def analyze_table_structure(self, dataset_id, table_id):
        """Analyze the structure of the specified table"""
        try:
            table_ref = f"{self.project_id}.{dataset_id}.{table_id}"
            
            # Get table schema
            table = self.client.get_table(table_ref)
            
            print(f"\n📊 Table Analysis: {table_ref}")
            print("=" * 60)
            
            # Basic table info
            print(f"Table ID: {table.table_id}")
            print(f"Dataset ID: {table.dataset_id}")
            print(f"Project ID: {table.project}")
            print(f"Created: {table.created}")
            print(f"Modified: {table.modified}")
            print(f"Row Count: {table.num_rows:,}")
            print(f"Size: {table.num_bytes / (1024*1024):.2f} MB")
            
            # Schema analysis
            print(f"\n📋 Schema Analysis:")
            print("-" * 40)
            
            column_info = []
            for field in table.schema:
                column_info.append({
                    'name': field.name,
                    'type': field.field_type,
                    'mode': field.mode,
                    'description': field.description or 'No description'
                })
                print(f"  {field.name}: {field.field_type} ({field.mode})")
            
            return column_info, table.num_rows
            
        except Exception as e:
            print(f"❌ Error analyzing table: {e}")
            return None, None
    
    def generate_analysis_queries(self, dataset_id, table_id, column_info):
        """Generate comprehensive analysis queries with logic explanations"""
        
        print(f"\n🔍 Analysis Queries with Logic")
        print("=" * 60)
        
        queries = {}
        
        # 1. Basic Descriptive Statistics
        print("\n1️⃣ BASIC DESCRIPTIVE STATISTICS")
        print("-" * 40)
        print("Logic: Understand the fundamental characteristics of the data")
        print("Purpose: Get overview of data distribution, identify outliers, understand data quality")
        
        numeric_columns = [col['name'] for col in column_info if col['type'] in ['INT64', 'FLOAT64', 'NUMERIC']]
        categorical_columns = [col['name'] for col in column_info if col['type'] in ['STRING', 'BOOL']]
        date_columns = [col['name'] for col in column_info if col['type'] in ['DATE', 'DATETIME', 'TIMESTAMP']]
        
        if numeric_columns:
            print(f"📊 Numeric columns found: {numeric_columns}")
            queries['basic_stats'] = f"""
-- Basic Descriptive Statistics for Numeric Columns
-- Logic: Calculate mean, median, standard deviation, min, max for all numeric columns
-- Purpose: Understand data distribution and identify potential outliers
SELECT 
    'Overall Statistics' as analysis_type,
    COUNT(*) as total_records,
    {', '.join([f'AVG({col}) as {col}_avg, STDDEV({col}) as {col}_stddev, MIN({col}) as {col}_min, MAX({col}) as {col}_max' for col in numeric_columns])}
FROM `{self.project_id}.{dataset_id}.{table_id}`
WHERE {' AND '.join([f'{col} IS NOT NULL' for col in numeric_columns])}
            """
        
        # 2. Data Quality Analysis
        print("\n2️⃣ DATA QUALITY ANALYSIS")
        print("-" * 40)
        print("Logic: Check for missing values, duplicates, and data consistency")
        print("Purpose: Ensure data reliability and identify areas needing data cleaning")
        
        queries['data_quality'] = f"""
-- Data Quality Analysis
-- Logic: Check for missing values, duplicates, and data consistency issues
-- Purpose: Identify data quality problems that could affect analysis accuracy
SELECT 
    'Data Quality Check' as analysis_type,
    COUNT(*) as total_records,
    {', '.join([f'COUNT({col}) as {col}_non_null, COUNT(*) - COUNT({col}) as {col}_missing' for col in [col['name'] for col in column_info]])},
    COUNT(*) - COUNT(DISTINCT *) as duplicate_records
FROM `{self.project_id}.{dataset_id}.{table_id}`
        """
        
        # 3. Categorical Analysis
        if categorical_columns:
            print(f"\n3️⃣ CATEGORICAL ANALYSIS")
            print("-" * 40)
            print("Logic: Analyze distribution of categorical variables")
            print("Purpose: Understand categories, identify dominant values, spot data entry issues")
            
            for col in categorical_columns[:3]:  # Limit to first 3 categorical columns
                queries[f'categorical_{col}'] = f"""
-- Categorical Analysis for {col}
-- Logic: Count frequency of each category and calculate percentages
-- Purpose: Understand category distribution and identify dominant categories
SELECT 
    {col},
    COUNT(*) as frequency,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM `{self.project_id}.{dataset_id}.{table_id}`
WHERE {col} IS NOT NULL
GROUP BY {col}
ORDER BY frequency DESC
LIMIT 20
                """
        
        # 4. Temporal Analysis (if date columns exist)
        if date_columns:
            print(f"\n4️⃣ TEMPORAL ANALYSIS")
            print("-" * 40)
            print("Logic: Analyze patterns over time")
            print("Purpose: Identify trends, seasonality, and temporal patterns")
            
            for col in date_columns[:2]:  # Limit to first 2 date columns
                queries[f'temporal_{col}'] = f"""
-- Temporal Analysis for {col}
-- Logic: Extract time components and analyze patterns
-- Purpose: Identify trends, seasonality, and time-based insights
SELECT 
    EXTRACT(YEAR FROM {col}) as year,
    EXTRACT(MONTH FROM {col}) as month,
    EXTRACT(DAYOFWEEK FROM {col}) as day_of_week,
    COUNT(*) as record_count,
    {', '.join([f'AVG({num_col}) as {num_col}_avg' for num_col in numeric_columns[:3]]) if numeric_columns else '1 as dummy'}
FROM `{self.project_id}.{dataset_id}.{table_id}`
WHERE {col} IS NOT NULL
GROUP BY year, month, day_of_week
ORDER BY year, month, day_of_week
                """
        
        # 5. Correlation Analysis
        if len(numeric_columns) > 1:
            print(f"\n5️⃣ CORRELATION ANALYSIS")
            print("-" * 40)
            print("Logic: Calculate correlations between numeric variables")
            print("Purpose: Identify relationships and dependencies between variables")
            
            queries['correlation'] = f"""
-- Correlation Analysis
-- Logic: Calculate Pearson correlation coefficients between all numeric variables
-- Purpose: Identify strong relationships and potential multicollinearity
SELECT 
    'Correlation Matrix' as analysis_type,
    {', '.join([f'CORR({col1}, {col2}) as {col1}_{col2}_corr' 
                for i, col1 in enumerate(numeric_columns) 
                for col2 in numeric_columns[i+1:]])}
FROM `{self.project_id}.{dataset_id}.{table_id}`
WHERE {' AND '.join([f'{col} IS NOT NULL' for col in numeric_columns])}
        """
        
        # 6. Outlier Detection
        if numeric_columns:
            print(f"\n6️⃣ OUTLIER DETECTION")
            print("-" * 40)
            print("Logic: Identify outliers using IQR method")
            print("Purpose: Find extreme values that could skew analysis")
            
            for col in numeric_columns[:3]:  # Limit to first 3 numeric columns
                queries[f'outliers_{col}'] = f"""
-- Outlier Detection for {col}
-- Logic: Use IQR method to identify outliers (values beyond Q1-1.5*IQR and Q3+1.5*IQR)
-- Purpose: Identify extreme values that could affect analysis
WITH stats AS (
    SELECT 
        PERCENTILE_CONT({col}, 0.25) OVER() as q1,
        PERCENTILE_CONT({col}, 0.75) OVER() as q3,
        PERCENTILE_CONT({col}, 0.5) OVER() as median
    FROM `{self.project_id}.{dataset_id}.{table_id}`
    WHERE {col} IS NOT NULL
    LIMIT 1
)
SELECT 
    'Outlier Analysis' as analysis_type,
    COUNT(*) as total_records,
    COUNT(CASE WHEN {col} < (q1 - 1.5 * (q3 - q1)) THEN 1 END) as lower_outliers,
    COUNT(CASE WHEN {col} > (q3 + 1.5 * (q3 - q1)) THEN 1 END) as upper_outliers,
    ROUND(COUNT(CASE WHEN {col} < (q1 - 1.5 * (q3 - q1)) OR {col} > (q3 + 1.5 * (q3 - q1)) THEN 1 END) * 100.0 / COUNT(*), 2) as outlier_percentage
FROM `{self.project_id}.{dataset_id}.{table_id}`, stats
WHERE {col} IS NOT NULL
                """
        
        # 7. Summary Dashboard
        print(f"\n7️⃣ SUMMARY DASHBOARD")
        print("-" * 40)
        print("Logic: Create a comprehensive summary of all key metrics")
        print("Purpose: Provide a single view of the most important insights")
        
        queries['summary_dashboard'] = f"""
-- Summary Dashboard
-- Logic: Combine key metrics from all analyses into a single comprehensive view
-- Purpose: Provide executives and stakeholders with a complete overview
SELECT 
    'Summary Dashboard' as analysis_type,
    COUNT(*) as total_records,
    {', '.join([f'AVG({col}) as {col}_average' for col in numeric_columns[:5]]) if numeric_columns else '1 as dummy'},
    {', '.join([f'COUNT(DISTINCT {col}) as {col}_unique_values' for col in categorical_columns[:3]]) if categorical_columns else '1 as dummy'},
    CURRENT_TIMESTAMP() as analysis_timestamp
FROM `{self.project_id}.{dataset_id}.{table_id}`
        """
        
        return queries
    
    def create_analysis_views(self, dataset_id, table_id, queries):
        """Create BigQuery views for each analysis query"""
        
        print(f"\n🏗️ Creating Analysis Views")
        print("=" * 60)
        
        created_views = []
        
        for view_name, query in queries.items():
            try:
                # Clean view name (BigQuery naming restrictions)
                clean_view_name = f"{table_id}_{view_name}_view"
                view_ref = f"{self.project_id}.{dataset_id}.{clean_view_name}"
                
                # Create view
                view = bigquery.Table(view_ref)
                view.view_query = query
                
                # Check if view exists
                try:
                    self.client.get_table(view_ref)
                    print(f"🔄 Updating existing view: {clean_view_name}")
                    self.client.delete_table(view_ref)
                except:
                    print(f"🆕 Creating new view: {clean_view_name}")
                
                # Create the view
                view = self.client.create_table(view, exists_ok=True)
                created_views.append(clean_view_name)
                print(f"✅ Created view: {clean_view_name}")
                
            except Exception as e:
                print(f"❌ Error creating view {view_name}: {e}")
        
        return created_views
    
    def run_sample_analysis(self, dataset_id, table_id):
        """Run a sample analysis to demonstrate the views"""
        
        print(f"\n🧪 Running Sample Analysis")
        print("=" * 60)
        
        try:
            # Get a sample of data
            sample_query = f"""
            SELECT * FROM `{self.project_id}.{dataset_id}.{table_id}`
            LIMIT 5
            """
            
            print("📋 Sample Data:")
            print("-" * 40)
            df = self.client.query(sample_query).to_dataframe()
            print(df.to_string(index=False))
            
            # Run basic stats
            if len(df.columns) > 0:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if numeric_cols:
                    print(f"\n📊 Numeric columns: {numeric_cols}")
                    print(f"📈 Data types: {df.dtypes.to_dict()}")
                    print(f"🔢 Shape: {df.shape}")
            
        except Exception as e:
            print(f"❌ Error running sample analysis: {e}")

def main():
    """Main function to run the table analysis"""
    
    print("🔍 BigQuery Table Analysis Tool")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = TableAnalyzer()
    
    if analyzer.client is None:
        print("❌ Failed to initialize BigQuery client")
        return
    
    # Get table details from user
    print("\n📝 Please provide your table details:")
    dataset_id = input("Dataset ID (e.g., 'sales_analysis'): ").strip()
    table_id = input("Table ID (e.g., 'retail_sales'): ").strip()
    
    if not dataset_id or not table_id:
        print("❌ Dataset ID and Table ID are required")
        return
    
    try:
        # Analyze table structure
        column_info, row_count = analyzer.analyze_table_structure(dataset_id, table_id)
        
        if column_info is None:
            print("❌ Could not analyze table structure")
            return
        
        # Generate analysis queries
        queries = analyzer.generate_analysis_queries(dataset_id, table_id, column_info)
        
        # Create views
        created_views = analyzer.create_analysis_views(dataset_id, table_id, queries)
        
        # Run sample analysis
        analyzer.run_sample_analysis(dataset_id, table_id)
        
        # Summary
        print(f"\n🎉 Analysis Complete!")
        print("=" * 50)
        print(f"✅ Analyzed table: {dataset_id}.{table_id}")
        print(f"✅ Created {len(created_views)} analysis views")
        print(f"✅ Total records: {row_count:,}")
        
        print(f"\n📊 Created Views:")
        for view in created_views:
            print(f"  - {view}")
        
        print(f"\n🔍 Next Steps:")
        print(f"  1. Check your BigQuery console for the new views")
        print(f"  2. Run queries against the views for insights")
        print(f"  3. Use the views in your Streamlit dashboard")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    main()
