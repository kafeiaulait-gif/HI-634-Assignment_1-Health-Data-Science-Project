
### What Each Version Contains (6 Pages / Sections):


1.  Section 1: Question and Data Source

	* Focused research question on predicting > 50% >50% coronary stenosis from routine clinical & exercise markers.

	* UCI Heart Disease citation (Cleveland Clinic cohort, ID 45; Detrano et al., 1989).

	* Unit of observation (adult patient clinical encounter, 𝑁=303 N=303) and point-of-care clinical triage implications.

	* Clinical data suitability rationale (angiographic ground truth across the full clinical diagnostic cascade).


2.  Section 2: Initial Exploration & Data Quality Audit

	* Structural overview (303×14 303×14 dimensions, 0 duplicate rows).

	* Complete 14-attribute clinical data dictionary table with scales, units, and categories.

	* Missing value audit: exactly 6 '?' entries confined strictly to tertiary imaging (ca missing 4, thal missing 2; 100% complete for the other 12 features).

	* Four concrete findings guiding preparation (nominal integer codes, localized missingness, authentic cholesterol extremes up to 564 mg/dl, and the asymptomatic chest pain paradox).


3.  Section 3: Preparation, Leakage Prevention, & Reproducibility

	* Target binarization (𝑛𝑢𝑚>0→1 num>0→1) and class balance (54.1% absence vs. 45.9% presence).

	* Leakage-free stratified 80/20 train/test holdout (𝑁=242 N=242 train, 𝑁=61 N=61 test) executed before transformer fitting.

	* Scikit-learn Pipeline and ColumnTransformer architecture with imputation, scaling, and dummy coding.

	* Identifier removal, target isolation, and temporal measurement sequence audit.

	* Structured data cleaning decisions changelog table.


4.  Section 4: Model Comparison and Evaluation

	* Metric selection rationale: Primary safety metric Sensitivity / Recall (and ROC-AUC) to avoid fatal False Negatives, complemented by Specificity, Precision, F1, and Accuracy.

	* 5-Fold Stratified Cross-Validation on training data (𝑁=242 N=242) across Majority Baseline, Logistic Regression, Random Forest, and Gradient Boosting.

	* Untouched test set evaluation (𝑁=61 N=61): Random Forest achieved 91.8% Accuracy, 92.9% Sensitivity, 90.9% Specificity, 0.912 F1, and 0.959 ROC-AUC.

	* Unsupervised K-Means clustering (𝑘=2,3,4k=2,3,4): demonstrating that numerical silhouette scores must be paired with clinical risk profiles (Cluster 0 carries a 75.8% disease rate; at 𝑘=4 k=4, Cluster 3 isolates a 94.9% disease rate).


5.  Section 5: Figures and Interpretation

	* Figure 1: Attribute Data Completeness & Missing Value Audit (𝑁=303 N=303) with full caption.

	* Figure 2: Exercise ST Depression vs. Peak Heart Rate by Outcome (𝑁=303 N=303) with full caption.

	* Figure 3: Selected Random Forest Confusion Matrix & ROC Curve (𝑁=61 N=61) with full caption.

	* Plain-language clinical error analysis: consequences of Type I False Positives (unnecessary angiography) vs. Type II False Negatives (unheralded heart attack).

	* Non-causal reporting: correlational framing recognizing exercise markers as functional manifestations of ischemia.

6.  Section 6: Limitations, Next Steps, Conclusion, & References

	* Clinical limitations (68% male historical referral cohort, single-center tertiary filter, modest test size).
	
	* Actionable next steps (multi-center validation on Hungarian/Zurich/Long Beach cohorts, decision-curve analysis, multi-vessel progression modeling).

	* Conclusion, formal academic references, and runnable asset appendix.


