"""
Resource Recommendation Model Training Module
Trains regression models to recommend optimal resource allocation
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.impute import SimpleImputer
import joblib
from pathlib import Path


class ResourceModelTrainer:
    """Trains model to recommend dengue control resources"""
    
    def __init__(self, df: pd.DataFrame, feature_names: list, risk_labels: pd.Series = None):
        self.df = df.copy()
        self.feature_names = feature_names
        self.risk_labels = risk_labels
        self.model = None
        self.imputer = None
        self.X = None
        self.y = None
        self.resource_columns = []
        
    def define_resource_variables(self) -> list:
        """Task 1: Define resource output variables"""
        print("Defining resource output variables...")
        
        self.resource_columns = [
            'Fogging_Units',
            'Health_Inspectors',
            'Inspection_Teams',
            'Treatment_Units'
        ]
        
        print(f"Resource variables: {self.resource_columns}")
        return self.resource_columns
    
    def generate_synthetic_targets(self) -> pd.DataFrame:
        """Task 2: Generate synthetic training targets for resources"""
        print("\nGenerating synthetic training targets...")
        
        resources = []
        
        for idx, row in self.df.iterrows():
            # Handle NaN values with safe defaults
            population = row.get('Population', 100000)
            if pd.isna(population):
                population = 100000
            
            cases = row.get('Cases', 0)
            if pd.isna(cases):
                cases = 0
                
            cases_per_1000 = row.get('Cases_per_1000', 0)
            if pd.isna(cases_per_1000):
                cases_per_1000 = 0
                
            growth_rate = row.get('Case_Growth_Rate', 0)
            if pd.isna(growth_rate):
                growth_rate = 0
            
            # Get risk level if available
            if self.risk_labels is not None and idx < len(self.risk_labels):
                risk = self.risk_labels.iloc[idx]
            else:
                # Estimate risk from cases per 1000
                if cases_per_1000 >= 0.5:
                    risk = 'High'
                elif cases_per_1000 >= 0.2:
                    risk = 'Medium'
                else:
                    risk = 'Low'
            
            # Base allocation factors
            risk_multiplier = {'Low': 1.0, 'Medium': 1.5, 'High': 2.5}.get(risk, 1.0)
            pop_factor = population / 100000
            case_factor = max(1, cases / 10)
            growth_factor = 1 + max(0, growth_rate)
            
            # Calculate resource needs
            fogging = max(1, int((2 * pop_factor + case_factor * 0.5) * risk_multiplier * growth_factor))
            fogging = min(fogging, 20)
            
            inspectors = max(1, int((1 + pop_factor * 0.5) * risk_multiplier))
            inspectors = min(inspectors, 15)
            
            teams = max(1, int((1 + case_factor * 0.3) * risk_multiplier * growth_factor))
            teams = min(teams, 10)
            
            treatment = max(1, int((case_factor * 0.5 + 1) * risk_multiplier))
            treatment = min(treatment, 25)
            
            # Add variation
            noise_factor = np.random.uniform(0.9, 1.1)
            
            resources.append({
                'Fogging_Units': max(1, int(fogging * noise_factor)),
                'Health_Inspectors': max(1, int(inspectors * noise_factor)),
                'Inspection_Teams': max(1, int(teams * noise_factor)),
                'Treatment_Units': max(1, int(treatment * noise_factor))
            })
        
        resources_df = pd.DataFrame(resources)
        
        for col in self.resource_columns:
            self.df[col] = resources_df[col]
        
        print("Synthetic targets generated:")
        print(resources_df.describe())
        
        return resources_df
    
    def prepare_training_data(self) -> tuple:
        """Prepare X and y for training with NaN handling"""
        print("\nPreparing training data...")
        
        # Extract features
        self.X = self.df[self.feature_names].copy()
        
        # Handle NaN and infinite values in features
        self.X = self.X.replace([np.inf, -np.inf], np.nan)
        
        # Create and fit imputer with add_indicator to handle columns with all NaN
        self.imputer = SimpleImputer(strategy='median', add_indicator=False)
        X_imputed = self.imputer.fit_transform(self.X)
        
        # Get feature names that were kept (some might be dropped if all NaN)
        feature_mask = np.std(X_imputed, axis=0) != 0  # Features with variation
        kept_features = [feat for i, feat in enumerate(self.feature_names) 
                        if i < X_imputed.shape[1]]
        
        self.X = pd.DataFrame(
            X_imputed,
            columns=kept_features,
            index=self.X.index
        )
        
        # Update feature names to only kept features
        self.feature_names = kept_features
        
        # Verify no NaN remaining
        if self.X.isna().any().any():
            print("Warning: Still have NaN values, filling with 0")
            self.X = self.X.fillna(0)
        
        # Targets
        self.y = self.df[self.resource_columns].values
        
        print(f"Feature matrix shape: {self.X.shape}")
        print(f"Target matrix shape: {self.y.shape}")
        print(f"Features used: {self.feature_names}")
        
        return self.X, self.y
    
    def train_resource_model(self, test_size: float = 0.2, random_state: int = 42) -> MultiOutputRegressor:
        """Task 3: Train resource recommendation regression model"""
        print("\n" + "="*60)
        print("Training Resource Recommendation Model")
        print("="*60)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y,
            test_size=test_size,
            random_state=random_state
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Initialize model
        base_estimator = RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model = MultiOutputRegressor(base_estimator)
        
        # Train model
        print("\nTraining model...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        print("\nModel Training Complete!")
        self._evaluate_model(X_train, y_train, X_test, y_test)
        
        return self.model
    
    def _evaluate_model(self, X_train, y_train, X_test, y_test):
        """Evaluate model performance"""
        print("\n" + "="*60)
        print("Model Evaluation")
        print("="*60)
        
        # Predictions
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        # Overall metrics
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        print(f"Training MAE: {train_mae:.2f}")
        print(f"Test MAE: {test_mae:.2f}")
        print(f"Training R²: {train_r2:.4f}")
        print(f"Test R²: {test_r2:.4f}")
        
        # Per-resource metrics
        print("\nPer-Resource Performance (Test Set):")
        print("-" * 60)
        
        for i, resource_name in enumerate(self.resource_columns):
            mae = mean_absolute_error(y_test[:, i], test_pred[:, i])
            r2 = r2_score(y_test[:, i], test_pred[:, i])
            
            print(f"{resource_name:20s} | MAE: {mae:6.2f} | R²: {r2:6.4f}")
        
        # Feature importance
        print("\nTop 10 Most Important Features (Fogging Units):")
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.estimators_[0].feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(feature_importance.head(10).to_string(index=False))
    
    def save_model(self, model_path: str):
        """Task 4: Save trained resource model"""
        print(f"\nSaving model to {model_path}...")
        
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'imputer': self.imputer,
            'feature_names': self.feature_names,
            'resource_columns': self.resource_columns
        }
        
        joblib.dump(model_data, model_path)
        print("Model saved successfully!")
    
    def run_full_pipeline(self, model_path: str) -> MultiOutputRegressor:
        """Execute complete resource model training pipeline"""
        print("="*60)
        print("Resource Model Training Pipeline")
        print("="*60)
        
        self.define_resource_variables()
        self.generate_synthetic_targets()
        self.prepare_training_data()
        self.train_resource_model()
        self.save_model(model_path)
        
        print("\n" + "="*60)
        print("Resource Model Training Complete!")
        print("="*60)
        
        return self.model


def load_resource_model(model_path: str) -> dict:
    """Load a trained resource model"""
    print(f"Loading resource model from {model_path}...")
    model_data = joblib.load(model_path)
    print("Model loaded successfully!")
    return model_data


if __name__ == "__main__":
    df = pd.read_csv('../data/processed_data.csv')
    
    feature_names = [
        'Cases', 'Cases_per_1000', 'Case_Growth_Rate',
        'Temp_avg', 'Precipitation_avg', 'Humidity_avg',
        'Population', 'Month_encoded', 'Month_sin', 'Month_cos'
    ]
    
    trainer = ResourceModelTrainer(df, feature_names, None)
    model = trainer.run_full_pipeline('../models/resource_model.pkl')