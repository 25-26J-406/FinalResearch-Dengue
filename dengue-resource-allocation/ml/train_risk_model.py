"""
Risk Prediction Model Training Module
Trains a classifier to predict dengue risk levels (Low/Medium/High)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
from pathlib import Path


class RiskModelTrainer:
    """Trains and evaluates risk classification model"""
    
    def __init__(self, df: pd.DataFrame, feature_names: list):
        self.df = df.copy()
        self.feature_names = feature_names
        self.model = None
        self.X = None
        self.y = None
        self.risk_labels = None
        
    def define_risk_labels(self) -> pd.Series:
        """
        Task 1: Define rule-based risk labels (Low/Medium/High)
        
        Risk classification based on:
        - Cases per 1000 population (incidence rate)
        - Absolute case count
        - Growth rate trend
        """
        print("Defining rule-based risk labels...")
        
        risk_labels = []
        
        for idx, row in self.df.iterrows():
            cases_per_1000 = row['Cases_per_1000']
            cases = row['Cases']
            growth_rate = row['Case_Growth_Rate']
            
            # Define thresholds
            HIGH_INCIDENCE_THRESHOLD = 0.5  # 0.5 cases per 1000 people
            MEDIUM_INCIDENCE_THRESHOLD = 0.2  # 0.2 cases per 1000 people
            HIGH_ABSOLUTE_THRESHOLD = 200  # 200 cases
            MEDIUM_ABSOLUTE_THRESHOLD = 50  # 50 cases
            HIGH_GROWTH_THRESHOLD = 0.5  # 50% growth
            
            # High Risk conditions
            if (cases_per_1000 >= HIGH_INCIDENCE_THRESHOLD or 
                cases >= HIGH_ABSOLUTE_THRESHOLD or 
                (cases_per_1000 >= MEDIUM_INCIDENCE_THRESHOLD and growth_rate >= HIGH_GROWTH_THRESHOLD)):
                risk_labels.append('High')
            
            # Medium Risk conditions
            elif (cases_per_1000 >= MEDIUM_INCIDENCE_THRESHOLD or 
                  cases >= MEDIUM_ABSOLUTE_THRESHOLD or
                  growth_rate >= HIGH_GROWTH_THRESHOLD):
                risk_labels.append('Medium')
            
            # Low Risk (everything else)
            else:
                risk_labels.append('Low')
        
        self.df['Risk_Level'] = risk_labels
        self.risk_labels = self.df['Risk_Level']
        
        # Print distribution
        print("Risk level distribution:")
        print(self.risk_labels.value_counts())
        print(f"\nPercentages:")
        print(self.risk_labels.value_counts(normalize=True) * 100)
        
        return self.risk_labels
    
    def encode_risk_labels(self) -> np.ndarray:
        """
        Task 2: Encode risk labels numerically
        Low = 0, Medium = 1, High = 2
        """
        print("\nEncoding risk labels numerically...")
        
        label_mapping = {
            'Low': 0,
            'Medium': 1,
            'High': 2
        }
        
        self.y = self.df['Risk_Level'].map(label_mapping).values
        
        print(f"Encoded {len(self.y)} labels")
        print(f"Label distribution: {np.bincount(self.y)}")
        
        return self.y
    
    def prepare_training_data(self) -> tuple:
        """Prepare X and y for training"""
        print("\nPreparing training data...")
        
        # Extract features
        self.X = self.df[self.feature_names].copy()
        
        # Handle missing and infinite values
        self.X = self.X.fillna(self.X.mean())
        self.X = self.X.replace([np.inf, -np.inf], 0)
        
        print(f"Feature matrix shape: {self.X.shape}")
        print(f"Features: {self.feature_names}")
        
        return self.X, self.y
    
    def train_risk_model(self, test_size: float = 0.2, random_state: int = 42) -> RandomForestClassifier:
        """
        Task 3: Train risk classification model
        Uses Random Forest Classifier for robust performance
        """
        print("\n" + "="*60)
        print("Training Risk Classification Model")
        print("="*60)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, 
            test_size=test_size, 
            random_state=random_state,
            stratify=self.y
        )
        
        print(f"Training set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Initialize model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            class_weight='balanced',  # Handle imbalanced classes
            n_jobs=-1
        )
        
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
        
        # Training accuracy
        train_pred = self.model.predict(X_train)
        train_acc = accuracy_score(y_train, train_pred)
        print(f"Training Accuracy: {train_acc:.4f}")
        
        # Test accuracy
        test_pred = self.model.predict(X_test)
        test_acc = accuracy_score(y_test, test_pred)
        print(f"Test Accuracy: {test_acc:.4f}")
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, self.X, self.y, cv=5)
        print(f"Cross-Validation Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        # Classification report
        label_names = ['Low', 'Medium', 'High']
        print("\nClassification Report (Test Set):")
        print(classification_report(y_test, test_pred, target_names=label_names))
        
        # Confusion matrix
        print("Confusion Matrix (Test Set):")
        cm = confusion_matrix(y_test, test_pred)
        print(cm)
        
        # Feature importance
        print("\nTop 10 Most Important Features:")
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(feature_importance.head(10).to_string(index=False))
    
    def save_model(self, model_path: str):
        """Task 4: Save trained risk model"""
        print(f"\nSaving model to {model_path}...")
        
        # Create directory if it doesn't exist
        Path(model_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model along with feature names and label mapping
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'label_mapping': {0: 'Low', 1: 'Medium', 2: 'High'}
        }
        
        joblib.dump(model_data, model_path)
        print(f"Model saved successfully!")
    
    def run_full_pipeline(self, model_path: str) -> RandomForestClassifier:
        """Execute complete risk model training pipeline"""
        print("="*60)
        print("Risk Model Training Pipeline")
        print("="*60)
        
        # Execute all tasks
        self.define_risk_labels()
        self.encode_risk_labels()
        self.prepare_training_data()
        self.train_risk_model()
        self.save_model(model_path)
        
        print("\n" + "="*60)
        print("Risk Model Training Complete!")
        print("="*60)
        
        return self.model


def load_risk_model(model_path: str) -> dict:
    """Load a trained risk model"""
    print(f"Loading risk model from {model_path}...")
    model_data = joblib.load(model_path)
    print("Model loaded successfully!")
    return model_data


if __name__ == "__main__":
    # Load processed data
    print("Loading processed data...")
    df = pd.read_csv('../data/processed_data.csv')
    
    # Define features to use
    feature_names = [
        'Cases',
        'Cases_per_1000',
        'Case_Growth_Rate',
        'Temp_avg',
        'Precipitation_avg',
        'Humidity_avg',
        'Month_encoded',
        'Month_sin',
        'Month_cos'
    ]
    
    # Create trainer
    trainer = RiskModelTrainer(df, feature_names)
    
    # Run full pipeline
    model = trainer.run_full_pipeline(
        model_path='../models/risk_model.pkl'
    )
    
    # Test loading
    print("\n" + "="*60)
    print("Testing Model Loading")
    print("="*60)
    loaded_model_data = load_risk_model('../models/risk_model.pkl')
    print(f"Features: {loaded_model_data['feature_names']}")
    print(f"Label mapping: {loaded_model_data['label_mapping']}")