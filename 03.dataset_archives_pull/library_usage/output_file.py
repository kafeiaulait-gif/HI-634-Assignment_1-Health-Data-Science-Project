import os
import sys
import pandas as pd
from lib.uci_utility import UCIDataPipeline
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Initialize the pipeline for the Heart Disease dataset (ID 45)
heartdisease_pipeline = UCIDataPipeline(dataset_id=45)
heartdisease_pipeline.fetch_data()

# -------------------------------------------------------------
# 1. EXPORT RAW DATA TO LOCAL DIRECTORY CSV FILES
# -------------------------------------------------------------
output_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'

print(f"💾 Saving raw dataset variables to local files in: {output_dir}")
heartdisease_pipeline.X.to_csv(os.path.join(output_dir, 'heart_disease_features.csv'), index=False)
heartdisease_pipeline.y.to_csv(os.path.join(output_dir, 'heart_disease_targets.csv'), index=False)

# -------------------------------------------------------------
# 2. PROCESS SPLITS AND TRAIN BASELINE MODEL
# -------------------------------------------------------------
X_train, X_test, y_train, y_test = heartdisease_pipeline.prepare_splits()

model_pipeline = Pipeline(steps=[
    ('preprocessing', heartdisease_pipeline.preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])

print("🏋️ Training baseline model...")
model_pipeline.fit(X_train, y_train)

print("📊 Evaluating model performance...")
predictions = model_pipeline.predict(X_test)
report_output = classification_report(y_test, predictions)

# Print metrics to standard console output
print("\nBaseline Model Report:")
print(report_output)

# -------------------------------------------------------------
# 3. OUTPUT THE RESULTS AND METRICS TO A FILE
# -------------------------------------------------------------
log_file_path = os.path.join(output_dir, 'heart_disease_results.txt')
print(f"📝 Writing metrics summary report to file: {log_file_path}")

with open(log_file_path, 'w', encoding='utf-8') as f:
    f.write("==================================================\n")
    f.write("UCI MACHINE LEARNING MODEL PIPELINE EVALUATION\n")
    f.write("Dataset: Heart Disease (ID: 45)\n")
    f.write("==================================================\n\n")
    f.write("CLASSIFICATION METRICS REPORT:\n")
    f.write(report_output)
    f.write("\n==================================================\n")
    f.write("Data Export Verification:\n")
    f.write(f"- Features frame saved to 'heart_disease_features.csv' ({len(heartdisease_pipeline.X)} rows)\n")
    f.write(f"- Target frame saved to 'heart_disease_targets.csv' ({len(heartdisease_pipeline.y)} rows)\n")
    
