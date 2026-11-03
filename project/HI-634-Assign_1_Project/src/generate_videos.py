"""
Generate Two Video Clips for PowerPoint Slides:
1. video1_clinical_relationship.mp4: Animated scatter & KDE mapping of peak heart rate vs. ST depression
2. video2_roc_threshold_sweep.mp4: Animated ROC curve and decision threshold sweep showing TP/FP/TN/FN
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import imageio
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix
from src.model_pipeline import build_preprocessor, RandomForestClassifier

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(PROJECT_ROOT, "automation", "figures")
VIDEOS_DIR = os.path.join(PROJECT_ROOT, "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "processed.cleveland.data")
cols = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'num']
df = pd.read_csv(RAW_PATH, header=None, names=cols, na_values='?')
df['target'] = (df['num'] > 0).astype(int)

# =========================================================================
# VIDEO 1: Clinical Relationship Animation (thalach vs oldpeak)
# =========================================================================
print("Generating Video 1: Clinical Relationship Animation...")
vid1_path = os.path.join(VIDEOS_DIR, "video1_clinical_relationship.mp4")
fps = 15
n_frames = 60

writer1 = imageio.get_writer(vid1_path, fps=fps, codec="libx264")

healthy = df[df['target'] == 0]
diseased = df[df['target'] == 1]

for frame_idx in range(n_frames):
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=100)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#FFFFFF')
    
    # Progressively reveal points
    progress = (frame_idx + 1) / n_frames
    n_h = int(len(healthy) * progress)
    n_d = int(len(diseased) * progress)
    
    if n_h > 0:
        ax.scatter(healthy['thalach'].iloc[:n_h], healthy['oldpeak'].iloc[:n_h], 
                   color='#1F77B4', alpha=0.75, s=45, label=f'Healthy Controls (n={n_h})', edgecolors='none')
    if n_d > 0:
        ax.scatter(diseased['thalach'].iloc[:n_d], diseased['oldpeak'].iloc[:n_d], 
                   color='#D95F02', alpha=0.75, s=45, label=f'Coronary Disease (n={n_d})', edgecolors='none')
        
    ax.axvline(150, color='gray', linestyle=':', alpha=0.6)
    ax.axhline(1.0, color='gray', linestyle=':', alpha=0.6)
    
    ax.set_xlim(65, 210)
    ax.set_ylim(-0.3, 6.5)
    ax.set_xlabel("Maximum Exercise Heart Rate - thalach (bpm)", fontsize=10, fontweight='bold', color='#1A365D')
    ax.set_ylabel("Exercise ST Depression - oldpeak (mm)", fontsize=10, fontweight='bold', color='#1A365D')
    ax.set_title(f"Clinical Phenotype Separation (N = {n_h + n_d} / 303 Patients)", fontsize=11, fontweight='bold', color='#1A365D')
    
    # Add quadrant labels on later frames
    if frame_idx > 30:
        ax.text(180, 0.3, "LOW RISK\n(67.7% Healthy)", fontsize=8.5, weight='bold', color='#1F77B4', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#EBF8FF', edgecolor='#3182CE', alpha=0.85))
        ax.text(105, 3.5, "HIGH RISK\n(89.9% Diseased)", fontsize=8.5, weight='bold', color='#D95F02', ha='center',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEEBC8', edgecolor='#DD6B20', alpha=0.85))
        
    ax.legend(loc='upper right', fontsize=8.5, frameon=True)
    plt.tight_layout()
    
    fig.canvas.draw()
    image = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    # Ensure dimensions divisible by 16 for h264
    h, w, _ = image.shape
    h_pad = (16 - h % 16) % 16
    w_pad = (16 - w % 16) % 16
    if h_pad or w_pad:
        image = np.pad(image, ((0, h_pad), (0, w_pad), (0, 0)), mode='edge')
    writer1.append_data(image)
    plt.close(fig)

writer1.close()
print(f"Video 1 generated: {vid1_path} ({os.path.getsize(vid1_path)} bytes)")

# =========================================================================
# VIDEO 2: ROC Curve & Decision Threshold Sweep
# =========================================================================
print("Generating Video 2: ROC Decision Sweep Animation...")
vid2_path = os.path.join(VIDEOS_DIR, "video2_roc_threshold_sweep.mp4")

X = df.drop(columns=['num', 'target'])
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

rf = Pipeline([
    ('preprocessor', build_preprocessor()),
    ('classifier', RandomForestClassifier(n_estimators=100, max_depth=4, random_state=42))
])
rf.fit(X_train, y_train)
y_probs = rf.predict_proba(X_test)[:, 1]

fpr_all, tpr_all, thresholds = roc_curve(y_test, y_probs)
auc_val = roc_auc_score(y_test, y_probs)

writer2 = imageio.get_writer(vid2_path, fps=fps, codec="libx264")
sweep_thresholds = np.linspace(0.99, 0.05, n_frames)

for frame_idx, thresh in enumerate(sweep_thresholds):
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.8), dpi=100)
    fig.patch.set_facecolor('#F8FAFC')
    
    # Calculate metrics at this threshold
    y_pred_thresh = (y_probs >= thresh).astype(int)
    cm = confusion_matrix(y_test, y_pred_thresh)
    tn, fp, fn, tp = cm.ravel()
    current_fpr = fp / (tn + fp)
    current_tpr = tp / (tp + fn)
    
    # Left Panel: ROC Curve
    axes[0].set_facecolor('#FFFFFF')
    axes[0].plot(fpr_all, tpr_all, color='#2CA02C', lw=2.5, label=f'Random Forest (AUC = {auc_val:.3f})')
    axes[0].plot([0, 1], [0, 1], 'k--', lw=1.2, label='Chance Baseline')
    axes[0].scatter([current_fpr], [current_tpr], color='#E53E3E', s=130, zorder=5, 
                    label=f'Threshold: {thresh:.2f}\nSens: {current_tpr:.1%}, Spec: {1-current_fpr:.1%}')
    axes[0].set_xlim(-0.02, 1.02)
    axes[0].set_ylim(-0.02, 1.05)
    axes[0].set_xlabel('False Positive Rate (1 - Specificity)', fontsize=9.5, fontweight='bold', color='#1A365D')
    axes[0].set_ylabel('True Positive Rate (Sensitivity / Recall)', fontsize=9.5, fontweight='bold', color='#1A365D')
    axes[0].set_title('A. ROC Curve Threshold Sweep', fontsize=11, fontweight='bold', color='#1A365D')
    axes[0].legend(loc='lower right', fontsize=8, frameon=True)
    
    # Right Panel: Live Confusion Matrix
    axes[1].set_facecolor('#FFFFFF')
    labels = [
        [f"True Neg (TN)\n{tn} / 33\n({tn/33*100:.0f}%)", f"False Pos (FP)\n{fp} / 33\n({fp/33*100:.0f}%)"],
        [f"False Neg (FN)\n{fn} / 28\n({fn/28*100:.0f}%)", f"True Pos (TP)\n{tp} / 28\n({tp/28*100:.0f}%)"]
    ]
    sns.heatmap(cm, annot=labels, fmt='', cmap='Blues', cbar=False, ax=axes[1], annot_kws={'size': 9, 'weight': 'bold'})
    axes[1].set_xticklabels(['Pred: Absent', 'Pred: Present'], fontsize=9, fontweight='bold')
    axes[1].set_yticklabels(['True: Absent', 'True: Present'], fontsize=9, fontweight='bold')
    axes[1].set_title(f'B. Live Test Confusion Matrix (N = 61)\nAccuracy: {(tp+tn)/61*100:.1f}% | Cutoff: {thresh:.2f}', fontsize=11, fontweight='bold', color='#1A365D')
    
    plt.tight_layout()
    fig.canvas.draw()
    image = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    h, w, _ = image.shape
    h_pad = (16 - h % 16) % 16
    w_pad = (16 - w % 16) % 16
    if h_pad or w_pad:
        image = np.pad(image, ((0, h_pad), (0, w_pad), (0, 0)), mode='edge')
    writer2.append_data(image)
    plt.close(fig)

writer2.close()
print(f"Video 2 generated: {vid2_path} ({os.path.getsize(vid2_path)} bytes)")
