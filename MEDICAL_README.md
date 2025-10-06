# 🏥 Medical Facility Analysis Dashboard

A comprehensive medical facility analytics dashboard built with Streamlit, featuring a star schema architecture and synthetic medical data generated using the Faker library.

## 🎯 Overview

This dashboard demonstrates advanced healthcare analytics using a star schema data model. It provides insights into patient demographics, doctor performance, department efficiency, treatment effectiveness, and financial metrics for a medical facility.

## 🏗️ Star Schema Architecture

The application implements a complete star schema with:

### Dimension Tables
- **Patients** (1,000 records): Demographics, insurance, medical history
- **Doctors** (100 records): Specialties, experience, departments
- **Departments** (8 records): Hospital departments and capacities
- **Treatments** (200 records): Medical procedures and costs
- **Dates** (5 years): Time dimension with calendar attributes

### Fact Table
- **Medical Visits** (5,000 records): Central fact table connecting all dimensions with key metrics

## 🚀 Features

### 📊 Analytics Dashboards
- **Patient Analytics**: Demographics, visit patterns, satisfaction analysis
- **Doctor Performance**: Productivity, specialization, patient outcomes
- **Department Analysis**: Utilization rates, efficiency metrics
- **Treatment Insights**: Effectiveness, costs, complication rates
- **Financial Analysis**: Revenue, insurance coverage, cost optimization

### 🎨 Interactive Visualizations
- Patient demographic distributions
- Doctor performance scatter plots
- Department utilization charts
- Treatment effectiveness analysis
- Financial trend analysis
- Time-series visualizations

### 📈 Key Metrics
- Patient satisfaction scores
- Readmission rates
- Department utilization
- Treatment costs and outcomes
- Insurance coverage analysis
- Revenue optimization insights

## 🛠️ Installation

1. **Clone or download the files:**
   ```bash
   # Download medical_streamlit_app.py and medical_requirements.txt
   ```

2. **Install dependencies:**
   ```bash
   pip install -r medical_requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run medical_streamlit_app.py
   ```

4. **Access the dashboard:**
   - Open your browser to `http://localhost:8501`

## 📋 Requirements

- Python 3.8+
- Streamlit 1.28.0+
- Pandas 2.0.0+
- Plotly 5.15.0+
- Faker 19.0.0+
- NumPy 1.24.0+
- Altair 5.0.0+

## 🎮 Usage

### Navigation
Use the sidebar to navigate between different analysis pages:

1. **🏠 Home**: Overview and key metrics
2. **📊 Star Schema Overview**: Data architecture and table details
3. **👥 Patient Analytics**: Patient demographics and visit patterns
4. **👨‍⚕️ Doctor Performance**: Doctor productivity and outcomes
5. **🏥 Department Analysis**: Department efficiency and utilization
6. **💊 Treatment Insights**: Treatment effectiveness and safety
7. **📈 Financial Analysis**: Revenue and cost analysis
8. **📋 About**: Technical documentation

### Data Generation
- All data is synthetically generated using the Faker library
- Data is cached for performance (regenerated on app restart)
- Realistic medical scenarios and relationships
- HIPAA-compliant synthetic data (no real patient information)

## 📊 Sample Insights

The dashboard provides insights such as:
- Patient satisfaction trends by age group and gender
- Doctor performance correlation with experience and specialty
- Department utilization rates and efficiency metrics
- Treatment cost analysis and insurance coverage patterns
- Seasonal trends in medical visits and procedures

## 🔧 Customization

### Adding New Metrics
Modify the `create_star_schema_data()` function to add new fields or calculations.

### Changing Data Volume
Adjust the range parameters in the data generation loops:
- Patients: Currently 1,000 (line ~50)
- Doctors: Currently 100 (line ~75)
- Visits: Currently 5,000 (line ~150)

### Custom Visualizations
Add new charts in the respective page sections using Plotly or Altair.

## 🏥 Healthcare Metrics Explained

### Quality Indicators
- **Patient Satisfaction**: 1-10 scale rating system
- **Readmission Rate**: 30-day readmission tracking
- **Complication Rate**: Treatment-related complications
- **Length of Stay**: Average hours per visit/admission

### Operational Metrics
- **Utilization Rate**: Department capacity usage
- **Doctor Productivity**: Visits per doctor per period
- **Treatment Frequency**: Most common procedures
- **Resource Allocation**: Equipment and staff efficiency

### Financial Metrics
- **Revenue per Visit**: Average treatment costs
- **Insurance Coverage**: Reimbursement rates by provider
- **Cost per Treatment**: Procedure-specific costs
- **Profitability**: Department and treatment profitability

## 🔒 Data Privacy

- All data is synthetically generated using Faker
- No real patient information is used or stored
- HIPAA-compliant synthetic data generation
- Data is generated fresh on each application start

## 🚀 Deployment

### Local Development
```bash
streamlit run medical_streamlit_app.py
```

### Streamlit Cloud
1. Upload files to GitHub repository
2. Connect to Streamlit Cloud
3. Deploy with medical_requirements.txt

### Docker Deployment
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r medical_requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "medical_streamlit_app.py"]
```

## 📈 Performance Optimization

- Data caching with `@st.cache_data`
- Efficient pandas operations
- Optimized visualization rendering
- Lazy loading of large datasets

## 🤝 Contributing

To extend the dashboard:
1. Add new dimension tables in `create_star_schema_data()`
2. Create new analysis pages following existing patterns
3. Add corresponding navigation options
4. Update requirements if new dependencies are added

## 📝 Assignment Context

This dashboard was created for a database systems assignment focusing on:
- Star schema design and implementation
- Synthetic data generation techniques
- Healthcare analytics and visualization
- Business intelligence dashboard development

## 🏆 Key Learning Outcomes

- Understanding of star schema architecture
- Proficiency with Faker for realistic data generation
- Healthcare analytics and KPI development
- Interactive dashboard creation with Streamlit
- Data visualization best practices

---

**🏥 Medical Facility Analysis Dashboard | Assignment 2 | Star Schema & Faker Implementation**
