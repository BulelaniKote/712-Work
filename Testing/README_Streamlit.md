# 📊 Data Analysis Dashboard - Streamlit Application

A comprehensive, interactive data analysis dashboard built with Streamlit that provides insights into multiple datasets including college student analysis, retail sales, and Istanbul sales data.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to the Testing directory:**
   ```bash
   cd "C:\Users\CONDORGREEN\src\712 Work\Testing"
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r streamlit_requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser:**
   The application will automatically open in your default browser at `http://localhost:8501`

## 📋 Features

### 🏠 Home Page
- Dashboard overview with quick statistics
- Summary of all available datasets
- Navigation to different analysis sections

### 📈 College Student Analysis
- Interactive data exploration
- Statistical summaries
- Dynamic visualizations (histograms, bar charts, correlation matrices)
- Scatter plot analysis
- Real-time column selection for analysis

### 🛍️ Retail Sales Analysis
- Sales trend analysis over time
- Product performance insights
- Time series visualizations
- Monthly and yearly sales comparisons
- Product ranking by sales volume

### 🏙️ Istanbul Sales Analysis
- Regional distribution analysis
- Sales performance by location
- Statistical summaries with box plots
- Geographic insights

### 📊 Data Explorer
- Upload and analyze your own CSV files
- Interactive column analysis
- Automatic data type detection
- Custom visualizations for any dataset

### 📋 About
- Comprehensive documentation
- Technology stack information
- Usage instructions

## 🛠️ Technical Details

### Dependencies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computing
- **Seaborn**: Statistical data visualization
- **Matplotlib**: Additional plotting capabilities
- **OpenPyXL**: Excel file support

### Data Sources
The application is designed to work with the following datasets:
- `College Student Analysis.csv` - Academic performance data
- `retail_sales_dataset.csv` - Sales and product data
- `istanbul_sales_data.csv` - Regional business data

## 🎯 Usage Instructions

1. **Navigation**: Use the sidebar to switch between different analysis pages
2. **Data Exploration**: Select columns and chart types to customize your analysis
3. **File Upload**: In the Data Explorer section, upload your own CSV files for analysis
4. **Interactive Features**: Hover over charts for detailed information, zoom, and pan
5. **Real-time Updates**: All visualizations update automatically when you change selections

## 🔧 Customization

### Adding New Datasets
1. Place your CSV file in the Testing directory
2. Add a new data loading function in `streamlit_app.py`
3. Create a new page section for your dataset
4. Add navigation options in the sidebar

### Modifying Visualizations
- All charts use Plotly for interactivity
- Customize colors, layouts, and chart types in the code
- Add new chart types by importing additional Plotly components

### Styling
- Custom CSS is included for better visual appearance
- Modify the CSS section to change colors, fonts, and layouts
- Add new CSS classes for custom styling

## 📊 Available Visualizations

- **Histograms**: Distribution analysis for numeric data
- **Bar Charts**: Categorical data analysis
- **Scatter Plots**: Correlation analysis between variables
- **Correlation Matrices**: Heat maps showing variable relationships
- **Time Series**: Trend analysis over time
- **Pie Charts**: Proportional distribution analysis
- **Box Plots**: Outlier detection and distribution spread

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

2. **Missing dependencies:**
   ```bash
   pip install --upgrade -r streamlit_requirements.txt
   ```

3. **Data loading errors:**
   - Ensure CSV files are in the correct directory
   - Check file permissions
   - Verify CSV format is valid

4. **Memory issues with large datasets:**
   - Use data sampling for initial exploration
   - Implement data caching with `@st.cache_data`

### Performance Tips

- Use `@st.cache_data` decorator for expensive data loading operations
- Implement data sampling for large datasets
- Use efficient data types (e.g., category for categorical data)
- Limit the number of simultaneous visualizations

## 📈 Future Enhancements

- Export functionality for charts and data
- Advanced filtering and search capabilities
- Machine learning model integration
- Real-time data streaming
- User authentication and data privacy
- Mobile-responsive design improvements

## 🤝 Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Created with ❤️ using Streamlit**

*For support or questions, please refer to the Streamlit documentation or create an issue in the repository.*
