"""
Reproducible Analysis & Figure Generation Script
Generates processed dataset and figure artifacts in reports/figures/
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CLEVELAND_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "processed.cleveland.data")
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "heart_disease.csv")
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "heart_disease_cleaned.csv")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "reports", "figures")

COLUMN_NAMES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"
]

def run_pipeline():
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # 1. Load Data
    if os.path.exists(RAW_CLEVELAND_PATH):
        print(f"Loading raw headerless data from: {RAW_CLEVELAND_PATH}")
        df = pd.read_csv(RAW_CLEVELAND_PATH, names=COLUMN_NAMES, na_values="?", header=None)
    else:
        print(f"Loading raw data from: {RAW_DATA_PATH}")
        df = pd.read_csv(RAW_DATA_PATH)
    
    # 2. Basic Cleaning & Processing
    # Convert 'num' (diagnosis 0-4) to binary disease indicator: 0 = absent, 1 = present (>0)
    df_cleaned = df.copy()
    df_cleaned["target"] = (df_cleaned["num"] > 0).astype(int)
    
    # Save processed data
    df_cleaned.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"Processed dataset saved to: {PROCESSED_DATA_PATH}")
    
    # 3. Generate Summary Table
    summary = df_cleaned.describe().T
    summary_path = os.path.join(FIGURES_DIR, "summary_statistics.csv")
    summary.to_csv(summary_path)
    print(f"Summary table saved to: {summary_path}")
    
    # 4. Generate Figures
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    # Figure 1: Age Distribution by Heart Disease Status
    plt.figure(figsize=(8, 5))
    sns.histplot(
        data=df_cleaned, 
        x="age", 
        hue="target", 
        multiple="stack", 
        kde=True, 
        palette={0: "#2b5c8f", 1: "#d95f02"}
    )
    plt.title("Age Distribution by Heart Disease Status (0 = No Disease, 1 = Disease)")
    plt.xlabel("Age (years)")
    plt.ylabel("Count")
    fig1_path = os.path.join(FIGURES_DIR, "age_distribution.png")
    plt.tight_layout()
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    print(f"Figure 1 saved to: {fig1_path}")
    
    # Figure 2: Correlation Heatmap
    plt.figure(figsize=(10, 8))
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
    corr = df_cleaned[numeric_cols].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="vlag", cbar=True, square=True)
    plt.title("Feature Correlation Matrix")
    fig2_path = os.path.join(FIGURES_DIR, "correlation_matrix.png")
    plt.tight_layout()
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    print(f"Figure 2 saved to: {fig2_path}")
    
    print("Pipeline execution complete. All tables and figures reproduced successfully.")

if __name__ == "__main__":
    run_pipeline()
