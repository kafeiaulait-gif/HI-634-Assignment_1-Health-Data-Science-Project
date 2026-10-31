# Dataset Exploration & Technical Inventory Report
**Project:** HI-634 Assignment 1 — Option 2: UCI Heart Disease  
**Dataset:** Cleveland Clinic Foundation Database (UCI ID 45)  
**Location:** `/home/kafeiaulait/HI-634-Assign_1_Project`  
**Date:** October 29, 2026  

---

## 1. File Inventory

| File Path | Format | Size | Purpose & Integrity Status |
| :--- | :--- | :--- | :--- |
| [`data/raw/processed.cleveland.data`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/processed.cleveland.data) | Headerless ASCII CSV | 10.3 KB | **Primary Raw Source:** Official UCI Cleveland data file; contains 303 rows, 14 attributes, `'?'` missing markers. Kept strictly immutable. |
| [`data/raw/heart_disease.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/heart_disease.csv) | Standard CSV | 12.5 KB | Secondary raw archive with initial column headers. Kept immutable. |
| [`data/processed/heart_disease_cleaned.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/processed/heart_disease_cleaned.csv) | Standard CSV | 13.1 KB | Processed dataset containing verified 14 clinical features + engineered binary `target`. |
| [`reports/cleaning_decisions_log.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/cleaning_decisions_log.csv) | CSV | 1.7 KB | Structured log recording findings, decisions, and clinical reasons for all cleaning actions. |
| [`reports/figures/summary_statistics.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/summary_statistics.csv) | CSV | 1.1 KB | Descriptive statistics for continuous clinical parameters. |
| [`reports/figures/model_performance_table.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/figures/model_performance_table.csv) | CSV | 774 B | Cross-validation and test set evaluation metrics across all tested models. |

---

## 2. Row & Column Dimensions

* **Raw Data Dimensions (`processed.cleveland.data`):** **303 rows $\times$ 14 columns**
* **Cleaned Data Dimensions (`heart_disease_cleaned.csv`):** **303 rows $\times$ 15 columns** (includes engineered binary outcome `target`)
* **Unit of Observation:** One individual adult patient clinical encounter evaluated for coronary disease.

---

## 3. Sample Rows

### Raw Unprocessed Format (`data/raw/processed.cleveland.data`):
```text
63,1,1,145,233,1,2,150,0,2.3,3,0.0,6.0,0
67,1,4,160,286,0,2,108,1,1.5,2,3.0,3.0,2
67,1,4,120,229,0,2,129,1,2.6,2,2.0,7.0,1
37,1,3,130,250,0,0,187,0,3.5,3,0.0,3.0,0
41,0,2,130,204,0,2,172,0,1.4,1,0.0,3.0,0
```

### Structured Formatted Format (First 5 Rows with UCI Column Names):
| age | sex | cp | trestbps | chol | fbs | restecg | thalach | exang | oldpeak | slope | ca | thal | num | target |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| 63 | 1 | 1 | 145 | 233 | 1 | 2 | 150 | 0 | 2.3 | 3 | 0.0 | 6.0 | 0 | 0 |
| 67 | 1 | 4 | 160 | 286 | 0 | 2 | 108 | 1 | 1.5 | 2 | 3.0 | 3.0 | 2 | 1 |
| 67 | 1 | 4 | 120 | 229 | 0 | 2 | 129 | 1 | 2.6 | 2 | 2.0 | 7.0 | 1 | 1 |
| 37 | 1 | 3 | 130 | 250 | 0 | 0 | 187 | 0 | 3.5 | 3 | 0.0 | 3.0 | 0 | 0 |
| 41 | 0 | 2 | 130 | 204 | 0 | 2 | 172 | 0 | 1.4 | 1 | 0.0 | 3.0 | 0 | 0 |

---

## 4. Variable Types & Codebook Definitions (UCI Documentation)

| Col # | Attribute Name | Data Type | Units / Scale | Clinical Description & Categorical Codes |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `age` | Continuous | Years (29–77) | Patient chronological age |
| **2** | `sex` | Binary | 0, 1 | Biological sex (`1` = Male; `0` = Female) |
| **3** | `cp` | Nominal | 1, 2, 3, 4 | Chest pain type:<br>• `1`: Typical angina<br>• `2`: Atypical angina<br>• `3`: Non-anginal pain<br>• `4`: Asymptomatic |
| **4** | `trestbps` | Continuous | mm Hg (94–200) | Resting blood pressure upon admission to hospital |
| **5** | `chol` | Continuous | mg/dl (126–564) | Serum cholesterol level |
| **6** | `fbs` | Binary | 0, 1 | Fasting blood sugar > 120 mg/dl (`1` = True; `0` = False) |
| **7** | `restecg` | Nominal | 0, 1, 2 | Resting electrocardiographic results:<br>• `0`: Normal<br>• `1`: ST-T wave abnormality (T wave inversions / ST shift > 0.05 mV)<br>• `2`: Probable/definite left ventricular hypertrophy (Estes' criteria) |
| **8** | `thalach` | Continuous | bpm (71–202) | Maximum heart rate achieved during exercise stress test |
| **9** | `exang` | Binary | 0, 1 | Exercise-induced angina (`1` = Yes; `0` = No) |
| **10** | `oldpeak` | Continuous | mm (0.0–6.2) | ST depression induced by exercise relative to rest |
| **11** | `slope` | Ordinal | 1, 2, 3 | Slope of peak exercise ST segment:<br>• `1`: Upsloping<br>• `2`: Flat<br>• `3`: Downsloping |
| **12** | `ca` | Discrete Count | 0, 1, 2, 3 | Number of major vessels (0–3) colored by fluoroscopy *(Contains 4 missing `'?'`)* |
| **13** | `thal` | Nominal | 3, 6, 7 | Thallium heart scan defect:<br>• `3.0`: Normal<br>• `6.0`: Fixed defect<br>• `7.0`: Reversible defect *(Contains 2 missing `'?'`)* |
| **14** | `num` | Ordinal (Target)| 0, 1, 2, 3, 4 | Angiographic disease status (coronary artery diameter narrowing):<br>• `0`: < 50% stenosis (absence of significant disease)<br>• `1, 2, 3, 4`: > 50% stenosis (presence of disease in 1 to 4 vessels) |

---

## 5. Missingness & Duplicate Audit

### A. Missing Values
* **Raw File Markers:** Exactly **6 `'?'` characters** in the raw text file.
* **Missing Value Breakdown:**
  * `ca`: **4 missing values (1.32%)** — Rows 166, 192, 287, 302
  * `thal`: **2 missing values (0.66%)** — Rows 87, 266
  * All remaining 12 columns: **0 missing values (0.00%)**
* **Cohort Impact:** 6 out of 303 rows affected (1.98%). Complete records exist for 297 patients (98.02%).

### B. Duplicate Records
* **Exact Duplicate Rows:** **0 duplicate rows (0.00%)** across all 14 columns.

---

## 6. Distributions of Outcome & Important Predictors

### 6.1 Outcome Distributions (Before & After Binarization)
* **Before Binarization (`num` 0 to 4):**
  * `num = 0` (Absence): 164 patients (**54.13%**)
  * `num = 1` (Mild): 55 patients (**18.15%**)
  * `num = 2` (Moderate): 36 patients (**11.88%**)
  * `num = 3` (Severe): 35 patients (**11.55%**)
  * `num = 4` (Critical): 13 patients (**4.29%**)
* **After Binarization (`target = 0` vs. `target = 1`):**
  * `target = 0` (Disease Absence): **164 patients (54.13%)**
  * `target = 1` (Disease Presence): **139 patients (45.87%)**
  * *Class Balance Ratio: 1.18 to 1. Naturally balanced, avoiding class imbalance distortion.*

### 6.2 Continuous Predictor Distributions (Overall and by Outcome)
| Feature | Overall Mean $\pm$ SD | Median (IQR) | Absence (`0`) Mean $\pm$ SD | Presence (`1`) Mean $\pm$ SD | Hypothesis Test ($p$-value) |
| :--- | :-: | :-: | :-: | :-: | :--- |
| **`age`** | $54.44 \pm 9.04$ | 56.0 (13.0) | $52.59 \pm 9.51$ | $56.63 \pm 7.94$ | $t = -4.05, \mathbf{p = 7.06 \times 10^{-5}}$ |
| **`trestbps`** | $131.69 \pm 17.60$ | 130.0 (20.0) | $129.25 \pm 16.20$ | $134.57 \pm 18.77$ | $t = -2.62, \mathbf{p = 0.0094}$ |
| **`chol`** | $246.69 \pm 51.78$ | 241.0 (64.0) | $242.64 \pm 53.46$ | $251.47 \pm 49.49$ | $t = -1.49, p = 0.137$ |
| **`thalach`** | $149.61 \pm 22.88$ | 153.0 (32.5) | $158.38 \pm 19.20$ | $139.26 \pm 22.59$ | $t = 7.78, \mathbf{p = 9.11 \times 10^{-14}}$ |
| **`oldpeak`** | $1.04 \pm 1.16$ | 0.80 (1.60) | $0.59 \pm 0.78$ | $1.57 \pm 1.30$ | $t = -7.71, \mathbf{p = 2.20 \times 10^{-13}}$ |

### 6.3 Categorical Predictor Distributions by Outcome
* **`cp` (Chest Pain Type):**
  * `1` (Typical angina): 23 patients (16 healthy / 69.6%, 7 diseased / 30.4%)
  * `2` (Atypical angina): 50 patients (41 healthy / 82.0%, 9 diseased / 18.0%)
  * `3` (Non-anginal pain): 86 patients (68 healthy / 79.1%, 18 diseased / 20.9%)
  * `4` (Asymptomatic): **144 patients (39 healthy / 27.1%, 105 diseased / 72.9%)** — $\chi^2 = 81.82, \mathbf{p = 1.25 \times 10^{-17}}$
* **`thal` (Thallium Scan):**
  * `3.0` (Normal): 166 patients (129 healthy / 77.7%, 37 diseased / 22.3%)
  * `6.0` (Fixed defect): 18 patients (6 healthy / 33.3%, 12 diseased / 66.7%)
  * `7.0` (Reversible defect): 117 patients (28 healthy / 23.9%, 89 diseased / 76.1%) — $\chi^2 = 83.29, \mathbf{p = 8.20 \times 10^{-19}}$

---

## 7. Linked Files & Key Uniqueness Assessment

* **Dataset Structure:** Option 2 represents a single flat clinical database table ($N=303$).
* **Cross-File Integrity Verification:**
  * When cross-referencing [`data/raw/processed.cleveland.data`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/processed.cleveland.data) with the initial CSV snapshot [`data/raw/heart_disease.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/heart_disease.csv), **row counts match exactly (303 rows)**.
  * Every row represents an implicit primary key corresponding to a single patient encounter.
  * **Unmatched rows before join: 0 rows (0.00%)**.
  * No external tables or foreign keys are required, preventing referential join failures.

---

## 8. Concrete Findings Guiding Data Preparation

### Concrete Finding 1: Sparse Missingness in Specialized Cardiac Diagnostics (`ca`, `thal`)
* **Observation:** Missing values are confined strictly to fluoroscopy vessel count (`ca`, 4 missing) and thallium scan defect (`thal`, 2 missing), totaling 6 out of 303 cases (1.98%). All routine clinical exam features (`age`, `sex`, `trestbps`, `chol`, `restecg`) have 100% complete data.
* **Preparation Action:** Do not discard rows. Apply median imputation for `ca` and mode imputation for `thal` encapsulated inside the scikit-learn training pipeline to prevent data leakage.

### Concrete Finding 2: Naturally Balanced Binary Outcome vs. Sparse Multi-Class Tail
* **Observation:** The binary diagnostic outcome is naturally well-balanced (54.1% absence vs. 45.9% presence). However, the original multi-class target `num = 4` (critical four-vessel disease) contains only 13 cases (4.29%).
* **Preparation Action:** Formulate the primary question as binary classification (`target = 1` if `num > 0` else `0`). This matches the clinical screening threshold (>50% stenosis) while avoiding extreme sample sparsity.

### Concrete Finding 3: Extreme Right-Skewed Outliers in Serum Cholesterol
* **Observation:** Patient 152 exhibits a serum cholesterol of **564 mg/dl**, and three additional patients exceed 400 mg/dl, while the median is 241 mg/dl.
* **Preparation Action:** These values are clinically plausible (familial hypercholesterolemia) and should not be removed as errors. Standard scaling (`StandardScaler`) must be fitted on `X_train` to prevent distance-based distortion in linear and gradient models.

### Concrete Finding 4: Diagnostic Paradox in Chest Pain Presentation (`cp`)
* **Observation:** The single largest presentation category is asymptomatic chest pain (`cp = 4`, 47.5% of cohort), and this subgroup paradoxically exhibits the highest disease prevalence (72.9% positive). Integer coding (1 to 4) incorrectly suggests typical angina (`1`) is less severe than asymptomatic (`4`).
* **Preparation Action:** Categorical nominal encoding via `OneHotEncoder(drop='first')` is required within the pipeline to eliminate false numeric hierarchy.
