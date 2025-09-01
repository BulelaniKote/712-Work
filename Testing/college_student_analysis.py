import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_and_clean_data(file_path):
    """Load and clean the college student data"""
    print("Loading and cleaning data...")
    
    # Load the CSV file
    df = pd.read_csv(file_path)
    
    # Basic data cleaning
    df = df.dropna()
    
    # Convert categorical variables
    df['Internship_Experience'] = df['Internship_Experience'].map({'Yes': 1, 'No': 0})
    df['Placement'] = df['Placement'].map({'Yes': 1, 'No': 0})
    
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
        'Total_Students': len(df),
        'Placement_Rate': df['Placement'].mean() * 100,
        'Internship_Rate': df['Internship_Experience'].mean() * 100,
        'IQ_Mean': df['IQ'].mean(),
        'CGPA_Mean': df['CGPA'].mean(),
        'Academic_Performance_Mean': df['Academic_Performance'].mean(),
        'Communication_Skills_Mean': df['Communication_Skills'].mean(),
        'Projects_Completed_Mean': df['Projects_Completed'].mean(),
        'Extra_Curricular_Score_Mean': df['Extra_Curricular_Score'].mean()
    }
    
    return stats_summary, additional_stats

def perform_correlation_analysis(df):
    """Perform correlation analysis between variables"""
    print("Performing correlation analysis...")
    
    # Calculate correlation matrix using only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    correlation_matrix = numeric_df.corr()
    
    # Find top correlations with Placement
    placement_correlations = correlation_matrix['Placement'].sort_values(ascending=False)
    
    return correlation_matrix, placement_correlations

def analyze_placement_factors(df):
    """Analyze factors affecting placement"""
    print("Analyzing placement factors...")
    
    # Compare means between placed and not placed students
    placement_analysis = {}
    
    # Get numeric columns only
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for column in numeric_columns:
        if column != 'Placement':
            placed_mean = df[df['Placement'] == 1][column].mean()
            not_placed_mean = df[df['Placement'] == 0][column].mean()
            difference = placed_mean - not_placed_mean
            
            placement_analysis[column] = {
                'Placed_Mean': placed_mean,
                'Not_Placed_Mean': not_placed_mean,
                'Difference': difference
            }
    
    return placement_analysis

def perform_statistical_tests(df):
    """Perform statistical tests to determine significant factors"""
    print("Performing statistical tests...")
    
    statistical_tests = {}
    
    # Get numeric columns only
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for column in numeric_columns:
        if column != 'Placement':
            # T-test for continuous variables
            placed_data = df[df['Placement'] == 1][column]
            not_placed_data = df[df['Placement'] == 0][column]
            
            t_stat, p_value = stats.ttest_ind(placed_data, not_placed_data)
            
            statistical_tests[column] = {
                't_statistic': t_stat,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
    
    return statistical_tests

def create_visualizations(df):
    """Create various visualizations"""
    print("Creating visualizations...")
    
    # Set up the plotting area
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('College Student Analysis - Key Insights', fontsize=16, fontweight='bold')
    
    # 1. Placement Distribution
    placement_counts = df['Placement'].value_counts()
    axes[0, 0].pie(placement_counts.values, labels=['Not Placed', 'Placed'], autopct='%1.1f%%', startangle=90)
    axes[0, 0].set_title('Placement Distribution')
    
    # 2. IQ Distribution by Placement
    df.boxplot(column='IQ', by='Placement', ax=axes[0, 1])
    axes[0, 1].set_title('IQ Distribution by Placement Status')
    axes[0, 1].set_xlabel('Placement Status')
    axes[0, 1].set_ylabel('IQ Score')
    
    # 3. CGPA Distribution by Placement
    df.boxplot(column='CGPA', by='Placement', ax=axes[0, 2])
    axes[0, 2].set_title('CGPA Distribution by Placement Status')
    axes[0, 2].set_xlabel('Placement Status')
    axes[0, 2].set_ylabel('CGPA')
    
    # 4. Academic Performance vs Placement
    sns.boxplot(data=df, x='Placement', y='Academic_Performance', ax=axes[1, 0])
    axes[1, 0].set_title('Academic Performance by Placement Status')
    axes[1, 0].set_xlabel('Placement Status')
    axes[1, 0].set_ylabel('Academic Performance Score')
    
    # 5. Communication Skills vs Placement
    sns.boxplot(data=df, x='Placement', y='Communication_Skills', ax=axes[1, 1])
    axes[1, 1].set_title('Communication Skills by Placement Status')
    axes[1, 1].set_xlabel('Placement Status')
    axes[1, 1].set_ylabel('Communication Skills Score')
    
    # 6. Projects Completed vs Placement
    sns.boxplot(data=df, x='Placement', y='Projects_Completed', ax=axes[1, 2])
    axes[1, 2].set_title('Projects Completed by Placement Status')
    axes[1, 2].set_xlabel('Placement Status')
    axes[1, 2].set_ylabel('Number of Projects Completed')
    
    plt.tight_layout()
    plt.savefig('college_student_analysis_visualizations.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    return "Visualizations saved as 'college_student_analysis_visualizations.png'"

def generate_plantuml_diagram(df, stats_summary, placement_analysis, statistical_tests):
    """Generate PlantUML diagram showing data relationships"""
    print("Generating PlantUML diagram...")
    
    # Get top factors affecting placement using numeric dataframe
    numeric_df = df.select_dtypes(include=[np.number])
    placement_correlations = numeric_df.corr()['Placement'].sort_values(ascending=False)
    top_factors = placement_correlations[1:6].index.tolist()  # Exclude Placement itself
    
    plantuml_content = f"""@startuml College_Student_Analysis

!define RECTANGLE class

title College Student Analysis - Data Model and Relationships

package "Student Data" {{
    RECTANGLE Student {{
        + College_ID: String
        + IQ: Integer
        + Prev_Sem_Result: Float
        + CGPA: Float
        + Academic_Performance: Integer
        + Internship_Experience: Boolean
        + Extra_Curricular_Score: Integer
        + Communication_Skills: Integer
        + Projects_Completed: Integer
        + Placement: Boolean
    }}
}}

package "Key Insights" {{
    RECTANGLE Placement_Analysis {{
        + Total Students: {stats_summary['Placement']['count']:.0f}
        + Placement Rate: {stats_summary['Placement']['mean']*100:.1f}%
        + Internship Rate: {stats_summary['Internship_Experience']['mean']*100:.1f}%
    }}
    
    RECTANGLE Top_Factors {{
        + Factor 1: {top_factors[0]}
        + Factor 2: {top_factors[1]}
        + Factor 3: {top_factors[2]}
        + Factor 4: {top_factors[3]}
        + Factor 5: {top_factors[4]}
    }}
    
    RECTANGLE Statistical_Significance {{
        + Significant Factors: {sum(1 for test in statistical_tests.values() if test['significant'])}
        + Total Factors Tested: {len(statistical_tests)}
    }}
}}

package "Performance Metrics" {{
    RECTANGLE Academic_Metrics {{
        + Average IQ: {stats_summary['IQ']['mean']:.1f}
        + Average CGPA: {stats_summary['CGPA']['mean']:.2f}
        + Average Academic Performance: {stats_summary['Academic_Performance']['mean']:.1f}
    }}
    
    RECTANGLE Skills_Metrics {{
        + Average Communication: {stats_summary['Communication_Skills']['mean']:.1f}
        + Average Projects: {stats_summary['Projects_Completed']['mean']:.1f}
        + Average Extra Curricular: {stats_summary['Extra_Curricular_Score']['mean']:.1f}
    }}
}}

' Relationships
Student ||--|| Placement_Analysis : "affects"
Student ||--|| Top_Factors : "influenced by"
Student ||--|| Academic_Metrics : "measured by"
Student ||--|| Skills_Metrics : "evaluated by"
Top_Factors ||--|| Statistical_Significance : "validated by"

note right of Top_Factors
  Top factors affecting placement:
  {top_factors[0]}: {placement_correlations[top_factors[0]]:.3f}
  {top_factors[1]}: {placement_correlations[top_factors[1]]:.3f}
  {top_factors[2]}: {placement_correlations[top_factors[2]]:.3f}
  {top_factors[3]}: {placement_correlations[top_factors[3]]:.3f}
  {top_factors[4]}: {placement_correlations[top_factors[4]]:.3f}
end note

note right of Statistical_Significance
  Significant factors (p < 0.05):
  {', '.join([factor for factor, test in statistical_tests.items() if test['significant']])}
end note

@enduml"""
    
    # Save PlantUML content to file
    with open('college_student_analysis.puml', 'w') as f:
        f.write(plantuml_content)
    
    return "PlantUML diagram saved as 'college_student_analysis.puml'"

def create_excel_report(df, stats_summary, placement_analysis, statistical_tests, additional_stats):
    """Create comprehensive Excel report"""
    print("Creating Excel report...")
    
    # Create Excel writer
    with pd.ExcelWriter('college_student_analysis_results.xlsx', engine='openpyxl') as writer:
        
        # 1. Raw Data
        df.to_excel(writer, sheet_name='Raw_Data', index=False)
        
        # 2. Descriptive Statistics
        stats_summary.to_excel(writer, sheet_name='Descriptive_Statistics')
        
        # 3. Additional Statistics
        additional_stats_df = pd.DataFrame(list(additional_stats.items()), 
                                         columns=['Metric', 'Value'])
        additional_stats_df.to_excel(writer, sheet_name='Additional_Statistics', index=False)
        
        # 4. Correlation Matrix
        numeric_df = df.select_dtypes(include=[np.number])
        correlation_matrix_excel = numeric_df.corr()
        correlation_matrix_excel.to_excel(writer, sheet_name='Correlation_Matrix')
        
        # 5. Placement Analysis
        placement_df = pd.DataFrame(placement_analysis).T
        placement_df.to_excel(writer, sheet_name='Placement_Analysis')
        
        # 6. Statistical Tests
        stats_df = pd.DataFrame(statistical_tests).T
        stats_df.to_excel(writer, sheet_name='Statistical_Tests')
        
        # 7. Summary Insights
        insights_data = {
            'Insight': [
                'Total Students Analyzed',
                'Placement Rate',
                'Internship Experience Rate',
                'Average IQ Score',
                'Average CGPA',
                'Average Academic Performance',
                'Average Communication Skills',
                'Average Projects Completed',
                'Most Important Factor for Placement',
                'Number of Statistically Significant Factors'
            ],
            'Value': [
                additional_stats['Total_Students'],
                f"{additional_stats['Placement_Rate']:.1f}%",
                f"{additional_stats['Internship_Rate']:.1f}%",
                f"{additional_stats['IQ_Mean']:.1f}",
                f"{additional_stats['CGPA_Mean']:.2f}",
                f"{additional_stats['Academic_Performance_Mean']:.1f}",
                f"{additional_stats['Communication_Skills_Mean']:.1f}",
                f"{additional_stats['Projects_Completed_Mean']:.1f}",
                correlation_matrix_excel['Placement'].sort_values(ascending=False).index[1],
                sum(1 for test in statistical_tests.values() if test['significant'])
            ]
        }
        insights_df = pd.DataFrame(insights_data)
        insights_df.to_excel(writer, sheet_name='Key_Insights', index=False)
        
        # 8. Top Factors Analysis
        placement_correlations_excel = correlation_matrix['Placement'].sort_values(ascending=False)
        top_factors_data = {
            'Factor': placement_correlations_excel.index[1:11],  # Exclude Placement itself
            'Correlation_with_Placement': placement_correlations_excel.values[1:11],
            'Significance': [statistical_tests[factor]['significant'] for factor in placement_correlations_excel.index[1:11]]
        }
        top_factors_df = pd.DataFrame(top_factors_data)
        top_factors_df.to_excel(writer, sheet_name='Top_Factors', index=False)
    
    return "Excel report saved as 'college_student_analysis_results.xlsx'"

def main():
    """Main function to run the complete analysis"""
    print("=" * 60)
    print("COLLEGE STUDENT ANALYSIS")
    print("=" * 60)
    
    # Load and clean data
    df = load_and_clean_data('College Student Analysis.csv')
    
    # Generate descriptive statistics
    stats_summary, additional_stats = generate_descriptive_statistics(df)
    
    # Perform correlation analysis
    correlation_matrix, placement_correlations = perform_correlation_analysis(df)
    
    # Analyze placement factors
    placement_analysis = analyze_placement_factors(df)
    
    # Perform statistical tests
    statistical_tests = perform_statistical_tests(df)
    
    # Create visualizations
    viz_result = create_visualizations(df)
    print(f"✓ {viz_result}")
    
    # Generate PlantUML diagram
    puml_result = generate_plantuml_diagram(df, stats_summary, placement_analysis, statistical_tests)
    print(f"✓ {puml_result}")
    
    # Create Excel report
    excel_result = create_excel_report(df, stats_summary, placement_analysis, statistical_tests, additional_stats)
    print(f"✓ {excel_result}")
    
    # Print key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"• Total Students Analyzed: {additional_stats['Total_Students']}")
    print(f"• Placement Rate: {additional_stats['Placement_Rate']:.1f}%")
    print(f"• Internship Experience Rate: {additional_stats['Internship_Rate']:.1f}%")
    print(f"• Average IQ Score: {additional_stats['IQ_Mean']:.1f}")
    print(f"• Average CGPA: {additional_stats['CGPA_Mean']:.2f}")
    print(f"• Most Important Factor for Placement: {correlation_matrix['Placement'].sort_values(ascending=False).index[1]}")
    print(f"• Statistically Significant Factors: {sum(1 for test in statistical_tests.values() if test['significant'])}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE!")
    print("=" * 60)
    print("Generated files:")
    print("1. college_student_analysis.puml - PlantUML diagram")
    print("2. college_student_analysis_results.xlsx - Excel report")
    print("3. college_student_analysis_visualizations.png - Visualizations")

if __name__ == "__main__":
    main()
