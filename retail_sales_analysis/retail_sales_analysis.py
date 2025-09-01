import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_clean_data(file_path):
    """Load and clean the retail sales data"""
    print("Loading and cleaning retail sales data...")
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Basic data cleaning
    df = df.dropna()
    
    # Convert date column
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Add derived columns
    df['month'] = df['Date'].dt.month
    df['year'] = df['Date'].dt.year
    df['day_of_week'] = df['Date'].dt.day_name()
    df['quarter'] = df['Date'].dt.quarter
    df['day_of_month'] = df['Date'].dt.day
    
    print(f"Data loaded successfully! Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    return df

def generate_descriptive_statistics(df):
    """Generate comprehensive descriptive statistics"""
    print("\nGenerating descriptive statistics...")
    
    # Basic statistics
    stats_summary = df.describe()
    
    # Additional statistics
    additional_stats = {
        'Total_Transactions': len(df),
        'Total_Revenue': df['Total Amount'].sum(),
        'Average_Transaction_Value': df['Total Amount'].mean(),
        'Total_Quantity_Sold': df['Quantity'].sum(),
        'Unique_Customers': df['Customer ID'].nunique(),
        'Unique_Products': df['Product Category'].nunique(),
        'Date_Range_Start': df['Date'].min().strftime('%Y-%m-%d'),
        'Date_Range_End': df['Date'].max().strftime('%Y-%m-%d'),
        'Average_Age': df['Age'].mean(),
        'Male_Customers_Percentage': (df['Gender'] == 'Male').mean() * 100,
        'Female_Customers_Percentage': (df['Gender'] == 'Female').mean() * 100,
        'Average_Price_per_Unit': df['Price per Unit'].mean(),
        'Total_Units_Sold': df['Quantity'].sum()
    }
    
    return stats_summary, additional_stats

def perform_correlation_analysis(df):
    """Perform correlation analysis between variables"""
    print("Performing correlation analysis...")
    
    # Select numeric columns for correlation
    numeric_columns = ['Age', 'Quantity', 'Price per Unit', 'Total Amount']
    correlation_matrix = df[numeric_columns].corr()
    
    return correlation_matrix

def analyze_sales_by_category(df):
    """Analyze sales performance by product category"""
    print("Analyzing sales by product category...")
    
    category_analysis = df.groupby('Product Category').agg({
        'Total Amount': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'Price per Unit': ['mean', 'min', 'max'],
        'Customer ID': 'nunique'
    }).round(2)
    
    # Flatten column names
    category_analysis.columns = ['_'.join(col).strip() for col in category_analysis.columns]
    
    return category_analysis

def analyze_sales_by_gender(df):
    """Analyze sales performance by gender"""
    print("Analyzing sales by gender...")
    
    gender_analysis = df.groupby('Gender').agg({
        'Total Amount': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'Price per Unit': ['mean', 'min', 'max'],
        'Customer ID': 'nunique'
    }).round(2)
    
    # Flatten column names
    gender_analysis.columns = ['_'.join(col).strip() for col in gender_analysis.columns]
    
    return gender_analysis

def analyze_temporal_patterns(df):
    """Analyze temporal patterns in sales"""
    print("Analyzing temporal patterns...")
    
    # Monthly analysis
    monthly_analysis = df.groupby(['year', 'month']).agg({
        'Total Amount': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'Customer ID': 'nunique'
    }).round(2)
    
    # Day of week analysis
    dow_analysis = df.groupby('day_of_week').agg({
        'Total Amount': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'Customer ID': 'nunique'
    }).round(2)
    
    # Quarter analysis
    quarter_analysis = df.groupby(['year', 'quarter']).agg({
        'Total Amount': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'Customer ID': 'nunique'
    }).round(2)
    
    return monthly_analysis, dow_analysis, quarter_analysis

def analyze_demographics(df):
    """Analyze customer demographics"""
    print("Analyzing customer demographics...")
    
    # Age group analysis
    df['age_group'] = pd.cut(df['Age'], bins=[0, 25, 35, 45, 55, 100], 
                            labels=['18-25', '26-35', '36-45', '46-55', '55+'])
    
    age_analysis = df.groupby('age_group').agg({
        'Total Amount': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'Customer ID': 'nunique'
    }).round(2)
    
    # Gender analysis
    gender_analysis = df.groupby('Gender').agg({
        'Total Amount': ['sum', 'mean', 'count'],
        'Quantity': ['sum', 'mean'],
        'Customer ID': 'nunique'
    }).round(2)
    
    return age_analysis, gender_analysis

def analyze_customer_behavior(df):
    """Analyze customer behavior patterns"""
    print("Analyzing customer behavior...")
    
    # Customer frequency analysis
    customer_frequency = df.groupby('Customer ID').agg({
        'Transaction ID': 'count',
        'Total Amount': ['sum', 'mean'],
        'Quantity': ['sum', 'mean']
    }).round(2)
    
    # Flatten column names
    customer_frequency.columns = ['_'.join(col).strip() for col in customer_frequency.columns]
    
    # Product category preferences by customer
    customer_category_pref = df.groupby(['Customer ID', 'Product Category']).agg({
        'Total Amount': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    return customer_frequency, customer_category_pref

def perform_statistical_tests(df):
    """Perform statistical tests to determine significant factors"""
    print("Performing statistical tests...")
    
    statistical_tests = {}
    
    # Test gender differences in spending
    male_spending = df[df['Gender'] == 'Male']['Total Amount']
    female_spending = df[df['Gender'] == 'Female']['Total Amount']
    
    t_stat, p_value = stats.ttest_ind(male_spending, female_spending)
    statistical_tests['Gender_Spending_Difference'] = {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }
    
    # Test age correlation with spending
    age_corr, age_p_value = stats.pearsonr(df['Age'], df['Total Amount'])
    statistical_tests['Age_Spending_Correlation'] = {
        'correlation': age_corr,
        'p_value': age_p_value,
        'significant': age_p_value < 0.05
    }
    
    # Test quantity correlation with price
    quantity_price_corr, qp_p_value = stats.pearsonr(df['Quantity'], df['Price per Unit'])
    statistical_tests['Quantity_Price_Correlation'] = {
        'correlation': quantity_price_corr,
        'p_value': qp_p_value,
        'significant': qp_p_value < 0.05
    }
    
    return statistical_tests

def create_visualizations(df):
    """Create various visualizations"""
    print("Creating visualizations...")
    
    # Set up the plotting area
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('Retail Sales Data Analysis - Key Insights', fontsize=16, fontweight='bold')
    
    # 1. Sales by Product Category
    category_sales = df.groupby('Product Category')['Total Amount'].sum().sort_values(ascending=True)
    axes[0, 0].barh(range(len(category_sales)), category_sales.values)
    axes[0, 0].set_yticks(range(len(category_sales)))
    axes[0, 0].set_yticklabels(category_sales.index)
    axes[0, 0].set_title('Total Sales by Product Category')
    axes[0, 0].set_xlabel('Total Sales Amount')
    
    # 2. Gender Distribution
    gender_counts = df['Gender'].value_counts()
    axes[0, 1].pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0, 1].set_title('Customer Gender Distribution')
    
    # 3. Age Distribution
    axes[0, 2].hist(df['Age'], bins=20, alpha=0.7, edgecolor='black')
    axes[0, 2].set_title('Customer Age Distribution')
    axes[0, 2].set_xlabel('Age')
    axes[0, 2].set_ylabel('Frequency')
    
    # 4. Gender vs Average Transaction Value
    gender_avg = df.groupby('Gender')['Total Amount'].mean()
    axes[1, 0].bar(gender_avg.index, gender_avg.values)
    axes[1, 0].set_title('Average Transaction Value by Gender')
    axes[1, 0].set_ylabel('Average Transaction Value')
    
    # 5. Monthly Sales Trend
    monthly_sales = df.groupby(['year', 'month'])['Total Amount'].sum()
    monthly_sales.plot(kind='line', ax=axes[1, 1], marker='o')
    axes[1, 1].set_title('Monthly Sales Trend')
    axes[1, 1].set_xlabel('Year-Month')
    axes[1, 1].set_ylabel('Total Sales')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # 6. Day of Week Sales
    dow_sales = df.groupby('day_of_week')['Total Amount'].sum()
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_sales = dow_sales.reindex(dow_order)
    axes[1, 2].bar(dow_sales.index, dow_sales.values)
    axes[1, 2].set_title('Sales by Day of Week')
    axes[1, 2].set_ylabel('Total Sales')
    axes[1, 2].tick_params(axis='x', rotation=45)
    
    # 7. Price per Unit vs Quantity Scatter
    axes[2, 0].scatter(df['Price per Unit'], df['Quantity'], alpha=0.6)
    axes[2, 0].set_title('Price per Unit vs Quantity Relationship')
    axes[2, 0].set_xlabel('Price per Unit')
    axes[2, 0].set_ylabel('Quantity')
    
    # 8. Category vs Average Price
    category_price = df.groupby('Product Category')['Price per Unit'].mean().sort_values(ascending=True)
    axes[2, 1].barh(range(len(category_price)), category_price.values)
    axes[2, 1].set_yticks(range(len(category_price)))
    axes[2, 1].set_yticklabels(category_price.index)
    axes[2, 1].set_title('Average Price by Category')
    axes[2, 1].set_xlabel('Average Price per Unit')
    
    # 9. Age vs Spending Scatter
    axes[2, 2].scatter(df['Age'], df['Total Amount'], alpha=0.6)
    axes[2, 2].set_title('Age vs Total Amount Relationship')
    axes[2, 2].set_xlabel('Age')
    axes[2, 2].set_ylabel('Total Amount')
    
    plt.tight_layout()
    plt.savefig('retail_sales_analysis_visualizations.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return "Visualizations saved as 'retail_sales_analysis_visualizations.png'"

def generate_plantuml_diagram(df, stats_summary, category_analysis, gender_analysis, statistical_tests):
    """Generate PlantUML diagram showing data relationships"""
    print("Generating PlantUML diagram...")
    
    # Get top performing categories
    top_categories = category_analysis['Total Amount_sum'].sort_values(ascending=False).head(5).index.tolist()
    # Ensure we have at least 5 categories, pad with empty strings if needed
    while len(top_categories) < 5:
        top_categories.append('N/A')
    
    plantuml_content = f"""@startuml Retail_Sales_Analysis

!define RECTANGLE class

title Retail Sales Data Analysis - Data Model and Relationships

package "Sales Transaction" {{
    RECTANGLE Transaction {{
        + Transaction ID: Integer
        + Date: Date
        + Customer ID: String
        + Gender: String
        + Age: Integer
        + Product Category: String
        + Quantity: Integer
        + Price per Unit: Float
        + Total Amount: Float
    }}
}}

package "Key Insights" {{
    RECTANGLE Sales_Overview {{
        + Total Transactions: {len(df):.0f}
        + Total Revenue: {df['Total Amount'].sum():,.0f}
        + Average Transaction: {df['Total Amount'].mean():.2f}
        + Unique Customers: {df['Customer ID'].nunique():.0f}
    }}
    
    RECTANGLE Top_Categories {{
        + Category 1: {top_categories[0]}
        + Category 2: {top_categories[1]}
        + Category 3: {top_categories[2]}
        + Category 4: {top_categories[3]}
        + Category 5: {top_categories[4]}
    }}
    
    RECTANGLE Gender_Analysis {{
        + Male Customers: {gender_analysis.loc['Male', 'Customer ID_nunique']:.0f}
        + Female Customers: {gender_analysis.loc['Female', 'Customer ID_nunique']:.0f}
        + Male Avg Spending: {gender_analysis.loc['Male', 'Total Amount_mean']:.2f}
        + Female Avg Spending: {gender_analysis.loc['Female', 'Total Amount_mean']:.2f}
    }}
}}

package "Performance Metrics" {{
    RECTANGLE Category_Performance {{
        + Total Categories: {len(category_analysis)}
        + Highest Revenue Category: {top_categories[0]}
        + Average Price Range: {df['Price per Unit'].min():.2f} - {df['Price per Unit'].max():.2f}
    }}
    
    RECTANGLE Customer_Behavior {{
        + Average Age: {df['Age'].mean():.1f}
        + Age Range: {df['Age'].min():.0f} - {df['Age'].max():.0f}
        + Average Quantity per Transaction: {df['Quantity'].mean():.1f}
    }}
    
    RECTANGLE Statistical_Insights {{
        + Gender Spending Difference: {'Significant' if statistical_tests['Gender_Spending_Difference']['significant'] else 'Not Significant'}
        + Age-Spending Correlation: {'Significant' if statistical_tests['Age_Spending_Correlation']['significant'] else 'Not Significant'}
        + Quantity-Price Correlation: {'Significant' if statistical_tests['Quantity_Price_Correlation']['significant'] else 'Not Significant'}
    }}
}}

package "Temporal Analysis" {{
    RECTANGLE Time_Patterns {{
        + Date Range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}
        + Total Months: {df['month'].nunique()}
        + Average Daily Transactions: {len(df) / df['Date'].nunique():.1f}
    }}
}}

' Relationships
Transaction ||--|| Sales_Overview : "generates"
Transaction ||--|| Top_Categories : "belongs to"
Transaction ||--|| Gender_Analysis : "represents"
Transaction ||--|| Category_Performance : "contributes to"
Transaction ||--|| Customer_Behavior : "reflects"
Transaction ||--|| Statistical_Insights : "validates"
Transaction ||--|| Time_Patterns : "occurs during"

note right of Top_Categories
  Top revenue categories:
  {top_categories[0]}: {f"{category_analysis.loc[top_categories[0], 'Total Amount_sum']:,.0f}" if top_categories[0] != 'N/A' else 'N/A'}
  {top_categories[1]}: {f"{category_analysis.loc[top_categories[1], 'Total Amount_sum']:,.0f}" if top_categories[1] != 'N/A' else 'N/A'}
  {top_categories[2]}: {f"{category_analysis.loc[top_categories[2], 'Total Amount_sum']:,.0f}" if top_categories[2] != 'N/A' else 'N/A'}
  {top_categories[3]}: {f"{category_analysis.loc[top_categories[3], 'Total Amount_sum']:,.0f}" if top_categories[3] != 'N/A' else 'N/A'}
  {top_categories[4]}: {f"{category_analysis.loc[top_categories[4], 'Total Amount_sum']:,.0f}" if top_categories[4] != 'N/A' else 'N/A'}
end note

note right of Statistical_Insights
  Statistical test results:
  Gender difference p-value: {statistical_tests['Gender_Spending_Difference']['p_value']:.4f}
  Age correlation: {statistical_tests['Age_Spending_Correlation']['correlation']:.3f}
  Quantity-Price correlation: {statistical_tests['Quantity_Price_Correlation']['correlation']:.3f}
end note

@enduml"""
    
    # Save PlantUML content to file
    with open('retail_sales_analysis.puml', 'w') as f:
        f.write(plantuml_content)
    
    return "PlantUML diagram saved as 'retail_sales_analysis.puml'"

def create_excel_report(df, stats_summary, category_analysis, gender_analysis, 
                       monthly_analysis, dow_analysis, quarter_analysis, age_analysis, 
                       customer_frequency, customer_category_pref, statistical_tests, additional_stats):
    """Create comprehensive Excel report"""
    print("Creating Excel report...")
    
    # Create Excel writer
    with pd.ExcelWriter('retail_sales_analysis_results.xlsx', engine='openpyxl') as writer:
        
        # 1. Raw Data
        df.to_excel(writer, sheet_name='Raw_Data', index=False)
        
        # 2. Descriptive Statistics
        stats_summary.to_excel(writer, sheet_name='Descriptive_Statistics')
        
        # 3. Additional Statistics
        additional_stats_df = pd.DataFrame(list(additional_stats.items()), 
                                          columns=['Metric', 'Value'])
        additional_stats_df.to_excel(writer, sheet_name='Additional_Statistics', index=False)
        
        # 4. Category Analysis
        category_analysis.to_excel(writer, sheet_name='Category_Analysis')
        
        # 5. Gender Analysis
        gender_analysis.to_excel(writer, sheet_name='Gender_Analysis')
        
        # 6. Monthly Analysis
        monthly_analysis.to_excel(writer, sheet_name='Monthly_Analysis')
        
        # 7. Day of Week Analysis
        dow_analysis.to_excel(writer, sheet_name='Day_of_Week_Analysis')
        
        # 8. Quarter Analysis
        quarter_analysis.to_excel(writer, sheet_name='Quarter_Analysis')
        
        # 9. Age Analysis
        age_analysis.to_excel(writer, sheet_name='Age_Analysis')
        
        # 10. Customer Frequency Analysis
        customer_frequency.to_excel(writer, sheet_name='Customer_Frequency')
        
        # 11. Customer Category Preferences
        customer_category_pref.to_excel(writer, sheet_name='Customer_Category_Prefs', index=False)
        
        # 12. Statistical Tests
        stats_df = pd.DataFrame(statistical_tests).T
        stats_df.to_excel(writer, sheet_name='Statistical_Tests')
        
        # 13. Summary Insights
        insights_data = {
            'Insight': [
                'Total Transactions',
                'Total Revenue',
                'Average Transaction Value',
                'Total Quantity Sold',
                'Unique Customers',
                'Unique Product Categories',
                'Date Range Start',
                'Date Range End',
                'Average Customer Age',
                'Male Customers Percentage',
                'Female Customers Percentage',
                'Average Price per Unit',
                'Top Revenue Category',
                'Gender with Higher Spending',
                'Significant Gender Difference in Spending'
            ],
            'Value': [
                additional_stats['Total_Transactions'],
                f"{additional_stats['Total_Revenue']:,.2f}",
                f"{additional_stats['Average_Transaction_Value']:.2f}",
                additional_stats['Total_Quantity_Sold'],
                additional_stats['Unique_Customers'],
                additional_stats['Unique_Products'],
                additional_stats['Date_Range_Start'],
                additional_stats['Date_Range_End'],
                f"{additional_stats['Average_Age']:.1f}",
                f"{additional_stats['Male_Customers_Percentage']:.1f}%",
                f"{additional_stats['Female_Customers_Percentage']:.1f}%",
                f"{additional_stats['Average_Price_per_Unit']:.2f}",
                category_analysis['Total Amount_sum'].idxmax(),
                'Male' if gender_analysis.loc['Male', 'Total Amount_mean'] > gender_analysis.loc['Female', 'Total Amount_mean'] else 'Female',
                'Yes' if statistical_tests['Gender_Spending_Difference']['significant'] else 'No'
            ]
        }
        insights_df = pd.DataFrame(insights_data)
        insights_df.to_excel(writer, sheet_name='Key_Insights', index=False)
    
    return "Excel report saved as 'retail_sales_analysis_results.xlsx'"

def main():
    """Main function to run the complete analysis"""
    print("=" * 60)
    print("RETAIL SALES DATA ANALYSIS")
    print("=" * 60)
    
    # Load and clean data
    df = load_and_clean_data('../retail_sales_dataset.csv')
    
    # Generate descriptive statistics
    stats_summary, additional_stats = generate_descriptive_statistics(df)
    
    # Perform correlation analysis
    correlation_matrix = perform_correlation_analysis(df)
    
    # Analyze sales by category
    category_analysis = analyze_sales_by_category(df)
    
    # Analyze sales by gender
    gender_analysis = analyze_sales_by_gender(df)
    
    # Analyze temporal patterns
    monthly_analysis, dow_analysis, quarter_analysis = analyze_temporal_patterns(df)
    
    # Analyze demographics
    age_analysis, gender_demo_analysis = analyze_demographics(df)
    
    # Analyze customer behavior
    customer_frequency, customer_category_pref = analyze_customer_behavior(df)
    
    # Perform statistical tests
    statistical_tests = perform_statistical_tests(df)
    
    # Create visualizations
    viz_result = create_visualizations(df)
    print(f"✓ {viz_result}")
    
    # Generate PlantUML diagram
    puml_result = generate_plantuml_diagram(df, stats_summary, category_analysis, gender_analysis, statistical_tests)
    print(f"✓ {puml_result}")
    
    # Create Excel report
    excel_result = create_excel_report(df, stats_summary, category_analysis, gender_analysis,
                                     monthly_analysis, dow_analysis, quarter_analysis, age_analysis,
                                     customer_frequency, customer_category_pref, statistical_tests, additional_stats)
    print(f"✓ {excel_result}")
    
    # Print key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"• Total Transactions: {additional_stats['Total_Transactions']}")
    print(f"• Total Revenue: {additional_stats['Total_Revenue']:,.2f}")
    print(f"• Average Transaction Value: {additional_stats['Average_Transaction_Value']:.2f}")
    print(f"• Unique Customers: {additional_stats['Unique_Customers']}")
    print(f"• Unique Product Categories: {additional_stats['Unique_Products']}")
    print(f"• Top Revenue Category: {category_analysis['Total Amount_sum'].idxmax()}")
    print(f"• Gender with Higher Spending: {'Male' if gender_analysis.loc['Male', 'Total Amount_mean'] > gender_analysis.loc['Female', 'Total Amount_mean'] else 'Female'}")
    print(f"• Significant Gender Difference in Spending: {'Yes' if statistical_tests['Gender_Spending_Difference']['significant'] else 'No'}")
    print(f"• Age-Spending Correlation: {statistical_tests['Age_Spending_Correlation']['correlation']:.3f}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print("Generated files:")
    print("1. retail_sales_analysis.puml - PlantUML diagram")
    print("2. retail_sales_analysis_results.xlsx - Excel report")
    print("3. retail_sales_analysis_visualizations.png - Visualizations")

if __name__ == "__main__":
    main()
