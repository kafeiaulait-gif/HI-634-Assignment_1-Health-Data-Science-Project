"""
Master Automation Runner for HI-634 Assignment 1: Option 2 (UCI Heart Disease)
Executes the entire end-to-end clinical machine learning pipeline in one step:
1. Data Ingestion & Codebook Verification
2. Data Preprocessing & Decision Logging
3. Model Training, 5-Fold Stratified CV & Test Evaluation
4. Figure Generation (EDA, ROC, Confusion Matrices, Metrics, Importances)
5. Headless Jupyter Notebook Execution
"""

import os
import sys
import subprocess
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.insert(0, PROJECT_ROOT)

PYTHON_EXE = os.path.join(PROJECT_ROOT, ".venv", "bin", "python")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable

def run_command(desc, cmd):
    print(f"\n========================================================")
    print(f"[*] RUNNING: {desc}")
    print(f"    Command: {' '.join(cmd)}")
    print(f"========================================================")
    start = time.time()
    env = os.environ.copy()
    env["MPLCONFIGDIR"] = "/tmp"
    res = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, capture_output=True, text=True)
    elapsed = time.time() - start
    if res.returncode == 0:
        print(f"[+] SUCCESS in {elapsed:.2f}s")
        if res.stdout.strip():
            print(res.stdout.strip()[:1000])
    else:
        print(f"[!] FAILED in {elapsed:.2f}s")
        print(res.stderr)
        sys.exit(res.returncode)

def main():
    print("=================================================================")
    print("      HI-634 HEALTH INFORMATICS: MASTER AUTOMATION PIPELINE      ")
    print("      Option 2: UCI Cleveland Heart Disease Classification       ")
    print("=================================================================")
    
    # Step 1: Ingest and verify raw data
    run_command("Step 1: Data Ingestion & Verification", [PYTHON_EXE, "src/download_data.py"])
    
    # Step 2: Data preprocessing and cleaning decisions logging
    run_command("Step 2: Preprocessing & Decision Logging", [PYTHON_EXE, "src/data_preprocessing.py"])
    
    # Step 3: Model training, CV, test evaluation, and figure generation
    run_command("Step 3: Model Training & Evaluation Pipeline", [PYTHON_EXE, "src/model_pipeline.py"])
    
    # Step 4: Visual explanation figure generator
    run_command("Step 4: Labeled Visual Explanations Generator", [PYTHON_EXE, "src/generate_visual_explanations.py"])
    
    # Step 5: Headless execution of Jupyter notebook
    nb_path = "notebooks/exploratory_data_analysis.ipynb"
    jupyter_exe = os.path.join(PROJECT_ROOT, ".venv", "bin", "jupyter")
    if os.path.exists(jupyter_exe):
        run_command("Step 5: Interactive Notebook Execution", [
            jupyter_exe, "nbconvert", "--to", "notebook", "--execute", "--inplace", nb_path
        ])
        
    print("\n=================================================================")
    print("[+] MASTER AUTOMATION PIPELINE COMPLETED SUCCESSFULLY!")
    print("    All outputs, tables, and figures have been generated.")
    print("=================================================================")

if __name__ == "__main__":
    main()
