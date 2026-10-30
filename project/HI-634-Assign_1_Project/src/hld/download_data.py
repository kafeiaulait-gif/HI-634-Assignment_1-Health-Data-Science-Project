"""
Data Download and Ingestion Script for Heart Disease Dataset
UCI Machine Learning Repository ID: 45
Source URL: https://archive.ics.uci.edu/dataset/45/heart+disease
Download / Access Date: October 29, 2026
"""

import os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "processed.cleveland.data")
RAW_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "heart_disease.csv")

# The 14 official UCI attribute names in documented order:
COLUMN_NAMES = [
    "age",       # 1. Age in years
    "sex",       # 2. Sex (1 = male, 0 = female)
    "cp",        # 3. Chest pain type (1: typical angina, 2: atypical angina, 3: non-anginal pain, 4: asymptomatic)
    "trestbps",  # 4. Resting blood pressure in mm Hg
    "chol",      # 5. Serum cholesterol in mg/dl
    "fbs",       # 6. Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
    "restecg",   # 7. Resting ECG (0: normal, 1: ST-T wave abnormality, 2: left ventricular hypertrophy)
    "thalach",   # 8. Maximum heart rate achieved
    "exang",     # 9. Exercise-induced angina (1 = yes, 0 = no)
    "oldpeak",   # 10. ST depression induced by exercise relative to rest
    "slope",     # 11. Slope of the peak exercise ST segment (1: upsloping, 2: flat, 3: downsloping)
    "ca",        # 12. Number of major vessels (0-3) colored by fluoroscopy
    "thal",      # 13. Thalassemia (3: normal, 6: fixed defect, 7: reversible defect)
    "num"        # 14. Target: angiographic disease status (0: no disease, 1-4: disease severity)
]

def load_cleveland_data():
    """
    Loads processed.cleveland.data with verified 14 column names and handles missing '?' values.
    """
    if os.path.exists(RAW_DATA_PATH):
        print(f"Loading raw headerless data from {RAW_DATA_PATH}...")
        df = pd.read_csv(RAW_DATA_PATH, names=COLUMN_NAMES, na_values="?", header=None)
        return df
    elif os.path.exists(RAW_CSV_PATH):
        print(f"Loading fallback raw data from {RAW_CSV_PATH}...")
        df = pd.read_csv(RAW_CSV_PATH)
        return df
    else:
        # Attempt UCI fetch
        try:
            from ucimlrepo import fetch_ucirepo
            print("Fetching from UCI Machine Learning Repository (ID 45)...")
            heart_disease = fetch_ucirepo(id=45)
            df = pd.concat([heart_disease.data.features, heart_disease.data.targets], axis=1)
            os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
            df.to_csv(RAW_DATA_PATH, header=False, index=False, na_rep="?")
            return df
        except Exception as e:
            raise FileNotFoundError(f"Data file not found and remote download failed: {e}")

if __name__ == "__main__":
    df = load_cleveland_data()
    print(f"Successfully loaded dataset: shape {df.shape}")
    print("\nColumns and Data Types:")
    print(df.dtypes)
    print("\nMissing Values Count:")
    print(df.isna().sum())
    print("\nFirst 5 Records:")
    print(df.head())
