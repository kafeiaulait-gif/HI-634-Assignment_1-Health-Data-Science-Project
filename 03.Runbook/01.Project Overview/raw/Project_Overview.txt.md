https://uab.instructure.com/courses/1691197/assignments/7676526

Assignment 1 Health Data Science Project

Due Nov 3 by 11:59pm     Points 50     Submitting a file upload

HI 634

Assignment 1 Health Data Science Project

In this project, you will use a coding agent to investigate openly available clinical or public health data. Your work is to decide what question the data can answer, inspect the raw files, justify each preparation choice, compare methods, and explain the result in ordinary language. You may use Codex, Claude Code, Antigravity, or OpenCode. You are responsible for checking what the agent produces.

Choose one or more dataset options
Complete the full workflow for at least one option below. You may use more than one option if you can explain what the additional data contributes. Analyze unrelated datasets separately; join files only when a documented key and a compatible unit of observation make the join meaningful. The grading criteria stay the same regardless of how many options you choose.

Option

What the files contain

Suggested task

Difficulty

1  UCI Chronic Kidney Disease

One clinical table with many missing entries

Classification

Introductory

2  UCI Heart Disease

Four centers; use the processed Cleveland file

Classification

Introductory

3  CDC NHANES 2017 to 2018

Demographics, body measures, and diabetes modules

Classification

Intermediate

4  Synthea synthetic records

Linked patient, encounter, condition, and medication files

Clustering

Intermediate

5  CDC PLACES plus SVI

County health estimates and social vulnerability data

Regression

Intermediate

6  PubMed 20k RCT

Labeled sentences in research abstracts

NLP classification

Intermediate

 

Learning goals
Describe the source, structure, units, variables, and missingness of a public dataset.
Explain how observed data problems led to specific preparation decisions.
Compare a simple baseline with at least two alternative methods using suitable measures.
Communicate results, uncertainty, and limitations through a report, figures, and a demo.
Deliverables and grading
Deliverable

Weight

What to show

Data analysis and modeling report

50%

Your question, source, exploration, decisions, methods, comparison, figures, results, and limitations.

Presentation or demo

25%

A clear walkthrough of the project and the result, including a run or guided demonstration of the analysis.

Questions and answers during the demo

25%

Your own explanation of data choices, method selection, errors, and what the result does or does not mean.

 

Data use  Use only the linked public or synthetic sources. Do not introduce private patient records, attempt reidentification, or use a course model to make decisions about an individual patient.

Set up your project with a coding agent
Create a new folder for the assignment and open it in your chosen coding agent. The agent can write and run Python, but ask it to explain each step and show the actual output before you accept its interpretation. Begin with a local Python virtual environment so the project has its own package versions.

Operating system

Ask the agent to run

macOS or Linux

python3 -m venv .venv
source .venv/bin/activate

Windows PowerShell

py -m venv .venv
.\.venv\Scripts\Activate.ps1

 

Ask the agent to create requirements.txt with pandas, numpy, matplotlib, seaborn, scikit-learn, and jupyter. It may add ucimlrepo for UCI import and any small, explained dependency required by your option. Then ask it to run python -m pip install -r requirements.txt inside .venv, show the Python path and package versions, and load a small sample of the selected data. If activation fails, it should explain the operating system message and use the environment's Python directly.

Keep a reproducible folder structure
Folder or file

Purpose

data/raw/

Original downloads; do not overwrite them during cleaning.

data/processed/

Joined or cleaned tables created by your code.

notebooks/ or src/

The notebook or Python script that repeats every analysis step.

reports/figures/

Figures used in the written report and presentation.

requirements.txt and README.md

Packages and plain-language instructions for rerunning the project.

 

Add .venv/ and data/raw/ to .gitignore if you use Git. Keep a note of the download page and date. A reviewer should be able to download the data again and reproduce your tables and figures by following your README.

Copy this first prompt into your agent
I am completing HI 634 Assignment 1 with [DATASET OPTION]. Work only in this project folder. Create and use a local .venv. Keep raw files unchanged. First show me the file inventory, variable meanings, missingness, duplicates, distributions, and possible data quality issues. Explain findings in plain language before proposing cleaning. For every change, record the finding, the decision, and the reason. Use source documentation for variable codes. Fit preprocessing only on training data, keep a test set separate when predicting, compare a baseline with two alternatives, and make labeled figures. Save a reproducible notebook or script, requirements.txt, README.md, and report figures. Ask me to make the key decisions rather than silently choosing for me.

Follow the same reasoning sequence for any option
1 Define a focused question
State one question that matches the dataset. A classification question predicts a category; a regression question predicts a number; clustering describes groups without a known answer label; and natural language processing here classifies text. Name the unit of observation: a patient record, survey participant, county, or abstract sentence. This determines how tables may be joined and how results can be interpreted.

2 Explore the original files
Ask the agent for a file inventory; number of rows and columns; sample rows; variable types and definitions; missing counts and percentages; duplicate counts; and distributions of the outcome and important predictors. For linked files, check whether keys are unique where expected and count unmatched rows before joining. Record at least three concrete findings, such as a field with many missing values or an imbalanced target.

3 Prepare data in response to findings
Keep original files in data/raw. Convert only documented missing-value codes, correct data types, and explain any excluded rows. Do not remove an unusual value merely because it looks extreme. For prediction, split the data before fitting an imputer, encoder, scaler, or text vectorizer. Put these steps in a scikit-learn Pipeline or ColumnTransformer when possible. Remove row IDs from predictors and check that no feature reveals the answer or was measured after it.

Observed finding

Possible decision

What to document

Blood pressure contains '?'.

Convert '?' to missing; consider training-set median imputation.

Count affected rows and compare before and after distributions.

Category counts are uneven.

Use a stratified split and report class-level measures.

Show the training and test class counts.

A join loses records.

Inspect key format and unmatched values before proceeding.

Report row counts before and after the join.

 

4 Compare and assess methods
Compare a simple baseline with at least two alternatives. Choose a primary measure that fits the question, then show other measures that reveal different errors. For prediction, make model choices using only training data or a validation set and evaluate the selected model once on the untouched test set. For clustering, compare scores with group sizes and profiles; a numerical score alone does not make a group meaningful.

5 Explain the result visually and in words
Include at least three labeled visuals: one about data quality or missingness, one distribution or relationship, and one about the chosen result or its errors. If missing values are absent, say so and show a small count table. Captions should state the unit, sample size, what is plotted, and the conclusion you draw. Avoid interpreting an association as proof of cause.

Submit a report and demonstrate the project
Written report worth 50 percent
For one option, aim for a clear 4 to 6 page report, excluding references and an optional appendix. If you choose additional options, give each its own concise question, source, method, result, and reason for inclusion. Submit the report as a DOCX or PDF, along with the notebook or script, requirements.txt, and README. The report should stand on its own even if the reader never opens the code.

Report section

Required evidence

Points

Question and data source

Focused question, dataset citation and link, unit of observation, and why the selected data can address it.

5

Initial exploration

Tables or figures for structure, missingness, duplicates, distributions, and at least three findings.

10

Preparation and reproducibility

Before/after counts, decision log, justified cleaning, leakage checks, and runnable project files.

10

Model comparison and evaluation

Baseline plus two alternatives, suitable measures, fair train/test or clustering comparison, and error analysis or cluster profiles.

15

Figures and interpretation

Labeled visuals, selected method, plain-language findings, limitations, and a reasonable next step.

10

 

Presentation or demo worth 25 percent
Show the project folder and the notebook or script. Walk through the question, one important exploration finding, the preparation decision it caused, the comparison table, and the final visualization. Run the analysis or demonstrate a saved reproducible run. Explain the result for a nontechnical audience and keep the sequence easy to follow. Ten points are for showing a reproducible workflow, ten for clear explanation of results and visuals, and five for organization.

Questions and answers worth 25 percent
Be prepared to explain your own choices without reading an agent-generated answer. Ten points are for explaining the raw-data findings and cleaning choices; ten are for justifying the methods, metrics, and errors; five are for limitations and how you checked the agent's work. Typical questions include: What was missing? Why did you use that method? What would a false negative mean? What does your plot show? What can you not conclude from this dataset?

How to describe common measures
For classification, a confusion matrix counts correct and incorrect predictions. Precision is the share of predicted positives that are truly positive; recall is the share of actual positives found; F1 combines precision and recall. Macro F1 averages class-level F1 scores equally. For regression, MAE is average absolute error in the outcome's units, RMSE gives extra weight to large errors, and R squared compares performance with a mean-prediction baseline. For clustering, a silhouette score describes group compactness and separation, so interpret it alongside cluster sizes and profiles.

Final submission check
The report cites each dataset and codebook, defines every important acronym, and explains each figure.
The README gives the environment setup and exact command to rerun the analysis.
The code preserves the raw data, uses a fixed random seed when relevant, and recreates reported results.
You can explain one decision the coding agent proposed that you accepted, changed, or rejected.
Option 1 UCI Chronic Kidney Disease
This is a manageable first classification project because the table is small and the supplied answer is a disease category. UCI lists 400 records, 24 predictors, and missing values in many fields. Your goal is to compare ways of classifying ckd versus notckd while showing how missing data affected your decisions.

Sources  UCI Chronic Kidney Disease datasetLinks to an external site.  |  Download UCI ZIPLinks to an external site.

Download and define the question
Open the UCI page and click Download. The download is a ZIP file containing Chronic_Kidney_Disease.rar, which contains ARFF data. Keep the original ZIP in data/raw/ckd. For the easiest analysis path, ask the agent to use the documented UCI Python importer, fetch_ucirepo(id=336), and save an imported working copy without overwriting the original archive. The ARFF files contain inconsistent whitespace and may fail in a standard ARFF reader unless cleaned first.

Example question: How well can the available measurements distinguish the two supplied class labels? Each row is one record. The class label is the answer to predict and must never be included among model inputs.

Explore the raw table
Check the actual row count, number of columns, data types, duplicate rows, and class balance. Inspect the original archive for '?' and stray whitespace, then compare it with the importer's missing-value counts. Look at numeric ranges for age, blood pressure, serum creatinine, and hemoglobin; compare a few values with the UCI definitions before treating them as plausible or implausible.

Create a missingness table and a class-count chart. Record at least three findings, such as a column whose data type is text because of missing markers, a highly incomplete field, or a difference between the two class sizes.

Prepare the data
Trim leading and trailing whitespace in text predictors and the class label, then standardize documented missing markers and convert numeric columns to numbers. The tested UCI import had two class values written as 'ckd' with a trailing tab and one diabetes-category value with a leading tab; record the original counts before combining these variants. Keep before-and-after counts for rows and missing cells. Do not fill in missing target labels.

Make a stratified train/test split before fitting transformations. Ask the agent to compare reasonable missing-data treatments, such as median imputation for numeric fields and most-frequent or explicit Unknown categories for categorical fields. Use a pipeline so the imputation and encoding are learned only from training data.

Compare methods and present results
Compare a majority-class baseline, logistic regression, and a decision tree or random forest. Report test-set precision, recall, F1, and a confusion matrix. Explain which error matters more for your stated question rather than selecting a model by accuracy alone.

Show missingness by field, the class balance, and the confusion matrix. In the report, state how many records remained, which variables you used, why you chose the final method, and how uncertain you are about performance from a small sample.

Prompt to give your coding agent
Use the UCI kidney dataset. Show me its raw missing-value patterns and class balance before writing cleaning code. Propose a documented preprocessing pipeline, then compare majority class, logistic regression, and a tree-based model with a held-out test set.

Interpretation boundary  A good classification score on this historical teaching dataset does not establish that a model is ready for clinical use.

Option 2 UCI Heart Disease
The UCI archive describes four data sources. For this project use only the processed Cleveland subset, which has 303 records and 14 commonly used fields. The outcome called num is 0 when heart disease is absent and 1 to 4 when it is present. This option lets you practice small-sample classification and carefully interpret errors.

Sources  UCI Heart Disease datasetLinks to an external site.  |  Download UCI ZIPLinks to an external site.

Download and define the question
Open the UCI page, select Download, and extract the archive into data/raw/heart. Ask the agent to locate processed.cleveland.data and the attribute descriptions. The processed file has no convenient column header, so assign the 14 names using the UCI documentation and verify their order.

Example question: Can the recorded measurements distinguish presence from absence of the documented heart-disease outcome? Create a binary label with num equal to 0 for absence and values above 0 for presence. State this transformation in the report.

Explore the raw table
Verify the row and column counts, then inspect the frequencies of num before and after making the binary label. Count '?' entries and other missing values, especially in fields such as ca and thal if present in your copy. Examine age, resting blood pressure, cholesterol, and categorical chest-pain values using the codebook.

Check duplicate rows, class balance, and the distributions of at least two predictors by outcome. Write down three findings that will guide preparation. For example, a numeric-looking code such as chest-pain type may represent a category rather than a continuous quantity.

Prepare the data
Convert '?' to missing values. Treat coded categories as categories, impute or encode them within the training pipeline, and document any excluded rows. Separate predictors from the binary outcome. Make a stratified test split before fitting an imputer, encoder, or scaler. Do not combine the other centers for this first analysis.

Compare methods and present results
Compare a majority-class baseline, logistic regression, and a decision tree or random forest. Use cross-validation on training data to compare methods if practical, then assess the selected method once on the test set. Report precision, recall, F1, and the confusion matrix with the positive class clearly named.

Show the outcome balance, one predictor by outcome group, and the confusion matrix. Explain in plain language what a false positive and a false negative mean here. Relate your choice of model to both its measured performance and its interpretability.

Prompt to give your coding agent
Use the processed Cleveland heart-disease file. Verify the 14 column names and num values from UCI documentation. Show missing markers and target balance before cleaning. Compare a baseline, logistic regression, and a tree-based method without fitting preprocessing on the test data.

Interpretation boundary  The Cleveland sample is small and old. Treat the exercise as a method comparison, not as a current diagnostic model.

Option 3 CDC NHANES 2017 to 2018
NHANES is a public survey with separate data modules. This option uses demographics, body measurements, and diabetes questionnaire responses so that you can practice a documented multi-table join. The example outcome is whether an adult reports being told by a clinician that they have diabetes.

Sources  NHANES 2017 to 2018 data pageLinks to an external site.  |  Diabetes codebookLinks to an external site.  |  Body measures codebookLinks to an external site.  |  DEMO_J.xptLinks to an external site.  |  BMX_J.xptLinks to an external site.  |  DIQ_J.xptLinks to an external site.

Download and define the question
On the cycle page, save DEMO_J, BMX_J, and DIQ_J from their Data links. Each is an .XPT file. Save them under data/raw/nhanes and open the corresponding Doc pages. Ask the agent to read the files with pandas.read_sas(..., format='xport'). Each joined row should represent one survey participant identified by SEQN.

Example question: Among adults age 20 or older in these public-use files, how well do age, body mass index, and a few documented characteristics distinguish DIQ010 yes from no? DIQ010 is a self-report about being told of diabetes by a doctor or health professional; it is not a laboratory diagnosis.

Explore the three modules and the join
List row counts and check whether SEQN is unique within each module. Inspect RIDAGEYR in demographics, BMXBMI in body measures, and DIQ010 in the diabetes module. The DIQ010 codebook lists 1 as Yes, 2 as No, 3 as Borderline, 7 as Refused, and 9 as Don't know. Count all categories and missing values before defining a binary outcome.

Join by SEQN and report the number of participants before and after each join, including unmatched keys. Plot age and BMI distributions, the diabetes response counts, and BMI missingness. Read the codebooks before interpreting special values in any additional predictor.

Prepare the analysis sample
Keep participants age 20 or older. Use only DIQ010 values 1 and 2 for the example binary outcome; exclude and count borderline, refused, don't know, and missing responses. Select a small set of documented predictors such as age, BMI, and gender. Record how many adults lack BMI and decide whether to impute that predictor or restrict the analysis, with a reason.

Make a stratified train/test split after defining the eligible sample. Fit any BMI imputation and categorical encoding only on the training portion. Do not use the target response or variables derived from it as model inputs.

Compare methods and present results
Compare a majority-class baseline, logistic regression, and a decision tree. Report class counts, precision, recall, F1, and a confusion matrix on the test set. Show a table of exclusions, BMI by response group, and the final confusion matrix. Explain whether missing BMI or class imbalance could have affected the result.

Prompt to give your coding agent
Use DEMO_J, BMX_J, and DIQ_J from NHANES 2017 to 2018. Read their codebooks first. Show SEQN join counts, DIQ010 response categories, and BMI missingness before making an adult yes/no analysis sample. Compare a baseline, logistic regression, and a tree.

Interpretation boundary  NHANES requires survey weights and design variables for national estimates. This simplified modeling exercise does not estimate U.S. diabetes prevalence.

Option 4 Synthea Synthetic Health Records
Synthea's related CSV tables contain synthetic patients and clinical events. Summarize encounters, conditions, and medications to one row per patient, then compare ways of clustering those patient summaries.

Sources  Official Synthea sample filesLinks to an external site.  |  Synthea CSV data dictionaryLinks to an external site.  |  Tested April 2020 CSV ZIPLinks to an external site.

Download and define the question
Download the tested April 2020 CSV ZIP from the link above, not the changing 'latest' file. Extract it into data/raw/synthea; the files are inside a csv/ folder. Start with patients.csv, encounters.csv, conditions.csv, and medications.csv. Read the data dictionary and verify the headers and patient count (1,171 in the tested archive).

Example question: Do synthetic patients separate into groups based on numbers of encounters, recorded conditions, and medication records? Each final analysis row should represent one patient. There is no known correct cluster label to predict.

Explore the linked files
Count rows and columns. Verify that patients.csv uses a unique Id and the event files use PATIENT as a foreign key. Check unmatched event rows. Plot event counts per patient and investigate unusually high values before calling them errors.

Tabulate missing values. A blank event end date can mean ongoing or unrecorded, unlike a missing patient key. Show encounter and condition count distributions, including patients with no recorded events.

Prepare one patient level table
Group each event table by patient key, calculate counts, and join the results to patients. Explain whether an unmatched or absent event becomes a count of zero, a missing value, or an exclusion. Check that the joined result still has one row per patient. Use a small set of numeric features and show a before/after table of row counts.

Exclude identifiers and generated names and addresses. Compare scaled raw counts with log1p-transformed counts followed by scaling; very high counts can dominate distances. Save the patient summary in data/processed, not over the raw files.

Compare methods and present results
Compare two- and three-cluster KMeans with hierarchical clustering. Report cluster sizes, feature medians, and silhouette scores. In the tested archive, raw counts isolate a few high-use patients yet score highly; compare log-transformed counts before selecting a grouping.

Show event-count distributions, cluster sizes, and a profile chart. Describe observed differences such as more encounters, not medical diagnoses, and state a sensible next question.

Prompt to give your coding agent
Use Synthea CSV files to build one summary row per synthetic patient. First show table keys, unmatched events, missing fields, and event-count distributions. Then compare KMeans with two and three groups and hierarchical clustering; report cluster sizes and profiles, not only silhouette scores.

Interpretation boundary  Synthea records are generated. Patterns may reflect the generator and are not estimates of real clinical populations.

Option 5 CDC PLACES and Social Vulnerability Index
This option combines two county-level public data sources. The CDC PLACES GIS-friendly county file has modeled health measures, while the Social Vulnerability Index provides county measures of social vulnerability. You will practice aligning geographic keys and interpreting a regression on area-level estimates.

Sources  PLACES county data 2025 releaseLinks to an external site.  |  SVI data download pageLinks to an external site.  |  PLACES portal guideLinks to an external site.  |  PLACES direct CSVLinks to an external site.  |  SVI direct CSVLinks to an external site.  |  SVI 2022 county guideLinks to an external site.

Download and define the question
Open the 2025 PLACES county GIS-friendly page and choose Export, then CSV. On the SVI page choose Year 2022, Geography United States, Geography Type Counties, and CSV; the direct CSV links above are also available. Save both original files in data/raw/counties. Open the PLACES column descriptions and the 2022 SVI county documentation before selecting measures.

Example question: How well do a few SVI indicators predict the county-level PLACES field DIABETES_CrudePrev? This field is a crude prevalence percentage, so prediction errors are measured in percentage points. Each row must represent one county or county equivalent; do not treat it as one person.

Explore sources and the join
List county counts and inspect the five-digit FIPS key in both sources. Read it as text to preserve leading zeros. Check duplicate keys, missing or suppressed PLACES estimates, and counties that do not match. Check SVI documentation for special unavailable-value codes such as -999 before treating a predictor as numeric. Plot the diabetes measure and candidate SVI indicators; investigate extreme values before excluding them.

The releases refer to different years. Record the years and avoid treating the joined table as a single-time survey. Note that modeled PLACES estimates are not direct measurements of each person in a county.

Prepare the county table
Join on cleaned county FIPS and show counts before and after the join. Choose a small number of documented SVI measures as predictors. Remove the FIPS key from model inputs, and do not include another version of the diabetes outcome or a variable that directly reveals it. Drop rows lacking the target and record how many; decide how to handle missing predictors after inspecting their pattern.

Set aside test counties before fitting imputation or scaling. Use a reproducible split and explain why nearby counties may have similar values, so a random split may give an optimistic impression of performance elsewhere.

Compare methods and present results
Compare a training-mean baseline, linear regression, and random forest regression. Report MAE, RMSE, and R squared on the same held-out counties. Explain MAE in percentage points if the outcome is a percentage. Show missing or unmatched county counts, a diabetes-versus-SVI scatterplot, and observed-versus-predicted values or residuals.

Prompt to give your coding agent
Download PLACES county GIS-friendly data and SVI 2022 county CSV. Before modeling, verify FIPS keys, matched county counts, missing estimates, the exact diabetes field, and its units. Compare mean prediction, linear regression, and random forest using held-out counties.

Interpretation boundary  These are area-level estimates. A county association cannot be applied to an individual, and the exercise cannot establish cause or rank overall county health.

Option 6 PubMed 20k RCT Biomedical Text
This option uses sentences from randomized-trial abstracts rather than person-level health records. Each sentence has a label for its role in the abstract. Your task is to classify sentence roles from text while preserving the dataset's supplied training, development, and test files.

Sources  Dataset repositoryLinks to an external site.  |  train.txtLinks to an external site.  |  dev.txtLinks to an external site.  |  test.txtLinks to an external site.

Download and define the question
Open the repository and choose the PubMed_20k_RCT folder. Download train.txt, dev.txt, and test.txt to data/raw/pubmed20k. The raw-file links above also open each file directly. Use the 20k set rather than the larger 200k set for this assignment.

Example question: Can a simple text representation distinguish the role of a sentence in a trial abstract? One analysis row is one labeled sentence. Keep an abstract identifier only for checking structure and possible duplicates; do not use it as a word feature.

Explore the text before modeling
Ask the agent to explain how the file marks abstract boundaries and sentence labels. Count abstracts and sentences in each split; inspect the exact label names, label frequencies, empty sentences, missing labels, duplicate text, and sentence length distributions. Read several short examples of each class so that the labels have a meaning beyond their names.

Check whether duplicate sentences or abstracts cross the supplied splits. If a problem is found, document it and discuss its effect before changing the official split. Missing values may be absent here; report that finding instead of inventing a cleaning step.

Prepare text and compare methods
Remove blank separator lines while retaining the sentence and label. Fit a TF-IDF word representation only on train.txt. Do not randomly mix sentences across abstracts or refit the vectorizer on dev or test. Compare a most-frequent-label baseline, multinomial Naive Bayes, and logistic regression.

Use dev.txt to compare or tune methods with macro F1, which gives each role equal weight. After choosing one method, evaluate it once on test.txt. Report test macro F1, per-class precision and recall, and a confusion matrix. Identify which roles are most often confused.

Visualize and interpret
Show role counts, sentence-length distributions, and either per-class F1 or a confusion matrix. Include a few correctly and incorrectly classified sentences. Explain the wording that may have led to an error and whether class imbalance or very short sentences make some roles harder to identify.

Prompt to give your coding agent
Use the PubMed_20k_RCT train, dev, and test files. First parse abstract boundaries and show sentence and label counts. Fit TF-IDF on training text only; compare a majority-label baseline, Naive Bayes, and logistic regression; select on dev macro F1 and test once.

Interpretation boundary  The files contain research abstracts rather than patient records. Check the repository and source terms before redistributing the text outside coursework.

Note: We will discuss the presentation and QnA session during the class.
