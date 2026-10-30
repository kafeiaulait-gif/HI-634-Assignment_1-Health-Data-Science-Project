"""
Data Preprocessing Module for HI-634 Assignment 1: Option 2 (UCI Heart Disease)

Strictly adheres to:
1. Keeping raw data files unchanged.
2. Logging finding, decision, and reason for every data transformation.
3. Defining binary target: 0 = No heart disease, 1 = Heart disease present.
"""

import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "processed.cleveland.data")
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "heart_disease_cleaned.csv")
CHANGELOG_PATH = os.path.join(PROJECT_ROOT, "reports", "cleaning_decisions_log.csv")

COLUMN_NAMES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
]

def load_and_clean_data():
    # 1. Read raw file without modifying original
    print(f"Reading raw data from: {RAW_DATA_PATH}")
    df_raw = pd.read_csv(RAW_DATA_PATH, header=None, names=COLUMN_NAMES, na_values="?")
    
    # 2. Track decisions and rationale
    changelog = [
        {
            "Step": 1,
            "Feature": "Raw Data Ingestion",
            "Finding": "Raw file is headerless and marks missing values as '?'",
            "Decision": "Assigned 14 column names per UCI documentation and parsed '?' as np.nan",
            "Reason": "Ensures column identity alignment and correct pandas null recognition without modifying raw file."
        },
        {
            "Step": 2,
            "Feature": "num (Target variable)",
            "Finding": "Target encoded as 0 (absence) and 1, 2, 3, 4 (stages of coronary disease). Stage 4 has only 13 cases.",
            "Decision": "Binarized target: target = 0 if num == 0 else 1. Retained original num for reference.",
            "Reason": "Aligns with clinical objective of screening for coronary artery disease (>50% stenosis) and benchmark literature."
        },
        {
            "Step": 3,
            "Feature": "ca & thal (Missingness)",
            "Finding": "ca is missing 4 entries (1.32%); thal is missing 2 entries (0.66%). Total 6 rows affected (1.98%).",
            "Decision": "Retained rows in dataset; deferred imputation to scikit-learn Pipeline (fit strictly on training fold).",
            "Reason": "Preserves sample size (N=303) and strictly prevents data leakage across train/test splits."
        },
        {
            "Step": 4,
            "Feature": "chol (Cholesterol Outliers)",
            "Finding": "Row 152 has cholesterol of 564 mg/dl; 3 other patients > 400 mg/dl.",
            "Decision": "Preserved values as authentic clinical records; applied Robust/StandardScaler inside model pipeline.",
            "Reason": "Severe hypercholesterolemia is physiologically real; scaling prevents distance-based distortion without discarding valid clinical data."
        },
        {
            "Step": 5,
            "Feature": "cp, restecg, thal (Nominal Variables)",
            "Finding": "Categorical variables coded as integers (e.g. cp=1..4, restecg=0..2, thal=3,6,7) imply false numerical hierarchy if unencoded.",
            "Decision": "Designated nominal variables for One-Hot Encoding within training pipeline; binary features (sex, fbs, exang) kept as 0/1.",
            "Reason": "Prevents linear and distance models from interpreting arbitrary categorical integer codes as continuous magnitudes."
        }
    ]
    
    # 3. Create cleaned dataframe
    df_cleaned = df_raw.copy()
    df_cleaned["target"] = (df_cleaned["num"] > 0).astype(int)
    
    # Save processed dataset
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df_cleaned.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Cleaned data saved to: {PROCESSED_DATA_PATH} (Shape: {df_cleaned.shape})")
    
    # Save changelog
    os.makedirs(os.path.dirname(CHANGELOG_PATH), exist_ok=True)
    df_changelog = pd.DataFrame(changelog)
    df_changelog.to_csv(CHANGELOG_PATH, index=False)
    print(f"Cleaning decisions log saved to: {CHANGELOG_PATH}")
    
    return df_cleaned, df_changelog

if __name__ == "__main__":
    df, log = load_and_clean_data()
    print("\nDecision Changelog Summary:")
    print(log[["Step", "Feature", "Decision"]])
