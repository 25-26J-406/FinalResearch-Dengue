import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except Exception:
    LGB_AVAILABLE = False


ROOT = Path(".")
DATA_PATH = Path("data/dengue_cases_weekly2021_2024.csv")
OUT_DIR = Path("models")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def find_data():
    if DATA_PATH.exists():
        return DATA_PATH
    raise FileNotFoundError("data CSV not found at data/dengue_cases_weekly2021_2024.csv")


def load_data(path):
    df = pd.read_csv(path)
    return df


def profile_data(df):
    print("Columns:", list(df.columns))
    print("Rows:", len(df))
    print(df.head().T)
    print(df.isna().sum())


def prepare_dataset(df):
    # Normalize column names lookup
    cols = {c.lower(): c for c in df.columns}

    # Date parsing (week_start_date or Week_Start_Date)
    date_col = cols.get("week_start_date") or cols.get("week_start") or next((c for c in df.columns if "start" in c.lower() and "date" in c.lower()), None)
    if date_col:
        df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    else:
        # try Year+Week to construct approximate date
        if "Year" in df.columns and "Week" in df.columns:
            df["date"] = pd.to_datetime(df["Year"].astype(str) + df["Week"].astype(str) + '1', format='%Y%W%w', errors='coerce')
        else:
            df["date"] = pd.NaT

    # Standard column names
    district_col = cols.get("district") or cols.get("district_name") or next((c for c in df.columns if "district" in c.lower()), None)
    cases_col = cols.get("number_of_cases") or cols.get("number of cases") or cols.get("cases") or next((c for c in df.columns if "case" in c.lower()), None)
    pop_col = cols.get("population") or next((c for c in df.columns if "pop" in c.lower()), None)

    # temperature
    temp_max = next((c for c in df.columns if "max temp" in c.lower() or "avg max temp" in c.lower()), None)
    temp_min = next((c for c in df.columns if "min temp" in c.lower() or "avg min temp" in c.lower()), None)
    temp_any = next((c for c in df.columns if "temp" in c.lower()), None)
    if temp_max and temp_min:
        df["temperature"] = (pd.to_numeric(df[temp_max], errors="coerce") + pd.to_numeric(df[temp_min], errors="coerce")) / 2.0
    elif temp_any:
        df["temperature"] = pd.to_numeric(df[temp_any], errors="coerce")
    else:
        df["temperature"] = np.nan

    # rainfall
    rain_col = next((c for c in df.columns if "precip" in c.lower() or "rain" in c.lower()), None)
    if rain_col:
        df["rainfall"] = pd.to_numeric(df[rain_col], errors="coerce")
    else:
        df["rainfall"] = np.nan

    # humidity
    hum_col = next((c for c in df.columns if "humid" in c.lower()), None)
    if hum_col:
        df["humidity"] = pd.to_numeric(df[hum_col], errors="coerce")
    else:
        df["humidity"] = np.nan

    # basic columns
    df["district"] = df[district_col] if district_col in df.columns else df[district_col] if district_col else "Unknown"
    df["cases"] = pd.to_numeric(df[cases_col], errors="coerce") if cases_col else pd.to_numeric(df.get("Number_of_Cases", df.get("cases")), errors="coerce")
    df["population"] = pd.to_numeric(df[pop_col], errors="coerce") if pop_col else pd.to_numeric(df.get("Population", 0), errors="coerce").fillna(0)

    # Impute humidity: group median by district then global median
    df["humidity"] = df["humidity"].fillna(df.groupby("district")["humidity"].transform("median"))
    if df["humidity"].isna().any():
        df["humidity"] = df["humidity"].fillna(df["humidity"].median())

    # If population missing or zero, set to 1 to avoid division by zero
    df["population"] = df["population"].replace(0, np.nan)
    df["population"] = df["population"].fillna(df["population"].median())

    # derive incidence per 1000
    df["incidence_per_1000"] = (df["cases"].fillna(0) / df["population"]) * 1000.0
    df["incidence_per_1000"] = df["incidence_per_1000"].fillna(0.0)

    # create risk label by tertiles of incidence (3 classes)
    try:
        df["risk"] = pd.qcut(df["incidence_per_1000"].replace([np.inf, -np.inf], np.nan).fillna(0), q=3, labels=[0, 1, 2]).astype(int)
    except Exception:
        # fallback to simple bins
        df["risk"] = pd.cut(df["incidence_per_1000"], bins=[-1, 1, 5, np.inf], labels=[0, 1, 2]).astype(int)

    # temporal features
    df["year"] = pd.to_numeric(df.get("Year") if "Year" in df.columns else df["date"].dt.year, errors="coerce").fillna(df["date"].dt.year)
    df["month"] = pd.to_numeric(df.get("Month") if "Month" in df.columns else df["date"].dt.month, errors="coerce").fillna(df["date"].dt.month)
    df["month"] = df["month"].fillna(1).astype(int)
    # seasonality
    df["month_sin"] = np.sin(2 * np.pi * df["month"]/12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"]/12)

    # sort and create lags / rolling features by district
    df = df.sort_values(["district", "date"]).reset_index(drop=True)
    for k in (1,2):
        df[f"cases_lag_{k}"] = df.groupby("district")["cases"].shift(k)
    df["cases_roll_4_mean"] = df.groupby("district")["cases"].shift(1).rolling(4, min_periods=1).mean().reset_index(level=0, drop=True)
    df["temp_roll_4_mean"] = df.groupby("district")["temperature"].shift(1).rolling(4, min_periods=1).mean().reset_index(level=0, drop=True)
    df["rain_roll_4_sum"] = df.groupby("district")["rainfall"].shift(1).rolling(4, min_periods=1).sum().reset_index(level=0, drop=True)

    # Fill lag NaNs with 0 or column median
    lag_cols = [c for c in df.columns if c.startswith("cases_lag_") or c.endswith("roll_4_mean") or c.endswith("roll_4_sum")]
    for c in lag_cols:
        df[c] = df[c].fillna(0.0)

    # final features list
    features = ["year", "month", "temperature", "humidity", "rainfall", "cases_lag_1", "cases_lag_2", "cases_roll_4_mean", "temp_roll_4_mean", "rain_roll_4_sum", "month_sin", "month_cos"]

    # ensure features exist
    for f in features:
        if f not in df.columns:
            df[f] = 0.0

    X = df[features].astype(float)
    y = df["risk"].astype(int).values
    meta = df[["district", "date", "cases", "population", "incidence_per_1000"] + features]
    return X, y, meta


def train_and_save(X, y, meta):
    # Use TimeSeriesSplit for temporal CV
    tss = TimeSeriesSplit(n_splits=5)

    # Candidate estimators: RandomForest, optional LightGBM
    estimators = []
    estimators.append(("rf", RandomForestClassifier(random_state=42)))
    if LGB_AVAILABLE:
        estimators.append(("lgb", lgb.LGBMClassifier(random_state=42)))

    # Build pipeline with scaler + classifier placeholder
    pipeline = Pipeline([("scaler", StandardScaler()), ("clf", RandomForestClassifier(random_state=42))])

    param_distributions = {
        "clf__n_estimators": [100, 200, 400],
        "clf__max_depth": [None, 5, 10, 20],
        "clf__min_samples_split": [2, 5, 10],
        "clf__min_samples_leaf": [1, 2, 4],
        "clf__max_features": ["sqrt", "log2", None],
    }

    # Randomized search
    search = RandomizedSearchCV(pipeline, param_distributions=param_distributions, n_iter=20, cv=tss, scoring="f1_macro", n_jobs=-1, random_state=42, verbose=1)

    print("Starting RandomizedSearchCV (time-series split)...")
    search.fit(X, y)

    best = search.best_estimator_
    best_params = search.best_params_
    best_score = float(search.best_score_)

    # Calibrate probabilities using a held-out split
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)
    # fit best on train portion
    best.fit(X_train, y_train)
    try:
        calibrated = CalibratedClassifierCV(base_estimator=best.named_steps['clf'], cv='prefit')
        # Need to scale X_val
        X_val_scaled = best.named_steps['scaler'].transform(X_val)
        calibrated.fit(X_val_scaled, y_val)
        # wrap calibrated into pipeline
        final_pipeline = Pipeline([('scaler', best.named_steps['scaler']), ('clf', calibrated)])
    except Exception:
        final_pipeline = best

    # Evaluate on validation/test holdout
    X_test = X_val
    y_test = y_val
    y_pred = final_pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()

    # Persist artifacts
    joblib.dump(final_pipeline, OUT_DIR / "pipeline_best.joblib")
    # also save raw best estimator components if present
    try:
        if hasattr(best.named_steps['clf'], 'feature_importances_'):
            joblib.dump(best.named_steps['clf'], OUT_DIR / 'dengue_model_best.pkl')
        joblib.dump(best.named_steps['scaler'], OUT_DIR / 'scaler_best.pkl')
    except Exception:
        pass

    metrics = {
        'search_best_score': best_score,
        'validation_accuracy': float(acc),
        'validation_f1_macro': float(f1),
        'classification_report': report,
        'confusion_matrix': cm,
        'best_params': best_params,
    }

    with open(OUT_DIR / 'metrics_v1.json', 'w', encoding='utf8') as f:
        json.dump(metrics, f, indent=2)
    with open(OUT_DIR / 'best_params_v1.json', 'w', encoding='utf8') as f:
        json.dump(best_params, f, indent=2)

    print("Training complete. Pipeline saved to:", OUT_DIR / 'pipeline_best.joblib')
    print("Metrics saved to:", OUT_DIR / 'metrics_v1.json')


def main():
    data_path = find_data()
    print("Loading data from:", data_path)
    df = load_data(data_path)
    print("Profiling data...")
    profile_data(df)
    X, y, meta = prepare_dataset(df)
    print("Prepared dataset X.shape=", X.shape)
    train_and_save(X, y, meta)


if __name__ == '__main__':
    main()
