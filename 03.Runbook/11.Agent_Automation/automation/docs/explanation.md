# Visual Explanations & Clinical Findings Report
**Project:** HI-634 Assignment 1 — Option 2: UCI Heart Disease  
**Dataset:** Cleveland Clinic Foundation Database (UCI ID 45)  
**Location:** `/home/kafeiaulait/HI-634-Assign_1_Project`  
**Date:** October 29, 2026  

---

## 1. Visual 1: Data Quality & Missingness Audit

### Embedded Visualization:
![Figure 1: Attribute Data Completeness & Missing Value Audit](file:///home/kafeiaulait/HI-634-Assign_1_Project/explanation/fig1_data_quality_missingness.png)

### Data Completeness & Missing Value Count Table:
| Attribute Name | Documented Clinical Meaning | Total Records ($N$) | Missing Count (`'?'`) | Completeness Rate (%) | Quality Assessment |
| :--- | :--- | :-: | :-: | :-: | :--- |
| `age` | Patient chronological age | 303 | 0 | 100.0% | Complete clinical record |
| `sex` | Biological sex | 303 | 0 | 100.0% | Complete clinical record |
| `cp` | Chest pain classification | 303 | 0 | 100.0% | Complete clinical record |
| `trestbps` | Resting admission blood pressure | 303 | 0 | 100.0% | Complete clinical record |
| `chol` | Serum cholesterol level | 303 | 0 | 100.0% | Complete clinical record |
| `fbs` | Fasting blood sugar > 120 mg/dl | 303 | 0 | 100.0% | Complete clinical record |
| `restecg` | Resting electrocardiogram results | 303 | 0 | 100.0% | Complete clinical record |
| `thalach` | Peak exercise heart rate achieved | 303 | 0 | 100.0% | Complete clinical record |
| `exang` | Exercise-induced angina indicator | 303 | 0 | 100.0% | Complete clinical record |
| `oldpeak` | Exercise-induced ST depression | 303 | 0 | 100.0% | Complete clinical record |
| `slope` | Slope of peak exercise ST segment | 303 | 0 | 100.0% | Complete clinical record |
| **`ca`** | **Major vessels colored by fluoroscopy** | **303** | **4** | **98.68%** | **4 missing values (1.32%)** |
| **`thal`** | **Thallium heart scan defect status** | **303** | **2** | **99.34%** | **2 missing values (0.66%)** |
| `num` | Angiographic disease status (Target) | 303 | 0 | 100.0% | Complete clinical outcome |

### Formal Visual Caption (Figure 1):
> **Caption 1 (Data Quality & Missingness):**
> * **Unit of Observation:** An individual adult patient clinical encounter.
> * **Sample Size:** $N = 303$ unique patient records from the Cleveland Clinic database.
> * **What is Plotted:** Horizontal bar chart illustrating the data completeness rate (percentage of non-missing entries) across all 14 clinical attributes, highlighting attributes containing `'?'` missing markers in orange and complete attributes in green.
> * **Conclusion Drawn:** Missing data is exceedingly rare across the cohort (totaling only 6 missing cells across 4,242 data points, or 0.14% of all values). Missingness is confined exclusively to specialized tertiary procedures (`ca` missing 4 values, 1.32%; `thal` missing 2 values, 0.66%), while all 12 routine demographic, vital, and baseline exercise parameters are 100% complete. This finding indicates high baseline data quality and justifies preserving all 303 records through in-pipeline median/mode imputation rather than discarding patient rows.

---

## 2. Visual 2: Clinical Distribution & Feature Relationship

### Embedded Visualization:
![Figure 2: Exercise ST Depression vs. Peak Heart Rate by Cardiac Outcome](file:///home/kafeiaulait/HI-634-Assign_1_Project/explanation/fig2_clinical_relationship.png)

### Bivariate Distribution Summary Table:
| Clinical Quadrant | Physiological Definition | Healthy Controls (`target=0`, $n=164$) | Coronary Disease (`target=1`, $n=139$) | Clinical Prevalence & Correlational Finding |
| :--- | :--- | :-: | :-: | :--- |
| **High HR ($\ge 150$), Low ST Dep ($< 1.0$)** | Normal chronotropic acceleration; preserved myocardial perfusion | **111 patients (67.7%)** | 18 patients (12.9%) | Strongly associated with disease absence ($\text{OR} = 0.07, p < 10^{-15}$). |
| **Low HR ($< 150$), High ST Dep ($\ge 1.0$)** | Chronotropic incompetence; exercise-induced subendocardial ischemia | 8 patients (4.9%) | **71 patients (51.1%)** | Strongly associated with presence of significant coronary stenosis ($\text{OR} = 20.3, p < 10^{-14}$). |
| **Intermediate Quadrants** | Mixed chronotropic or electrical response | 45 patients (27.4%) | 50 patients (36.0%) | Represents intermediate diagnostic uncertainty requiring multivariable modeling. |

### Formal Visual Caption (Figure 2):
> **Caption 2 (Clinical Distribution & Relationship):**
> * **Unit of Observation:** An individual adult patient clinical encounter.
> * **Sample Size:** $N = 303$ unique patient records from the Cleveland Clinic database.
> * **What is Plotted:** Bivariate scatter plot with overlaid kernel density estimation (KDE) contours comparing maximum heart rate achieved during treadmill exercise (`thalach`, x-axis, in beats per minute) against ST-segment depression induced by exercise relative to rest (`oldpeak`, y-axis, in millimeters), stratified by confirmed angiographic coronary disease status ($0$ = Absence in blue, $1$ = Presence in orange). Dashed reference lines mark clinical thresholds ($150$ bpm and $1.0$ mm).
> * **Conclusion Drawn:** A strong inverse statistical association exists between peak exercise heart rate and exercise-induced ST depression across diagnostic groups. Patients with confirmed coronary disease concentrate heavily in the lower-right quadrant (impaired peak heart rate $<150$ bpm and deep ST depression $>1.0$ mm), whereas healthy individuals cluster in the upper-left quadrant (peak heart rate $>150$ bpm with minimal ST shift $<1.0$ mm).
> * **Causal Caution:** *These observed patterns represent statistical associations and functional clinical markers of cardiac strain, not proof that lower heart rates or ST shifts cause arterial stenosis.* Rather, both markers serve as observable physiological manifestations of underlying vascular obstruction that restricts coronary blood flow during elevated myocardial oxygen demand.

---

## 3. Visual 3: Chosen Result & Diagnostic Error Analysis (Random Forest)

### Embedded Visualization:
![Figure 3: Random Forest Evaluation & Diagnostic Error Characterization](file:///home/kafeiaulait/HI-634-Assign_1_Project/explanation/fig3_model_error_analysis.png)

### Test Set Performance & Error Breakdown Table ($N = 61$ Unseen Patients):
| Diagnostic Outcome Category | Metric Value | Patient Count | Clinical Impact & Decision Consequences |
| :--- | :-: | :-: | :--- |
| **True Negatives (TN)** | Specificity = **90.9%** | **30 patients** | Correctly identified as disease-free; safely spared from unnecessary invasive cardiac catheterization. |
| **True Positives (TP)** | Sensitivity = **92.9%** | **26 patients** | Correctly identified as having significant coronary stenosis; promptly referred for revascularization and cardioprotective medical therapy. |
| **False Positives (FP)** | Type I Error Rate = **9.1%** | **3 patients** | Healthy individuals incorrectly predicted to have disease. Results in transient psychological anxiety and costs associated with confirmatory angiography, but patients are ultimately protected. |
| **False Negatives (FN)** | Type II Error Rate = **7.1%** | **2 patients** | **Critical Error:** Diseased patients incorrectly classified as healthy. Falsely reassured individuals risk unheralded myocardial infarction or fatal cardiac arrest without treatment. |
| **Overall Accuracy** | **91.8%** | **56 / 61 correct** | Random Forest misclassified only 5 out of 61 patients on the untouched hold-out test set. |
| **Area Under ROC Curve (AUC)** | **0.959** | Test $N=61$ | Outstanding global discriminative capacity across all operating classification thresholds. |

### Formal Visual Caption (Figure 3):
> **Caption 3 (Model Diagnostic Performance & Error Analysis):**
> * **Unit of Observation:** An individual adult patient clinical encounter.
> * **Sample Size:** $N = 61$ patient records comprising the untouched, stratified hold-out test partition (33 healthy controls, 28 coronary disease cases).
> * **What is Plotted:** Two-panel diagnostic evaluation of the selected Random Forest model (trained strictly on $N = 242$ training records). 
>   * **Panel A:** Confusion matrix heatmap detailing True Negatives ($n=30$), False Positives ($n=3$), False Negatives ($n=2$), and True Positives ($n=26$).
>   * **Panel B:** Receiver Operating Characteristic (ROC) curve displaying True Positive Rate against False Positive Rate across all thresholds ($\text{AUC} = 0.959$), with the red circular marker indicating the clinical operating point at the default $0.50$ probability threshold (Sensitivity = 92.9%, Specificity = 90.9%).
> * **Conclusion Drawn:** The selected Random Forest model achieves high diagnostic accuracy (91.8%) and prioritizes clinical safety by limiting False Negatives to only 2 cases (3.3% of test patients), successfully identifying 92.9% of all patients with coronary artery disease. Concurrently, it maintains strong specificity (90.9%), generating only 3 False Positives out of 33 healthy controls.
> * **Informatics & Decision Support Context:** The model operates as an effective non-invasive screening filter, accurately triaging high-risk patients toward definitive angiography while safely diverting low-risk patients away from unnecessary invasive procedures.
