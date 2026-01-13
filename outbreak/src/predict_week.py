import os
import logging
from pathlib import Path
from datetime import date, timedelta

import joblib
import numpy as np
import pandas as pd
import requests
from flask import Flask, request, jsonify, render_template, send_file, redirect

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dengue-predict")

# Resolve project root (repo)/templates/static location
ROOT = Path(__file__).resolve().parents[1]

app = Flask(
    __name__,
    template_folder=str(ROOT / "templates"),
    static_folder=str(ROOT / "static"),
)

# Optional: enable CORS if frontend served from other origin
try:
    from flask_cors import CORS
    CORS(app)
except Exception:
    logger.info("flask-cors not installed; skipping CORS setup")

# Model/scaler paths
MODEL_LEGACY = ROOT / "models" / "dengue_model.pkl"
MODEL_BEST = ROOT / "models" / "dengue_model_best.pkl"
SCALER_LEGACY = ROOT / "models" / "scaler.pkl"
SCALER_BEST = ROOT / "models" / "scaler_best.pkl"
PIPELINE_BEST = ROOT / "models" / "pipeline_best.joblib"
PIPELINE_V1 = ROOT / "models" / "pipeline_v1.joblib"

# Load pipeline if available, else scaler+model
pipeline = None
model = None
scaler = None
try:
    if PIPELINE_BEST.exists():
        pipeline = joblib.load(PIPELINE_BEST)
        logger.info("Loaded pipeline from %s", PIPELINE_BEST)
    elif PIPELINE_V1.exists():
        pipeline = joblib.load(PIPELINE_V1)
        logger.info("Loaded pipeline from %s", PIPELINE_V1)
    else:
        # load model/scaler pairs (prefer _best)
        if MODEL_BEST.exists() and SCALER_BEST.exists():
            model = joblib.load(MODEL_BEST)
            scaler = joblib.load(SCALER_BEST)
            logger.info("Loaded model from %s and scaler from %s", MODEL_BEST, SCALER_BEST)
        elif MODEL_LEGACY.exists() and SCALER_LEGACY.exists():
            model = joblib.load(MODEL_LEGACY)
            scaler = joblib.load(SCALER_LEGACY)
            logger.info("Loaded model from %s and scaler from %s", MODEL_LEGACY, SCALER_LEGACY)
        else:
            raise FileNotFoundError("No model or pipeline artifacts found in models/ directory")
except Exception as e:
    logger.exception("Failed to load model/pipeline/scaler: %s", e)
    raise

# External service endpoints
GEOCODE_URL = "https://nominatim.openstreetmap.org/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
USER_AGENT = "DengueRiskApp/1.0 (contact@example.com)"

# Local dataset path for fallback weather/geocode lookup
LOCAL_DATA_CSV = ROOT / "data" / "dengue_cases_weekly2021_2024.csv"

# Fallback coordinates for Sri Lankan districts
DISTRICT_COORDS = {
    'ampara': (7.2918, 81.6724, 650000),
    'anuradhapura': (8.3114, 80.4037, 860000),
    'badulla': (6.9934, 81.0550, 815000),
    'batticaloa': (7.7310, 81.6924, 526000),
    'colombo': (6.9271, 79.8612, 2324000),
    'galle': (6.0535, 80.2210, 1063000),
    'gampaha': (7.0840, 80.0098, 2304000),
    'hambantota': (6.1429, 81.1212, 599000),
    'jaffna': (9.6615, 80.0255, 583000),
    'kalutara': (6.5854, 79.9607, 1222000),
    'kandy': (7.2906, 80.6337, 1375000),
    'kegalle': (7.2513, 80.3464, 840000),
    'kilinochchi': (9.3803, 80.3750, 113000),
    'kurunegala': (7.4818, 80.3609, 1618000),
    'mannar': (8.9810, 79.9044, 99000),
    'matale': (7.4675, 80.6234, 484000),
    'matara': (5.9549, 80.5550, 814000),
    'monaragala': (6.8728, 81.3507, 451000),
    'mullaitivu': (9.2671, 80.8142, 92000),
    'nuwara eliya': (6.9497, 80.7891, 711000),
    'polonnaruwa': (7.9403, 81.0188, 406000),
    'puttalam': (8.0362, 79.8283, 762000),
    'ratnapura': (6.6828, 80.4014, 1088000),
    'trincomalee': (8.5874, 81.2152, 379000),
    'vavuniya': (8.7542, 80.4982, 172000)
}


def lookup_local_weather_and_coords(name):
    """Try to find district by name in local CSV and compute average temp/rain and coordinates.
    Returns dict with keys: avg_temp, avg_humidity, avg_rain, lat, lon, display_name or None.
    """
    try:
        if not LOCAL_DATA_CSV.exists():
            return None
        df = pd.read_csv(LOCAL_DATA_CSV)
        if "District" not in df.columns:
            return None
        # case-insensitive match
        candidates = df[df["District"].str.lower() == name.lower()]
        if candidates.empty:
            # try contains
            candidates = df[df["District"].str.lower().str.contains(name.lower())]
        if candidates.empty:
            return None

        # Temperature: average of Avg Max Temp and Avg Min Temp where present
        temp_cols = [c for c in df.columns if "max temp" in c.lower() or "avg max temp" in c.lower() or "avg max" in c.lower()]
        min_cols = [c for c in df.columns if "min temp" in c.lower() or "avg min temp" in c.lower() or "avg min" in c.lower()]
        if temp_cols and min_cols:
            max_col = temp_cols[0]
            min_col = min_cols[0]
            temps = (pd.to_numeric(candidates[max_col], errors="coerce") + pd.to_numeric(candidates[min_col], errors="coerce")) / 2.0
            avg_temp = float(temps.mean())
        else:
            # try any temp-like column
            any_temp = next((c for c in df.columns if "temp" in c.lower()), None)
            if any_temp:
                    avg_temp = float(pd.to_numeric(candidates[any_temp], errors="coerce").mean())
            else:
                avg_temp = None

        # Rainfall
        rain_col = next((c for c in df.columns if "total rain" in c.lower() or "precip" in c.lower() or "rain" in c.lower()), None)
        avg_rain = float(pd.to_numeric(candidates[rain_col], errors="coerce").mean()) if rain_col else None

        # Latitude / Longitude if present
        lat = None; lon = None
        if "Latitude" in df.columns and "Longitude" in df.columns:
            lat_series = pd.to_numeric(candidates["Latitude"], errors="coerce").dropna()
            lon_series = pd.to_numeric(candidates["Longitude"], errors="coerce").dropna()
            if not lat_series.empty and not lon_series.empty:
                lat = float(lat_series.mean())
                lon = float(lon_series.mean())
        
        # Fallback to hardcoded coordinates if not in CSV
        district_name = candidates["District"].iloc[0]
        if (lat is None or lon is None) and district_name.lower() in DISTRICT_COORDS:
            lat, lon, pop_fallback = DISTRICT_COORDS[district_name.lower()]
        else:
            pop_fallback = None

        # population if present in CSV
        pop_col = next((c for c in df.columns if "population" in c.lower() or c.lower().startswith("pop")), None)
        avg_pop = None
        if pop_col:
            try:
                pop_series = pd.to_numeric(candidates[pop_col], errors="coerce").dropna()
                if not pop_series.empty:
                    avg_pop = int(pop_series.mean())
            except Exception:
                avg_pop = None
        
        # Use fallback population if CSV empty
        if avg_pop is None and pop_fallback:
            avg_pop = pop_fallback

        # humidity not present in CSV — use None so caller can fallback
        return {
            "avg_temp": avg_temp,
            "avg_humidity": None,
            "avg_rain": avg_rain,
            "lat": lat,
            "lon": lon,
            "population": avg_pop,
            "display_name": district_name
        }
    except Exception:
        logger.exception("Local lookup failed")
        return None


def validate_features_list(features):
    if not isinstance(features, list):
        return False, "features must be a list"
    if len(features) != 5:
        return False, "features must contain exactly 5 values: [year, month, temperature, humidity, rainfall]"
    try:
        arr = [float(x) for x in features]
    except Exception:
        return False, "each feature must be numeric"
    return True, np.array(arr, dtype=float)


def geocode_city(city):
    params = {"q": city, "format": "json", "limit": 1}
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(GEOCODE_URL, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError("Location not found")
    item = data[0]
    return {
        "lat": float(item["lat"]),
        "lon": float(item["lon"]),
        "display_name": item.get("display_name", city),
    }


def fetch_7day_weather(lat, lon):
    start = date.today()
    end = start + timedelta(days=6)
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "hourly": "relativehumidity_2m",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": "auto",
    }
    r = requests.get(WEATHER_URL, params=params, timeout=15)
    r.raise_for_status()
    j = r.json()

    temps = []
    if "daily" in j and j["daily"].get("temperature_2m_max") and j["daily"].get("temperature_2m_min"):
        maxs = j["daily"]["temperature_2m_max"]
        mins = j["daily"]["temperature_2m_min"]
        temps = [ (float(a)+float(b))/2.0 for a,b in zip(maxs, mins) ]
    avg_temp = float(np.mean(temps)) if temps else None

    rain = None
    if "daily" in j and j["daily"].get("precipitation_sum"):
        rain_vals = [float(x) for x in j["daily"]["precipitation_sum"]]
        rain = float(np.mean(rain_vals))

    humidity = None
    if "hourly" in j and j["hourly"].get("relativehumidity_2m"):
        hum_vals = [float(x) for x in j["hourly"]["relativehumidity_2m"]]
        humidity = float(np.mean(hum_vals))

    return {"avg_temp": avg_temp, "avg_humidity": humidity, "avg_rain": rain}


def make_prediction_from_features(arr):
    # Use pipeline if available (it includes scaler + clf), otherwise apply scaler then model
    risk_pct = None
    if pipeline is not None:
        X = np.array([arr], dtype=float)
        logger.debug("Using pipeline to predict; input: %s", X)
        pred = pipeline.predict(X)[0]
        try:
            proba = pipeline.predict_proba(X)[0]
            risk_pct = float(np.max(proba) * 100)
        except Exception:
            risk_pct = None
    else:
        X = scaler.transform([arr])
        logger.debug("Scaled features: %s", X)
        pred = model.predict(X)[0]
        try:
            proba = model.predict_proba(X)[0]
            risk_pct = float(np.max(proba) * 100)
        except Exception:
            risk_pct = None

    if risk_pct is None:
        try:
            cls = int(pred)
            risk_pct = float({0: 10.0, 1: 50.0, 2: 90.0}.get(cls, 50.0))
        except Exception:
            risk_pct = 50.0
    color = "green" if risk_pct < 33 else "yellow" if risk_pct < 66 else "red"
    return {"prediction_raw": str(pred), "risk_pct": round(risk_pct, 1), "color": color}


@app.route("/")
def index():
    # Redirect to the static served index to avoid template loader edge-cases
    return redirect("/index.html")


@app.route("/index.html")
def index_html():
    tpl = Path(ROOT) / "templates" / "index.html"
    if tpl.exists():
        return send_file(str(tpl))
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    payload = request.get_json()

    # Direct features path
    if "features" in payload:
        ok, result = validate_features_list(payload["features"])
        if not ok:
            return jsonify({"error": result}), 400
        features = result
        try:
            pred = make_prediction_from_features(features)
        except Exception as e:
            logger.exception("Prediction failed: %s", e)
            return jsonify({"error": "Prediction failed"}), 500

        return jsonify({
            "district": payload.get("district", "Unknown"),
            "population": payload.get("population", 0),
            "rain": float(features[4]),
            "temp": float(features[2]),
            "humidity": float(features[3]),
            "risk": pred["risk_pct"],
            "color": pred["color"],
            "lat": payload.get("lat", 0.0),
            "lon": payload.get("lon", 0.0),
        })

    lat = payload.get("lat")
    lon = payload.get("lon")
    city = payload.get("city") or payload.get("district") or payload.get("location")

    if city:
        try:
            geo = geocode_city(city)
            lat = geo["lat"]
            lon = geo["lon"]
            district = geo["display_name"]
        except ValueError:
            # try local CSV lookup as a fallback
            logger.info("Geocoding failed for %s; trying local CSV lookup", city)
            local = lookup_local_weather_and_coords(city)
            if local:
                lat = local.get("lat") or 0.0
                lon = local.get("lon") or 0.0
                district = local.get("display_name", city)
                # attach local weather to payload for later use
                weather = {"avg_temp": local.get("avg_temp"), "avg_humidity": local.get("avg_humidity"), "avg_rain": local.get("avg_rain")}
            else:
                return jsonify({"error": "Location not found"}), 404
        except Exception:
            logger.exception("Geocoding error for %s", city)
            # try local lookup before failing
            local = lookup_local_weather_and_coords(city)
            if local:
                lat = local.get("lat") or 0.0
                lon = local.get("lon") or 0.0
                district = local.get("display_name", city)
                weather = {"avg_temp": local.get("avg_temp"), "avg_humidity": local.get("avg_humidity"), "avg_rain": local.get("avg_rain")}
            else:
                return jsonify({"error": "Geocoding failed"}), 502
    else:
        if lat is None or lon is None:
            return jsonify({"error": "Provide either 'features' or 'city' or both 'lat' and 'lon'"}), 400
        try:
            lat = float(lat); lon = float(lon)
            district = payload.get("district", f"{lat},{lon}")
        except Exception:
            return jsonify({"error": "lat and lon must be numeric"}), 400

    try:
        weather = fetch_7day_weather(lat, lon)
    except Exception:
        logger.exception("Weather fetch failed for %s,%s", lat, lon)
        # allow previously found local weather (from CSV) to be used
        local = None
        try:
            # try to lookup by district name if available
            if district:
                local = lookup_local_weather_and_coords(district)
        except Exception:
            local = None

        if local:
            weather = {"avg_temp": local.get("avg_temp"), "avg_humidity": local.get("avg_humidity"), "avg_rain": local.get("avg_rain")}
            # if lat/lon missing, try fill
            if not lat and local.get("lat"):
                lat = local.get("lat")
                lon = local.get("lon")
        else:
            return jsonify({"error": "Failed to fetch weather data"}), 502

    avg_temp = weather.get("avg_temp") if weather.get("avg_temp") is not None else 25.0
    avg_humidity = weather.get("avg_humidity") if weather.get("avg_humidity") is not None else 60.0
    avg_rain = weather.get("avg_rain") if weather.get("avg_rain") is not None else 1.0

    today = date.today()
    features_arr = np.array([float(today.year), float(today.month), float(avg_temp), float(avg_humidity), float(avg_rain)], dtype=float)

    try:
        pred = make_prediction_from_features(features_arr)
    except Exception:
        logger.exception("Prediction failed")
        return jsonify({"error": "Prediction failed"}), 500

    # Resolve population: prefer payload, then any local CSV lookup, else 0
    population = payload.get("population")
    if not population:
        # if we used a local lookup earlier, it may be bound in local variable
        if 'local' in locals() and local and local.get('population'):
            population = local.get('population')
        else:
            try:
                looked = lookup_local_weather_and_coords(district)
                if looked and looked.get('population'):
                    population = looked.get('population')
            except Exception:
                population = None
    if population is None:
        population = 0

    return jsonify({
        "district": district,
        "population": int(population) if isinstance(population, (int, float)) else population,
        "rain": round(float(avg_rain), 2),
        "temp": round(float(avg_temp), 2),
        "humidity": round(float(avg_humidity), 1) if avg_humidity is not None else None,
        "risk": pred["risk_pct"],
        "color": pred["color"],
        "lat": lat,
        "lon": lon
    })


@app.route("/places", methods=["GET"])
def places():
    """Return all known districts from the local CSV with coords and predicted risk/color."""
    try:
        if not LOCAL_DATA_CSV.exists():
            return jsonify({"error": "Local data CSV not found"}), 404
        df = pd.read_csv(LOCAL_DATA_CSV)
        if "District" not in df.columns:
            return jsonify({"error": "No 'District' column in CSV"}), 400

        places = []
        errors = []
        # group by district and compute averages
        for name, grp in df.groupby("District"):
            try:
                # Check if Latitude/Longitude columns exist and have valid data
                lat = None
                lon = None
                if "Latitude" in grp.columns:
                    lat_series = pd.to_numeric(grp["Latitude"], errors="coerce").dropna()
                    if not lat_series.empty:
                        lat = float(lat_series.mean())
                if "Longitude" in grp.columns:
                    lon_series = pd.to_numeric(grp["Longitude"], errors="coerce").dropna()
                    if not lon_series.empty:
                        lon = float(lon_series.mean())
                
                # skip if lat/lon missing or invalid
                if lat is None or lon is None or np.isnan(lat) or np.isnan(lon):
                    errors.append(f"Skipping {name}: missing coordinates")
                    continue

                # temperature average
                temp_cols = [c for c in grp.columns if "max temp" in c.lower() or "avg max temp" in c.lower() or "avg max" in c.lower()]
                min_cols = [c for c in grp.columns if "min temp" in c.lower() or "avg min temp" in c.lower() or "avg min" in c.lower()]
                if temp_cols and min_cols:
                    tmax = pd.to_numeric(grp[temp_cols[0]], errors="coerce")
                    tmin = pd.to_numeric(grp[min_cols[0]], errors="coerce")
                    avg_temp = float(((tmax + tmin) / 2.0).mean())
                else:
                    any_temp = next((c for c in grp.columns if "temp" in c.lower()), None)
                    avg_temp = float(pd.to_numeric(grp[any_temp], errors="coerce").mean()) if any_temp else None

                # rain
                rain_col = next((c for c in grp.columns if "precip" in c.lower() or "rain" in c.lower()), None)
                avg_rain = float(pd.to_numeric(grp[rain_col], errors="coerce").mean()) if rain_col else None

                # population
                pop_col = next((c for c in grp.columns if "population" in c.lower() or c.lower().startswith("pop")), None)
                population = None
                if pop_col:
                    pop_series = pd.to_numeric(grp[pop_col], errors="coerce").dropna()
                    if not pop_series.empty:
                        population = int(pop_series.mean())

                # humidity not present in CSV -> leave None so prediction uses defaults
                avg_humidity = None

                # if lat/lon available, try to fetch real 7-day weather
                try:
                    w = fetch_7day_weather(lat, lon)
                    avg_temp = w.get('avg_temp') if w.get('avg_temp') is not None else avg_temp
                    avg_rain = w.get('avg_rain') if w.get('avg_rain') is not None else avg_rain
                    avg_humidity = w.get('avg_humidity') if w.get('avg_humidity') is not None else avg_humidity
                except Exception as e:
                    errors.append(f"Weather fetch failed for {name}: {e}")

                # assemble features and predict (use today's year/month)
                today = date.today()
                feat = np.array([float(today.year), float(today.month), float(avg_temp) if avg_temp is not None else 25.0, float(avg_humidity) if avg_humidity is not None else 60.0, float(avg_rain) if avg_rain is not None else 0.0], dtype=float)
                try:
                    pred = make_prediction_from_features(feat)
                    risk = pred.get("risk_pct")
                    color = pred.get("color")
                except Exception as e:
                    errors.append(f"Prediction failed for {name}: {e}")
                    risk = None
                    color = "green"

                places.append({
                    "district": name,
                    "lat": lat,
                    "lon": lon,
                    "population": population,
                    "temp": round(float(avg_temp), 2) if avg_temp is not None else None,
                    "rain": round(float(avg_rain), 2) if avg_rain is not None else None,
                    "humidity": avg_humidity,
                    "risk": risk,
                    "color": color,
                })
            except Exception as e:
                errors.append(f"District {name} error: {e}")
                continue

        if not places:
            logger.error(f"No valid places found. Errors: {errors}")
            return jsonify({"error": "No valid places found", "details": errors}), 500
        if errors:
            logger.warning(f"Some places had errors: {errors}")
        return jsonify({"places": places, "errors": errors if len(errors) < 10 else errors[:10]})
    except Exception as e:
        logger.exception(f"Failed to build places list: {e}")
        return jsonify({"error": f"Internal error building places: {str(e)}"}), 500


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    # Log registered routes for diagnostics
    try:
        route_info = []
        for r in app.url_map.iter_rules():
            route_info.append(f"{r} -> {sorted(list(r.methods))}")
        logger.info("Registered routes with methods:\n%s", "\n".join(route_info))
    except Exception:
        logger.exception("Failed to list routes")
    app.run(port=5000, debug=debug)