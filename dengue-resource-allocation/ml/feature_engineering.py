"""
Feature Engineering Module
Selects and prepares features for machine learning models
"""

import pandas as pd
import numpy as np


class FeatureEngineer:
    """Handles feature selection and engineering for ML models"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.feature_matrix = None
        self.feature_names = []
        
    def select_epidemiological_features(self) -> list:
        """Task 1: Select epidemiological features"""
        print("Selecting epidemiological features...")
        
        epi_features = [
            'Cases',
            'Cases_per_1000',
            'Case_Growth_Rate'
        ]
        
        # Verify all features exist
        available = [f for f in epi_features if f in self.df.columns]
        
        print(f"Selected {len(available)} epidemiological features: {available}")
        return available
    
    def select_environmental_features(self) -> list:
        """Task 2: Select environmental features"""
        print("Selecting environmental features...")
        
        env_features = [
            'Temp_avg',
            'Precipitation_avg',
            'Humidity_avg'
        ]
        
        # Verify all features exist
        available = [f for f in env_features if f in self.df.columns]
        
        print(f"Selected {len(available)} environmental features: {available}")
        return available
    
    def select_population_normalized_features(self) -> list:
        """Task 3: Select population-normalized features"""
        print("Selecting population-normalized features...")
        
        pop_features = [
            'Cases_per_1000',
            'Population'
        ]
        
        # Verify all features exist
        available = [f for f in pop_features if f in self.df.columns]
        
        print(f"Selected {len(available)} population-normalized features: {available}")
        return available
    
    def create_temporal_features(self) -> list:
        """Create temporal features from month"""
        print("Creating temporal features...")
        
        temporal_features = [
            'Month_encoded',
            'Month_sin',
            'Month_cos'
        ]
        
        # Verify all features exist
        available = [f for f in temporal_features if f in self.df.columns]
        
        print(f"Created {len(available)} temporal features: {available}")
        return available
    
    def create_feature_matrix(self) -> pd.DataFrame:
        """Task 4: Create final feature matrix for ML"""
        print("\nCreating final feature matrix...")
        
        # Collect all feature groups
        epi_features = self.select_epidemiological_features()
        env_features = self.select_environmental_features()
        temporal_features = self.create_temporal_features()
        
        # Combine all features (avoid duplicates)
        all_features = []
        seen = set()
        
        for feature_list in [epi_features, env_features, temporal_features]:
            for feature in feature_list:
                if feature not in seen:
                    all_features.append(feature)
                    seen.add(feature)
        
        self.feature_names = all_features
        
        # Create feature matrix
        self.feature_matrix = self.df[all_features].copy()
        
        # Handle missing values
        self.feature_matrix = self.feature_matrix.fillna(self.feature_matrix.mean())
        
        # Handle any infinite values
        self.feature_matrix = self.feature_matrix.replace([np.inf, -np.inf], 0)
        
        print(f"Feature matrix created with shape: {self.feature_matrix.shape}")
        print(f"Features: {self.feature_names}")
        
        return self.feature_matrix
    
    def get_features_for_prediction(self, include_district_info: bool = True) -> pd.DataFrame:
        """Get feature matrix with district and date information for predictions"""
        features_df = self.feature_matrix.copy()
        
        if include_district_info:
            # Add district, year, month for identification
            info_cols = ['District', 'Year', 'Month']
            for col in info_cols:
                if col in self.df.columns:
                    features_df[col] = self.df[col].values
        
        return features_df
    
    def create_aggregated_features(self) -> pd.DataFrame:
        """Create district-level aggregated features for risk assessment"""
        print("\nCreating aggregated district features...")
        
        # Group by district and compute statistics
        agg_dict = {
            'Cases': ['mean', 'std', 'max'],
            'Cases_per_1000': ['mean', 'std', 'max'],
            'Case_Growth_Rate': ['mean', 'max'],
            'Temp_avg': 'mean',
            'Precipitation_avg': 'mean',
            'Humidity_avg': 'mean',
            'Population': 'mean'
        }
        
        district_features = self.df.groupby('District').agg(agg_dict)
        
        # Flatten column names
        district_features.columns = [
            f"{col[0]}_{col[1]}" if col[1] else col[0] 
            for col in district_features.columns
        ]
        
        district_features = district_features.reset_index()
        
        print(f"Aggregated features shape: {district_features.shape}")
        
        return district_features
    
    def get_latest_district_data(self) -> pd.DataFrame:
        """Get most recent data for each district for real-time predictions"""
        print("\nExtracting latest district data...")
        
        # Get the most recent record for each district
        latest_data = self.df.sort_values('Date').groupby('District').tail(1)
        
        # Select relevant columns
        cols_to_keep = ['District', 'Year', 'Month'] + self.feature_names
        cols_to_keep = [c for c in cols_to_keep if c in latest_data.columns]
        
        latest_district_data = latest_data[cols_to_keep].copy()
        
        print(f"Latest data extracted for {len(latest_district_data)} districts")
        
        return latest_district_data


def prepare_features_for_training(df: pd.DataFrame) -> tuple:
    """
    Convenience function to prepare features for model training
    
    Returns:
        tuple: (X, metadata_df) where X is the feature matrix and 
               metadata_df contains district/time info
    """
    engineer = FeatureEngineer(df)
    
    # Create feature matrix
    X = engineer.create_feature_matrix()
    
    # Get metadata
    metadata = df[['District', 'Year', 'Month', 'Date']].copy()
    
    return X, metadata, engineer.feature_names


def prepare_features_for_prediction(df: pd.DataFrame, feature_names: list) -> pd.DataFrame:
    """
    Prepare features for prediction using pre-defined feature names
    
    Args:
        df: DataFrame with raw data
        feature_names: List of feature names to extract
    
    Returns:
        DataFrame with features
    """
    # Ensure all required features exist
    available_features = [f for f in feature_names if f in df.columns]
    
    if len(available_features) != len(feature_names):
        missing = set(feature_names) - set(available_features)
        print(f"Warning: Missing features: {missing}")
    
    # Extract features
    X = df[available_features].copy()
    
    # Handle missing and infinite values
    X = X.fillna(X.mean())
    X = X.replace([np.inf, -np.inf], 0)
    
    return X


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.append('..')
    
    # Load processed data
    df = pd.read_csv('../data/processed_data.csv')
    
    # Create feature engineer
    engineer = FeatureEngineer(df)
    
    # Create feature matrix
    X = engineer.create_feature_matrix()
    
    print("\n" + "="*60)
    print("Feature Engineering Complete!")
    print("="*60)
    print(f"Feature matrix shape: {X.shape}")
    print(f"\nFeature names:")
    for i, name in enumerate(engineer.feature_names, 1):
        print(f"  {i}. {name}")
    
    # Show sample
    print("\nSample features:")
    print(X.head())
    
    # Create aggregated features
    district_agg = engineer.create_aggregated_features()
    print("\nAggregated district features:")
    print(district_agg.head())
    
    # Get latest data
    latest = engineer.get_latest_district_data()
    print("\nLatest district data:")
    print(latest.head())