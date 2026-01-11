"""
Data Preparation Module
Handles loading, cleaning, merging, and preprocessing of dengue and population data
"""

import pandas as pd
import numpy as np
from pathlib import Path


class DataPreprocessor:
    """Handles all data preparation tasks"""
    
    def __init__(self, dengue_path: str, population_path: str):
        self.dengue_path = dengue_path
        self.population_path = population_path
        self.dengue_df = None
        self.population_df = None
        self.merged_df = None
        
    def load_dengue_data(self) -> pd.DataFrame:
        """Task 1: Load dengue CSV dataset"""
        print("Loading dengue dataset...")
        self.dengue_df = pd.read_csv(self.dengue_path)
        print(f"Loaded {len(self.dengue_df)} dengue records")
        return self.dengue_df
    
    def load_population_data(self) -> pd.DataFrame:
        """Task 2: Load population census CSV dataset"""
        print("Loading population census dataset...")
        self.population_df = pd.read_csv(self.population_path)
        print(f"Loaded population data for {len(self.population_df)} districts")
        return self.population_df
    
    def convert_population_to_long_format(self) -> pd.DataFrame:
        """Task 3: Convert population data to long format"""
        print("Converting population data to long format...")
        
        # Melt the dataframe to convert year columns to rows
        year_columns = [col for col in self.population_df.columns if col != 'District']
        
        population_long = pd.melt(
            self.population_df,
            id_vars=['District'],
            value_vars=year_columns,
            var_name='Year',
            value_name='Population_thousands'
        )
        
        # Convert Year to integer
        population_long['Year'] = population_long['Year'].astype(int)
        
        self.population_df = population_long
        print(f"Converted to {len(population_long)} district-year records")
        return population_long
    
    def convert_population_values(self) -> pd.DataFrame:
        """Task 4: Convert population values from thousands to actual numbers"""
        print("Converting population from thousands to actual values...")
        
        # Multiply by 1000 to get actual population
        self.population_df['Population'] = self.population_df['Population_thousands'] * 1000
        
        # Drop the thousands column
        self.population_df = self.population_df.drop('Population_thousands', axis=1)
        
        print("Population values converted to actual numbers")
        return self.population_df
    
    def interpolate_population(self) -> pd.DataFrame:
        """Task 5: Interpolate population for missing years"""
        print("Interpolating population for missing years...")
        
        # Get unique districts
        districts = self.population_df['District'].unique()
        
        # Get min and max years from dengue data
        min_year = self.dengue_df['Year'].min()
        max_year = self.dengue_df['Year'].max()
        
        interpolated_dfs = []
        
        for district in districts:
            # Filter for current district
            district_pop = self.population_df[
                self.population_df['District'] == district
            ].sort_values('Year')
            
            # Create full year range
            all_years = pd.DataFrame({
                'Year': range(min_year, max_year + 1)
            })
            
            # Merge with existing data
            district_full = all_years.merge(district_pop, on='Year', how='left')
            district_full['District'] = district
            
            # Interpolate missing population values
            district_full['Population'] = district_full['Population'].interpolate(
                method='linear'
            )
            
            # Forward fill for any remaining NaN at the edges
            district_full['Population'] = district_full['Population'].ffill().bfill()
            
            interpolated_dfs.append(district_full)
        
        self.population_df = pd.concat(interpolated_dfs, ignore_index=True)
        print(f"Interpolated population data: {len(self.population_df)} records")
        return self.population_df
    
    def merge_datasets(self) -> pd.DataFrame:
        """Task 6: Merge dengue data with population data by district and year"""
        print("Merging dengue and population datasets...")
        
        # First, ensure population data has all years needed
        min_year = self.dengue_df['Year'].min()
        max_year = self.dengue_df['Year'].max()
        
        # Filter population data to only include years in dengue data range
        self.population_df = self.population_df[
            (self.population_df['Year'] >= min_year) & 
            (self.population_df['Year'] <= max_year)
        ]
        
        # Merge on District and Year
        self.merged_df = self.dengue_df.merge(
            self.population_df[['District', 'Year', 'Population']],
            on=['District', 'Year'],
            how='left'
        )
        
        print(f"Merged dataset contains {len(self.merged_df)} records")
        
        # Check for missing population values
        missing = self.merged_df['Population'].isna().sum()
        if missing > 0:
            print(f"Warning: {missing} records have missing population data")
            print("Districts with missing population:")
            missing_districts = self.merged_df[self.merged_df['Population'].isna()]['District'].unique()
            for district in missing_districts[:5]:  # Show first 5
                print(f"  - {district}")
            
            # Fill missing population with median by district
            print("Filling missing population values with district median...")
            self.merged_df['Population'] = self.merged_df.groupby('District')['Population'].transform(
                lambda x: x.fillna(x.median())
            )
            
            # If still NaN (district has no population data), use overall median
            remaining_missing = self.merged_df['Population'].isna().sum()
            if remaining_missing > 0:
                overall_median = self.merged_df['Population'].median()
                self.merged_df['Population'].fillna(overall_median, inplace=True)
                print(f"Filled {remaining_missing} remaining NaN values with overall median: {overall_median:.0f}")
        
        return self.merged_df
    
    def sort_data(self) -> pd.DataFrame:
        """Task 7: Sort data by district and date"""
        print("Sorting data by district and date...")
        
        # Create a date column for better sorting
        self.merged_df['Date'] = pd.to_datetime(
            self.merged_df['Year'].astype(str) + '-' + 
            self.merged_df['Month'].astype(str).str.zfill(2) + '-01'
        )
        
        # Sort by District and Date
        self.merged_df = self.merged_df.sort_values(
            ['District', 'Date']
        ).reset_index(drop=True)
        
        print("Data sorted successfully")
        return self.merged_df
    
    def compute_cases_per_capita(self) -> pd.DataFrame:
        """Task 8: Compute cases per 1000 population"""
        print("Computing cases per 1000 population...")
        
        # Calculate cases per 1000 population
        self.merged_df['Cases_per_1000'] = (
            self.merged_df['Cases'] / self.merged_df['Population']
        ) * 1000
        
        # Handle any division by zero or invalid values
        self.merged_df['Cases_per_1000'] = self.merged_df['Cases_per_1000'].fillna(0)
        
        print("Cases per capita computed")
        return self.merged_df
    
    def compute_growth_rate(self) -> pd.DataFrame:
        """Task 9: Compute month-to-month case growth rate"""
        print("Computing month-to-month case growth rate...")
        
        # Group by district and calculate growth rate
        def calculate_growth(group):
            # Shift to get previous month's cases
            group['Prev_Cases'] = group['Cases'].shift(1)
            
            # Calculate growth rate: (current - previous) / previous
            group['Case_Growth_Rate'] = (
                (group['Cases'] - group['Prev_Cases']) / group['Prev_Cases']
            )
            
            # Replace inf and -inf with 0
            group['Case_Growth_Rate'] = group['Case_Growth_Rate'].replace(
                [np.inf, -np.inf], 0
            )
            
            # Fill NaN (first month) with 0
            group['Case_Growth_Rate'] = group['Case_Growth_Rate'].fillna(0)
            
            return group
        
        self.merged_df = self.merged_df.groupby('District', group_keys=False).apply(
            calculate_growth
        )
        
        print("Growth rate computed")
        return self.merged_df
    
    def encode_month(self) -> pd.DataFrame:
        """Task 10: Encode month as numeric feature"""
        print("Encoding month as numeric feature...")
        
        # Month is already numeric, but let's ensure it's the right type
        self.merged_df['Month_encoded'] = self.merged_df['Month'].astype(int)
        
        # Also create cyclical features for better ML performance
        self.merged_df['Month_sin'] = np.sin(2 * np.pi * self.merged_df['Month'] / 12)
        self.merged_df['Month_cos'] = np.cos(2 * np.pi * self.merged_df['Month'] / 12)
        
        print("Month encoded successfully")
        return self.merged_df
    
    def run_full_pipeline(self, output_path: str = None) -> pd.DataFrame:
        """Execute all preprocessing tasks in sequence"""
        print("="*60)
        print("Starting Data Preprocessing Pipeline")
        print("="*60)
        
        # Execute all tasks
        self.load_dengue_data()
        self.load_population_data()
        self.convert_population_to_long_format()
        self.convert_population_values()
        self.interpolate_population()
        self.merge_datasets()
        self.sort_data()
        self.compute_cases_per_capita()
        self.compute_growth_rate()
        self.encode_month()
        
        # Save processed data if path provided
        if output_path:
            self.merged_df.to_csv(output_path, index=False)
            print(f"\nProcessed data saved to: {output_path}")
        
        print("="*60)
        print("Data Preprocessing Complete!")
        print("="*60)
        print(f"Final dataset shape: {self.merged_df.shape}")
        print(f"Columns: {list(self.merged_df.columns)}")
        
        return self.merged_df


if __name__ == "__main__":
    # Example usage
    preprocessor = DataPreprocessor(
        dengue_path='../data/dengue_data_with_weather_data.csv',
        population_path='../data/population_by_district_in_census_years.csv'
    )
    
    processed_df = preprocessor.run_full_pipeline(
        output_path='../data/processed_data.csv'
    )
    
    print("\nSample of processed data:")
    print(processed_df.head(10))