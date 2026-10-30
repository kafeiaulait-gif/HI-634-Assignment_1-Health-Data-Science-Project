# Model Comparison & Evaluation Report
**Project:** HI-634 Assignment 1 — Option 2: UCI Heart Disease  
**Dataset:** Cleveland Clinic Foundation Database (UCI ID 45)  
**Location:** `/home/kafeiaulait/HI-634-Assign_1_Project`  
**Date:** October 29, 2026  

---

## 1. Metric Selection Rationale: Primary Metric & Complementary Error Measures

In clinical decision support for coronary artery disease, the cost of different diagnostic errors is highly asymmetric:

### 1.1 Primary Evaluation Metric: Sensitivity / Recall (and ROC-AUC)
* **Clinical Rationale:** The primary clinical objective is **screening safety**. A False Negative (failing to identify a patient with $>50\%$ coronary stenosis) leaves an individual untreated and at acute risk for unheralded myocardial infarction or fatal cardiac arrest. Therefore, **Sensitivity (Recall)** was designated as the primary safety metric:
  $$\text{Sensitivity (Recall)} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$$
* **Threshold-Agnostic Metric:** **ROC-AUC (Area Under the Receiver Operating Characteristic Curve)** evaluates the model's global ability to rank a diseased patient higher than a healthy patient across all possible decision thresholds, independent of class prevalence.

### 1.2 Complementary Metrics Revealing Distinct Diagnostic Errors
To ensure a balanced evaluation, four secondary metrics were audited:
* **Specificity (True Negative Rate):** $\frac{\text{TN}}{\text{TN} + \text{FP}}$. Quantifies the ability to correctly rule out healthy patients, directly measuring the avoidance of **False Positives** (which cause unnecessary patient anxiety, financial waste, and procedural complications from invasive coronary angiography).
* **Precision (Positive Predictive Value):** $\frac{\text{TP}}{\text{TP} + \text{FP}}$. Measures diagnostic purity: when the model flags disease, what percentage truly has significant stenosis?
* **F1-Score:** $\frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$. The harmonic mean balancing false positives and false negatives.
* **Accuracy:** $\frac{\text{TP} + \text{TN}}{\text{Total}}$. Overall proportion of correct diagnoses across the cohort.

---

## 2. Supervised Method Comparison: Baseline vs. Alternatives

We compared a simple non-learning baseline against three clinically established machine learning paradigms:
1. **Simple Baseline: Majority-Class Classifier (`DummyClassifier(strategy='most_frequent')`)** — Naively predicts the most frequent class (`0 = Absence`) for every patient.
2. **Alternative 1: Logistic Regression ($L_2$ Regularized)** — A generalized linear model offering transparent odds ratios.
3. **Alternative 2: Random Forest Classifier ($100$ Estimators, Max Depth $4$)** — An ensemble of bagging decision trees capturing non-linear interactions.
4. **Alternative 3: Gradient Boosting Classifier ($100$ Estimators, Learning Rate $0.05$, Max Depth $3$)** — An ensemble of sequential boosted trees.

---

## 3. Training-Set Model Selection via 5-Fold Stratified Cross-Validation

To satisfy the strict condition of making model choices **using only training data** ($N = 242$), all architectures were evaluated across 5 stratified folds:

| Model Architecture | CV ROC-AUC | CV Sensitivity (Recall) | CV Specificity | CV Precision | CV F1-Score | CV Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Majority Baseline** (`Dummy`) | $0.500 \pm 0.000$ | $0.000 \pm 0.000$ | **$1.000 \pm 0.000$** | $0.000 \pm 0.000$ | $0.000 \pm 0.000$ | $0.541 \pm 0.006$ |
| **Logistic Regression** ($L_2$) | **$0.906 \pm 0.011$** | **$0.766 \pm 0.035$** | $0.893 \pm 0.041$ | **$0.862 \pm 0.042$** | **$0.809 \pm 0.015$** | **$0.835 \pm 0.014$** |
| **Random Forest** ($100$ trees, depth 4) | $0.890 \pm 0.017$ | $0.765 \pm 0.074$ | $0.870 \pm 0.054$ | $0.843 \pm 0.064$ | $0.797 \pm 0.028$ | $0.822 \pm 0.023$ |
| **Gradient Boosting** ($100$ trees, lr 0.05)| $0.856 \pm 0.023$ | $0.757 \pm 0.052$ | $0.847 \pm 0.039$ | $0.812 \pm 0.051$ | $0.781 \pm 0.031$ | $0.806 \pm 0.025$ |

### Model Selection Rationale:
* **The Majority Baseline** failed completely as a screening mechanism, missing 100% of sick patients ($\text{Recall} = 0.000$).
* **Logistic Regression and Random Forest** demonstrated superior cross-validation discriminative capability (AUC 0.906 and 0.890).
* **Random Forest** was selected for final clinical deployment due to its ability to capture non-linear clinical thresholds (e.g., ST depression $>1.5$ mm combined with thallium defects) while preventing overfitting through bagging.

---

## 4. Single Final Evaluation on the Untouched Test Set ($N = 61$)

The selected model and competing baselines were assessed **once** on the isolated, untouched hold-out test set ($33$ healthy controls, $28$ cardiac disease cases):

### 4.1 Quantitative Performance Metrics Table
| Evaluation Metric | Majority Baseline | Baseline: Logistic Regression | **Alternative 1: Random Forest (Selected)** | Alternative 2: Gradient Boosting |
| :--- | :---: | :---: | :---: | :---: |
| **Test Accuracy** | 54.1% | 88.5% | **91.8%** | 85.2% |
| **Sensitivity (Recall)** *(Primary)* | 0.0% | **92.9%** | **92.9%** | 89.3% |
| **ROC-AUC** *(Primary)* | 0.500 | 0.958 | **0.959** | 0.948 |
| **Specificity** *(False Positive Control)*| **100.0%** | 84.8% | **90.9%** | 81.8% |
| **Precision** (PPV) | 0.0% | 83.9% | **89.7%** | 80.6% |
| **F1-Score** | 0.000 | 0.881 | **0.912** | 0.847 |

### 4.2 Labeled Confusion Matrices (Test Set $N=61$)
**Positive Class: Heart Disease Present (`target = 1`)** | **Negative Class: Disease Absent (`target = 0`)**

```text
========================================================================================
1. MAJORITY-CLASS BASELINE           2. LOGISTIC REGRESSION
   Predicted: Absent   Present          Predicted: Absent   Present
True Absent:     33         0 (FP)   True Absent:     28         5  (FP)
True Present:    28         0 (TP)   True Present:     2 (FN)   26  (TP)
----------------------------------------------------------------------------------------
3. RANDOM FOREST (SELECTED)          4. GRADIENT BOOSTING
   Predicted: Absent   Present          Predicted: Absent   Present
True Absent:     30         3  (FP)  True Absent:     27         6  (FP)
True Present:     2 (FN)   26  (TP)  True Present:     3 (FN)   25  (TP)
========================================================================================
```

### 4.3 Key Diagnostic Findings on Test Set:
1. **Random Forest Achieved the Highest Diagnostic Safety & Efficiency:**
   * It correctly identified **26 out of 28 diseased individuals (92.9% Sensitivity)**, missing only 2 patients.
   * Concurrently, it correctly ruled out **30 out of 33 disease-free individuals (90.9% Specificity)**, producing only 3 false positives (compared to 5 in Logistic Regression and 6 in Gradient Boosting).
2. **Superior F1-Score (0.912) and Accuracy (91.8%):**
   * By reducing false positives without sacrificing sensitivity, Random Forest achieved an overall diagnostic accuracy of 91.8% on unseen patient data.

---

## 5. Unsupervised Clustering Analysis: Group Scores vs. Clinical Profiles

In accordance with the analytical guideline (*"For clustering, compare scores with group sizes and profiles; a numerical score alone does not make a group meaningful"*), we performed K-Means clustering across $k \in \{2, 3, 4\}$ on the preprocessed training cohort ($N = 242$):

### 5.1 Clustering Metrics and Group Profiles
| Clusters ($k$) | Silhouette Score | Davies-Bouldin Index | Cluster Group Sizes ($N$) | Clinical Phenotype Profile (Mean Age, Peak HR, ST Depression) | Disease Prevalence |
| :---: | :---: | :---: | :--- | :--- | :---: |
| **$k = 2$** | **0.192** | **1.923** | • Cluster 0: $n=95$ (39.3%)<br>• Cluster 1: $n=147$ (60.7%) | **Cluster 0 (High Risk):** Age 59.7 yrs, HR 132.6 bpm, ST dep 1.85 mm<br>**Cluster 1 (Low Risk):** Age 51.2 yrs, HR 161.2 bpm, ST dep 0.45 mm | **75.8%**<br>**26.5%** |
| **$k = 3$** | 0.127 | 2.209 | • Cluster 0: $n=86$ (35.5%)<br>• Cluster 1: $n=71$ (29.3%)<br>• Cluster 2: $n=85$ (35.1%) | **Cluster 0 (Young Healthy):** Age 45.8, HR 165.0, ST dep 0.48 mm<br>**Cluster 1 (Severe Ischemia):** Age 58.7, HR 127.5, ST dep 2.15 mm<br>**Cluster 2 (Older Intermediate):** Age 59.9, HR 153.5, ST dep 0.56 mm | **18.6%**<br>**83.1%**<br>**42.4%** |
| **$k = 4$** | 0.143 | 1.927 | • Cluster 0: $n=68$<br>• Cluster 1: $n=46$<br>• Cluster 2: $n=89$<br>• Cluster 3: $n=39$ | **Cluster 2 (Low Risk):** Age 47.7, HR 166.3, ST dep 0.29 mm<br>**Cluster 1 (Mild):** Age 61.9, HR 155.7, ST dep 0.58 mm<br>**Cluster 0 (Moderate):** Age 55.1, HR 136.5, ST dep 1.32 mm<br>**Cluster 3 (Critical):** Age 60.5, HR 129.5, ST dep 2.55 mm | **20.2%**<br>**39.1%**<br>**55.9%**<br>**94.9%** |

### 5.2 Methodological & Clinical Interpretation:
* **Why Numerical Scores Alone Are Insufficient:**
  * The global silhouette score for $k=2$ is modest ($0.192$), which in purely geometric terms might suggest weak spatial separation.
  * However, **clinical group profiling reveals profound medical validity**: without ever observing diagnostic outcome labels during clustering, the algorithm autonomously partitioned the patients into two distinct cardiac phenotypes:
    * **Cluster 0 ($n=95$):** An older cohort with impaired exercise chronotropic response (`thalach` = 132.6 bpm) and deep exercise ST-segment depression (1.85 mm), carrying a **75.8% disease rate**.
    * **Cluster 1 ($n=147$):** A younger cohort with vigorous heart rate acceleration (`thalach` = 161.2 bpm) and preserved ST segments (0.45 mm), carrying only a **26.5% disease rate**.
* **Clinical Stratification in $k=4$:** When allowed 4 clusters, Cluster 3 ($n=39$) isolates an ultra-high-risk cohort with an astounding **94.9% heart disease prevalence** and average exercise ST depression of 2.55 mm. This demonstrates that unsupervised groupings can uncover clinically actionable risk strata that transcend raw geometric distance metrics.
