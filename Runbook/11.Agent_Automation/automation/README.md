# Master Automation Package & Executive Deliverable
**Course:** HI-634 Health Informatics  
**Assignment:** Assignment 1 — Option 2: UCI Heart Disease Classification  
**Date:** October 29, 2026  
**Environment:** Python 3.13.5 local `.venv`  
**Location:** `/home/kafeiaulait/HI-634-Assign_1_Project/automation`  

---

## 1. Overview of the Automation Package

This `automation/` master folder provides a completely self-contained, turnkey archive containing every deliverable, diagnostic log, statistical test, machine learning model, figure, and documentation file generated for HI-634 Assignment 1.

### Master Folder Structure:
```text
automation/
├── README.md                           # This master documentation and executive summary
├── scripts/
│   └── run_all.py                      # One-click master runner executing all 5 pipeline steps
├── docs/                               # All consolidated prompt deliverables
│   ├── question.txt                    # Prompt 1: Focused question & observation unit
│   ├── inventory.md                    # Prompt 2: File inventory, codebook & distributions
│   ├── findings.md                     # Prompt 3: Preparation in response to findings
│   ├── comparisons.md                  # Prompt 4: Model comparison, CV & clustering
│   ├── explanation.md                  # Prompt 5: Visual explanations, error analysis & captions
│   ├── prompt_output.md                # Full technical output export
│   ├── README.md                       # Main repository README
│   └── requirements.txt                # Pinned dependency requirements
├── figures/                            # All 300 DPI publication-quality visual artifacts
│   ├── fig1_data_quality_missingness.png # Completeness bar chart across all 14 attributes
│   ├── fig2_clinical_relationship.png   # ST depression vs. peak HR scatter & KDE contours
│   ├── fig3_model_error_analysis.png    # Random Forest confusion matrix & ROC curve
│   ├── roc_curves_comparison.png       # Multi-model ROC comparison with AUC labels
│   ├── confusion_matrices_comparison.png # Side-by-side test confusion matrices
│   ├── confusion_matrices_baseline_rf.png# Majority baseline vs. Logistic vs. Random Forest
│   ├── model_metrics_comparison.png    # Grouped bar chart comparing performance metrics
│   ├── feature_importance_comparison.png # Top 10 Random Forest predictors
│   ├── age_distribution.png            # Age histogram and KDE by outcome
│   ├── correlation_matrix.png          # Full clinical correlation heatmap
│   ├── summary_statistics.csv          # Descriptive stats for continuous variables
│   └── model_performance_table.csv     # Model evaluation metrics table
└── data/                               # Preserved datasets
    ├── raw/
    │   ├── processed.cleveland.data    # Authentic raw UCI headerless file (immutable)
    │   └── heart_disease.csv           # Raw CSV archive (immutable)
    └── processed/
        └── heart_disease_cleaned.csv   # Processed dataset with engineered binary target
```

---

## 2. One-Click Master Pipeline Execution

To automatically rerun the entire analytical workflow from scratch (ingestion $\to$ cleaning $\to$ 5-fold CV $\to$ test set evaluation $\to$ all 10 figures $\to$ headless Jupyter notebook execution):

```bash
# From the project root:
MPLCONFIGDIR=/tmp .venv/bin/python automation/scripts/run_all.py
```

### Automated Steps Performed:
1. **Step 1 (`src/download_data.py`):** Ingests raw data and verifies the 14 attributes against the official UCI Cleveland codebook (`heart-disease.names`).
2. **Step 2 (`src/data_preprocessing.py`):** Parses `'?'` markers to `np.nan`, creates the binary diagnostic target ($num > 0 \to 1$), and logs all decisions into `reports/cleaning_decisions_log.csv`.
3. **Step 3 (`src/model_pipeline.py`):** Performs an 80/20 stratified split, builds leakage-free scikit-learn `Pipeline` objects, conducts 5-fold cross-validation on `X_train`, evaluates once on untouched `X_test`, and saves evaluation figures.
4. **Step 4 (`src/generate_visual_explanations.py`):** Generates high-resolution labeled figures with explicit error characterizations and count tables.
5. **Step 5 (`jupyter nbconvert`):** Executes [`notebooks/exploratory_data_analysis.ipynb`](file:///home/kafeiaulait/HI-634-Assign_1_Project/notebooks/exploratory_data_analysis.ipynb) headlessly in place, embedding all outputs directly into the notebook cells.

---

## 3. Executive Summary of Clinical Findings & Model Results

### A. The Core Clinical Question (Prompt 1)
* **Question:** *"Can routine clinical examination and non-invasive diagnostic exercise measurements predict the presence (versus absence) of significant coronary artery disease (>50% angiographic vessel diameter stenosis) in adult patients evaluated for suspected cardiac pathology?"*
* **Unit of Observation:** An individual adult patient clinical encounter ($N = 303$ unique patient records).

### B. Data Quality & Audit (Prompt 2 & 3)
* **Dimensions:** 303 rows $\times$ 14 columns.
* **Duplicates:** **0 duplicate records (0.00%)**.
* **Missingness:** Exactly **6 `'?'` missing entries** (0.14% of all cells), confined to specialized fluoroscopy (`ca`, 4 missing) and thallium scintigraphy (`thal`, 2 missing). All other 12 features are 100% complete.
* **Target Balance:** Naturally balanced (164 healthy controls / 54.1% vs. 139 coronary disease cases / 45.9%).
* **Extreme Clinical Outliers:** Patient 152 exhibits cholesterol of **564 mg/dl** (and three others $>400$ mg/dl); preserved without truncation as authentic familial hypercholesterolemia.

### C. Supervised Model Comparison & Error Metrics (Prompt 4)
Evaluated on the isolated hold-out test set ($N = 61$ unseen patients; 33 healthy, 28 diseased):

| Model | Test Accuracy | Sensitivity / Recall *(Primary)* | Specificity *(False Positive Control)* | Precision | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Majority-Class Baseline** | 54.1% | 0.0% | **100.0%** | 0.0% | 0.000 | 0.500 |
| **Logistic Regression** ($L_2$) | 88.5% | **92.9%** | 84.8% | 83.9% | 0.881 | **0.958** |
| **Random Forest (Selected)** | **91.8%** | **92.9%** | **90.9%** | **89.7%** | **0.912** | **0.959** |
| **Gradient Boosting** | 85.2% | 89.3% | 81.8% | 80.6% | 0.847 | 0.948 |

* **Selected Model Rationale:** Random Forest achieved the highest overall accuracy (**91.8%**) and F1-score (**0.912**), detecting **26 of 28 cardiac cases (92.9% Sensitivity)** while generating only 3 False Positives out of 33 controls (**90.9% Specificity**).

### D. Unsupervised Clustering Insights (Prompt 4)
* K-Means clustering ($k=2$) revealed strong clinical phenotype separation despite a modest geometric silhouette score ($0.192$):
  * **Cluster 0 ($n=95$):** High-risk phenotype (mean age 59.7, impaired peak HR 132.6 bpm, deep ST depression 1.85 mm), carrying a **75.8% disease rate**.
  * **Cluster 1 ($n=147$):** Low-risk phenotype (mean age 51.2, robust peak HR 161.2 bpm, minimal ST shift 0.45 mm), carrying only a **26.5% disease rate**.
* At $k=4$, Cluster 3 ($n=39$) autonomously isolates an ultra-high-risk cohort with an astonishing **94.9% heart disease prevalence**.

### E. Visual Artifacts & Non-Causal Reporting (Prompt 5)
* Labeled figures with complete captions specifying the unit of observation, sample size, plotted dimensions, and clinical interpretations are archived in [`automation/figures/`](file:///home/kafeiaulait/HI-634-Assign_1_Project/automation/figures/).
* All findings explicitly maintain **correlational and associative phrasing**, recognizing that exercise-induced ST depression and chronotropic incompetence are functional manifestations of coronary ischemia, not the biological cause of vascular atherosclerosis.
