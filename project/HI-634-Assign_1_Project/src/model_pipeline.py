"""
Model Training, Preprocessing Pipeline, and Evaluation Module
Option 2: UCI Heart Disease (HI-634 Assignment 1)

Guarantees:
1. Preprocessing (imputation and scaling) is fit ONLY on training data.
2. An isolated 20% stratified test set is kept separate and evaluated once.
3. Baseline (Logistic Regression) compared against Alternative 1 (Random Forest)
   and Alternative 2 (Gradient Boosting).
4. Generates labeled figures and a structured metrics summary.
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "heart_disease_cleaned.csv")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "reports", "figures")

def build_preprocessor():
    # Continuous numeric features -> Impute median + Standard Scale
    numeric_features = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    # Categorical nominal features -> Impute mode + One-Hot Encode (drop first)
    nominal_features = ["cp", "restecg", "thal"]
    nominal_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"))
    ])
    
    # Discrete / Ordinal features -> Impute median
    ordinal_features = ["ca", "slope"]
    ordinal_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    # Binary features -> Pass through (already 0/1)
    binary_features = ["sex", "fbs", "exang"]
    binary_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent"))
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ("num", numeric_transformer, numeric_features),
        ("nom", nominal_transformer, nominal_features),
        ("ord", ordinal_transformer, ordinal_features),
        ("bin", binary_transformer, binary_features)
    ])
    
    return preprocessor

def run_experiment():
    os.makedirs(FIGURES_DIR, exist_ok=True)
    
    # 1. Load Cleaned Dataset
    print(f"Loading data from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    
    # Define features and target (exclude 'num' which is original multi-class target)
    feature_cols = [c for c in df.columns if c not in ["num", "target"]]
    X = df[feature_cols]
    y = df["target"]
    
    print(f"Features: {X.shape[1]}, Instances: {X.shape[0]}")
    print(f"Target distribution: 0={sum(y==0)}, 1={sum(y==1)} ({sum(y==1)/len(y)*100:.1f}% positive)")
    
    # 2. Strict Train-Test Split (80/20 Stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Train split: {X_train.shape[0]} samples | Test split: {X_test.shape[0]} samples")
    
    # 3. Define Models
    models = {
        "Baseline: Logistic Regression": Pipeline(steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42))
        ]),
        "Alternative 1: Random Forest": Pipeline(steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42))
        ]),
        "Alternative 2: Gradient Boosting": Pipeline(steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", GradientBoostingClassifier(n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42))
        ])
    }
    
    # 4. Train, Cross-Validate, and Evaluate
    results = []
    trained_models = {}
    y_preds = {}
    y_probs = {}
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, pipeline in models.items():
        print(f"\n--- Training {name} ---")
        
        # 5-fold cross-validation strictly on training data
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="roc_auc")
        print(f"5-Fold CV ROC-AUC (Train): {cv_scores.mean():.3f} +/- {cv_scores.std():.3f}")
        
        # Fit pipeline on full training set
        pipeline.fit(X_train, y_train)
        trained_models[name] = pipeline
        
        # Predict on unseen test set
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        y_preds[name] = y_pred
        y_probs[name] = y_prob
        
        # Compute test set metrics
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)  # Sensitivity
        spec = tn / (tn + fp)              # Specificity
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        print(f"Test Accuracy:    {acc:.3f}")
        print(f"Test Sensitivity: {rec:.3f}")
        print(f"Test Specificity: {spec:.3f}")
        print(f"Test F1-Score:    {f1:.3f}")
        print(f"Test ROC-AUC:     {auc:.3f}")
        
        results.append({
            "Model": name,
            "CV_ROC_AUC_Mean": cv_scores.mean(),
            "CV_ROC_AUC_Std": cv_scores.std(),
            "Test_Accuracy": acc,
            "Test_Precision": prec,
            "Test_Sensitivity_Recall": rec,
            "Test_Specificity": spec,
            "Test_F1_Score": f1,
            "Test_ROC_AUC": auc,
            "True_Negatives": tn,
            "False_Positives": fp,
            "False_Negatives": fn,
            "True_Positives": tp
        })
    
    df_results = pd.DataFrame(results)
    results_path = os.path.join(FIGURES_DIR, "model_performance_table.csv")
    df_results.to_csv(results_path, index=False)
    print(f"\nModel performance table saved to: {results_path}")
    
    # 5. Generate Figures
    generate_evaluation_figures(y_test, y_preds, y_probs, df_results, trained_models, X_train)
    
    return df_results

def generate_evaluation_figures(y_test, y_preds, y_probs, df_results, trained_models, X_train):
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    
    # ---------------- FIGURE 1: ROC Curves Comparison ----------------
    plt.figure(figsize=(8, 6))
    colors = {"Baseline: Logistic Regression": "#1f77b4", "Alternative 1: Random Forest": "#2ca02c", "Alternative 2: Gradient Boosting": "#ff7f0e"}
    
    for name, prob in y_probs.items():
        fpr, tpr, _ = roc_curve(y_test, prob)
        auc = roc_auc_score(y_test, prob)
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", color=colors[name], lw=2)
        
    plt.plot([0, 1], [0, 1], "k--", lw=1.5, label="Random Guess (AUC = 0.500)")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=11)
    plt.ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11)
    plt.title("ROC Curves Comparison (Test Set N=61)", fontsize=13, fontweight="bold")
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    roc_fig_path = os.path.join(FIGURES_DIR, "roc_curves_comparison.png")
    plt.savefig(roc_fig_path, dpi=300)
    plt.close()
    print(f"ROC curves figure saved to: {roc_fig_path}")
    
    # ---------------- FIGURE 2: Confusion Matrices Comparison ----------------
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    model_names = list(y_preds.keys())
    
    for i, name in enumerate(model_names):
        cm = confusion_matrix(y_test, y_preds[name])
        sns.heatmap(
            cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=axes[i],
            xticklabels=["No Disease (0)", "Disease (1)"],
            yticklabels=["No Disease (0)", "Disease (1)"]
        )
        axes[i].set_title(name, fontsize=11, fontweight="bold")
        axes[i].set_xlabel("Predicted Label", fontsize=10)
        axes[i].set_ylabel("True Clinical Label", fontsize=10)
        
    plt.suptitle("Confusion Matrices on Unseen Test Set (N=61)", fontsize=14, fontweight="bold", y=1.03)
    plt.tight_layout()
    cm_fig_path = os.path.join(FIGURES_DIR, "confusion_matrices_comparison.png")
    plt.savefig(cm_fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Confusion matrices figure saved to: {cm_fig_path}")
    
    # ---------------- FIGURE 3: Performance Metrics Bar Chart ----------------
    metrics_to_plot = ["Test_Accuracy", "Test_Sensitivity_Recall", "Test_Specificity", "Test_F1_Score", "Test_ROC_AUC"]
    plot_df = df_results.melt(id_vars=["Model"], value_vars=metrics_to_plot, var_name="Metric", value_name="Score")
    plot_df["Metric"] = plot_df["Metric"].str.replace("Test_", "").str.replace("_", " ")
    
    plt.figure(figsize=(10, 5.5))
    ax = sns.barplot(data=plot_df, x="Metric", y="Score", hue="Model", palette="deep")
    plt.title("Model Performance Metrics Comparison on Unseen Test Set", fontsize=13, fontweight="bold")
    plt.ylabel("Score (0.0 to 1.0)", fontsize=11)
    plt.ylim(0.0, 1.05)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
    
    # Add data labels
    for p in ax.patches:
        height = p.get_height()
        if height > 0.05:
            ax.annotate(f"{height:.2f}",
                        (p.get_x() + p.get_width() / 2., height / 2.),
                        ha="center", va="center", fontsize=8, color="white", weight="bold")
            
    plt.tight_layout()
    metrics_fig_path = os.path.join(FIGURES_DIR, "model_metrics_comparison.png")
    plt.savefig(metrics_fig_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Metrics comparison bar chart saved to: {metrics_fig_path}")
    
    # ---------------- FIGURE 4: Feature Importance (Random Forest vs Logistic Regression) ----------------
    # Extract feature names from fitted OneHotEncoder
    rf_pipe = trained_models["Alternative 1: Random Forest"]
    lr_pipe = trained_models["Baseline: Logistic Regression"]
    
    preprocessor = rf_pipe.named_steps["preprocessor"]
    nom_cols = preprocessor.named_transformers_["nom"].named_steps["onehot"].get_feature_names_out(["cp", "restecg", "thal"]).tolist()
    all_feature_names = ["age", "trestbps", "chol", "thalach", "oldpeak"] + nom_cols + ["ca", "slope"] + ["sex", "fbs", "exang"]
    
    rf_importances = rf_pipe.named_steps["classifier"].feature_importances_
    lr_coefficients = lr_pipe.named_steps["classifier"].coef_[0]
    
    feat_df = pd.DataFrame({
        "Feature": all_feature_names,
        "RF_Importance": rf_importances,
        "LR_Abs_Coefficient": np.abs(lr_coefficients)
    }).sort_values(by="RF_Importance", ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=feat_df.head(10), x="RF_Importance", y="Feature", hue="Feature", palette="viridis", legend=False)
    plt.title("Top 10 Clinical Features by Predictive Importance (Random Forest)", fontsize=13, fontweight="bold")
    plt.xlabel("Gini Feature Importance", fontsize=11)
    plt.ylabel("Clinical Feature / Encoded Category", fontsize=11)
    plt.tight_layout()
    feat_fig_path = os.path.join(FIGURES_DIR, "feature_importance_comparison.png")
    plt.savefig(feat_fig_path, dpi=300)
    plt.close()
    print(f"Feature importance figure saved to: {feat_fig_path}")

if __name__ == "__main__":
    run_experiment()
