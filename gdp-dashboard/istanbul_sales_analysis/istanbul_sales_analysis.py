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
    """Load and clean the Istanbul sales data"""
    print("Loading and cleaning Istanbul sales data...")
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Basic data cleaning
    df = df.dropna()
    
    # Convert date column
    df['invoice_date'] = pd.to_datetime(df['invoice_date'])
    
    # Add derived columns
    df['total_amount'] = df['quantity'] * df['price']
    df['month'] = df['invoice_date'].dt.month
    df['year'] = df['invoice_date'].dt.year
    df['day_of_week'] = df['invoice_date'].dt.day_name()
    df['quarter'] = df['invoice_date'].dt.quarter
    
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
        'Total_Revenue': df['total_amount'].sum(),
        'Average_Transaction_Value': df['total_amount'].mean(),
        'Total_Quantity_Sold': df['quantity'].sum(),
        'Unique_Customers': df['customer_id'].nunique(),
        'Unique_Products': df['category'].nunique(),
        'Unique_Malls': df['shopping_mall'].nunique(),
        'Date_Range_Start': df['invoice_date'].min().strftime('%Y-%m-%d'),
        'Date_Range_End': df['invoice_date'].max().strftime('%Y-%m-%d'),
        'Average_Age': df['age'].mean(),
        'Male_Customers_Percentage': (df['gender'] == 'Male').mean() * 100,
        'Female_Customers_Percentage': (df['gender'] == 'Female').mean() * 100
    }
    
    return stats_summary, additional_stats

def perform_correlation_analysis(df):
    """Perform correlation analysis between variables"""
    print("Performing correlation analysis...")
    
    # Select numeric columns for correlation
    numeric_columns = ['age', 'quantity', 'price', 'total_amount']
    correlation_matrix = df[numeric_columns].corr()
    
    return correlation_matrix

def analyze_sales_by_category(df):
    """Analyze sales performance by category"""
    print("Analyzing sales by category...")
    
    category_analysis = df.groupby('category').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean'],
        'price': ['mean', 'min', 'max']
    }).round(2)
    
    # Flatten column names
    category_analysis.columns = ['_'.join(col).strip() for col in category_analysis.columns]
    
    return category_analysis

def analyze_sales_by_mall(df):
    """Analyze sales performance by shopping mall"""
    print("Analyzing sales by shopping mall...")
    
    mall_analysis = df.groupby('shopping_mall').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean'],
        'customer_id': 'nunique'
    }).round(2)
    
    # Flatten column names
    mall_analysis.columns = ['_'.join(col).strip() for col in mall_analysis.columns]
    
    return mall_analysis

def analyze_payment_methods(df):
    """Analyze payment method preferences"""
    print("Analyzing payment methods...")
    
    payment_analysis = df.groupby('payment_method').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean']
    }).round(2)
    
    # Flatten column names
    payment_analysis.columns = ['_'.join(col).strip() for col in payment_analysis.columns]
    
    return payment_analysis

def analyze_temporal_patterns(df):
    """Analyze temporal patterns in sales"""
    print("Analyzing temporal patterns...")
    
    # Monthly analysis
    monthly_analysis = df.groupby(['year', 'month']).agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean']
    }).round(2)
    
    # Day of week analysis
    dow_analysis = df.groupby('day_of_week').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean']
    }).round(2)
    
    # Quarter analysis
    quarter_analysis = df.groupby(['year', 'quarter']).agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean']
    }).round(2)
    
    return monthly_analysis, dow_analysis, quarter_analysis

def analyze_demographics(df):
    """Analyze customer demographics"""
    print("Analyzing customer demographics...")
    
    # Age group analysis
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 45, 55, 100], 
                            labels=['18-25', '26-35', '36-45', '46-55', '55+'])
    
    age_analysis = df.groupby('age_group').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean'],
        'customer_id': 'nunique'
    }).round(2)
    
    # Gender analysis
    gender_analysis = df.groupby('gender').agg({
        'total_amount': ['sum', 'mean', 'count'],
        'quantity': ['sum', 'mean'],
        'customer_id': 'nunique'
    }).round(2)
    
    return age_analysis, gender_analysis

def create_visualizations(df):
    """Create various visualizations"""
    print("Creating visualizations...")
    
    # Set up the plotting area
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('Istanbul Sales Data Analysis - Key Insights', fontsize=16, fontweight='bold')
    
    # 1. Sales by Category
    category_sales = df.groupby('category')['total_amount'].sum().sort_values(ascending=True)
    axes[0, 0].barh(range(len(category_sales)), category_sales.values)
    axes[0, 0].set_yticks(range(len(category_sales)))
    axes[0, 0].set_yticklabels(category_sales.index)
    axes[0, 0].set_title('Total Sales by Category')
    axes[0, 0].set_xlabel('Total Sales Amount')
    
    # 2. Sales by Mall
    mall_sales = df.groupby('shopping_mall')['total_amount'].sum().sort_values(ascending=True)
    axes[0, 1].barh(range(len(mall_sales)), mall_sales.values)
    axes[0, 1].set_yticks(range(len(mall_sales)))
    axes[0, 1].set_yticklabels(mall_sales.index, fontsize=8)
    axes[0, 1].set_title('Total Sales by Shopping Mall')
    axes[0, 1].set_xlabel('Total Sales Amount')
    
    # 3. Payment Method Distribution
    payment_counts = df['payment_method'].value_counts()
    axes[0, 2].pie(payment_counts.values, labels=payment_counts.index, autopct='%1.1f%%', startangle=90)
    axes[0, 2].set_title('Payment Method Distribution')
    
    # 4. Age Distribution
    axes[1, 0].hist(df['age'], bins=20, alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Customer Age Distribution')
    axes[1, 0].set_xlabel('Age')
    axes[1, 0].set_ylabel('Frequency')
    
    # 5. Gender vs Average Transaction Value
    gender_avg = df.groupby('gender')['total_amount'].mean()
    axes[1, 1].bar(gender_avg.index, gender_avg.values)
    axes[1, 1].set_title('Average Transaction Value by Gender')
    axes[1, 1].set_ylabel('Average Transaction Value')
    
    # 6. Monthly Sales Trend
    monthly_sales = df.groupby(['year', 'month'])['total_amount'].sum()
    monthly_sales.plot(kind='line', ax=axes[1, 2], marker='o')
    axes[1, 2].set_title('Monthly Sales Trend')
    axes[1, 2].set_xlabel('Year-Month')
    axes[1, 2].set_ylabel('Total Sales')
    axes[1, 2].tick_params(axis='x', rotation=45)
    
    # 7. Day of Week Sales
    dow_sales = df.groupby('day_of_week')['total_amount'].sum()
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_sales = dow_sales.reindex(dow_order)
    axes[2, 0].bar(dow_sales.index, dow_sales.values)
    axes[2, 0].set_title('Sales by Day of Week')
    axes[2, 0].set_ylabel('Total Sales')
    axes[2, 0].tick_params(axis='x', rotation=45)
    
    # 8. Price vs Quantity Scatter
    axes[2, 1].scatter(df['price'], df['quantity'], alpha=0.6)
    axes[2, 1].set_title('Price vs Quantity Relationship')
    axes[2, 1].set_xlabel('Price')
    axes[2, 1].set_ylabel('Quantity')
    
    # 9. Category vs Average Price
    category_price = df.groupby('category')['price'].mean().sort_values(ascending=True)
    axes[2, 2].barh(range(len(category_price)), category_price.values)
    axes[2, 2].set_yticks(range(len(category_price)))
    axes[2, 2].set_yticklabels(category_price.index)
    axes[2, 2].set_title('Average Price by Category')
    axes[2, 2].set_xlabel('Average Price')
    
    plt.tight_layout()
    plt.savefig('istanbul_sales_analysis_visualizations.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return "Visualizations saved as 'istanbul_sales_analysis_visualizations.png'"

def generate_plantuml_diagram(df, stats_summary, category_analysis, mall_analysis, payment_analysis):
    """Generate PlantUML diagram showing data relationships"""
    print("Generating PlantUML diagram...")
    
    # Get top performing categories and malls
    top_categories = category_analysis['total_amount_sum'].sort_values(ascending=False).head(5).index.tolist()
    top_malls = mall_analysis['total_amount_sum'].sort_values(ascending=False).head(5).index.tolist()
    
    plantuml_content = f"""@startuml Istanbul_Sales_Analysis

!define RECTANGLE class

title Istanbul Sales Data Analysis - Data Model and Relationships

package "Sales Transaction" {{
    RECTANGLE Transaction {{
        + invoice_no: String
        + customer_id: String
        + gender: String
        + age: Integer
        + category: String
        + quantity: Integer
        + price: Float
        + payment_method: String
        + invoice_date: Date
        + shopping_mall: String
        + total_amount: Float
    }}
}}

package "Key Insights" {{
    RECTANGLE Sales_Overview {{
        + Total Transactions: {len(df):.0f}
        + Total Revenue: {df['total_amount'].sum():,.0f}
        + Average Transaction: {df['total_amount'].mean():.2f}
        + Unique Customers: {df['customer_id'].nunique():.0f}
    }}
    
    RECTANGLE Top_Categories {{
        + Category 1: {top_categories[0]}
        + Category 2: {top_categories[1]}
        + Category 3: {top_categories[2]}
        + Category 4: {top_categories[3]}
        + Category 5: {top_categories[4]}
    }}
    
    RECTANGLE Top_Malls {{
        + Mall 1: {top_malls[0]}
        + Mall 2: {top_malls[1]}
        + Mall 3: {top_malls[2]}
        + Mall 4: {top_malls[3]}
        + Mall 5: {top_malls[4]}
    }}
}}

package "Performance Metrics" {{
    RECTANGLE Category_Performance {{
        + Total Categories: {len(category_analysis)}
        + Highest Revenue Category: {top_categories[0]}
        + Average Price Range: {df['price'].min():.2f} - {df['price'].max():.2f}
    }}
    
    RECTANGLE Mall_Performance {{
        + Total Malls: {len(mall_analysis)}
        + Highest Revenue Mall: {top_malls[0]}
        + Average Transactions per Mall: {len(df) / len(mall_analysis):.0f}
    }}
    
    RECTANGLE Payment_Analysis {{
        + Payment Methods: {len(payment_analysis)}
        + Most Popular Method: {payment_analysis['total_amount_count'].idxmax()}
        + Average Transaction by Method: {payment_analysis['total_amount_mean'].max():.2f}
    }}
}}

package "Customer Demographics" {{
    RECTANGLE Customer_Profile {{
        + Average Age: {df['age'].mean():.1f}
        + Age Range: {df['age'].min():.0f} - {df['age'].max():.0f}
        + Gender Distribution: {(df['gender'] == 'Female').mean()*100:.1f}% Female, {(df['gender'] == 'Male').mean()*100:.1f}% Male
    }}
}}

' Relationships
Transaction ||--|| Sales_Overview : "generates"
Transaction ||--|| Top_Categories : "belongs to"
Transaction ||--|| Top_Malls : "occurs at"
Transaction ||--|| Category_Performance : "contributes to"
Transaction ||--|| Mall_Performance : "contributes to"
Transaction ||--|| Payment_Analysis : "uses"
Transaction ||--|| Customer_Profile : "represents"

note right of Top_Categories
  Top revenue categories:
  {top_categories[0]}: {category_analysis.loc[top_categories[0], 'total_amount_sum']:,.0f}
  {top_categories[1]}: {category_analysis.loc[top_categories[1], 'total_amount_sum']:,.0f}
  {top_categories[2]}: {category_analysis.loc[top_categories[2], 'total_amount_sum']:,.0f}
  {top_categories[3]}: {category_analysis.loc[top_categories[3], 'total_amount_sum']:,.0f}
  {top_categories[4]}: {category_analysis.loc[top_categories[4], 'total_amount_sum']:,.0f}
end note

note right of Top_Malls
  Top revenue malls:
  {top_malls[0]}: {mall_analysis.loc[top_malls[0], 'total_amount_sum']:,.0f}
  {top_malls[1]}: {mall_analysis.loc[top_malls[1], 'total_amount_sum']:,.0f}
  {top_malls[2]}: {mall_analysis.loc[top_malls[2], 'total_amount_sum']:,.0f}
  {top_malls[3]}: {mall_analysis.loc[top_malls[3], 'total_amount_sum']:,.0f}
  {top_malls[4]}: {mall_analysis.loc[top_malls[4], 'total_amount_sum']:,.0f}
end note

@enduml"""
    
    # Save PlantUML content to file
    with open('istanbul_sales_analysis.puml', 'w') as f:
        f.write(plantuml_content)
    
    return "PlantUML diagram saved as 'istanbul_sales_analysis.puml'"

def create_excel_report(df, stats_summary, category_analysis, mall_analysis, payment_analysis, 
                       monthly_analysis, dow_analysis, quarter_analysis, age_analysis, gender_analysis, additional_stats):
    """Create comprehensive Excel report"""
    print("Creating Excel report...")
    
    # Create Excel writer
    with pd.ExcelWriter('istanbul_sales_analysis_results.xlsx', engine='openpyxl') as writer:
        
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
        
        # 5. Mall Analysis
        mall_analysis.to_excel(writer, sheet_name='Mall_Analysis')
        
        # 6. Payment Analysis
        payment_analysis.to_excel(writer, sheet_name='Payment_Analysis')
        
        # 7. Monthly Analysis
        monthly_analysis.to_excel(writer, sheet_name='Monthly_Analysis')
        
        # 8. Day of Week Analysis
        dow_analysis.to_excel(writer, sheet_name='Day_of_Week_Analysis')
        
        # 9. Quarter Analysis
        quarter_analysis.to_excel(writer, sheet_name='Quarter_Analysis')
        
        # 10. Age Analysis
        age_analysis.to_excel(writer, sheet_name='Age_Analysis')
        
        # 11. Gender Analysis
        gender_analysis.to_excel(writer, sheet_name='Gender_Analysis')
        
        # 12. Summary Insights
        insights_data = {
            'Insight': [
                'Total Transactions',
                'Total Revenue',
                'Average Transaction Value',
                'Total Quantity Sold',
                'Unique Customers',
                'Unique Product Categories',
                'Unique Shopping Malls',
                'Date Range Start',
                'Date Range End',
                'Average Customer Age',
                'Male Customers Percentage',
                'Female Customers Percentage',
                'Top Revenue Category',
                'Top Revenue Mall',
                'Most Popular Payment Method'
            ],
            'Value': [
                additional_stats['Total_Transactions'],
                f"{additional_stats['Total_Revenue']:,.2f}",
                f"{additional_stats['Average_Transaction_Value']:.2f}",
                additional_stats['Total_Quantity_Sold'],
                additional_stats['Unique_Customers'],
                additional_stats['Unique_Products'],
                additional_stats['Unique_Malls'],
                additional_stats['Date_Range_Start'],
                additional_stats['Date_Range_End'],
                f"{additional_stats['Average_Age']:.1f}",
                f"{additional_stats['Male_Customers_Percentage']:.1f}%",
                f"{additional_stats['Female_Customers_Percentage']:.1f}%",
                category_analysis['total_amount_sum'].idxmax(),
                mall_analysis['total_amount_sum'].idxmax(),
                payment_analysis['total_amount_count'].idxmax()
            ]
        }
        insights_df = pd.DataFrame(insights_data)
        insights_df.to_excel(writer, sheet_name='Key_Insights', index=False)
    
    return "Excel report saved as 'istanbul_sales_analysis_results.xlsx'"

def main():
    """Main function to run the complete analysis"""
    print("=" * 60)
    print("ISTANBUL SALES DATA ANALYSIS")
    print("=" * 60)
    
    # Load and clean data
    df = load_and_clean_data('../istanbul_sales_data.csv')
    
    # Generate descriptive statistics
    stats_summary, additional_stats = generate_descriptive_statistics(df)
    
    # Perform correlation analysis
    correlation_matrix = perform_correlation_analysis(df)
    
    # Analyze sales by category
    category_analysis = analyze_sales_by_category(df)
    
    # Analyze sales by mall
    mall_analysis = analyze_sales_by_mall(df)
    
    # Analyze payment methods
    payment_analysis = analyze_payment_methods(df)
    
    # Analyze temporal patterns
    monthly_analysis, dow_analysis, quarter_analysis = analyze_temporal_patterns(df)
    
    # Analyze demographics
    age_analysis, gender_analysis = analyze_demographics(df)
    
    # Create visualizations
    viz_result = create_visualizations(df)
    print(f"✓ {viz_result}")
    
    # Generate PlantUML diagram
    puml_result = generate_plantuml_diagram(df, stats_summary, category_analysis, mall_analysis, payment_analysis)
    print(f"✓ {puml_result}")
    
    # Create Excel report
    excel_result = create_excel_report(df, stats_summary, category_analysis, mall_analysis, payment_analysis,
                                     monthly_analysis, dow_analysis, quarter_analysis, age_analysis, gender_analysis, additional_stats)
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
    print(f"• Unique Shopping Malls: {additional_stats['Unique_Malls']}")
    print(f"• Top Revenue Category: {category_analysis['total_amount_sum'].idxmax()}")
    print(f"• Top Revenue Mall: {mall_analysis['total_amount_sum'].idxmax()}")
    print(f"• Most Popular Payment Method: {payment_analysis['total_amount_count'].idxmax()}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print("Generated files:")
    print("1. istanbul_sales_analysis.puml - PlantUML diagram")
    print("2. istanbul_sales_analysis_results.xlsx - Excel report")
    print("3. istanbul_sales_analysis_visualizations.png - Visualizations")

if __name__ == "__main__":
    main()
