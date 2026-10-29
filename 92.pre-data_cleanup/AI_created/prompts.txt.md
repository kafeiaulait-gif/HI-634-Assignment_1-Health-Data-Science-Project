
### So the next thing I would like is a Python script that would take a list of dataset files in a folder and prepare, preprocess, sanitize, cleanse, curate, and stage data so it is ready for AI ingestion, curation, analyzing, and providing ouitputs.  Things like deduplicating records, handling missing values, detecting outliers and avoiding, data type casting, feature engineering, normalizing and scaling, entity resolution, and data augmentaiton.  If you can thing of anything else, let me know. 

I have created data_curator.py, an end-to-end data preparation, sanitization, curation, feature engineering, and AI staging pipeline.

<br>

Like data_profiler.py, it is built entirely using the Python 3.8+ Standard Library (zero pip/external dependencies required) and is fully compatible with .env configurations, folder traversals, UCI headerless presets, and diverse dataset formats (.csv, .tsv, .data, .txt, .json, .jsonl).

---

## Key Capabilities Implemented

| Capability | How It Works & Why It Matters |
| :---: | :---: |
| **Deduplicating Records** | Removes exact row duplicates across all features or on custom key subsets (`--dedup-keys`), logging dropped records in the audit trail. |
| **Handling Missing Values** | Detects arbitrary missing indicators (`""`, `"?"`, `"NA"`, `"null"`, `"-9"`, `"-999"`, `"."`). Drops high-missingness columns (>50%) and uninformative rows (>60%). Performs median/mean/mode/zero imputation and automatically creates binary missingness flags (`col_is_missing`) so models learn informative missingness signals. |
| **Detecting & Avoiding Outliers** | Computes Tukey's IQR fences ($[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$), Z-scores, or Median Absolute Deviations (MAD). Outliers are avoided / treated via Winsorization / clipping (capping to fences without losing records or skewing gradient descent), trimming, median replacement, or indicator flags (`col_is_outlier`). |
| **Data Type Casting & Sanitization** | Automatically cleans column names to lowercase `snake_case`, strips whitespace, and reliably casts values to `Integer`, `Float`, `Boolean`, `Datetime (ISO 8601)`, `Categorical`, or `String`. |
| **Entity Resolution & Record Linkage** | Features pure-Python `Jaro-Winkler` and `Levenshtein` similarity algorithms with blocking to resolve duplicate entities (e.g., patient records with minor name typos) and assign unified canonical IDs (`canonical_entity_id`). |
| **Feature Engineering** | Generates clinical interaction terms (ratios such as blood pressure / cholesterol and products), non-linear $\ln(1+x)$ transformations for skewed variables. |
| **Normalizing & Scaling** | Implements `StandardScaler` (Z-score: mean 0, variance 1), `MinMaxScaler` ($[0,1]$), `RobustScaler` (Median/IQR), and `MaxAbsScaler`. Saves parameters to `scaler_parameters.json`. |
| **Data Augmentation** | Synthesizes samples for training data via **Gaussian Tabular Jittering** ($x + \mathcal{N}(0, (0.05 \cdot \sigma)^2)$), **Tabular Mixup** (convex interpolation between records), or **Target Class Balancing** (oversampling minority classes). All synthetic rows are marked with `is_synthetic = 1`. |

<br>

## Additional Enterprise & AI-Grade Features Included

In addition to your requested capabilities, several production-grade data engineering features were built into the pipeline:

1.  HIPAA Safe Harbor PII/PHI Redaction (--phi-redact):

    * Automatically detects and redacts direct identifiers: SSNs ([REDACTED_SSN]), emails, phone numbers, IP addresses, and Medical Record Numbers (MRNs).
	
    * Generates cryptographically salted SHA-256 pseudonyms for patient and subject identifiers.

2.  Zero Data Leakage Guarantee:

    * Partitions datasets into stratified Train, Validation, and Test splits (train.csv, val.csv, test.csv).
	
    * Fits all scalers, median imputers, and categorical vocabularies strictly on the Training split, then propagates them to validation and test splits.

3.  Multi-Modal AI Deliverables:

    * Tabular ML (train.csv, val.csv, test.csv, curated_full.csv): Clean numeric/encoded tables ready for XGBoost, LightGBM, Random Forest, or Scikit-Learn.
	
    * LLM & Fine-Tuning Format (staged_for_llm.jsonl): Each record is staged as a structured natural language patient narrative / prompt-completion pair:
	

```	
	json

		{"text": "Clinical Record Profile: age is 58, cholesterol is 240.0, resting bp is 135.0...", "target": 1, "metadata": {"entity_id": "ENT_0001", "is_synthetic": 0}}

```

		* Tensor Matrices (staged_tensors.json): Pre-extracted feature matrix 𝑋 X, target vector 𝑦 y, and feature indices ready for direct ingestion into PyTorch DataLoader or TensorFlow tf.data.

4.  AI Governance & Provenance Manifest (staging_manifest.json & DATA_CARD.md):

    * Records cryptographic SHA-256 checksums of source files.
	
    * Emits a GitHub-Flavored Markdown Data Card with an interactive Mermaid transformation waterfall, step-by-step row/column lineage, and a complete data dictionary.

---

## Command-Line Usage

1. Curate a directory of files with the UCI Heart Disease preset

    bash
	
        python3 data_curator.py source_dir/ --uci-heart --output-dir staged_data/

2. Curate specific datasets with class balancing and target stratification

    bash
	
        python3 data_curator.py cleveland.data hungarian.data --target-col num --augment balance --output-dir staged_data/

3. Curate clinical patient files with fuzzy entity resolution and PII redaction

    bash
	
        python3 data_curator.py patients.csv --entity-keys "full_name" --dedup-keys "patient_id" --phi-redact --scale-method standard

4. Automatic .env fallback

	If invoked with no arguments:

    bash
	
        python3 data_curator.py

<br>

        It reads SOURCE_FOLDER, SOURCE_FILES, or TARGET_FOLDER from .env, or provides an interactive prompt.



<br>
<br>





