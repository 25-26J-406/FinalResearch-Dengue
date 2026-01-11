"""
Data Preparation Module - Windows Compatible
Handles loading, cleaning, merging, and preprocessing of dengue and population data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Get the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Add project root to Python path
sys.path.insert(0, str(PROJECT_ROOT))

from ml.preprocess import DataPreprocessor


if __name__ == "__main__":
    # Use absolute paths
    dengue_path = DATA_DIR / 'dengue_data_with_weather_data.csv'
    population_path = DATA_DIR / 'population_by_district_in_census_years.csv'
    output_path = DATA_DIR / 'processed_data.csv'
    
    # Check if files exist
    if not dengue_path.exists():
        print(f"❌ ERROR: Dengue data file not found!")
        print(f"Expected location: {dengue_path}")
        print(f"\nPlease ensure the file 'dengue_data_with_weather_data.csv' is in the data/ directory")
        sys.exit(1)
    
    if not population_path.exists():
        print(f"❌ ERROR: Population data file not found!")
        print(f"Expected location: {population_path}")
        print(f"\nPlease ensure the file 'population_by_district_in_census_years.csv' is in the data/ directory")
        sys.exit(1)
    
    print(f"✓ Found dengue data: {dengue_path.name}")
    print(f"✓ Found population data: {population_path.name}")
    print()
    
    # Create preprocessor with absolute paths
    preprocessor = DataPreprocessor(
        dengue_path=str(dengue_path),
        population_path=str(population_path)
    )
    
    # Run pipeline
    processed_df = preprocessor.run_full_pipeline(
        output_path=str(output_path)
    )
    
    print("\nSample of processed data:")
    print(processed_df.head(10))