# Dengue Resource Allocation & Hotspot Recommendation System

A comprehensive machine learning-powered system for dengue risk prediction, hotspot identification, and optimal resource allocation at the district level.

## 📋 Overview

This system uses dengue surveillance data and environmental factors to:
- **Classify districts** into Low, Medium, or High dengue risk categories
- **Identify hotspots** (high-risk districts requiring immediate attention)
- **Recommend optimal resources** (fogging units, inspectors, teams, treatment units)
- **Manage resource allocation** through a RESTful API

## 🏗️ Architecture

```
Data Collection → Preprocessing → Feature Engineering → ML Models → Predictions → API
                                                       ↓
                                                  Risk Model
                                                  Resource Model
                                                       ↓
                                              JSON Storage → REST API
```

## 📁 Project Structure

```
dengue-resource-allocation/
│
├── data/                                    # Data directory
│   ├── dengue_data_with_weather_data.csv   # Input: Dengue cases + weather
│   ├── population_by_district_in_census_years.csv  # Input: Population data
│   ├── processed_data.csv                  # Output: Processed dataset
│   └── storage.json                        # Output: Persistent storage
│
├── models/                                  # Trained ML models
│   ├── risk_model.pkl                      # Risk classification model
│   └── resource_model.pkl                  # Resource recommendation model
│
├── ml/                                      # Machine learning modules
│   ├── preprocess.py                       # Data preprocessing pipeline
│   ├── feature_engineering.py              # Feature selection & engineering
│   ├── train_risk_model.py                 # Risk model training
│   ├── train_resource_model.py             # Resource model training
│   └── predict.py                          # Prediction system
│
├── backend/                                 # FastAPI backend
│   ├── main.py                             # API entry point
│   ├── config.py                           # Configuration
│   ├── json_store.py                       # JSON storage manager
│   ├── schemas.py                          # Pydantic models
│   ├── utils.py                            # Helper functions
│   └── routes/                             # API routes
│       ├── resources.py                    # Resource CRUD endpoints
│       ├── predictions.py                  # Prediction endpoints
│       └── admin.py                        # Admin dashboard endpoints
│
├── requirements.txt                         # Python dependencies
├── README.md                               # This file
└── run.sh                                  # Master execution script
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Your datasets in CSV format

### Installation & Setup

1. **Clone or download this repository**

2. **Place your datasets** in the `data/` directory:
   - `dengue_data_with_weather_data.csv`
   - `population_by_district_in_census_years.csv`

3. **Make the run script executable**:
   ```bash
   chmod +x run.sh
   ```

4. **Run the complete system**:
   ```bash
   ./run.sh
   ```

The script will:
- Create a virtual environment
- Install dependencies
- Preprocess data
- Train ML models (if not already trained)
- Generate predictions
- Start the API server

### Manual Setup (Alternative)

If you prefer manual control:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run data preprocessing
python3 ml/preprocess.py

# 4. Train models
python3 ml/train_risk_model.py
python3 ml/train_resource_model.py

# 5. Generate predictions
python3 ml/predict.py

# 6. Start API server
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 Data Requirements

### Dengue Data CSV
Required columns:
- `Year`, `Month`, `District`
- `Cases` (number of dengue cases)
- `Temp_avg`, `Precipitation_avg`, `Humidity_avg` (environmental factors)
- `Latitude`, `Longitude`, `Elevation` (optional, for geographical context)

### Population Data CSV
Required format:
- First column: `District`
- Subsequent columns: Census years (e.g., `1981`, `2001`, `2012`)
- Values: Population in thousands

## 🎯 Machine Learning Models

### Risk Classification Model
- **Algorithm**: Random Forest Classifier
- **Classes**: Low, Medium, High risk
- **Features**: 
  - Cases per 1000 population
  - Case growth rate
  - Temperature, precipitation, humidity
  - Temporal features (month encoding)
- **Output**: Risk level + confidence probabilities

### Resource Recommendation Model
- **Algorithm**: Multi-Output Random Forest Regressor
- **Outputs**: 
  - Fogging Units
  - Health Inspectors
  - Inspection Teams
  - Treatment Units
- **Logic**: Based on population, risk level, and epidemiological indicators

## 🌐 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

#### Resource Management
```bash
# Get available resources
GET /resources/

# Update resources
POST /resources/
Body: {"Fogging_Units": 100, "Health_Inspectors": 50, ...}

# Assign resources to district
POST /resources/assign
Body: {"district": "Colombo", "Fogging_Units": 10, ...}

# Get assignments
GET /resources/assignments?district=Colombo
```

#### Predictions
```bash
# Generate new predictions
POST /predictions/generate

# Get all district predictions
GET /predictions/districts

# Get hotspots
GET /predictions/hotspots

# Get resource recommendations
GET /predictions/recommendations
```

#### Admin Dashboard
```bash
# Get complete overview
GET /admin/overview

# Get statistics
GET /admin/statistics

# Analyze resource gap
GET /admin/resource-gap

# Compare districts
GET /admin/district-comparison
```

## 📈 Example Usage

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Generate predictions
response = requests.post(f"{BASE_URL}/predictions/generate")
print(response.json())

# 2. Get hotspots
response = requests.get(f"{BASE_URL}/predictions/hotspots")
hotspots = response.json()['hotspots']
print(f"Found {len(hotspots)} hotspots")

# 3. Set available resources
resources = {
    "Fogging_Units": 100,
    "Health_Inspectors": 50,
    "Inspection_Teams": 30,
    "Treatment_Units": 80
}
response = requests.post(f"{BASE_URL}/resources/", json=resources)

# 4. Assign resources to a hotspot
assignment = {
    "district": "Colombo",
    "Fogging_Units": 15,
    "Health_Inspectors": 8,
    "Inspection_Teams": 5,
    "Treatment_Units": 12
}
response = requests.post(f"{BASE_URL}/resources/assign", json=assignment)
print(response.json())

# 5. Get admin overview
response = requests.get(f"{BASE_URL}/admin/overview")
overview = response.json()
print(f"High risk districts: {overview['summary']['high_risk_count']}")
```

### cURL Examples

```bash
# Generate predictions
curl -X POST http://localhost:8000/predictions/generate

# Get hotspots
curl http://localhost:8000/predictions/hotspots

# Assign resources
curl -X POST http://localhost:8000/resources/assign \
  -H "Content-Type: application/json" \
  -d '{"district": "Colombo", "Fogging_Units": 10, "Health_Inspectors": 5}'
```

## 🔧 Configuration

Edit `backend/config.py` to customize:
- File paths
- Default resource quantities
- Risk level thresholds
- API settings (host, port, CORS)

## 📊 Storage System

All data is stored in `data/storage.json`:
- **Available resources**: Current inventory
- **District predictions**: Latest risk assessments
- **Hotspots**: High-risk districts
- **Recommendations**: ML-generated resource needs
- **Assignments**: Resource allocation history

The JSON store is thread-safe and persists all changes immediately.

## 🧪 Testing

Test individual components:

```bash
# Test preprocessing
python3 ml/preprocess.py

# Test feature engineering
python3 ml/feature_engineering.py

# Test models
python3 ml/train_risk_model.py
python3 ml/train_resource_model.py

# Test predictions
python3 ml/predict.py

# Test JSON store
python3 backend/json_store.py

# Test utilities
python3 backend/utils.py
```

## 📝 Implementation Checklist

### Data Preparation ✅
- [x] Load dengue dataset
- [x] Load population dataset
- [x] Convert population to long format
- [x] Convert population from thousands
- [x] Interpolate missing years
- [x] Merge datasets
- [x] Sort by district and date
- [x] Compute cases per capita
- [x] Compute growth rate
- [x] Encode temporal features

### Feature Engineering ✅
- [x] Select epidemiological features
- [x] Select environmental features
- [x] Select population-normalized features
- [x] Create feature matrix

### Risk Model ✅
- [x] Define risk labels
- [x] Encode labels
- [x] Train classification model
- [x] Save model

### Resource Model ✅
- [x] Define resource variables
- [x] Generate training targets
- [x] Train regression model
- [x] Save model

### Predictions ✅
- [x] Predict risk levels
- [x] Identify hotspots
- [x] Generate recommendations

### Backend ✅
- [x] Initialize FastAPI
- [x] Load models on startup
- [x] JSON storage system
- [x] Resource CRUD APIs
- [x] Prediction APIs
- [x] Admin APIs
- [x] Assignment logic

## 🐛 Troubleshooting

### Models not found
```
Solution: Run the training scripts manually:
python3 ml/train_risk_model.py
python3 ml/train_resource_model.py
```

### Data files missing
```
Solution: Ensure CSVs are in data/ directory with exact names
```

### Port already in use
```
Solution: Change port in backend/config.py or:
python3 -m uvicorn backend.main:app --port 8001
```

### JSON storage errors
```
Solution: Delete data/storage.json and restart (will reinitialize)
```

## 📄 License

This project is provided as-is for educational and research purposes.

## 👥 Contributing

Contributions are welcome! Please ensure:
- Code follows existing structure
- All tests pass
- Documentation is updated

## 📧 Support

For issues or questions, please check:
1. This README
2. API documentation at `/docs`
3. Individual module docstrings

---

**Built with**: Python, FastAPI, scikit-learn, pandas, numpy

**Last Updated**: January 2026