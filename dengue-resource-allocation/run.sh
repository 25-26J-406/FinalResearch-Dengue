#!/bin/bash

# Dengue Resource Allocation System - Master Run Script
# This script handles the complete workflow from data preparation to API startup

set -e  # Exit on error

echo "======================================================================"
echo "Dengue Resource Allocation & Hotspot Recommendation System"
echo "======================================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_info "Virtual environment not found. Creating..."
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Install dependencies
print_info "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_status "Dependencies installed"

# Check if data files exist
echo ""
echo "======================================================================"
echo "Step 1: Checking Data Files"
echo "======================================================================"

if [ ! -f "data/dengue_data_with_weather_data.csv" ]; then
    print_error "dengue_data_with_weather_data.csv not found in data/ directory"
    echo "Please place your dataset in the data/ directory and run again"
    exit 1
fi

if [ ! -f "data/population_by_district_in_census_years.csv" ]; then
    print_error "population_by_district_in_census_years.csv not found in data/ directory"
    echo "Please place your dataset in the data/ directory and run again"
    exit 1
fi

print_status "Data files found"

# Run data preprocessing
echo ""
echo "======================================================================"
echo "Step 2: Data Preprocessing"
echo "======================================================================"
print_info "Running data preprocessing pipeline..."
python3 ml/preprocess.py
print_status "Data preprocessing complete"

# Check if models need to be trained
echo ""
echo "======================================================================"
echo "Step 3: Machine Learning Models"
echo "======================================================================"

TRAIN_MODELS=false

if [ ! -f "models/risk_model.pkl" ]; then
    print_info "Risk model not found. Will train..."
    TRAIN_MODELS=true
fi

if [ ! -f "models/resource_model.pkl" ]; then
    print_info "Resource model not found. Will train..."
    TRAIN_MODELS=true
fi

if [ "$TRAIN_MODELS" = true ]; then
    print_info "Training risk prediction model..."
    python3 ml/train_risk_model.py
    print_status "Risk model trained"
    
    print_info "Training resource recommendation model..."
    python3 ml/train_resource_model.py
    print_status "Resource model trained"
else
    print_status "ML models already exist"
fi

# Generate initial predictions
echo ""
echo "======================================================================"
echo "Step 4: Generating Initial Predictions"
echo "======================================================================"
print_info "Running prediction system..."
python3 ml/predict.py
print_status "Predictions generated"

# Start API server
echo ""
echo "======================================================================"
echo "Step 5: Starting API Server"
echo "======================================================================"
print_status "All prerequisites complete"
print_info "Starting FastAPI server..."
echo ""

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload