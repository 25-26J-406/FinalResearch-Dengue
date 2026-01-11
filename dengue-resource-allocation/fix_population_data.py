"""
Quick fix script to handle missing population data
"""

from pathlib import Path
import pandas as pd
import numpy as np

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_PATH = DATA_DIR / "processed_data.csv"

print("="*70)
print("FIXING POPULATION DATA")
print("="*70)

# Load processed data
print("\nLoading processed data...")
df = pd.read_csv(PROCESSED_DATA_PATH)
print(f"Loaded {len(df)} records")

# Check for missing population
missing = df['Population'].isna().sum()
print(f"Found {missing} records with missing population")

if missing > 0:
    print("\nFixing missing population values...")
    
    # Method 1: Fill with district median
    df['Population'] = df.groupby('District')['Population'].transform(
        lambda x: x.fillna(x.median())
    )
    
    # Method 2: Fill remaining with overall median
    remaining = df['Population'].isna().sum()
    if remaining > 0:
        overall_median = df['Population'].median()
        print(f"Filling {remaining} values with overall median: {overall_median:.0f}")
        df['Population'].fillna(overall_median, inplace=True)
    
    # Verify no more NaN
    final_missing = df['Population'].isna().sum()
    print(f"\n✓ After fix: {final_missing} missing values")
    
    # Recalculate Cases_per_1000
    print("\nRecalculating Cases_per_1000...")
    df['Cases_per_1000'] = (df['Cases'] / df['Population']) * 1000
    df['Cases_per_1000'] = df['Cases_per_1000'].replace([np.inf, -np.inf], 0).fillna(0)
    
    # Save fixed data
    df.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"\n✅ Fixed data saved to: {PROCESSED_DATA_PATH}")
    
    print("\n" + "="*70)
    print("Population Statistics:")
    print("="*70)
    print(df['Population'].describe())
    
else:
    print("\n✓ No missing population values found!")

print("\n" + "="*70)
print("✅ Data fix complete!")
print("="*70)
print("\nYou can now run: python train_all_models.py")