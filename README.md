# Digital Pathways to Prevention: An Integrated AI Framework for Dengue Prediction and Control

**Sri Lanka Institute of Information Technology (SLIIT)**  
Faculty of Computing  
Final Year Research Project 2025/2026  
**Project ID:** 25-26J-406

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Individual Components](#individual-components)
7. [Installation & Setup](#installation--setup)
8. [Running the System](#running-the-system)
9. [Team Members & Contributions](#team-members--contributions)
10. [License](#license)

---

## Project Overview

This Final Year Research Project focuses on developing an **Integrated AI Framework for Dengue Prediction and Control** in Sri Lanka. The system aims to bridge the gap between traditional manual surveillance and modern technology by coalescing real-time predictions, field data, species intelligence, and optimization algorithms into one coherent decision-support platform.

### Problem Statement

Identifying mosquito breeding sites is currently labor-intensive and prone to human error. Furthermore, resource allocation for dengue control is often reactive rather than proactive, leading to delays in responding to emerging hotspots.

### Objectives

- **Forecast Outbreaks:** Predict dengue risks at district/city levels using historical data, weather patterns, and social signals.
- **Automate Detection:** Use deep learning on aerial imagery to identify breeding sites.
- **Species Identification:** Enable real-time mosquito classification (Aedes aegypti/albopictus) via smartphone cameras.
- **Optimize Response:** Allocate PHIs and fogging teams efficiently using GIS and pathfinding algorithms.

---

## Key Features

| Feature | Description | Technology |
|---------|-------------|------------|
| **Dengue Outbreak Prediction** | Forecasts risk levels (Low/Med/High) using weather & social data | LSTM / Random Forest |
| **Breeding Site Detection** | Identifies stagnant water/containers from aerial images | Deep Learning (CNN/YOLO) |
| **Mosquito Species ID** | Mobile-based classification of Aedes vectors | CNN Mobile Classifier |
| **Hotspot Recommendation** | Spatial clustering for risk concentration | DBSCAN / K-Means / KDE |
| **Resource Optimization** | Optimal route planning for fogging/inspection teams | Linear Programming / A* |
| **Commuter Alerts** | Personalized risk alerts for travelers | Geofencing / Mobile Push |
| **Interactive Dashboard** | Visualization for MOH and PHI decision support | React / GIS Maps |

---

## System Architecture

```


┌─────────────────────────────────────────────────────────────────────────────────┐
│              Digital Pathways to Prevention - System Architecture                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐                 │
│  │   Data Sources  │   │   User Inputs   │   │  Field Devices  │                 │
│  │  - Weather API  │   │  - Mobile App   │   │  - Drones/UAV   │                 │
│  │  - Social Media │   │  - Species Cam  │   │  - Aerial Imgs  │                 │
│  │  - EPI History  │   │  - User Loc     │   │                 │                 │
│  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘                 │
│           │                     │                     │                          │
│           └──────────────┬──────┴──────┬──────────────┘                          │
│                          │             │                                         │
│                    ┌─────▼─────┐ ┌─────▼─────┐                                   │
│                    │ Data Prep │ │  Image    │                                   │
│                    │ Pipeline  │ │ Process   │                                   │
│                    └─────┬─────┘ └─────┬─────┘                                   │
│  ┌───────────────────────┼─────────────┼──────────────────────────────────────┐  │
│  │                       │             │                                      │  │
│  │                 CORE INTELLIGENCE ENGINE                                   │  │
│  │                                                                            │  │
│  │  ┌─────────────────────────────┐   ┌───────────────────────────────────┐   │  │
│  │  │   Prediction Service        │   │    Computer Vision Service        │   │  │
│  │  │  - LSTM/RF Models           │   │   - Breeding Site Detect (Aerial) │   │  │
│  │  │  - Risk Scoring             │   │   - Species Classification (App)  │   │  │
│  │  └──────────────┬──────────────┘   └─────────────────┬─────────────────┘   │  │
│  │                 │                                    │                     │  │
│  │                 └──────────────┬─────────────────────┘                     │  │
│  │                                │                                           │  │
│  │                      ┌─────────▼─────────┐                                 │  │
│  │                      │  Central Database │                                 │  │
│  │                      │ (Geo/User/Model)  │                                 │  │
│  │                      └─────────┬─────────┘                                 │  │
│  │                                │                                           │  │
│  │                      ┌─────────▼─────────┐                                 │  │
│  │                      │ Optimization Core │                                 │  │
│  │                      │ - Resource Alloc. │                                 │  │
│  │                      │ - Pathfinding     │                                 │  │
│  │                      └─────────┬─────────┘                                 │  │
│  └────────────────────────────────┼───────────────────────────────────────────┘  │
│                                   │                                              │
│  ┌────────────────────────────────▼───────────────────────────────────────────┐  │
│  │                        CLIENT APPLICATIONS                                 │  │
│  │                                                                            │  │
│  │  ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐  │  │
│  │  │   Public App       │   │   Admin Dashboard  │   │   Field Unit App   │  │  │
│  │  │   (React Native)   │   │     (React/Web)    │   │     (Mobile)       │  │  │
│  │  │                    │   │                    │   │                    │  │  │
│  │  │  - Species Scan    │   │  - Heatmaps        │   │  - Route Plans     │  │  │
│  │  │  - Risk Alerts     │   │  - Resource Alloc  │   │  - Task List       │  │  │
│  │  │  - Report Site     │   │  - Analytics       │   │  - Site Valid.     │  │  │
│  │  └────────────────────┘   └────────────────────┘   └────────────────────┘  │  │
│  │                                                                            │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘


```

---

## Technology Stack

### Machine Learning & Data Science

| Component | Technology | Purpose |
|-----------|------------|---------|
| Outbreak Prediction | Python, LSTM, Random Forest | Forecasting risk levels |
| Breeding Site Vision | Python, TensorFlow/YOLO | Aerial image segmentation |
| Species ID | Python, CNN (TensorFlow/Keras) | Mosquito classification |
| Optimization | Linear Programming, A* | Resource allocation logic |
| Data Processing | Pandas, NumPy | Data cleaning and analysis |

### Backend & Database

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Server | Flask / FastAPI | Serving ML models and data |
| Database | PostgreSQL / MongoDB | Storing geospatial and user data |
| Weather Data | Open-Meteo API | Real-time weather input |

### Frontend Applications

| Application | Technology | Purpose |
|-------------|------------|---------|
| Admin Dashboard | React.js | Visualization for Health Authorities |
| Mobile App | React Native | Public reporting and species scan |
| Maps Integration | Leaflet / Google Maps API | GIS visualization |

---

## Project Structure

```
FinalYearProject-DengueAI/
│
├── backend/                          # Main API Server
│   ├── app.py                        # Application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── api/                          # API endpoints
│   └── services/                     # Business logic
│       ├── prediction_service.py     # Outbreak forecasting logic
│       └── optimization_service.py   # Resource allocation algorithms
│
├── models/                           # ML & Deep Learning Models
│   ├── breeding_site_detection/      # Aerial imagery models
│   │   ├── yolov8_custom.pt
│   │   └── train.py
│   ├── species_identification/       # Mosquito classification
│   │   ├── cnn_model.h5
│   │   └── preprocessing.py
│   └── outbreak_prediction/          # Risk forecasting
│       └── lstm_model.pkl
│
├── mobile_app/                       # React Native Application
│   ├── App.js
│   └── src/
│       ├── screens/                  # Scanner, Map, Alerts
│       └── components/
│
├── web_dashboard/                    # React Admin Panel
│   └── src/
│       ├── components/               # Heatmaps, Charts
│       └── pages/                    # Admin views
│
├── data/                             # Datasets (Sample)
│   ├── aerial_images/
│   ├── weather_history/
│   └── mosquito_classes/
│
├── notebooks/                        # Jupyter Notebooks for Research
│   ├── eda_weather.ipynb
│   └── model_training_vision.ipynb
│
├── README.md                         # This file
└── .gitignore
```

---

## Individual Components

### 1. Dengue Outbreak Prediction

**Developed by:** Gunasinghe C V

Forecasts dengue outbreaks at district/city levels using historical cases, Open-Meteo weather data, and social media signals. Utilizes rule-based thresholds and ML models to categorize risk as Low, Medium, or High.

### 2. Mosquito Breeding Site Detection

**Developed by:** Piyasena S H T

A deep learning system designed to analyze aerial/drone imagery. It automates the identification of stagnant water and water-holding containers, providing a practical tool for public health teams to monitor high-risk zones without labor-intensive field surveys.

### 3. Application of AI for Mosquito Species ID

**Developed by:** Amaranayaka M K D D

An AI-powered mobile function that identifies dengue-carrying mosquito species (Aedes aegypti vs. Aedes albopictus) via smartphone images. It integrates GPS data to map identified vectors for localized risk analysis.

### 4. Optimal Resource Allocation

**Developed by:** Kumari K.A.N.N.S

An optimization-based system utilizing GIS and spatial analysis. It employs algorithms like Linear Programming and Pathfinding (A*, Dijkstra) to determine the most efficient deployment of PHIs and fogging units based on predicted hotspots.

---

## Installation & Setup

### Prerequisites

- **Python** >= 3.9
- **Node.js** >= 18.x
- **npm** or **yarn**

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/DigitalPathwaysDengue.git
cd DigitalPathwaysDengue
```

### 2. Backend & Model Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 3. Web Dashboard Setup

```bash
cd web_dashboard
npm install
npm start
```

### 4. Mobile App Setup

```bash
cd mobile_app
npm install
npm start
```

---

## Team Members & Contributions

| Registration No | Name | Role / Component |
|-----------------|------|------------------|
| **IT22246882** | **Gunasinghe C V** | Dengue Outbreak Prediction |
| **IT22582010** | **Piyasena S H T** | Detection of Mosquito Breeding Sites (Aerial) |
| **IT22313348** | **Amaranayaka M K D D** | AI for Dengue Mosquito Species Identification |
| **IT22317612** | **Kumari K.A.N.N.S** | Optimal Resource Allocation & Hotspot Rec |

### Supervisors

- **Supervisor:** Mrs. Dushanthi Kuruppu
- **Co-Supervisor:** Ms. Tharushi Rubasinghe

---

## License

This project is developed as part of the Final Year Research Project at **Sri Lanka Institute of Information Technology (SLIIT)**. All rights reserved.