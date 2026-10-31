# Health Informatics (HI-634) - Assignment 1
## Option 2: UCI Heart Disease Classification Pipeline

A fully reproducible, clinical data science pipeline evaluating predictive models for coronary artery disease using the Cleveland Clinic dataset from the UCI Machine Learning Repository.

---

## 1. Project Overview & Data Provenance

* **Dataset:** UCI Heart Disease (Cleveland Database)
* **Official URL:** [https://archive.ics.uci.edu/dataset/45/heart+disease](https://archive.ics.uci.edu/dataset/45/heart+disease)
* **UCI Repository Identifier:** ID `45` (`ucimlrepo`)
* **Original Study Investigators:** Robert Detrano, M.D., Ph.D., et al. (Cleveland Clinic Foundation & V.A. Medical Center, Long Beach)
* **Date Retrieved / Verified:** October 29, 2026
* **Raw Data Integrity Guarantee:** Raw files [`data/raw/processed.cleveland.data`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/processed.cleveland.data) and [`data/raw/heart_disease.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/data/raw/heart_disease.csv) are immutable and kept strictly unchanged.

---

## 2. Directory & Artifact Structure

```text
HI-634-Assign_1_Project/
├── .gitignore                          # Ignores .venv, caches, checkpoints
├── requirements.txt                    # Pinned Python dependencies
├── README.md                           # Replication and project report guide
├── data/
│   ├── raw/
│   │   ├── processed.cleveland.data    # Authentic UCI headerless file (? for missing)
│   │   └── heart_disease.csv           # Raw CSV archive
│   └── processed/
│       └── heart_disease_cleaned.csv   # Processed dataset with engineered binary target
├── notebooks/
│   └── exploratory_data_analysis.ipynb # Executed interactive analysis notebook
├── src/
│   ├── download_data.py                # UCI ingestion and raw file verification
│   ├── data_preprocessing.py           # Cleaning, target binarization, and changelog logger
│   └── model_pipeline.py               # Leakage-free training, CV, testing, and figure generator
└── reports/
    ├── cleaning_decisions_log.csv      # Structured audit of all data decisions
    └── figures/
        ├── age_distribution.png        # EDA: Age distribution by clinical status
        ├── correlation_matrix.png      # EDA: Feature correlation matrix
        ├── roc_curves_comparison.png   # Model Eval: ROC curves for all 3 models
        ├── confusion_matrices_comparison.png # Model Eval: Labeled confusion matrices
        ├── model_metrics_comparison.png# Model Eval: Bar chart comparing performance
        ├── feature_importance_comparison.png # Top clinical predictors (Random Forest)
        ├── summary_statistics.csv      # Descriptive stats of clinical attributes
        └── model_performance_table.csv # Full quantitative metrics table
```

---

## 3. Data Dictionary: Official 14 UCI Attributes

| # | Column Name | Data Type | Units / Range | Clinical Meaning & Value Encodings |
| :-: | :--- | :--- | :--- | :--- |
| **1** | `age` | Continuous | 29 – 77 years | Patient age |
| **2** | `sex` | Binary | 0, 1 | `1` = Male; `0` = Female |
| **3** | `cp` | Nominal | 1, 2, 3, 4 | Chest pain type: `1`: Typical angina, `2`: Atypical angina, `3`: Non-anginal pain, `4`: Asymptomatic |
| **4** | `trestbps` | Continuous | 94 – 200 mm Hg | Resting blood pressure on admission to hospital |
| **5** | `chol` | Continuous | 126 – 564 mg/dl | Serum cholesterol level |
| **6** | `fbs` | Binary | 0, 1 | Fasting blood sugar > 120 mg/dl (`1` = true; `0` = false) |
| **7** | `restecg` | Nominal | 0, 1, 2 | Resting ECG: `0`: Normal, `1`: ST-T wave abnormality, `2`: Probable/definite left ventricular hypertrophy |
| **8** | `thalach` | Continuous | 71 – 202 bpm | Maximum heart rate achieved during exercise treadmill test |
| **9** | `exang` | Binary | 0, 1 | Exercise-induced angina (`1` = yes; `0` = no) |
| **10** | `oldpeak` | Continuous | 0.0 – 6.2 mm | ST depression induced by exercise relative to rest |
| **11** | `slope` | Ordinal | 1, 2, 3 | Slope of peak exercise ST segment: `1`: Upsloping, `2`: Flat, `3`: Downsloping |
| **12** | `ca` | Discrete | 0 – 3 | Number of major coronary vessels colored by fluoroscopy *(4 missing `?`)* |
| **13** | `thal` | Nominal | 3, 6, 7 | Thallium heart scintigraphy: `3.0`: Normal, `6.0`: Fixed defect, `7.0`: Reversible defect *(2 missing `?`)* |
| **14** | `num` | Discrete | 0 – 4 | Angiographic disease status: `0`: <50% stenosis (no disease); `1,2,3,4`: >50% stenosis |

---

## 4. Record of Data Cleaning Decisions

Every data transformation is logged with findings, decisions, and clinical/methodological rationale in [`reports/cleaning_decisions_log.csv`](file:///home/kafeiaulait/HI-634-Assign_1_Project/reports/cleaning_decisions_log.csv):

| Step | Feature | Finding | Decision | Methodological / Clinical Reason |
| :-: | :--- | :--- | :--- | :--- |
| **1** | Raw File Ingestion | Raw file is headerless and encodes missing values as `?` | Assigned 14 column names per UCI documentation and parsed `?` as `np.nan`. Raw files left untouched. | Preserves raw data provenance while ensuring valid null handling in pandas. |
| **2** | `num` (Target) | Multi-class target (0 to 4); stage 4 has only 13 patients. | Binarized: `target = 1` if `num > 0` else `0`. Retained original `num` in dataset. | Aligns with standard clinical screening threshold (>50% coronary narrowing) and benchmark literature. |
| **3** | `ca` & `thal` (Missingness) | `ca` missing 4 values (1.32%); `thal` missing 2 values (0.66%). Total 6 rows (1.98%). | Retained rows; deferred median/mode imputation to scikit-learn `Pipeline`. | Eliminates data leakage; imputers are fit exclusively on the training fold (`X_train`). |
| **4** | `chol` (Outliers) | Patient 152 has cholesterol of 564 mg/dl; 3 others > 400 mg/dl. | Preserved values without truncation; applied `StandardScaler` inside pipeline. | Severe hypercholesterolemia is clinically valid; standard scaling avoids distance distortion without discarding true clinical signals. |
| **5** | `cp`, `restecg`, `thal` | Arbitrary integer codes (e.g. `thal` 3, 6, 7) imply false numerical hierarchy. | Applied `OneHotEncoder(drop='first')` inside `ColumnTransformer`. | Prevents linear and distance models from misinterpreting categorical labels as continuous magnitudes. |

---

## 5. Experimental Design & Leakage Prevention

* **Train / Test Split:** 80% Training ($N=242$), 20% Test ($N=61$), stratified on `y` (`random_state=42`).
* **Strict Leakage Prevention:** Preprocessing (imputers, scalers, one-hot encoders) is integrated inside `sklearn.pipeline.Pipeline` objects and fitted **strictly on `X_train`**. The test set is transformed only and evaluated once.
* **Internal Validation:** 5-Fold Stratified Cross-Validation on the training partition.
* **Model Comparison:**
  * **Baseline:** Logistic Regression ($L_2$ regularization)
  * **Alternative 1:** Random Forest Classifier ($100$ trees, max depth $4$)
  * **Alternative 2:** Gradient Boosting Classifier ($100$ estimators, learning rate $0.05$, max depth $3$)

---

## 6. Experimental Results & Performance Comparison

Evaluated on the isolated, unseen test set ($N=61$ patients, $28$ positive / $33$ negative):

| Model | 5-Fold CV ROC-AUC (Train) | Test Accuracy | Test Sensitivity (Recall) | Test Specificity | Test F1-Score | Test ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline: Logistic Regression** | $0.906 \pm 0.011$ | 88.5% | 92.9% | 84.8% | 0.881 | **0.958** |
| **Alternative 1: Random Forest** | $0.890 \pm 0.017$ | **91.8%** | **92.9%** | **90.9%** | **0.912** | **0.959** |
| **Alternative 2: Gradient Boosting** | $0.856 \pm 0.023$ | 85.2% | 89.3% | 81.8% | 0.847 | 0.948 |

### Key Diagnostic Observations:
1. **Random Forest** achieved the best overall diagnostic profile, correctly classifying 56 of 61 test patients (91.8% accuracy), with high sensitivity (92.9% — detecting 26 of 28 cardiac disease cases) and high specificity (90.9% — correctly ruling out 30 of 33 healthy patients).
2. **Logistic Regression** performed strongly with an AUC of 0.958 and 92.9% sensitivity, demonstrating that clinical risk in this dataset has substantial linear separability when properly scaled and encoded.
3. **Top Clinical Predictors:** Feature importance analysis revealed that the number of fluoroscopy-colored major vessels (`ca`), thallium scan defects (`thal`), asymptomatic chest pain (`cp_4`), exercise ST depression (`oldpeak`), and peak exercise heart rate (`thalach`) dominate model predictions.

---

## 7. How to Reproduce All Tables and Figures

### Step 1: Activate Environment & Verify Dependencies
```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```
*(Or invoke directly: `./.venv/bin/python`)*

### Step 2: Run Data Preprocessing & Decision Logger
```bash
./.venv/bin/python src/data_preprocessing.py
```

### Step 3: Train Models, Evaluate Test Set, & Generate All Figures
```bash
MPLCONFIGDIR=/tmp ./.venv/bin/python src/model_pipeline.py
```

### Step 4: Run the Interactive Jupyter Notebook
```bash
./.venv/bin/jupyter notebook notebooks/exploratory_data_analysis.ipynb
```
*(Or execute headlessly: `MPLCONFIGDIR=/tmp ./.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/exploratory_data_analysis.ipynb`)*
