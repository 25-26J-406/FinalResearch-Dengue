"""
Complete Model Training Script
Runs the entire ML pipeline from preprocessing to model training
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ml.preprocess import DataPreprocessor
from ml.train_risk_model import RiskModelTrainer
from ml.train_resource_model import ResourceModelTrainer
import pandas as pd


def main():
    """Execute complete ML training pipeline"""
    
    print("="*70)
    print(" DENGUE RESOURCE ALLOCATION - COMPLETE TRAINING PIPELINE")
    print("="*70)
    print()
    
    # File paths
    dengue_path = 'data/dengue_data_with_weather_data.csv'
    population_path = 'data/population_by_district_in_census_years.csv'
    processed_path = 'data/processed_data.csv'
    risk_model_path = 'models/risk_model.pkl'
    resource_model_path = 'models/resource_model.pkl'
    
    # Check if data files exist
    if not Path(dengue_path).exists():
        print(f"❌ ERROR: Dengue data file not found: {dengue_path}")
        print("   Please place dengue_data_with_weather_data.csv in the data/ directory")
        sys.exit(1)
    
    if not Path(population_path).exists():
        print(f"❌ ERROR: Population data file not found: {population_path}")
        print("   Please place population_by_district_in_census_years.csv in the data/ directory")
        sys.exit(1)
    
    # ========================================================================
    # PHASE 1: DATA PREPROCESSING
    # ========================================================================
    print()
    print("="*70)
    print(" PHASE 1: DATA PREPROCESSING")
    print("="*70)
    print()
    
    preprocessor = DataPreprocessor(dengue_path, population_path)
    processed_df = preprocessor.run_full_pipeline(output_path=processed_path)
    
    print()
    print("✅ Data preprocessing complete!")
    print(f"   Processed data saved to: {processed_path}")
    print(f"   Dataset shape: {processed_df.shape}")
    
    # ========================================================================
    # PHASE 2: RISK MODEL TRAINING
    # ========================================================================
    print()
    print("="*70)
    print(" PHASE 2: RISK CLASSIFICATION MODEL")
    print("="*70)
    print()
    
    # Define features for risk model
    risk_features = [
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
    
    risk_trainer = RiskModelTrainer(processed_df, risk_features)
    risk_model = risk_trainer.run_full_pipeline(risk_model_path)
    
    # Get the risk labels that were generated
    risk_labels = risk_trainer.risk_labels
    
    print()
    print("✅ Risk model training complete!")
    print(f"   Model saved to: {risk_model_path}")
    
    # ========================================================================
    # PHASE 3: RESOURCE MODEL TRAINING
    # ========================================================================
    print()
    print("="*70)
    print(" PHASE 3: RESOURCE RECOMMENDATION MODEL")
    print("="*70)
    print()
    
    # Define features for resource model
    resource_features = [
        'Cases',
        'Cases_per_1000',
        'Case_Growth_Rate',
        'Temp_avg',
        'Precipitation_avg',
        'Humidity_avg',
        'Population',
        'Month_encoded',
        'Month_sin',
        'Month_cos'
    ]
    
    # Use risk labels from risk model trainer
    resource_trainer = ResourceModelTrainer(
        processed_df, 
        resource_features,
        risk_labels=risk_labels
    )
    resource_model = resource_trainer.run_full_pipeline(resource_model_path)
    
    print()
    print("✅ Resource model training complete!")
    print(f"   Model saved to: {resource_model_path}")
    
    # ========================================================================
    # PHASE 4: VALIDATION
    # ========================================================================
    print()
    print("="*70)
    print(" PHASE 4: VALIDATION")
    print("="*70)
    print()
    
    print("🔍 Validating trained models...")
    
    # Test loading models
    from ml.predict import DenguePredictionSystem
    
    try:
        predictor = DenguePredictionSystem(risk_model_path, resource_model_path)
        print("✅ Models loaded successfully")
        
        # Test prediction on a small sample
        sample_data = processed_df.groupby('District').tail(1).head(5)
        results = predictor.generate_complete_predictions(sample_data)
        
        print(f"✅ Predictions generated for {len(results['predictions'])} districts")
        print(f"✅ Identified {results['summary']['hotspot_count']} hotspots")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print()
    print("="*70)
    print(" TRAINING COMPLETE - SUMMARY")
    print("="*70)
    print()
    print("📁 Files created:")
    print(f"   ✓ {processed_path}")
    print(f"   ✓ {risk_model_path}")
    print(f"   ✓ {resource_model_path}")
    print()
    print("🎯 Models ready for deployment!")
    print()
    print("Next steps:")
    print("   1. Run predictions: python3 ml/predict.py")
    print("   2. Start API server: python3 -m uvicorn backend.main:app --reload")
    print("   3. Or use: ./run.sh")
    print()
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)