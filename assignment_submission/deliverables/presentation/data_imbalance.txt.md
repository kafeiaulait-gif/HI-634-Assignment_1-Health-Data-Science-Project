
# How much imbalance does data have?

---

The degree of imbalance depends on whether you look at the **binary diagnostic target**, the **raw multi-class disease stages**, or the **clinical predictor features**:

---

### 1. Primary Binary Target: Naturally Balanced (Very Mild Imbalance)

When framed as clinical screening for significant coronary stenosis ($> 50\%$ vessel narrowing), the binary outcome is **almost 1:1 balanced**:

| Class | Definition | Patient Count ($N = 303$) | Cohort Proportion | Imbalance Ratio |
| :---: | :--- | :---: | :---: | :---: |
| **0** | Absence of significant CAD ($< 50\%$ stenosis) | **164** | **54.13%** | **1.18 : 1** |
| **1** | Presence of significant CAD ($\ge 50\%$ stenosis) | **139** | **45.87%** | |

* **Implication:** The dataset does not suffer from severe binary target imbalance (unlike typical rare-disease datasets where the positive class is $< 5\%$). Techniques like SMOTE or heavy downsampling were unnecessary and would have distorted authentic clinical probabilities.
* **Preservation:** A stratified 80/20 train/test split was used to guarantee this exact 54.13%/45.87% ratio was maintained across partitions:
    * **Training (`X_train`, $N = 242$):** 131 healthy (54.1%) vs. 111 diseased (45.9%).
    * **Holdout Test (`X_test`, $N = 61$):** 33 healthy (54.1%) vs. 28 diseased (45.9%).

---

### 2. Original Raw Target (`num`): Severe Multi-Class Skew

Before binarization, the raw diagnostic column (`num`) measured the number of narrowed major vessels (0 to 4), exhibiting **heavy right-skewed imbalance**:

| Stage (`num`) | Vessels Narrowed | Patient Count | Proportion | Imbalance Ratio (vs. Class 0) |
| :---: | :--- | :---: | :---: | :---: |
| **0** | No significant stenosis | 164 | 54.13% | 1.0 : 1 |
| **1** | Mild (1 vessel) | 55 | 18.15% | 2.98 : 1 |
| **2** | Moderate (2 vessels) | 36 | 11.88% | 4.56 : 1 |
| **3** | Severe (3 vessels) | 35 | 11.55% | 4.69 : 1 |
| **4** | Critical (4 vessels) | 13 | 4.29% | **12.62 : 1** |

* **Implication:** Category 4 contains only 13 cases in the entire cohort. This severe tail sparsity is one of the primary medical and statistical reasons for collapsing the problem into binary classification (`num` $> 0$).

---

### 3. Key Predictor Imbalances

While the binary outcome is balanced, several clinical and demographic predictor features have significant category imbalances:

* **Biological Sex (`sex`):**
    * **206 males (68.0%) vs. 97 females (32.0%)** $\rightarrow$ **2.12 : 1 male predominance**, reflecting historical cardiovascular referral patterns.
* **Fasting Blood Sugar (`fbs`):**
    * **258 normal $\le 120$ mg/dL (85.1%) vs. 45 elevated $> 120$ mg/dL (14.9%)** $\rightarrow$ **5.73 : 1 imbalance**.
* **Resting ECG (`restecg`):**
    * Normal: 151 (49.8%)
    * Left Ventricular Hypertrophy: 148 (48.8%)
    * **ST-T wave abnormality: only 4 patients (1.3%)** $\rightarrow$ extreme category sparsity.
* **Chest Pain Type (`cp`):**
    * Asymptomatic (Type 4): 144 (47.5%)
    * Non-anginal pain (Type 3): 86 (28.4%)
    * Atypical angina (Type 2): 50 (16.5%)
    * **Typical angina (Type 1): only 23 patients (7.6%)**.

---

### Summary

* **Binary Target:** **1.18 : 1** (essentially balanced; no re-weighting needed).
* **Multi-class Target:** Up to **12.6 : 1** (severe skew in four-vessel disease).
* **Predictors:** Substantial demographic skew (68% male) and feature sparsity (15% elevated blood sugar, 1.3% resting ST-T abnormalities).


<br>
<br>