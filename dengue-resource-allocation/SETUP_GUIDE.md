# Complete Setup & Implementation Guide

## 📦 Installation Steps

### Step 1: Project Initialization

```bash
# Create project directory
mkdir dengue-resource-allocation
cd dengue-resource-allocation

# Create subdirectories
mkdir -p data models ml backend/routes

# Create empty files
touch requirements.txt README.md run.sh train_all_models.py
touch ml/__init__.py backend/__init__.py backend/routes/__init__.py
```

### Step 2: Copy All Implementation Files

Copy the provided code files into their respective locations:

**ML Module Files** (`ml/` directory):
- `preprocess.py` - Data preprocessing pipeline
- `feature_engineering.py` - Feature selection and engineering
- `train_risk_model.py` - Risk classification model training
- `train_resource_model.py` - Resource recommendation model training
- `predict.py` - Prediction system

**Backend Files** (`backend/` directory):
- `main.py` - FastAPI application entry point
- `config.py` - Configuration settings
- `json_store.py` - JSON storage manager
- `schemas.py` - Pydantic data models
- `utils.py` - Helper utilities

**Backend Routes** (`backend/routes/` directory):
- `resources.py` - Resource management endpoints
- `predictions.py` - Prediction endpoints
- `admin.py` - Admin dashboard endpoints

**Root Files**:
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation
- `run.sh` - Master execution script
- `train_all_models.py` - Complete training pipeline

### Step 3: Add Data Files

Place your CSV datasets in the `data/` directory:

```bash
data/
├── dengue_data_with_weather_data.csv
└── population_by_district_in_census_years.csv
```

### Step 4: Create Python Package Init Files

```bash
# Create __init__.py files for Python packages
touch ml/__init__.py
touch backend/__init__.py
touch backend/routes/__init__.py
```

### Step 5: Make Scripts Executable

```bash
chmod +x run.sh
```

## 🚀 Execution Workflow

### Option 1: Automated Setup (Recommended)

```bash
# Run the complete setup and start server
./run.sh
```

This script will:
1. Create virtual environment
2. Install dependencies
3. Preprocess data
4. Train ML models
5. Generate predictions
6. Start API server

### Option 2: Manual Step-by-Step

#### A. Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### B. Data Processing

```bash
# Run data preprocessing
python3 ml/preprocess.py
```

**Expected Output:**
- Creates `data/processed_data.csv`
- Shows preprocessing progress
- Displays data statistics

#### C. Model Training

**Option C1: Train All Models at Once**
```bash
python3 train_all_models.py
```

**Option C2: Train Models Individually**
```bash
# Train risk classification model
python3 ml/train_risk_model.py

# Train resource recommendation model
python3 ml/train_resource_model.py
```

**Expected Output:**
- Creates `models/risk_model.pkl`
- Creates `models/resource_model.pkl`
- Shows training metrics and evaluation results

#### D. Generate Predictions

```bash
# Test prediction system
python3 ml/predict.py
```

**Expected Output:**
- Shows predicted risk levels for all districts
- Identifies hotspots
- Displays resource recommendations

#### E. Start API Server

```bash
# Start with uvicorn
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
Starting Dengue Resource Allocation API
✓ Storage initialized
✓ Risk model loaded
✓ Resource model loaded
API Server Ready!
```

## 🧪 Testing the System

### 1. Test via Browser

Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Root Endpoint**: http://localhost:8000

### 2. Test via Command Line (curl)

```bash
# Health check
curl http://localhost:8000/health

# Generate predictions
curl -X POST http://localhost:8000/predictions/generate

# Get hotspots
curl http://localhost:8000/predictions/hotspots

# Get available resources
curl http://localhost:8000/resources/

# Set resources
curl -X POST http://localhost:8000/resources/ \
  -H "Content-Type: application/json" \
  -d '{
    "Fogging_Units": 100,
    "Health_Inspectors": 50,
    "Inspection_Teams": 30,
    "Treatment_Units": 80
  }'

# Assign resources to a district
curl -X POST http://localhost:8000/resources/assign \
  -H "Content-Type: application/json" \
  -d '{
    "district": "Colombo",
    "Fogging_Units": 10,
    "Health_Inspectors": 5,
    "Inspection_Teams": 3,
    "Treatment_Units": 8
  }'

# Get admin overview
curl http://localhost:8000/admin/overview
```

### 3. Test via Python Script

Create a test file `test_api.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_predictions():
    print("Testing prediction generation...")
    response = requests.post(f"{BASE_URL}/predictions/generate")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_hotspots():
    print("\nTesting hotspot retrieval...")
    response = requests.get(f"{BASE_URL}/predictions/hotspots")
    data = response.json()
    print(f"Found {data['count']} hotspots")
    for hotspot in data['hotspots'][:3]:
        print(f"  - {hotspot['District']}: {hotspot['Risk_Level']}")

def test_resources():
    print("\nTesting resource management...")
    
    # Set resources
    resources = {
        "Fogging_Units": 100,
        "Health_Inspectors": 50,
        "Inspection_Teams": 30,
        "Treatment_Units": 80
    }
    response = requests.post(f"{BASE_URL}/resources/", json=resources)
    print(f"Resources set: {response.json()['message']}")
    
    # Get resources
    response = requests.get(f"{BASE_URL}/resources/")
    print(f"Available: {response.json()['available_resources']}")

def test_assignment():
    print("\nTesting resource assignment...")
    assignment = {
        "district": "Colombo",
        "Fogging_Units": 10,
        "Health_Inspectors": 5,
        "Inspection_Teams": 3,
        "Treatment_Units": 8,
        "notes": "Test assignment"
    }
    response = requests.post(f"{BASE_URL}/resources/assign", json=assignment)
    print(json.dumps(response.json(), indent=2))

def test_admin():
    print("\nTesting admin overview...")
    response = requests.get(f"{BASE_URL}/admin/overview")
    data = response.json()
    print(f"Summary: {data['summary']}")

if __name__ == "__main__":
    test_predictions()
    test_hotspots()
    test_resources()
    test_assignment()
    test_admin()
```

Run the test:
```bash
python3 test_api.py
```

## 📊 Understanding the Data Flow

### 1. Data Preprocessing Flow

```
Raw CSV Files
    ↓
[Load & Merge]
    ↓
Population Interpolation
    ↓
Feature Calculation
    ↓
Processed CSV (data/processed_data.csv)
```

### 2. Model Training Flow

```
Processed Data
    ↓
[Feature Engineering]
    ↓
Training Set Split
    ↓
Model Training
    ↓
Model Evaluation
    ↓
Saved Models (.pkl files)
```

### 3. Prediction Flow

```
Latest District Data
    ↓
[Risk Model] → Risk Levels (Low/Medium/High)
    ↓
[Hotspot Detection] → Identify High-Risk Districts
    ↓
[Resource Model] → Resource Recommendations
    ↓
JSON Storage
```

### 4. API Flow

```
Client Request
    ↓
FastAPI Endpoint
    ↓
Business Logic
    ↓
JSON Storage (Read/Write)
    ↓
Response to Client
```

## 🔍 Troubleshooting Guide

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure you're in the project root directory
cd dengue-resource-allocation

# Ensure __init__.py files exist
touch ml/__init__.py backend/__init__.py backend/routes/__init__.py

# Run from project root
python3 -m ml.preprocess
```

### Issue: "Models not found" on API startup

**Solution:**
```bash
# Train models first
python3 train_all_models.py

# Or individually
python3 ml/train_risk_model.py
python3 ml/train_resource_model.py
```

### Issue: "Data files not found"

**Solution:**
```bash
# Verify files exist
ls data/

# Should show:
# dengue_data_with_weather_data.csv
# population_by_district_in_census_years.csv

# If missing, place your CSV files in data/ directory
```

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use a different port
python3 -m uvicorn backend.main:app --port 8001

# Or kill existing process
# Linux/Mac:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Permission denied for run.sh

**Solution:**
```bash
chmod +x run.sh
./run.sh
```

### Issue: JSON storage errors

**Solution:**
```bash
# Remove corrupted storage file
rm data/storage.json

# Restart API (will recreate)
python3 -m uvicorn backend.main:app --reload
```

## 📈 Performance Optimization

### For Large Datasets

1. **Batch Processing:**
   Modify `ml/preprocess.py` to process data in chunks

2. **Model Parameters:**
   Adjust in training scripts:
   ```python
   RandomForestClassifier(
       n_estimators=50,  # Reduce from 100
       max_depth=8,      # Reduce from 10
       n_jobs=-1         # Use all CPU cores
   )
   ```

3. **API Performance:**
   Use Gunicorn for production:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app
   ```

## 🔐 Security Considerations

### For Production Deployment

1. **Environment Variables:**
   ```bash
   # Create .env file
   echo "SECRET_KEY=your-secret-key" > .env
   echo "DATABASE_URL=your-db-url" >> .env
   ```

2. **CORS Configuration:**
   Update `backend/config.py`:
   ```python
   CORS_ORIGINS = [
       "https://yourdomain.com"
   ]
   ```

3. **Authentication:**
   Add authentication middleware to protect endpoints

4. **HTTPS:**
   Deploy behind a reverse proxy (Nginx) with SSL

## 📦 Deployment Options

### Option 1: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t dengue-api .
docker run -p 8000:8000 dengue-api
```

### Option 2: Cloud Deployment

**AWS EC2:**
1. Launch Ubuntu instance
2. Clone repository
3. Run setup script
4. Configure security groups

**Heroku:**
1. Add `Procfile`:
   ```
   web: uvicorn backend.main:app --host=0.0.0.0 --port=${PORT}
   ```
2. Deploy:
   ```bash
   heroku create
   git push heroku main
   ```

## 📝 Maintenance

### Regular Tasks

1. **Update Predictions:**
   ```bash
   curl -X POST http://localhost:8000/predictions/generate
   ```

2. **Backup Storage:**
   ```bash
   cp data/storage.json data/storage_backup_$(date +%Y%m%d).json
   ```

3. **Retrain Models:**
   ```bash
   python3 train_all_models.py
   ```

4. **Monitor Logs:**
   ```bash
   tail -f logs/api.log
   ```

---

**Need Help?** Check the main README.md or API documentation at `/docs`