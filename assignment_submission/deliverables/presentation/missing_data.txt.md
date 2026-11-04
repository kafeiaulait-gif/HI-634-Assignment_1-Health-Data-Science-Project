
How was missing data handled?

---


### 1. Ingestion and Identification

* **Documented Missing Code:** In the raw Cleveland Clinic dataset (`data/raw/processed.cleveland.data`), missing values were recorded as the character string `'?'`.
* **Parsing:** During data loading, `'?'` was converted directly to standard missing values (`np.nan`):

```python
df_raw = pd.read_csv('data/raw/processed.cleveland.data', header=None, names=COLUMN_NAMES, na_values='?')
```

* **Audit of Affected Features:** Across all 303 patient records and 14 variables (303 × 14 = 4,242 total cells), exactly **6 cells** (0.14% of the dataset) contained missing values across only two variables:
    * **`ca` (Major vessels colored by fluoroscopy, 0-3): 4 missing values** (1.32% of records; rows 166, 192, 287, 302).
    * **`thal` (Thallium scintigraphy defect, 3/6/7): 2 missing values** (0.66% of records; rows 87, 266).
    * **All other 12 features** (including age, resting BP, cholesterol, maximum heart rate, and ST depression) were **100% complete** (0 missing).

---

### 2. Zero Casewise Deletion Policy

* **Decision:** 0 rows were discarded.
* **Justification:** Discarding records (complete-case analysis) would discard authentic clinical encounters for a negligible fraction of missing data, reducing statistical power and potentially introducing selection bias (e.g., patients who could not complete fluoroscopy or thallium scans).

---

### 3. Data Leakage Prevention (Split Before Fit)

* **To prevent data leakage, no imputation was performed globally on the full dataset.**
* **The data was partitioned first using a stratified 80/20 train/test split (\(N_{\text{train}} = 242\), \(N_{\text{test}} = 61\)):**

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
```

* **All imputation statistics (medians, modes) were calculated strictly on the 242-patient training partition (`X_train`)** and then applied downstream to transform both `X_train` and the untouched holdout `X_test`.

---

### 4. Implementation in ColumnTransformer & Pipeline

Imputation was embedded inside a unified scikit-learn `ColumnTransformer` tailored to variable types:

```python
preprocessor = ColumnTransformer(transformers=[
    # 1. Discrete Counts / Ordinal ('ca', 'slope'): Median Imputation
    ('ord', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), ['ca', 'slope']),

    # 2. Nominal Categorical ('cp', 'restecg', 'thal'): Mode Imputation + One-Hot
    ('nom', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
    ]), ['cp', 'restecg', 'thal']),

    # 3. Continuous Features: Median Imputation + Standardization
    ('num', Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ]), ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']),

    # 4. Binary Indicators ('sex', 'fbs', 'exang'): Mode Imputation
    ('bin', Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent'))
    ]), ['sex', 'fbs', 'exang'])
])
```

---

### 5. Distributional Impact (Before vs. After on `X_train`)

The learned training statistics preserved original distributional properties without skewing the data:

| Feature | Imputation Strategy | Learned Training Metric | Before Imputation (`X_train`) | After Imputation (`X_train`) | Impact on Distribution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ca** | Median Imputer | `0.0` vessels | Mean = 0.610,<br>Median = 0.0,<br>SD = 0.883 | Mean = 0.607,<br>Median = 0.0,<br>SD = 0.883 | ΔMean = -0.003;<br>median and variance strictly preserved. |
| **thal** | Mode Imputer | `3.0` (Normal) | 3.0 : 135 (56.0%)<br>7.0 : 95 (39.4%)<br>6.0 : 11 (4.6%) | 3.0 : 136 (56.2%)<br>7.0 : 95 (39.3%)<br>6.0 : 11 (4.5%) | Mode preserved without shifting relative category frequencies. |

Post-transformation, both `X_train` and `X_test` contained **0 missing values**, with all details documented in `findings.md` and `cleaning_decisions_log.csv`.


