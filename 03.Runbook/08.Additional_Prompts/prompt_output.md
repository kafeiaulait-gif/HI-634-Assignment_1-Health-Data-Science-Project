# HI-634 Assignment 1: Option 2 — UCI Heart Disease
## Complete Comprehensive Output & Technical Report

**Course:** HI-634 Health Informatics  
**Assignment:** Assignment 1 — Option 2: UCI Heart Disease Classification  
**Date:** October 29, 2026  
**Environment:** Python 3.13.5 inside local `.venv`  
**Dataset:** Cleveland Clinic Heart Disease Database (UCI Machine Learning Repository, ID 45)  
**Author / Workspace:** `/home/kafeiaulait/HI-634-Assign_1_Project`

---

## Table of Contents
1. [Environment Setup & Shell Diagnostics](#1-environment-setup--shell-diagnostics)
2. [Project File Inventory & Git Configuration](#2-project-file-inventory--git-configuration)
3. [Data Provenance & Official 14-Attribute Codebook](#3-data-provenance--official-14-attribute-codebook)
4. [Exploratory Data Audit & Data Quality Findings](#4-exploratory-data-audit--data-quality-findings)
5. [Data Cleaning Decisions Changelog](#5-data-cleaning-decisions-changelog)
6. [Target Definition & Statistical Distinguishability](#6-target-definition--statistical-distinguishability)
7. [Zero-Leakage Pipeline Architecture](#7-zero-leakage-pipeline-architecture)
8. [Cross-Validation & Test Set Model Comparison](#8-cross-validation--test-set-model-comparison)
9. [Clinical Interpretation of Diagnostic Errors (FP vs. FN)](#9-clinical-interpretation-of-diagnostic-errors-fp-vs-fn)
10. [Model Selection: Performance vs. Interpretability](#10-model-selection-performance-vs-interpretability)
11. [Generated Visual Artifacts Inventory](#11-generated-visual-artifacts-inventory)
12. [Reproduction Instructions](#12-reproduction-instructions)

---

## 1. Environment Setup & Shell Diagnostics

### 1.1 Python Runtime & Virtual Environment Verification
* **Virtual Environment Path:** `/home/kafeiaulait/HI-634-Assign_1_Project/.venv`
* **Python Executable:** `/home/kafeiaulait/HI-634-Assign_1_Project/.venv/bin/python`
* **Python Version:** `3.13.5` (GCC 14.2.0, 64-bit Linux)
* **Base System Python:** `/usr/bin/python3` (Debian 13 Trixie)
* **Site-Packages Path:** `/home/kafeiaulait/HI-634-Assign_1_Project/.venv/lib/python3.13/site-packages`
* **Venv Isolation Check:** `sys.prefix != sys.base_prefix` evaluates to **`True`**.

### 1.2 Commands Executed for Environment Inspection
```bash
# 1. Virtual environment runtime diagnostics
.venv/bin/python -c "import sys, platform, site; print(f'Version: {sys.version}'); print(f'Executable: {sys.executable}'); print(f'Prefix: {sys.prefix}'); print(f'Base Prefix: {sys.base_prefix}'); print(f'Site Packages: {site.getsitepackages()}'); print(f'Platform: {platform.platform()}'); print(f'Architecture: {platform.architecture()}')"

# 2. Installed packages in virtual environment
.venv/bin/pip list

# 3. Operating system and shell details
which python3 && python3 --version && echo "User: $(whoami)" && echo "Shell: $SHELL ($BASH_VERSION)" && echo "Working Dir: $(pwd)" && cat /etc/os-release | grep -E '^(NAME|VERSION)='
```

### 1.3 Troubleshooting Virtual Environment Activation Across Operating Systems
| OS / Shell | Common Error Message | Cause & Explanation | Direct Fallback Workaround |
| :--- | :--- | :--- | :--- |
| **Linux / POSIX (Direct execution)** | `bash: .venv/bin/activate: Permission denied` | Running `.venv/bin/activate` directly as an executable instead of sourcing (`source` or `.`). Activation scripts modify the calling shell's state and do not have execution permissions. | Invoke Python directly from the environment:<br>`./.venv/bin/python script.py` |
| **Linux (POSIX `sh` / Dash)** | `sh: 1: source: not found` | The standard `/bin/sh` shell does not support the bash-specific `source` keyword. | Use the POSIX dot command or invoke directly:<br>`. .venv/bin/activate` or `./.venv/bin/python` |
| **Windows (PowerShell)** | `File ... activate.ps1 cannot be loaded because running scripts is disabled on this system` (`PSSecurityException`) | PowerShell's default execution policy (`Restricted`) prohibits running unsigned external automation scripts. | Temporarily bypass policy or execute directly:<br>`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`<br>or `.\.venv\Scripts\python.exe` |
| **Subshell Runners / CI Pipelines** | *Environment reverts to system Python on next command* | Automated runners spawn independent child subshells per step; environment variable mutations do not persist across steps. | Always target the absolute or relative interpreter path directly:<br>`/home/kafeiaulait/HI-634-Assign_1_Project/.venv/bin/python` |

---

## 2. Project File Inventory & Git Configuration

### 2.1 Workspace Directory Structure
```text
HI-634-Assign_1_Project/
├── .gitignore                          # Configured to ignore .venv, caches, checkpoints
├── requirements.txt                    # Pinned project dependencies
├── README.md                           # Replication guide and dataset documentation
├── prompt_output.md                    # Consolidated technical export of all results
├── data/
│   ├── raw/
│   │   ├── processed.cleveland.data    # Primary raw UCI headerless file (? for missing)
│   │   └── heart_disease.csv           # Raw CSV archive (kept unchanged)
│   └── processed/
│       └── heart_disease_cleaned.csv   # Cleaned dataset with engineered binary target
├── notebooks/
│   └── exploratory_data_analysis.ipynb # Executed interactive analysis notebook
├── src/
│   ├── download_data.py                # Ingestion and raw data integrity verification
│   ├── data_preprocessing.py           # Preprocessing pipeline and decision logger
│   └── model_pipeline.py               # Leakage-free training, CV, testing, and figure generator
└── reports/
    ├── cleaning_decisions_log.csv      # Structured audit of all data cleaning decisions
    └── figures/
        ├── age_distribution.png        # Figure: Age distribution by disease status
        ├── correlation_matrix.png      # Figure: Clinical feature correlation heatmap
        ├── outcome_distinguishability.png # Figure: Key predictors by binary outcome
        ├── roc_curves_comparison.png   # Figure: Multi-model ROC curves with AUC labels
        ├── confusion_matrices_comparison.png # Figure: Side-by-side confusion matrices
        ├── confusion_matrices_baseline_rf.png # Figure: Majority baseline vs. models
        ├── model_metrics_comparison.png# Figure: Bar chart of performance metrics
        ├── feature_importance_comparison.png # Figure: Top 10 Random Forest predictors
        ├── summary_statistics.csv      # Table: Continuous attribute descriptive stats
        └── model_performance_table.csv # Table: Comprehensive model evaluation metrics
```

### 2.2 `.gitignore` Configuration
The [`.gitignore`](file:///home/kafeiaulait/HI-634-Assign_1_Project/.gitignore) file was configured to prevent committing virtual environment binaries, operating system artifacts, and temporary bytecode caches:
```gitignore
# Virtual Environment
.venv/
venv/
ENV/
env/

# Python bytecode and cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Jupyter Notebook checkpoints
.ipynb_checkpoints/

# Temporary / OS files
.DS_Store
Thumbs.db
*.tmp
```

---

## 3. Data Provenance & Official 14-Attribute Codebook

### 3.1 Data Source Details
* **Database Name:** Heart Disease Dataset (Cleveland Clinic Foundation)
* **Official Repository:** UCI Machine Learning Repository
* **Dataset Identifier:** UCI Repo ID `45`
* **Download Page URL:** [https://archive.ics.uci.edu/dataset/45/heart+disease](https://archive.ics.uci.edu/dataset/45/heart+disease)
* **Original Study Investigators:** Robert Detrano, M.D., Ph.D., et al. (Cleveland Clinic Foundation and V.A. Medical Center, Long Beach)
* **Date Downloaded / Verified:** October 29, 2026
* **Single-Center Scope:** Restricted strictly to the Cleveland Clinic cohort ($N = 303$). The other three centers from the repository (Hungarian, Long Beach, Zurich) were intentionally excluded to preserve institutional protocol consistency.

### 3.2 The 14 Attributes in Documented Order
From `heart-disease.names`, the 14 attributes utilized across published machine learning benchmarks are:

| Col # | Attribute Name | Measurement Type | Clinical Definition & Value Encodings |
| :-: | :--- | :--- | :--- |
| **1** | `age` | Continuous (Years) | Patient age (range: 29 to 77) |
| **2** | `sex` | Binary | Biological sex (`1` = Male; `0` = Female) |
| **3** | `cp` | Nominal (Categorical) | Chest pain type:<br>• `1`: Typical angina<br>• `2`: Atypical angina<br>• `3`: Non-anginal pain<br>• `4`: Asymptomatic |
| **4** | `trestbps` | Continuous (mm Hg) | Resting blood pressure on admission to the hospital |
| **5** | `chol` | Continuous (mg/dl) | Serum cholesterol level |
| **6** | `fbs` | Binary | Fasting blood sugar > 120 mg/dl (`1` = True; `0` = False) |
| **7** | `restecg` | Nominal (Categorical) | Resting electrocardiographic results:<br>• `0`: Normal<br>• `1`: Having ST-T wave abnormality (T wave inversions / ST elevation or depression > 0.05 mV)<br>• `2`: Showing probable or definite left ventricular hypertrophy (Estes' criteria) |
| **8** | `thalach` | Continuous (bpm) | Maximum heart rate achieved during exercise treadmill test |
| **9** | `exang` | Binary | Exercise-induced angina (`1` = Yes; `0` = No) |
| **10** | `oldpeak` | Continuous (mm) | ST depression induced by exercise relative to rest |
| **11** | `slope` | Ordinal | Slope of peak exercise ST segment:<br>• `1`: Upsloping<br>• `2`: Flat<br>• `3`: Downsloping |
| **12** | `ca` | Discrete Count (0–3) | Number of major coronary vessels colored by fluoroscopy *(Contains 4 missing `'?'` values)* |
| **13** | `thal` | Nominal (Categorical) | Thallium heart scan / scintigraphy:<br>• `3.0`: Normal<br>• `6.0`: Fixed defect<br>• `7.0`: Reversible defect *(Contains 2 missing `'?'` values)* |
| **14** | `num` | Ordinal / Target (0–4) | Angiographic disease status (coronary artery diameter narrowing):<br>• `0`: < 50% stenosis (absence of significant disease)<br>• `1, 2, 3, 4`: > 50% stenosis in 1, 2, 3, or 4 vessels |

---

## 4. Exploratory Data Audit & Data Quality Findings

### 4.1 Cohort Volume, Duplicates, and Missingness
* **Total Instances:** 303 rows
* **Total Attributes:** 14 columns
* **Duplicate Rows:** **0 duplicate rows (0.00%)**. Every patient record is unique.
* **Missing Value Characters:** Exactly **6 `'?'` characters** appear in the raw text file:
  * `ca`: 4 missing entries (1.32%) — Rows 166, 192, 287, 302
  * `thal`: 2 missing entries (0.66%) — Rows 87, 266
  * All remaining 12 attributes: 0 missing entries (0.00%)
* **Complete-Case Prevalence:** 297 out of 303 patients (98.02%) have complete records.

### 4.2 Continuous Numerical Feature Distributions
| Feature | Count | Mean $\pm$ SD | Median (IQR) | Min – Max | Clinical Reference Context |
| :--- | :-: | :-: | :-: | :-: | :--- |
| **`age`** | 303 | $54.44 \pm 9.04$ | 56.0 (13.0) | 29.0 – 77.0 | Representative of cardiovascular evaluation cohorts. |
| **`trestbps`** | 303 | $131.69 \pm 17.60$ | 130.0 (20.0) | 94.0 – 200.0 | Stage 1/2 hypertension present in upper quartiles; max indicates acute hypertensive crisis. |
| **`chol`** | 303 | $246.69 \pm 51.78$ | 241.0 (64.0) | 126.0 – 564.0 | Elevated median; extreme right-tail skewness (Patient 152 at 564 mg/dl; 4 patients > 400 mg/dl). |
| **`thalach`** | 303 | $149.61 \pm 22.88$ | 153.0 (32.5) | 71.0 – 202.0 | Expected treadmill stress test response. |
| **`oldpeak`** | 303 | $1.04 \pm 1.16$ | 0.80 (1.60) | 0.00 – 6.20 | 99 patients (32.7%) exhibit 0.0 mm (no exercise ST depression). |

### 4.3 Categorical Feature Distributions
* **`sex`:** 206 Males (68.0%), 97 Females (32.0%)
* **`cp` (Chest Pain Type):**
  * `1` (Typical angina): 23 (7.59%)
  * `2` (Atypical angina): 50 (16.50%)
  * `3` (Non-anginal pain): 86 (28.38%)
  * `4` (Asymptomatic): **144 (47.52%)** — *Highest single presentation*
* **`fbs` (Fasting Blood Sugar > 120 mg/dl):** 0 = 258 (85.15%), 1 = 45 (14.85%)
* **`restecg`:** `0` (Normal) = 151 (49.83%), `1` (ST-T abnormality) = **4 (1.32%)**, `2` (LVH) = 148 (48.84%)
* **`exang` (Exercise Angina):** `0` = 204 (67.33%), `1` = 99 (32.67%)
* **`slope`:** `1` (Upsloping) = 142 (46.86%), `2` (Flat) = 140 (46.20%), `3` (Downsloping) = 21 (6.93%)
* **`ca`:** 0 vessels = 176 (58.09%), 1 = 65 (21.45%), 2 = 38 (12.54%), 3 = 20 (6.60%), Missing = 4 (1.32%)
* **`thal`:** `3.0` (Normal) = 166 (54.79%), `6.0` (Fixed defect) = 18 (5.94%), `7.0` (Reversible defect) = 117 (38.61%), Missing = 2 (0.66%)

---

## 5. Data Cleaning Decisions Changelog

Every preprocessing step was formally recorded in [`reports/cleaning_decisions_log.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/cleaning_decisions_log.csv):

| Step | Feature / Phase | Observed Finding | Action / Decision Taken | Methodological & Clinical Justification |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Raw File Ingestion** | Headerless CSV format; missing entries coded as `'?'`. | Assigned 14 column names per UCI documentation; parsed `'?'` as `np.nan`. Kept raw file immutable. | Guarantees exact column alignment and valid missing-value handling in pandas without altering raw provenance. |
| **2** | **Target (`num`) Definition** | Multi-class outcome (0 to 4); stage 4 has only 13 cases. | Binarized: $\text{target} = 1$ if $num > 0$ else $0$. Retained original `num` in dataset. | Matches the primary diagnostic threshold (>50% coronary narrowing) and published benchmark literature. |
| **3** | **Missingness Handling (`ca`, `thal`)** | `ca` missing 4 entries (1.32%); `thal` missing 2 entries (0.66%). Total 6 rows affected (1.98%). | Retained all 303 rows; deferred imputation to scikit-learn `Pipeline`. | Eliminates data leakage by fitting imputers (median for `ca`, mode for `thal`) strictly on `X_train`. |
| **4** | **Cholesterol Outliers (`chol`)** | Row 152 has cholesterol of 564 mg/dl; 3 others > 400 mg/dl. | Kept authentic clinical records; applied `StandardScaler` inside pipeline. | Severe hypercholesterolemia is clinically valid; scaling prevents distance distortion without discarding true patient signals. |
| **5** | **Nominal Encoding (`cp`, `restecg`, `thal`)** | Integer codes imply arbitrary continuous numerical magnitudes. | Applied `OneHotEncoder(drop='first')` inside `ColumnTransformer`. | Prevents linear and distance models from treating discrete categories as continuous quantities. |

---

## 6. Target Definition & Statistical Distinguishability

### 6.1 Binary Label Formulation & Prevalence
The clinical target was engineered as:
$$\text{target} = \begin{cases} 0, & \text{if } num = 0 \quad (\text{Absence: } < 50\% \text{ coronary stenosis}) \\ 1, & \text{if } num \in \{1, 2, 3, 4\} \quad (\text{Presence: } > 50\% \text{ coronary stenosis}) \end{cases}$$

* **Absence (`target = 0`):** 164 patients (**54.13%**)
* **Presence (`target = 1`):** 139 patients (**45.87%**)
* **Class Balance:** Naturally well-balanced ($1.18 : 1$), providing sufficient sample representation for both classes without synthetic rebalancing.

### 6.2 Statistical Distinguishability Tests

#### Continuous Attributes (Welch's Two-Sample t-Tests):
* **`thalach` (Max Heart Rate):** Absence = $158.38 \pm 19.20$ bpm vs. Presence = $139.26 \pm 22.59$ bpm ($t = 7.78, \mathbf{p = 9.11 \times 10^{-14}}$)
* **`oldpeak` (ST Depression):** Absence = $0.59 \pm 0.78$ mm vs. Presence = $1.57 \pm 1.30$ mm ($t = -7.71, \mathbf{p = 2.20 \times 10^{-13}}$)
* **`age`:** Absence = $52.59 \pm 9.51$ yrs vs. Presence = $56.63 \pm 7.94$ yrs ($t = -4.05, \mathbf{p = 7.06 \times 10^{-5}}$)
* **`trestbps` (Resting BP):** Absence = $129.25 \pm 16.20$ mm Hg vs. Presence = $134.57 \pm 18.77$ mm Hg ($t = -2.62, \mathbf{p = 0.0094}$)
* **`chol` (Cholesterol):** Absence = $242.64 \pm 53.46$ mg/dl vs. Presence = $251.47 \pm 49.49$ mg/dl ($t = -1.49, p = 0.137$)

#### Categorical Attributes ($\chi^2$ Contingency Tests):
* **`thal` (Thallium Scan):** $\chi^2 = 83.29, \text{dof} = 2, \mathbf{p = 8.20 \times 10^{-19}}$ (Reversible defect exhibits 75.2% disease rate vs 21.7% in normal scans)
* **`cp` (Chest Pain Type):** $\chi^2 = 81.82, \text{dof} = 3, \mathbf{p = 1.25 \times 10^{-17}}$ (Asymptomatic presentation exhibits 72.9% disease rate)
* **`ca` (Fluoroscopy Vessels):** $\chi^2 = 71.84, \text{dof} = 3, \mathbf{p = 1.72 \times 10^{-15}}$ (Having $\ge 1$ vessel colored carries 82.7% disease rate)
* **`exang` (Exercise Angina):** $\chi^2 = 54.69, \text{dof} = 1, \mathbf{p = 1.41 \times 10^{-13}}$ (Angina during exercise carries 76.8% disease rate)
* **`slope` (ST Slope):** $\chi^2 = 45.78, \text{dof} = 2, \mathbf{p = 1.14 \times 10^{-10}}$
* **`sex`:** $\chi^2 = 22.04, \text{dof} = 1, \mathbf{p = 2.67 \times 10^{-6}}$ (Males exhibit 55.3% disease rate vs 25.8% for females)
* **`fbs` (Fasting Blood Sugar):** $\chi^2 = 0.08, \text{dof} = 1, p = 0.781$ (Not independently predictive)

---

## 7. Zero-Leakage Pipeline Architecture

To ensure strict experimental integrity and prevent test-set contamination:
1. **Holdout Partitioning Occurs Prior to Any Transformation:**
   ```python
   X_train, X_test, y_train, y_test = train_test_split(
       X, y, test_size=0.20, random_state=42, stratify=y
   )
   ```
   * Training split: $N = 242$ patients (131 absence, 111 presence; 45.87% positive)
   * Test split: $N = 61$ patients (33 absence, 28 presence; 45.90% positive)
2. **Encapsulated Preprocessing (`ColumnTransformer`):**
   ```python
   preprocessor = ColumnTransformer(transformers=[
       ('num', Pipeline([('imputer', SimpleImputer(strategy='median')),
                         ('scaler', StandardScaler())]), numeric_features),
       ('nom', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')),
                         ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))]), nominal_features),
       ('ord', Pipeline([('imputer', SimpleImputer(strategy='median')),
                         ('scaler', StandardScaler())]), ordinal_features),
       ('bin', Pipeline([('imputer', SimpleImputer(strategy='most_frequent'))]), binary_features)
   ])
   ```
3. **Empirical Verification of Zero Contamination:**
   * Scaler mean for `age` on `X_train`: **54.550** (distinct from full cohort mean **54.439**).
   * Scaler mean for `chol` on `X_train`: **249.839** (distinct from full cohort mean **246.693**).
   * All imputation statistics and dummy categories were learned strictly from `X_train`.

---

## 8. Cross-Validation & Test Set Model Comparison

### 8.1 5-Fold Stratified Cross-Validation on Training Partition ($N = 242$)
| Model | CV Accuracy | CV Precision | CV Recall (Sensitivity) | CV F1-Score | CV ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Majority Baseline** (`Dummy`) | $0.541 \pm 0.006$ | $0.000 \pm 0.000$ | $0.000 \pm 0.000$ | $0.000 \pm 0.000$ | $0.500 \pm 0.000$ |
| **Logistic Regression** ($L_2$) | **$0.835 \pm 0.014$** | **$0.862 \pm 0.042$** | **$0.766 \pm 0.035$** | **$0.809 \pm 0.015$** | **$0.906 \pm 0.011$** |
| **Random Forest** ($100$ trees, depth 4) | $0.822 \pm 0.023$ | $0.843 \pm 0.064$ | $0.765 \pm 0.074$ | $0.797 \pm 0.028$ | $0.890 \pm 0.017$ |
| **Gradient Boosting** ($100$ trees, lr 0.05)| $0.806 \pm 0.025$ | $0.812 \pm 0.051$ | $0.757 \pm 0.052$ | $0.781 \pm 0.031$ | $0.856 \pm 0.023$ |

### 8.2 Final Evaluation on Unseen Test Set ($N = 61$)
**Positive Class: Heart Disease Present (`target = 1`, $>50\%$ diameter stenosis)**  
*(Test cohort contains 33 true absence, 28 true presence)*

| Evaluation Metric | Majority-Class Baseline | Logistic Regression | **Random Forest (Selected)** | Gradient Boosting |
| :--- | :---: | :---: | :---: | :---: |
| **Test Accuracy** | 54.1% | 88.5% | **91.8%** | 85.2% |
| **Precision** | 0.0% | 83.9% | **89.7%** | 80.6% |
| **Recall / Sensitivity** | 0.0% | **92.9%** | **92.9%** | 89.3% |
| **Specificity** | 100.0% | 84.8% | **90.9%** | 81.8% |
| **F1-Score** | 0.000 | 0.881 | **0.912** | 0.847 |
| **ROC-AUC** | 0.500 | 0.958 | **0.959** | 0.948 |
| **True Negatives (TN)** | 33 | 28 | **30** | 27 |
| **False Positives (FP)** | 0 | 5 | **3** | 6 |
| **False Negatives (FN)** | 28 | **2** | **2** | 3 |
| **True Positives (TP)** | 0 | **26** | **26** | 25 |

---

## 9. Clinical Interpretation of Diagnostic Errors (FP vs. FN)

* **False Positive (Type I Diagnostic Error):**
  * *Clinical Definition:* A patient without significant coronary artery stenosis ($<50\%$) is incorrectly predicted to have heart disease.
  * *Clinical Impact:* Causes emotional anxiety and prompts referral for invasive confirmatory testing (coronary catheterization/angiography). Invasive angiography carries risks of arterial dissection, retroperitoneal bleeding, radiocontrast-induced nephropathy, and allergic reactions, as well as institutional costs. Random Forest minimized false positives down to **only 3 patients** out of 33 healthy controls (90.9% specificity).
* **False Negative (Type II Diagnostic Error):**
  * *Clinical Definition:* A patient with clinically significant coronary narrowing ($>50\%$) is incorrectly classified as disease-free.
  * *Clinical Impact:* **The most dangerous error in cardiovascular medicine.** The patient is falsely reassured and discharged without secondary cardioprotective medical therapy (statins, beta-blockers, ACE inhibitors, aspirin) or revascularization (PCI/CABG). The untreated coronary lesion leaves the patient vulnerable to acute plaque rupture, fatal myocardial infarction, or sudden cardiac death. Both Random Forest and Logistic Regression minimized false negatives down to **only 2 patients** out of 28 diseased individuals (**92.9% Sensitivity**).

---

## 10. Model Selection: Performance vs. Interpretability

### 10.1 Selected Model: Random Forest Classifier
* **Performance Superiority:** Achieved the highest overall accuracy (**91.8%**), highest F1-score (**0.912**), and lowest total misclassifications (5 out of 61 patients).
* **Diagnostic Balance:** Delivered high sensitivity (**92.9%**) while achieving **90.9% specificity**, outperforming Logistic Regression by reducing false positives from 5 to 3 without increasing false negatives.
* **Top Clinical Predictors (Gini Importance):**
  1. `ca` (Fluoroscopy vessel count) — Dominant anatomical predictor
  2. `thal` (Thallium scan reversible/fixed defect) — Dominant perfusion predictor
  3. `cp_4` (Asymptomatic chest pain presentation) — Clinical paradox predictor
  4. `oldpeak` (Exercise-induced ST depression) — Functional ischemic predictor
  5. `thalach` (Peak heart rate achieved) — Chronotropic reserve predictor

### 10.2 Role of Logistic Regression
* **Interpretability Value:** Logistic Regression provides direct, transparent odds ratios ($\text{OR} = e^{\beta}$) for every clinical measurement, allowing clinicians to inspect additive linear risk weights.
* **Clinical Synthesis:** Random Forest is recommended as the operational risk-scoring model, with Logistic Regression serving as an explainable mechanistic benchmark.

---

## 11. Generated Visual Artifacts Inventory

All figures are rendered at 300 DPI in [`reports/figures/`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/):

1. **[`outcome_distinguishability.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/outcome_distinguishability.png):** 4-panel figure illustrating maximum heart rate boxplots, exercise ST depression boxplots, chest pain type distributions, and thallium scan distributions stratified by binary disease outcome.
2. **[`roc_curves_comparison.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/roc_curves_comparison.png):** Multi-model ROC curves plotting True Positive Rate vs. False Positive Rate for Logistic Regression, Random Forest, and Gradient Boosting with labeled AUC values.
3. **[`confusion_matrices_comparison.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/confusion_matrices_comparison.png):** 3-panel side-by-side heatmaps displaying True Negatives, False Positives, False Negatives, and True Positives on the unseen test set.
4. **[`confusion_matrices_baseline_rf.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/confusion_matrices_baseline_rf.png):** Direct visual comparison between the Majority-Class Baseline, Logistic Regression, and the Selected Random Forest model.
5. **[`model_metrics_comparison.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/model_metrics_comparison.png):** Grouped bar chart comparing Test Accuracy, Sensitivity, Specificity, F1-Score, and ROC-AUC across all models.
6. **[`feature_importance_comparison.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/feature_importance_comparison.png):** Horizontal bar chart ranking the top 10 clinical features by Gini importance.
7. **[`age_distribution.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/age_distribution.png):** Age histogram and KDE stratified by disease presence.
8. **[`correlation_matrix.png`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/correlation_matrix.png):** Full feature correlation heatmap across clinical variables.

---

## 12. Reproduction Instructions

To reproduce all tables, statistics, models, and figures from a clean checkout:

```bash
# 1. Activate the local virtual environment
source .venv/bin/activate

# 2. Verify / install dependencies
python -m pip install -r requirements.txt

# 3. Verify raw data ingestion & codebook
python src/download_data.py

# 4. Run data preprocessing and generate decisions changelog
python src/data_preprocessing.py

# 5. Train all models, perform 5-fold CV, evaluate test set, and render figures
MPLCONFIGDIR=/tmp python src/model_pipeline.py

# 6. Execute the complete interactive Jupyter notebook
MPLCONFIGDIR=/tmp jupyter nbconvert --to notebook --execute --inplace notebooks/exploratory_data_analysis.ipynb
```
