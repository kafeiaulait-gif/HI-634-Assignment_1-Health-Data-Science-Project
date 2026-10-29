
### If I were to upload some datafiles with a URL where the files came from; can you build me a Python script that will analyze the files; show things like a list of columns with datatypes, number of rows in each file, general analysis of each file, possible trends that are noticeable, statistical summary of data in files, and anthing else you thing would be of value in first reviewing the files?

Yes, I have built and tested a Python script for you: data_profiler.py.

---

It is designed as an automated Exploratory Data Analysis (EDA) & Dataset Profiling tool. It requires zero external packages (runs on Python's standard library out of the box), handles files uploaded locally or downloaded directly from remote URLs, and generates both a formatted terminal analysis and an exportable GitHub-Flavored Markdown report (<filename>_profile_report.md).

---

## What the Script Analyzes

| Category | What Is Checked & Reported |
| :---: | :---: |
| **Dimensions & Metadata** | Row count, column count, raw file size, and source URL provenance. |
| **Schema & Data Types** | Inferred types (`Integer`, `Float`, `Boolean`, `Datetime`, `Categorical`, `Text`, `Primary Key / ID`). |
| **Data Hygiene & Quality** | Missing values count & % (handles custom markers like `?`, `NA`, `null`, `None`, `-9`, `-999`), exact duplicate row counts, constant (zero-variance) columns, and an overall **Dataset Health Score (0-100)**. |
| **Statistical Summary** | **Numeric:** Mean, Std Dev, Variance, Min, 25% (Q1), Median (50%), 75% (Q3), Max, IQR, Fisher-Pearson Skewness, Outlier counts (via Tukey's $1.5 \times IQR$ method), and Zero-inflation (%).<br><br>**Categorical:** Distinct counts, top 5 most frequent values with percentages, and majority class dominance ratio. |
| **Noticeable Trends** | **Bivariate Correlations:** Pearson correlation matrix flagging strong positive ($r \geq +0.7$) and negative ($r \leq -0.7$) relationships.<br><br>**Distribution Shapes:** Highlights heavy right/left skewness ($ |
| **First-Review Action Items** | Automated checklist highlighting columns needing imputation, duplicate removal, columns to drop due to zero variance, multicollinear features, and candidate target/ID variables. |
| **Batch Comparison** | When multiple files are analyzed together, it generates a **Multi-Dataset Comparative Summary Table** comparing row counts, missingness, duplicates, and health scores across files. |

<br>

## How to Use It

The script can be run from your terminal in several ways:

1. Analyze a local file and record its Source URL

      bash

        python3 data_profiler.py myfile.csv --source-url "https://archive.ics.uci.edu/dataset/45/heart+disease"

2. Download and analyze directly from a remote URL

    bash

        python3 data_profiler.py --url "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"

3. Analyze multiple files or an entire directory in batch

    bash

        python3 data_profiler.py source_dir/


    Or specify multiple files:

        python3 data_profiler.py dataset_center1.csv dataset_center2.csv

4. Headerless datasets & domain presets (e.g., UCI Heart Disease)

    Many medical or machine learning benchmark files (such as UCI .data files) do not have column headers. You can pass column names manually or use the built-in preset:

    bash

    - Using custom column names:

          python3 data_profiler.py data.txt --columns "age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,num"


    - Using the built-in UCI Heart Disease preset (14 standard attributes):

          python3 data_profiler.py cleveland.data --uci-heart

5. Interactive prompt & .env integration

    If run without arguments (python3 data_profiler.py), it automatically checks your .env file for defined data paths or prompts you interactively for the file path and optional source URL.


<br>
<br>


