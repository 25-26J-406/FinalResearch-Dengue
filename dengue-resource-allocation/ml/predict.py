"""
Prediction Module
Handles risk prediction and resource recommendations for districts
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, List, Tuple


class DenguePredictionSystem:
    """Complete prediction system for dengue risk and resource allocation"""
    
    def __init__(self, risk_model_path: str, resource_model_path: str):
        """Initialize prediction system with trained models"""
        self.risk_model_data = self._load_model(risk_model_path)
        self.resource_model_data = self._load_model(resource_model_path)
        
        self.risk_model = self.risk_model_data['model']
        self.resource_model = self.resource_model_data['model']
        
        self.risk_features = self.risk_model_data['feature_names']
        self.resource_features = self.resource_model_data['feature_names']
        self.label_mapping = self.risk_model_data['label_mapping']
        self.resource_columns = self.resource_model_data['resource_columns']
    
    def _load_model(self, model_path: str) -> dict:
        """Load a trained model from disk"""
        try:
            return joblib.load(model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {model_path}: {e}")
    
    def predict_risk(self, district_data: pd.DataFrame) -> pd.DataFrame:
        """Predict risk levels for all districts"""
        print("Predicting risk levels for districts...")
        
        # Prepare features
        X = self._prepare_features(district_data, self.risk_features)
        
        # Ensure no NaN values
        if np.isnan(X).any():
            print("Warning: Found NaN in risk features, filling with 0")
            X = np.nan_to_num(X, nan=0.0)
        
        # Make predictions
        risk_predictions = self.risk_model.predict(X)
        risk_probabilities = self.risk_model.predict_proba(X)
        
        # Convert to risk labels
        risk_labels = [self.label_mapping[pred] for pred in risk_predictions]
        
        # Create results DataFrame
        results = pd.DataFrame({
            'District': district_data['District'].values,
            'Risk_Level': risk_labels,
            'Risk_Score': risk_predictions,
            'Low_Probability': risk_probabilities[:, 0],
            'Medium_Probability': risk_probabilities[:, 1],
            'High_Probability': risk_probabilities[:, 2]
        })
        
        print(f"Risk predictions completed for {len(results)} districts")
        print(f"Risk distribution: {results['Risk_Level'].value_counts().to_dict()}")
        
        return results
    
    def identify_hotspots(self, risk_predictions: pd.DataFrame) -> pd.DataFrame:
        """Mark High-risk districts as hotspots"""
        print("\nIdentifying dengue hotspots...")
        
        hotspots = risk_predictions.copy()
        hotspots['Is_Hotspot'] = hotspots['Risk_Level'] == 'High'
        hotspots['Hotspot_Priority'] = hotspots['High_Probability']
        hotspots = hotspots.sort_values('Hotspot_Priority', ascending=False)
        
        num_hotspots = hotspots['Is_Hotspot'].sum()
        print(f"Identified {num_hotspots} hotspot districts")
        
        if num_hotspots > 0:
            print("\nHotspot districts:")
            hotspot_list = hotspots[hotspots['Is_Hotspot']]['District'].tolist()
            for i, district in enumerate(hotspot_list, 1):
                print(f"  {i}. {district}")
        
        return hotspots
    
    def recommend_resources(self, district_data: pd.DataFrame) -> pd.DataFrame:
        """Predict resource recommendations for districts"""
        print("\nGenerating resource recommendations...")
        
        # Get available features
        available_features = [f for f in self.resource_features if f in district_data.columns]
        
        if len(available_features) < len(self.resource_features):
            missing = set(self.resource_features) - set(available_features)
            print(f"Warning: Missing features: {missing}")
        
        # Prepare features
        X = district_data[available_features].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        
        # Fill NaN
        for col in X.columns:
            if X[col].isna().any():
                mean_val = X[col].mean()
                X[col].fillna(mean_val if not pd.isna(mean_val) else 0, inplace=True)
        
        # Apply imputer if available
        if 'imputer' in self.resource_model_data and self.resource_model_data['imputer'] is not None:
            try:
                X_array = self.resource_model_data['imputer'].transform(X)
            except:
                X_array = X.values
        else:
            X_array = X.values
        
        # Make predictions
        resource_predictions = self.resource_model.predict(X_array)
        resource_predictions = np.round(resource_predictions).astype(int)
        resource_predictions = np.maximum(resource_predictions, 1)
        
        # Create results
        results = pd.DataFrame(resource_predictions, columns=self.resource_columns)
        results.insert(0, 'District', district_data['District'].values)
        
        print(f"Resource recommendations generated for {len(results)} districts")
        print("\nTotal resources recommended:")
        for col in self.resource_columns:
            print(f"  {col}: {results[col].sum()}")
        
        return results
    
    def _prepare_features(self, df: pd.DataFrame, feature_names: List[str]) -> np.ndarray:
        """Prepare features for prediction"""
        available_features = [f for f in feature_names if f in df.columns]
        X = df[available_features].copy()
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.mean()).fillna(0)
        return X.values
    
    def generate_complete_predictions(self, district_data: pd.DataFrame) -> Dict:
        """Generate complete predictions: risk levels, hotspots, and resources"""
        print("="*60)
        print("Generating Complete Predictions")
        print("="*60)
        
        risk_predictions = self.predict_risk(district_data)
        hotspot_data = self.identify_hotspots(risk_predictions)
        resource_recommendations = self.recommend_resources(district_data)
        
        complete_results = hotspot_data.merge(resource_recommendations, on='District', how='left')
        
        summary = {
            'total_districts': len(complete_results),
            'high_risk_count': (complete_results['Risk_Level'] == 'High').sum(),
            'medium_risk_count': (complete_results['Risk_Level'] == 'Medium').sum(),
            'low_risk_count': (complete_results['Risk_Level'] == 'Low').sum(),
            'hotspot_count': complete_results['Is_Hotspot'].sum(),
            'total_fogging_units': complete_results['Fogging_Units'].sum(),
            'total_inspectors': complete_results['Health_Inspectors'].sum(),
            'total_teams': complete_results['Inspection_Teams'].sum(),
            'total_treatment_units': complete_results['Treatment_Units'].sum()
        }
        
        print("\n" + "="*60)
        print("Prediction Summary")
        print("="*60)
        print(f"Total Districts: {summary['total_districts']}")
        print(f"High Risk: {summary['high_risk_count']}")
        print(f"Medium Risk: {summary['medium_risk_count']}")
        print(f"Low Risk: {summary['low_risk_count']}")
        print(f"Hotspots: {summary['hotspot_count']}")
        print(f"\nTotal Resources Needed:")
        print(f"  Fogging Units: {summary['total_fogging_units']}")
        print(f"  Health Inspectors: {summary['total_inspectors']}")
        print(f"  Inspection Teams: {summary['total_teams']}")
        print(f"  Treatment Units: {summary['total_treatment_units']}")
        
        return {
            'predictions': complete_results,
            'summary': summary,
            'hotspots': complete_results[complete_results['Is_Hotspot']].to_dict('records'),
            'high_risk_districts': complete_results[complete_results['Risk_Level'] == 'High'].to_dict('records')
        }


def predict_for_latest_data(processed_data_path: str, risk_model_path: str, resource_model_path: str) -> Dict:
    """Generate predictions for latest district data"""
    df = pd.read_csv(processed_data_path)
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-01')
    latest_data = df.sort_values('Date').groupby('District').tail(1).reset_index(drop=True)
    
    predictor = DenguePredictionSystem(risk_model_path, resource_model_path)
    results = predictor.generate_complete_predictions(latest_data)
    
    return results


if __name__ == "__main__":
    results = predict_for_latest_data(
        processed_data_path='data/processed_data.csv',
        risk_model_path='models/risk_model.pkl',
        resource_model_path='models/resource_model.pkl'
    )
    
    print("\n" + "="*60)
    print("Sample Predictions")
    print("="*60)
    print(results['predictions'].head(10))
    
    if results['hotspots']:
        print("\n" + "="*60)
        print("Hotspot Districts (Detailed)")
        print("="*60)
        hotspots_df = pd.DataFrame(results['hotspots'])
        print(hotspots_df[['District', 'Risk_Level', 'High_Probability', 
                           'Fogging_Units', 'Health_Inspectors']].to_string(index=False))