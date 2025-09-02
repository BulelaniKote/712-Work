# 🔗 BigQuery Integration Setup Guide

## Overview
Your Streamlit dashboard has been enhanced with BigQuery integration, allowing you to:
- Store data in Google Cloud BigQuery
- Run complex analytical queries
- Scale your data analysis to millions of records
- Access data from anywhere with proper authentication

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd gdp-dashboard
pip install -r requirements.txt
```

### 2. Test BigQuery Connection
```bash
python test_bigquery.py
```

### 3. Run Your Streamlit App
```bash
streamlit run streamlit_app.py
```

## 📊 What's New

### **New Navigation Page: 🔗 BigQuery**
- **BigQuery Status**: Shows connection status in sidebar
- **Table Management**: Create BigQuery tables automatically
- **Data Upload**: Upload CSV files to BigQuery
- **Query Execution**: Run basic and advanced analysis queries
- **Results Export**: Download query results as CSV

### **Enhanced Data Loading**
- All analysis pages now read from BigQuery first
- Fallback to sample data if BigQuery is unavailable
- Automatic data caching for performance

## 🏗️ BigQuery Setup

### **Automatic Setup**
1. Navigate to **🔗 BigQuery** page
2. Click **🏗️ Create Tables** button
3. Tables will be created automatically with proper schemas

### **Manual Setup (if needed)**
```sql
-- Create dataset
CREATE DATASET `moonlit-autumn-468306-p6.sales_analysis`;

-- Create tables (if automatic creation fails)
CREATE TABLE `moonlit-autumn-468306-p6.sales_analysis.istanbul_sales` (
    invoice_id STRING NOT NULL,
    invoice_date DATE NOT NULL,
    customer_id STRING NOT NULL,
    customer_age INT64,
    customer_gender STRING,
    product_category STRING,
    product_name STRING,
    quantity INT64,
    unit_price FLOAT64,
    total_amount FLOAT64,
    payment_method STRING,
    shopping_mall STRING,
    city STRING,
    created_at TIMESTAMP NOT NULL
);
```

## 📤 Data Upload Process

### **Step 1: Prepare Your Data**
- Ensure CSV files are in the correct locations:
  - `data/istanbul_sales_data.csv`
  - `data/College Student Analysis.csv`
  - `retail_sales_analysis/retail_sales_dataset.csv`

### **Step 2: Upload to BigQuery**
1. Go to **🔗 BigQuery** page
2. Select data type from dropdown
3. Click upload button
4. Monitor progress with spinner

### **Step 3: Verify Upload**
- Check BigQuery console
- Run test queries
- View data in Streamlit dashboard

## 🔍 Available Queries

### **Basic Analysis Queries**
- **Total Revenue**: Overall sales performance
- **Revenue by Category**: Product category analysis
- **Revenue by Mall**: Location performance
- **Monthly Trends**: Time series analysis
- **Customer Demographics**: Age and gender insights
- **Payment Methods**: Transaction method analysis

### **Advanced Analysis Queries**
- **Customer Segmentation**: High/Medium/Low value customers
- **Seasonal Analysis**: Monthly and weekly patterns
- **Product Correlation**: Category relationships
- **Performance Ranking**: Mall and store rankings

## 📈 Query Examples

### **Revenue Analysis**
```sql
SELECT 
    product_category,
    SUM(total_amount) as total_revenue,
    COUNT(*) as transaction_count,
    AVG(total_amount) as avg_transaction_value
FROM `moonlit-autumn-468306-p6.sales_analysis.istanbul_sales`
WHERE product_category IS NOT NULL
GROUP BY product_category
ORDER BY total_revenue DESC
LIMIT 10;
```

### **Customer Segmentation**
```sql
WITH customer_metrics AS (
    SELECT 
        customer_id,
        COUNT(*) as transaction_count,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_transaction_value
    FROM `moonlit-autumn-468306-p6.sales_analysis.istanbul_sales`
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN total_spent >= 1000 THEN 'High Value'
        WHEN total_spent >= 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_total_spent
FROM customer_metrics
GROUP BY customer_segment
ORDER BY avg_total_spent DESC;
```

## 🔧 Troubleshooting

### **Connection Issues**
- Verify `istanbul_sales_analysis/API.JSON` exists
- Check service account permissions
- Ensure project ID is correct
- Verify billing is enabled

### **Table Creation Errors**
- Check dataset permissions
- Verify schema definitions
- Ensure no naming conflicts
- Check BigQuery quotas

### **Query Errors**
- Verify table names and columns
- Check data types match
- Ensure proper SQL syntax
- Monitor query quotas

## 📱 Streamlit Interface

### **Sidebar Features**
- **BigQuery Status**: Connection indicator
- **Table Operations**: Create tables
- **Data Upload**: Select and upload datasets
- **Query Execution**: Run analysis queries
- **Results Export**: Download CSV files

### **Main Page Features**
- **Connection Status**: Shows project details
- **Table Management**: Create and manage tables
- **Data Upload**: Upload CSV files to BigQuery
- **Query Results**: Display and visualize results
- **Export Options**: Download results

## 🎯 Best Practices

### **Performance**
- Use LIMIT clauses for large datasets
- Cache frequently accessed data
- Optimize query structure
- Monitor query costs

### **Security**
- Keep API credentials secure
- Use service account with minimal permissions
- Regularly rotate credentials
- Monitor access logs

### **Data Management**
- Regular data backups
- Version control for schemas
- Data quality checks
- Performance monitoring

## 🚀 Next Steps

### **Immediate Actions**
1. Test BigQuery connection
2. Create tables
3. Upload your data
4. Run sample queries

### **Advanced Features**
- Custom query builder
- Automated data pipelines
- Real-time data streaming
- Machine learning integration

### **Scaling Up**
- Partition tables by date
- Use clustering for performance
- Implement data lifecycle management
- Set up automated backups

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify your credentials
3. Test with the provided test script
4. Check BigQuery console for errors

## 🎉 Success Indicators

- ✅ BigQuery status shows green in sidebar
- ✅ Tables created successfully
- ✅ Data uploaded without errors
- ✅ Queries execute and return results
- ✅ Results display in dashboard
- ✅ Export functionality works

---

**Your Streamlit dashboard is now powered by BigQuery! 🚀**
