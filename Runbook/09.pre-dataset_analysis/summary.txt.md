
### Summary of Inventory Highlights:

* File Inventory & Dimensions:

	* Raw file data/raw/processed.cleveland.data: 303 rows × 14 columns (headerless text, '?' missing markers).
	
	* Cleaned file data/processed/heart_disease_cleaned.csv: 303 rows × 15 columns (includes binary target).

* Sample Rows & Types:

	* Displays raw comma-separated text vs. verified 14-attribute clinical data dictionary (age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, num).
	
* Missingness & Duplicate Audit:

	* 0 duplicate rows (0.00%).
	
	* Exactly 6 missing '?' values confined strictly to specialized cardiac tests: ca (4 missing, 1.32%) and thal (2 missing, 0.66%). 100% complete data for the other 12 features.
	
* Distributions & Balances:

	* Outcome: Naturally balanced binary label (54.13% absence vs. 45.87% presence; 1.18:1 ratio). Multi-class stage 4 has only 13 cases (4.29%).
	
	* Key Predictors by Outcome: Significant separation confirmed for thalach (mean 158.4 bpm in health vs. 139.3 bpm in disease; 𝑝 = 9.11 × 10 − 14 p=9.11×10−14) and oldpeak (0.59 mm vs. 1.57 mm; 𝑝=2.20×10−13p=2.20×10−13).

* Linked File / Key Check:

	* The dataset is a single flat encounter table (𝑁=303 N=303). Cross-referencing between source copies confirmed 0 unmatched rows and unique implicit primary keys.
	
* Concrete Findings Guiding Preparation:

1. Sparse Missingness in ca & thal: Handled via in-pipeline median/mode imputation on training folds.

2. Balanced Target vs. Sparse Extreme Classes: Binarization aligns with clinical stenosis thresholds (>50%) and avoids extreme tail sparsity.

3. Extreme Cholesterol Outliers: Patient 152 at 564 mg/dl retained as authentic clinical data with standard scaling in pipeline.

4. Chest Pain Paradox: Asymptomatic patients (cp=4) represent 47.5% of the cohort and carry a 72.9% disease rate, requiring one-hot dummy coding.


<br><br>


