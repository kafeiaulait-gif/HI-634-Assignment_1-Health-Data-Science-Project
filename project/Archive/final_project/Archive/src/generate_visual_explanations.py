"""
Generate Three Visuals for Prompt 5:
1. Data Quality & Missingness (fig1_data_quality_missingness.png)
2. Distribution / Clinical Relationship (fig2_clinical_relationship.png)
3. Chosen Model Results & Diagnostic Error Analysis (fig3_model_error_analysis.png)
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
from src.model_pipeline import build_preprocessor, RandomForestClassifier

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(PROJECT_ROOT, "reports", "figures")
EXPLANATION_DIR = os.path.join(PROJECT_ROOT, "explanation")

os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(EXPLANATION_DIR, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# Load raw and cleaned data
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "processed.cleveland.data")
cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'num']
df_raw = pd.read_csv(RAW_PATH, header=None, names=cols, na_values='?')

# =========================================================================
# VISUAL 1: Data Quality & Missingness
# =========================================================================
fig, ax = plt.subplots(figsize=(10, 5))
missing_counts = df_raw.isna().sum()
total_rows = len(df_raw)
complete_counts = total_rows - missing_counts
pct_complete = (complete_counts / total_rows) * 100

colors = ['#2ca02c' if m == 0 else '#d95f02' for m in missing_counts]
bars = ax.barh(cols, pct_complete, color=colors, edgecolor='black', alpha=0.85)

ax.set_xlim(95, 100.5)
ax.set_xlabel("Data Completeness Rate (%)", fontsize=11, fontweight='bold')
ax.set_ylabel("Clinical Attribute", fontsize=11, fontweight='bold')
ax.set_title("Figure 1: Attribute Data Completeness & Missing Value Audit\nCleveland Clinic Cohort (N = 303 Patient Records)", fontsize=13, fontweight='bold')

for bar, m in zip(bars, missing_counts):
    width = bar.get_width()
    if m > 0:
        ax.text(width - 0.2, bar.get_y() + bar.get_height()/2, f"Missing: {m} ({m/total_rows*100:.1f}%)", 
                va='center', ha='right', color='white', fontweight='bold', fontsize=9)
    else:
        ax.text(99.9, bar.get_y() + bar.get_height()/2, "100% Complete (0 missing)", 
                va='center', ha='right', color='black', fontsize=8)

plt.tight_layout()
fig1_path = os.path.join(FIGURES_DIR, "fig1_data_quality_missingness.png")
fig1_exp = os.path.join(EXPLANATION_DIR, "fig1_data_quality_missingness.png")
plt.savefig(fig1_path, dpi=300)
plt.savefig(fig1_exp, dpi=300)
plt.close()
print("Saved Visual 1")

# Add target column after Figure 1
df_raw['target'] = (df_raw['num'] > 0).astype(int)

# =========================================================================
# VISUAL 2: Clinical Distribution & Relationship
# =========================================================================
plt.figure(figsize=(9, 6))
palette = {0: "#1f77b4", 1: "#d95f02"}

scatter = sns.scatterplot(
    data=df_raw,
    x="thalach",
    y="oldpeak",
    hue="target",
    palette=palette,
    alpha=0.85,
    s=70,
    edgecolor="black",
    linewidth=0.5
)

# Overlay kde contour lines to show density separation
sns.kdeplot(
    data=df_raw[df_raw['target']==0], x="thalach", y="oldpeak",
    color="#1f77b4", levels=4, alpha=0.4, linewidths=1.5
)
sns.kdeplot(
    data=df_raw[df_raw['target']==1], x="thalach", y="oldpeak",
    color="#d95f02", levels=4, alpha=0.4, linewidths=1.5
)

plt.axvline(150, color='gray', linestyle=':', alpha=0.7)
plt.axhline(1.0, color='gray', linestyle=':', alpha=0.7)

plt.title("Figure 2: Exercise ST Depression vs. Peak Heart Rate by Cardiac Outcome\nCleveland Clinic Cohort (N = 303 Patient Records)", fontsize=13, fontweight='bold')
plt.xlabel("Maximum Heart Rate Achieved - thalach (beats/min)", fontsize=11, fontweight='bold')
plt.ylabel("ST Depression Induced by Exercise - oldpeak (mm)", fontsize=11, fontweight='bold')
plt.legend(
    title="Clinical Status",
    labels=["Absence (<50% Stenosis)", "Presence (>50% Stenosis)"],
    loc="upper right",
    frameon=True
)
plt.tight_layout()
fig2_path = os.path.join(FIGURES_DIR, "fig2_clinical_relationship.png")
fig2_exp = os.path.join(EXPLANATION_DIR, "fig2_clinical_relationship.png")
plt.savefig(fig2_path, dpi=300)
plt.savefig(fig2_exp, dpi=300)
plt.close()
print("Saved Visual 2")

# =========================================================================
# VISUAL 3: Chosen Result & Diagnostic Error Analysis (Random Forest)
# =========================================================================
X = df_raw.drop(columns=['num', 'target'])
y = df_raw['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

from sklearn.pipeline import Pipeline
rf_pipe = Pipeline([
    ('preprocessor', build_preprocessor()),
    ('classifier', RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42))
])
rf_pipe.fit(X_train, y_train)

y_pred = rf_pipe.predict(X_test)
y_prob = rf_pipe.predict_proba(X_test)[:, 1]

cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
auc_score = roc_auc_score(y_test, y_prob)

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# Panel A: Labeled Confusion Matrix
labels = [
    [f"True Negative (TN)\n{tn} Patients (49.2%)\nCorrectly Ruled Out", f"False Positive (FP)\n{fp} Patients (4.9%)\nType I Error: Unneeded Angiogram"],
    [f"False Negative (FN)\n{fn} Patients (3.3%)\nType II Error: Missed Disease", f"True Positive (TP)\n{tp} Patients (42.6%)\nCorrectly Identified Disease"]
]
sns.heatmap(cm, annot=labels, fmt="", cmap="Blues", cbar=False, ax=axes[0], annot_kws={"size": 10, "weight": "bold"})
axes[0].set_title(f"A. Diagnostic Error Distribution on Test Set (N = 61)\nAccuracy: 91.8% | Sensitivity: 92.9% | Specificity: 90.9%", fontsize=11, fontweight="bold")
axes[0].set_xlabel("Predicted Diagnostic Label", fontsize=11, fontweight="bold")
axes[0].set_ylabel("True Angiographic Diagnosis", fontsize=11, fontweight="bold")
axes[0].set_xticklabels(["Absence (0)", "Presence (1)"])
axes[0].set_yticklabels(["Absence (0)", "Presence (1)"])

# Panel B: ROC Curve with Operating Point
axes[1].plot(fpr, tpr, color="#2ca02c", lw=2.5, label=f"Random Forest (AUC = {auc_score:.3f})")
axes[1].plot([0, 1], [0, 1], "k--", lw=1.5, label="Chance Baseline (AUC = 0.500)")
# Mark operating threshold point (FP rate = 3/33, TP rate = 26/28)
op_fpr = fp / (tn + fp)
op_tpr = tp / (tp + fn)
axes[1].scatter([op_fpr], [op_tpr], color="red", s=120, zorder=5, label=f"Clinical Operating Point\n(Sens={op_tpr:.1%}, Spec={1-op_fpr:.1%})")
axes[1].set_xlim([0.0, 1.0])
axes[1].set_ylim([0.0, 1.05])
axes[1].set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11, fontweight="bold")
axes[1].set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11, fontweight="bold")
axes[1].set_title(f"B. Receiver Operating Characteristic (ROC) Curve\nDiscriminative Capacity on Test Partition (N = 61)", fontsize=11, fontweight="bold")
axes[1].legend(loc="lower right", frameon=True)

plt.suptitle("Figure 3: Random Forest Evaluation & Diagnostic Error Characterization", fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
fig3_path = os.path.join(FIGURES_DIR, "fig3_model_error_analysis.png")
fig3_exp = os.path.join(EXPLANATION_DIR, "fig3_model_error_analysis.png")
plt.savefig(fig3_path, dpi=300, bbox_inches="tight")
plt.savefig(fig3_exp, dpi=300, bbox_inches="tight")
plt.close()
print("Saved Visual 3")
