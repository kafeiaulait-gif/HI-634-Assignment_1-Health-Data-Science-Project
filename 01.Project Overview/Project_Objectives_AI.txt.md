# Google Gemini AI evaluation of project scope:

## Prompt:

#### So yesterday, I was asking about a project that I need help with. I want to slowly prompt you with information and have you walk me through what the scope of the project, bulleted list of steps, deliverables, and objectives that are required.  Please provide an outline of how to go through all the requirments with a line by line list of each step and overal plan goals for the project.

---


🗂️ Master Project Overview & Scope

  * Course Assignment: HI 634 - Assignment 1 Health Data Science Project

  * Core Entity: A completely reproducible health data science pipeline executed by guiding an AI coding agent, fully audited and verified by you.

  * Dataset Chosen: Option 2: UCI Heart Disease (Processed Cleveland File) — Selected as the most accessible single-table option with highly predictable clinical targets.

  * Project Goal: Build a classification pipeline to predict the presence of heart disease while documenting every data anomaly, clinical cleaning choice, and model performance metric.

---

🎯 Core Project Objectives

1. Environment Isolation: Establish a locked-down, reproducible local Python environment so that your project's code never breaks due to external computer updates.

2. Rigorous Data Governance: Identify data anomalies, missing codes (like ?), and class imbalances in the raw Cleveland heart disease file without changing the original file.

3. Clinically Justified Preparation: Document a explicit, line-by-line defensive reasoning trail for every single cleaning and data-splitting choice.

4. Methodological Benchmarking: Evaluate a simple baseline classifier against exactly two advanced machine learning alternatives using training/validation data only.

5. Plain-Language Translation: Convert complex machine learning output matrices into actionable, honest, non-technical explanations regarding model uncertainty and limitations.

---

📋 Line-by-Line Execution Steps

#### Phase 1: Local System Infrastructure & Tool Installation

* Step 1.1: Download and install Git for Windows using the default settings from the official site to provide your computer with a command line framework.
* Step 1.2: Open PowerShell as an Administrator on your Windows machine by right-clicking the program application.
* Step 1.3: Paste the official Anthropic installation script irm https://claude.ai | iex into PowerShell to natively install Claude Code.
* Step 1.4: Create a dedicated, empty project folder on your computer named HI634_Assignment1.
* Step 1.5: Open a normal PowerShell window, navigate into your folder using the cd command, and type claude to wake up and authorize your agent.

#### Phase 2: Environment Isolation & Workspace Bootstrapping

* Step 2.1: Execute the environment command py -m venv .venv in your terminal to build an isolated python sandbox inside your folder.
* Step 2.2: Activate the environment using the execution command .\.venv\Scripts\Activate.ps1.
* Step 2.3: Paste your professor's Master Setup Prompt (provided in your query) directly into the Claude Code prompt line, making sure to replace [DATASET OPTION] with UCI Heart Disease (Processed Cleveland file).
* Step 2.4: Let the agent automatically draft a requirements.txt file containing pandas, numpy, matplotlib, seaborn, scikit-learn, jupyter, and ucimlrepo.
* Step 2.5: Monitor the agent as it executes the terminal installer: python -m pip install -r requirements.txt.
* Step 2.6: Review the environment output shown by the agent to verify that the active Python path points inside your folder's .venv block and no red installation errors occur.

#### Phase 3: Focused Question Definition

* Step 3.1: Define your core research question: "Can a patient's clinical and demographic attributes (such as age, sex, cholesterol, and blood pressure) accurately classify the presence or absence of heart disease using the Cleveland clinical dataset?"
* Step 3.2: Explicitly document your Unit of Observation: A single patient clinical record from the Cleveland clinic collection.
* Step 3.3: Have the agent create your project structure by setting up a data/raw/ directory to store the completely untouched master files.

#### Phase 4: Raw File Exploration & Audit

* Step 4.1: Have the agent use the ucimlrepo library to download the Heart Disease dataset and save the raw data into data/raw/.
* Step 4.2: Direct the agent to print out a full structural summary: total rows, total columns, data types, and a 5-row visual sample of the data.
* Step 4.3: Order the agent to check specifically for missingness values, counting how many fields contain placeholders like ?, NaN, or blanks.
* Step 4.4: Have the agent compute the exact balance of your target variable (how many patients have heart disease vs. how many do not).
* Step 4.5: Extract and save three concrete structural findings (e.g., specific columns containing ? values, heavily skewed cholesterol metrics, or class distributions) into a temporary log file.

#### Phase 5: Defensive Data Preparation & Pipeline Construction

* Step 5.1: Direct the agent to handle identified issues: convert any string values like ? into standard null values (NaN).
* Step 5.2: Isolate your target answer variable from your predictor columns, making sure to drop any patient IDs or columns that could accidentally leak the true diagnosis.
* Step 5.3: Execute the data split first: Split the dataset into a Training Set (80%) and an untouched Test Set (20%) using a stratified split to keep the heart disease ratios identical in both sets.
* Step 5.4: Instruct the agent to build a formal scikit-learn ColumnTransformer or Pipeline that handles numerical scaling and missing data imputation (e.g., filling missing values with the training set's median).
* Step 5.5: Document a side-by-side justification log outlining every decision made during cleaning, confirming that no extreme outliers were deleted without a clinical explanation.

#### Phase 6: Methodological Modeling & Comparison

* Step 6.1: Select a simple, transparent Baseline Model: A standard, un-tuned Logistic Regression model or a simple Decision Tree stump.
* Step 6.2: Select Alternative Model 1: A Random Forest Classifier.
* Step 6.3: Select Alternative Model 2: A Support Vector Machine (SVM) or a Gradient Boosting Classifier.
* Step 6.4: Train and tune all three models using only the 80% training data via cross-validation.
* Step 6.5: Evaluate all models across multiple metrics (Accuracy, Sensitivity/Recall for catching true sick patients, and Specificity) to check for different types of diagnostic errors.
* Step 6.6: Run the final, chosen top-performing model exactly once on the untouched 20% test data to calculate its true, unbiased accuracy score.

#### Phase 7: Visual Documentation & Plain-Language Translation

* Step 7.1: Have the agent generate Visual 1 (Data Quality): A missingness chart or a bar plot counting how many ? values were found in the clinical features.
* Step 7.2: Have the agent generate Visual 2 (Distribution): A clear, labeled histogram showing the distribution of an important clinical predictor (like serum cholesterol levels) across healthy vs. diseased patients.
* Step 7.3: Have the agent generate Visual 3 (Results/Errors): A clean Confusion Matrix or an ROC Curve showing the final model's performance on the test set.
* Step 7.4: Write clear captions for all three figures detailing the sample size, what the axes represent, and what the clinical takeaway is.
* Step 7.5: Write a plain-language summary translating your statistics into normal conversation, taking care to note that the model shows association, not absolute causation.

#### Phase 8: Deliverable Compilation & Verification

* Step 8.1: Instruct the agent to consolidate all your code into a single, clean, reproducible Python script or Jupyter Notebook.
* Step 8.2: Have the agent auto-generate a comprehensive README.md file that guides a user on how to run the script inside the virtual environment.
* Step 8.3: Do a final review of the generated files to ensure that all figures are exported cleanly as independent image files (e.g., .png).

#### Phase 9: Report Generation & Presentation Defense

* Step 9.1: Draft your final Data Analysis and Modeling Report (50% of grade) using the findings, pipeline steps, and tables built during the workflow.
* Step 9.2: Put together a short presentation file outlining your project journey and design decisions.
* Step 9.3: Record or prepare your Live Project Demo (25% of grade), ensuring you can run your script live in the terminal from scratch to show it working.
* Step 9.4: Practice your Q&A Defense (25% of grade) by explaining why you used median imputation for missing items, why you split the data before scaling, and what your confusion matrix errors mean for real patients.

---

📦 Deliverables & Project Goal Summary

1.  Project Milestone Block	Expected Final Artifact	Purpose & Grading Connection
2.  Workspace Baseline	requirements.txt & active local .venv	Secures environment reproducibility; protects against version errors.
3.  Data Lineage Record	Explicitly documented Data Justification Table	Proves human oversight and data governance for the Data Report (50%).
4.  Core Architecture	Reproducible Python Script or Jupyter Notebook	Powers the live execution for your Project Demo (25%).
5.  Visual Evidence Portfolio	Three distinct, captioned diagnostic .png figures	Visual validation of data anomalies and final test errors.
6.  Project Summary Document	Plain-Language README.md & Stakeholder Summary	Translates analytical metrics into clear answers for your Live Q&A (25%).

---

🏁 Final Project Plan Goals

* Establish human-in-the-loop control over Claude Code, making sure you authorize and understand every modification to the data structure.
* Prevent data leakage completely by strictly segregating all imputation, scaling, and validation tests within the training fold boundaries.
* Deliver an easily auditable health data product that a grader can download and run with a single command line instruction.


<br><br>

