
# Why Random Forest Was Selected for Coronary Artery Disease Classification
**Course:** HI-634 Health Informatics  
**Dataset:** Cleveland Clinic Foundation Database (UCI ID 45, N = 303)  
**Evaluation Cohort:** Untouched Hold-Out Test Set (N = 61; 33 controls, 28 cases)  
---
## 1. Superior Clinical Error Balance on the Test Set ($N = 61$)
In cardiac screening, the clinical penalty for diagnostic errors is highly asymmetric:
* **False Negative (Missed Disease):** Catastrophic. A patient with severe coronary stenosis ($>50\%$ vessel narrowing) is misdiagnosed as healthy and sent home without cardioprotective therapy or revascularization, risking unheralded myocardial infarction or sudden cardiac death.
* **False Positive (Unnecessary Referral):** Financially costly and invasive. A healthy individual is subjected to diagnostic cardiac catheterization and coronary angiography, carrying procedural risks (arterial puncture, contrast nephropathy, radiation exposure) and acute psychological distress.
Random Forest achieved the best overall clinical trade-off on the unseen holdout test cohort:
| Model Architecture | Sensitivity / Recall *(Safety)* | Specificity *(FP Control)* | False Negatives | False Positives | Test Accuracy | ROC-AUC | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Majority Baseline** (`Dummy`) | 0.0% | **100.0%** | 28 | **0** | 54.1% | 0.500 | 0.000 |
| **Logistic Regression** ($L_2$) | **92.9%** (26/28) | 84.8% (28/33) | **2** | 5 | 88.5% | 0.958 | 0.881 |
| **Random Forest (Selected)** | **92.9%** (26/28) | **90.9%** (30/33) | **2** | **3** | **91.8%** | **0.959** | **0.912** |
| **Gradient Boosting** | 89.3% (25/28) | 81.8% (27/33) | 3 | 6 | 85.2% | 0.948 | 0.847 |
> **Key Clinical Distinction:** While Logistic Regression matched Random Forest's sensitivity (92.9%), Random Forest reduced **False Positives by 40%** (from 5 down to 3). This delivered higher specificity (90.9% vs. 84.8%), higher diagnostic purity (Precision: 89.7% vs. 83.9%), and higher overall accuracy (91.8% vs. 88.5%).
---
## 2. Capturing Non-Linear Clinical Thresholds & Interactions
Cardiovascular pathology does not scale as a simple linear sum of isolated biomarkers. Instead, coronary ischemia emerges from **compound, multi-variable thresholds and non-linear interactions**:
* An exercise ST depression (`oldpeak`) $\ge 1.5$ mm is clinically concerning on its own, but when combined with an inability to reach age-predicted peak heart rate (`thalach` $< 140$ bpm) and a reversible defect on thallium scintigraphy (`thal = 7`), the likelihood of multi-vessel CAD increases non-linearly.
* Decision tree ensembles naturally segment continuous feature space into orthogonal, hierarchical partitions. This allows Random Forest to automatically model complex medical interactions without requiring manual polynomial feature engineering.
---
## 3. Inherent Robustness to Physiological Extremes (Outliers) & Mixed Modalities
The Cleveland cohort contains authentic, high-risk clinical extremes:
* **Patient 152:** Serum cholesterol reaches **564 mg/dL** (indicative of severe familial hypercholesterolemia).
* **Patient 126:** Resting systolic blood pressure reaches **200 mm Hg** (indicative of acute hypertensive crisis).
**Why Random Forest Excelled:**
* Parametric models (e.g., Logistic Regression) can experience leverage-point distortion or gradient instability from extreme continuous values unless extensive transformation or truncation is applied.
* Decision trees make split decisions based strictly on feature rank order rather than absolute Euclidean distance. Consequently, Random Forest is **naturally robust to extreme values**, allowing full preservation of legitimate medical pathology without risking model distortion.
* It seamlessly integrates heterogeneous data types: continuous vitals (`age`, `chol`, `thalach`), discrete counts (`ca`), ordinal scales (`slope`), and one-hot encoded nominal categories (`cp`, `restecg`, `thal`).
---
## 4. Overfitting Control via Ensemble Bagging
A single decision tree is prone to high variance and overfits small clinical cohorts ($N = 303$). Random Forest eliminates this limitation through dual randomization:
1. **Bootstrap Aggregation (Bagging):** Trains an ensemble of $100$ independent decision trees, each on a distinct bootstrap sample with replacement from the training set ($N_{\text{train}} = 242$).
2. **Feature Subspace Sampling:** Evaluates only a random subset of predictors ($\sqrt{p}$) at each split, decorrelating individual trees.
3. **Complexity Regularization:** Constraining the tree depth (`max_depth = 4`) prevented leaf-node memorization and ensured smooth, well-generalized decision boundaries.
---
## 5. Clinical Interpretability & Guideline Alignment (ACC/AHA)
Unlike black-box architectures (e.g., deep neural networks), Random Forest provides directly auditable Gini feature importance rankings. The top five predictors selected by the model were:
1. **`ca`** (Number of major vessels visualized by fluoroscopy)
2. **`thal`** (Reversible or fixed defect on thallium scintigraphy)
3. **`oldpeak`** (Exercise-induced ST depression relative to rest)
4. **`cp`** (Chest pain presentation, especially asymptomatic ischemia)
5. **`thalach`** (Maximum heart rate achieved during exercise stress)
These quantitative rankings correspond directly to established **American College of Cardiology / American Heart Association (ACC/AHA)** clinical guidelines for treadmill stress testing and coronary disease risk stratification.
---
## 6. Summary Conclusion
Random Forest was chosen because it:
1. Delivered the **highest overall test accuracy (91.8%) and ROC-AUC (0.959)** on unseen patient data.
2. Achieved the **primary safety threshold of 92.9% Sensitivity** (missing only 2 out of 28 diseased cases).
3. Cut **unnecessary angiographic referrals (False Positives) by 40%** relative to Logistic Regression.
4. Naturally accommodated non-linear clinical interactions and authentic extreme vitals without data manipulation.
5. Preserved clinical transparency and biological plausibility through interpretable feature rankings.

