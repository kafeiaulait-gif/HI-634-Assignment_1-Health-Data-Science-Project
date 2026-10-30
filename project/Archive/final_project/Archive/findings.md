# Data Preparation in Response to Findings
**Project:** HI-634 Assignment 1 — Option 2: UCI Heart Disease  
**Dataset:** Cleveland Clinic Foundation Database (UCI ID 45)  
**Location:** `/home/kafeiaulait/HI-634-Assign_1_Project`  
**Date:** October 29, 2026  

---

## 1. Raw Data Integrity Guarantee

* **Raw Data Path:** [`data/raw/processed.cleveland.data`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/processed.cleveland.data) and [`data/raw/heart_disease.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/heart_disease.csv)
* **Policy:** All raw files remain strictly immutable. Transformations are applied in memory and persisted exclusively to [`data/processed/heart_disease_cleaned.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/processed/heart_disease_cleaned.csv) or executed dynamically within scikit-learn `Pipeline` objects.

---

## 2. Missing-Value Code Conversion & Auditing

* **Documented Missing-Value Marker:** The UCI documentation (`heart-disease.names`) explicitly records `'?'` as the missing value symbol.
* **Conversion Action:** Parsed `'?'` into `np.nan` during data ingestion:
  ```python
  df_raw = pd.read_csv('data/raw/processed.cleveland.data', header=None, names=COLUMN_NAMES, na_values='?')
  ```
* **Audit of Affected Rows:**
  * **`ca` (Major vessels colored by fluoroscopy):** 4 missing values (1.32%) — Rows 166, 192, 287, 302.
  * **`thal` (Thallium scintigraphy defect):** 2 missing values (0.66%) — Rows 87, 266.
  * **Resting Blood Pressure (`trestbps`):** 0 missing values (100% complete).
  * **Serum Cholesterol (`chol`):** 0 missing values (100% complete).
  * **Total Missing Cells:** Exactly **6 `'?'` characters** across 303 rows (1.98% of patient records).
* **Documented Excluded Rows:** **0 rows excluded.** Complete-case discarding was rejected because dropping patients with specialized diagnostic missingness introduces selection bias and reduces sample power. Instead, missing entries are handled through in-pipeline imputation.

### Comparison of Feature Distributions: Before vs. After Training-Set Imputation
*(Computed strictly on the 242-patient training partition `X_train`)*:

| Feature | Imputation Strategy | Learned Training Statistic | Before Imputation (Observed Data) | After Imputation (Complete `X_train`) | Impact on Distribution |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **`ca`** | Median Imputer | `0.0` vessels | Mean = 0.610, Median = 0.0, SD = 0.883 | Mean = 0.607, Median = 0.0, SD = 0.883 | $\Delta \text{Mean} = -0.003$; variance and median preserved. |
| **`thal`** | Most Frequent Mode | `3.0` (Normal) | `3.0`: 135 (56.0%)<br>`7.0`: 95 (39.4%)<br>`6.0`: 11 (4.6%) | `3.0`: 136 (56.2%)<br>`7.0`: 95 (39.3%)<br>`6.0`: 11 (4.5%) | Preserves mode without shifting category frequencies. |

---

## 3. Preservation of Extreme Clinical Values (No Arbitrary Outlier Truncation)

* **Finding:** Several physiological measurements exhibit extreme numerical ranges:
  * **`chol` (Serum Cholesterol):** Reaches **564 mg/dl** (Patient 152), with three additional female patients exceeding 400 mg/dl (407, 409, 417 mg/dl), compared to a cohort median of 241 mg/dl.
  * **`trestbps` (Resting Blood Pressure):** Reaches **200 mm Hg** (Patient 126), compared to a cohort median of 130 mm Hg.
* **Clinical Assessment:** In cardiology, severe hypercholesterolemia ($> 400$ mg/dl) is a documented manifestation of familial dyslipidemia, and systolic BP of 200 mm Hg represents acute Stage 4/malignant hypertension. These represent true, high-risk cardiac pathology, not transcription or equipment errors.
* **Preparation Action:** **No extreme clinical values were removed or trimmed.** To prevent distance-based or gradient distortion in linear models (Logistic Regression), continuous features were rescaled using `StandardScaler()` fitted **strictly on `X_train`**.

---

## 4. Stratified Hold-Out Splitting Prior to Preprocessing

To guarantee zero data leakage, data partitioning occurred **before fitting any imputer, encoder, or scaler**:

```python
X = df.drop(columns=['num', 'target'])
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
```

### Class Counts Across Partitions:
| Partition | Total Records | Class 0 (Disease Absence) | Class 1 (Disease Presence) | Positive Prevalence (%) |
| :--- | :-: | :-: | :-: | :-: |
| **Full Dataset** | 303 | 164 | 139 | **45.87%** |
| **Training Partition (`X_train`)** | **242** | **131** | **111** | **45.87%** |
| **Test Partition (`X_test`)** | **61** | **33** | **28** | **45.90%** |

* **Class-Level Assessment:** Stratification successfully equalized disease prevalence across partitions, ensuring that test evaluation reflects realistic clinical prevalence.

---

## 5. Scikit-Learn `Pipeline` & `ColumnTransformer` Architecture

All preprocessing transformations are encapsulated within a unified scikit-learn pipeline, ensuring that all statistical parameters (means, standard deviations, medians, modes, dummy column headers) are fitted **solely on `X_train`**:

```python
preprocessor = ColumnTransformer(transformers=[
    # 1. Continuous Numerical: Median Impute + Z-score Standardization
    ('num', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']),

    # 2. Nominal Categorical: Mode Impute + One-Hot Encoding (drop first)
    ('nom', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ]), ['cp', 'restecg', 'thal']),

    # 3. Ordinal / Discrete Count: Median Impute + Z-score Standardization
    ('ord', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), ['ca', 'slope']),

    # 4. Binary Features (0/1): Mode Impute
    ('bin', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ]), ['sex', 'fbs', 'exang'])
])
```

* **Dimensionality Transformation:** The input feature matrix of 13 clinical variables expands into **17 numeric columns** post-transformation (with nominal features converted to binary indicator columns).
* **Missing Value Check Post-Transformation:** Exactly **0 NaNs** remain in `X_train_trans` and `X_test_trans`.

---

## 6. Target Leakage & Temporal Sequence Auditing

1. **Row Identifier Audit:**
   * No sequential database row IDs, patient medical record numbers (MRNs), or encounter identifiers were included in predictor matrix $X$.
2. **Target Isolation Audit:**
   * Both the original multi-class outcome `num` and the engineered target `target` were stripped from $X$ prior to splitting (`X = df.drop(columns=['num', 'target'])`).
3. **Temporal Measurement Sequence Audit:**
   * In clinical informatics, target leakage occurs when a feature is measured *after* the outcome or reflects treatment decisions made in response to knowing the diagnosis.
   * **Verification:** In this dataset, all 13 predictor features represent baseline demographics (`age`, `sex`), pre-procedural resting vitals (`trestbps`, `chol`, `fbs`, `restecg`), or non-invasive treadmill stress test parameters (`thalach`, `exang`, `oldpeak`, `slope`, `thal`, `ca`).
   * The gold-standard outcome (`num`) was obtained **subsequently** via invasive cardiac catheterization and coronary angiography. Therefore, no predictor leaks post-diagnostic clinical information or reveals the angiographic answer.

---

## 7. Canonical Findings Summary Table

| Observed Finding | Decision Taken | What is Documented & Verified |
| :--- | :--- | :--- |
| **Missing values coded as `'?'` in `ca` and `thal`.** | Converted `'?'` to `np.nan`; imputed using training-set median (for count `ca`) and training-set mode (for nominal `thal`). | Exactly 6 rows affected (4 in `ca`, 2 in `thal`). Verified before-and-after distributions on `X_train` ($\Delta \text{Mean} \le 0.003$). Zero rows discarded. |
| **Uneven category counts across features and classes.** | Executed stratified splitting (`stratify=y`) on an 80/20 train/test holdout; reported class-level metrics. | Training class counts: 131 healthy (54.1%), 111 diseased (45.9%). Test class counts: 33 healthy (54.1%), 28 diseased (45.9%). Reported class-level recall, specificity, and confusion matrices. |
| **Single-table data integrity (no records lost).** | Verified table format, row counts, and primary key alignment between source files. | Row counts before and after loading match exactly (303 rows). Zero unmatched rows or lost records. Single-center Cleveland Clinic protocol strictly enforced. |
