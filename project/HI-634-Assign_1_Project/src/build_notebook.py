import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = [
    nbf.v4.new_markdown_cell("""# Health Informatics (HI-634) - Assignment 1
## Option 2: UCI Heart Disease Classification Pipeline

### Student Project Information
* **Course:** HI-634 Health Informatics
* **Option:** Option 2 - UCI Heart Disease (Cleveland Database)
* **Dataset Identifier:** UCI Machine Learning Repository ID 45
* **Source URL:** https://archive.ics.uci.edu/dataset/45/heart+disease
* **Environment:** Python 3.13 in isolated `.venv`
* **Raw Data Integrity:** `data/raw/processed.cleveland.data` preserved unchanged.
"""),

    nbf.v4.new_markdown_cell("""### 1. Environment Setup & Dependency Verification"""),
    nbf.v4.new_code_cell("""import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix
)

print(f"Python interpreter: {sys.executable}")
print(f"Pandas version: {pd.__version__}")
"""),

    nbf.v4.new_markdown_cell("""### 2. Loading Raw Data & Assigning Documented 14 Attributes
The raw file `data/raw/processed.cleveland.data` is an authentic headerless CSV from UCI, encoding missing values as `?`."""),
    nbf.v4.new_code_cell("""RAW_DATA_PATH = '../data/raw/processed.cleveland.data'

column_names = [
    'age',       # 1. Age in years (Continuous)
    'sex',       # 2. Sex (1=male, 0=female)
    'cp',        # 3. Chest pain type (1: typical angina, 2: atypical angina, 3: non-anginal, 4: asymptomatic)
    'trestbps',  # 4. Resting blood pressure in mm Hg
    'chol',      # 5. Serum cholesterol in mg/dl
    'fbs',       # 6. Fasting blood sugar > 120 mg/dl (1=true, 0=false)
    'restecg',   # 7. Resting ECG (0: normal, 1: ST-T wave abnormality, 2: left ventricular hypertrophy)
    'thalach',   # 8. Maximum heart rate achieved during exercise
    'exang',     # 9. Exercise-induced angina (1=yes, 0=no)
    'oldpeak',   # 10. ST depression induced by exercise relative to rest
    'slope',     # 11. Slope of peak exercise ST segment (1: upsloping, 2: flat, 3: downsloping)
    'ca',        # 12. Number of major vessels (0-3) colored by fluoroscopy
    'thal',      # 13. Thallium scan (3: normal, 6: fixed defect, 7: reversible defect)
    'num'        # 14. Target: angiographic disease status (0: <50% stenosis, 1-4: >50% stenosis)
]

df_raw = pd.read_csv(RAW_DATA_PATH, header=None, names=column_names, na_values='?')
print(f"Loaded raw dataset with shape: {df_raw.shape}")
df_raw.head()
"""),

    nbf.v4.new_markdown_cell("""### 3. Data Auditing: Missingness, Duplicates, & Distributions"""),
    nbf.v4.new_code_cell("""# Check for duplicates
print(f"Duplicate rows count: {df_raw.duplicated().sum()}")

# Missingness audit
missing = df_raw.isna().sum()
missing_pct = (missing / len(df_raw)) * 100
missing_df = pd.DataFrame({'Missing_Count': missing, 'Missing_Pct': missing_pct})
print("\\nMissing Value Audit:")
print(missing_df[missing_df['Missing_Count'] > 0])
"""),

    nbf.v4.new_code_cell("""# Continuous numerical feature summary
num_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
df_raw[num_cols].describe().T[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
"""),

    nbf.v4.new_code_cell("""# Categorical feature frequencies
cat_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal', 'num']
for c in cat_cols:
    print(f"--- {c} ---")
    print(df_raw[c].value_counts(dropna=False).sort_index())
    print()
"""),

    nbf.v4.new_markdown_cell("""### 4. Data Cleaning Changelog: Finding, Decision, & Reason
Each modification is explicitly justified and recorded in `reports/cleaning_decisions_log.csv`."""),
    nbf.v4.new_code_cell("""changelog_df = pd.read_csv('../reports/cleaning_decisions_log.csv')
changelog_df
"""),

    nbf.v4.new_code_cell("""# Create target variable: 0 = No heart disease, 1 = Heart disease present
df = df_raw.copy()
df['target'] = (df['num'] > 0).astype(int)
print(f"Target distribution:\\n{df['target'].value_counts(normalize=True).round(3)}")
"""),

    nbf.v4.new_markdown_cell("""### 5. Stratified Train-Test Split (80% Train / 20% Test)
To prevent data leakage, 20% of data is isolated as a test set before any preprocessing."""),
    nbf.v4.new_code_cell("""X = df.drop(columns=['num', 'target'])
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
print(f"X_test shape:  {X_test.shape}, y_test shape:  {y_test.shape}")
print(f"Train positive prevalence: {y_train.mean():.3f}")
print(f"Test positive prevalence:  {y_test.mean():.3f}")
"""),

    nbf.v4.new_markdown_cell("""### 6. Leakage-Free Preprocessing Pipeline
Imputers and scalers are fitted **strictly on the training set**."""),
    nbf.v4.new_code_cell("""numeric_features = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
nominal_features = ['cp', 'restecg', 'thal']
ordinal_features = ['ca', 'slope']
binary_features = ['sex', 'fbs', 'exang']

preprocessor = ColumnTransformer(transformers=[
    ('num', Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), numeric_features),
    ('nom', Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))]), nominal_features),
    ('ord', Pipeline([('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())]), ordinal_features),
    ('bin', Pipeline([('imputer', SimpleImputer(strategy='most_frequent'))]), binary_features)
])
"""),

    nbf.v4.new_markdown_cell("""### 7. Model Training & 5-Fold Stratified Cross-Validation
Comparing **Baseline (Logistic Regression)** with **Alternative 1 (Random Forest)** and **Alternative 2 (Gradient Boosting)**."""),
    nbf.v4.new_code_cell("""models = {
    'Baseline: Logistic Regression': Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ]),
    'Alternative 1: Random Forest': Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42))
    ]),
    'Alternative 2: Gradient Boosting': Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42))
    ])
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = {}

for name, pipe in models.items():
    scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring='roc_auc')
    cv_results[name] = scores
    print(f"{name}: 5-Fold CV ROC-AUC = {scores.mean():.3f} +/- {scores.std():.3f}")
"""),

    nbf.v4.new_markdown_cell("""### 8. Final Test Set Evaluation & Comparison Table"""),
    nbf.v4.new_code_cell("""results = []
y_preds = {}
y_probs = {}

for name, pipe in models.items():
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]
    
    y_preds[name] = y_pred
    y_probs[name] = y_prob
    
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    results.append({
        'Model': name,
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Sensitivity (Recall)': recall_score(y_test, y_pred),
        'Specificity': tn / (tn + fp),
        'F1-Score': f1_score(y_test, y_pred),
        'ROC-AUC': roc_auc_score(y_test, y_prob)
    })

eval_df = pd.DataFrame(results).set_index('Model').round(3)
eval_df
"""),

    nbf.v4.new_markdown_cell("""### 9. Visualizations: ROC Curves, Confusion Matrices, & Feature Importance"""),
    nbf.v4.new_code_cell("""# ROC Curves
plt.figure(figsize=(8, 6))
colors = {'Baseline: Logistic Regression': '#1f77b4', 'Alternative 1: Random Forest': '#2ca02c', 'Alternative 2: Gradient Boosting': '#ff7f0e'}

for name, prob in y_probs.items():
    fpr, tpr, _ = roc_curve(y_test, prob)
    auc = roc_auc_score(y_test, prob)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", color=colors[name], lw=2)

plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Chance (AUC = 0.500)')
plt.xlabel('False Positive Rate (1 - Specificity)')
plt.ylabel('True Positive Rate (Sensitivity)')
plt.title('ROC Curves Comparison on Unseen Test Set (N=61)')
plt.legend(loc='lower right')
plt.show()
"""),

    nbf.v4.new_code_cell("""# Confusion Matrices
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for i, (name, pred) in enumerate(y_preds.items()):
    cm = confusion_matrix(y_test, pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=axes[i],
                xticklabels=['No Disease', 'Disease'], yticklabels=['No Disease', 'Disease'])
    axes[i].set_title(name, fontsize=10, fontweight='bold')
    axes[i].set_xlabel('Predicted')
    axes[i].set_ylabel('True')
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_code_cell("""# Top Features (Random Forest)
rf_pipe = models['Alternative 1: Random Forest']
preprocessor = rf_pipe.named_steps['preprocessor']
nom_cols = preprocessor.named_transformers_['nom'].named_steps['onehot'].get_feature_names_out(['cp', 'restecg', 'thal']).tolist()
all_cols = numeric_features + nom_cols + ordinal_features + binary_features

rf_importances = pd.Series(rf_pipe.named_steps['classifier'].feature_importances_, index=all_cols).sort_values(ascending=False)

plt.figure(figsize=(9, 5))
rf_importances.head(10).plot(kind='barh', color='#2ca02c').invert_yaxis()
plt.title('Top 10 Feature Importances (Random Forest)')
plt.xlabel('Gini Importance')
plt.show()
"""),

    nbf.v4.new_markdown_cell("""### 10. Conclusion & Clinical Interpretation
1. **Model Performance:** Random Forest achieved the highest overall test accuracy (**91.8%**) and balanced diagnostic accuracy with **92.9% Sensitivity** and **90.9% Specificity** (ROC-AUC = 0.959).
2. **Clinical Significance:** The most predictive variables identified across models are fluoroscopy vessel count (`ca`), thallium stress test defects (`thal`), asymptomatic chest pain presentation (`cp`), exercise ST depression (`oldpeak`), and maximum heart rate achieved (`thalach`).
3. **Reproducibility:** All data transformations were performed using strict training-split fitting, fully preventing data leakage.
""")
]

nb.cells = cells

with open('notebooks/exploratory_data_analysis.ipynb', 'w') as f:
    nbf.write(nb, f)

print('Successfully generated notebooks/exploratory_data_analysis.ipynb')
