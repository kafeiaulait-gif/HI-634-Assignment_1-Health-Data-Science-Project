#!/usr/bin/env python3
"""
================================================================================
Universal Data Profiler & Exploratory Data Analysis (EDA) Tool
================================================================================
A standalone, zero-external-dependency Python script designed to profile,
inspect, and summarize datasets from local files or remote URLs.

Key Capabilities:
  - Multi-source Ingestion: Local files (CSV, TSV, DATA, TXT, JSON, JSONL) or remote URLs.
  - Multi-file Batch Profiling: Automatically compares multiple files side-by-side.
  - Schema Inference: Int, Float, Boolean, Datetime, Categorical, Text, Primary Keys.
  - Data Hygiene: Missingness %, Duplicate detection, Constant / Quasi-constant flags.
  - Descriptive Statistics: Mean, Median, Std, IQR, Min, Max, Quantiles, Skewness.
  - Outlier Detection: Tukey's Fences (1.5 * IQR) flags and counts.
  - Relationship & Trend Mining: Pearson correlation matrix, skewness alerts,
    class imbalance warnings, zero-inflation checks.
  - Domain Presets: Includes presets like UCI Heart Disease 14 attributes (`--uci-heart`).
  - Actionable Recommendations: Cleaning checklist, imputation targets, redundancy alerts.
  - Environment Aware: Reads from `.env` file if no CLI arguments are supplied.
  - Deliverables: Rich console output + automated GitHub-Flavored Markdown report.

Works out of the box with Python 3.8+ Standard Library (zero pip dependencies required).
================================================================================
"""

import argparse
import csv
import datetime
import json
import math
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================

DEFAULT_MISSING_MARKERS = {
    "", "?", "na", "n/a", "nan", "null", "none", "-9", "-999", ".", "nil", "unknown", "missing"
}

DATETIME_FORMATS = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%d/%m/%Y",
    "%d/%m/%Y %H:%M:%S",
    "%Y/%m/%d",
    "%Y/%m/%d %H:%M:%S",
)

# Common domain preset schemas (e.g. UCI Machine Learning Heart Disease datasets)
UCI_HEART_COLUMNS = [
    "age",        # Age in years
    "sex",        # Sex (1 = male; 0 = female)
    "cp",         # Chest pain type (1: typical angina, 2: atypical, 3: non-anginal, 4: asymptomatic)
    "trestbps",   # Resting blood pressure (in mm Hg on admission)
    "chol",       # Serum cholesterol in mg/dl
    "fbs",        # Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)
    "restecg",    # Resting ECG results (0: normal, 1: ST-T wave abnormality, 2: left ventricular hypertrophy)
    "thalach",    # Maximum heart rate achieved
    "exang",      # Exercise induced angina (1 = yes; 0 = no)
    "oldpeak",    # ST depression induced by exercise relative to rest
    "slope",      # Slope of the peak exercise ST segment (1: upsloping, 2: flat, 3: downsloping)
    "ca",         # Number of major vessels (0-3) colored by fluoroscopy
    "thal",       # Thalassemia (3 = normal; 6 = fixed defect; 7 = reversible defect)
    "num"         # Diagnosis of heart disease (angiographic disease status: 0 = absent, 1-4 = present)
]


# ==============================================================================
# HELPER UTILITIES: NETWORK, PARSING, FORMATTING
# ==============================================================================

def load_env_variables(dotenv_path: Union[Path, str] = ".env") -> Dict[str, str]:
    """
    Parses key-value pairs from a .env file without external dependencies.
    """
    env_vars: Dict[str, str] = {}
    env_file = Path(dotenv_path)
    if not env_file.is_file():
        return env_vars

    with open(env_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                env_vars[key] = val
                os.environ.setdefault(key, val)
    return env_vars


def download_url(url: str, dest_dir: Path) -> Path:
    """
    Downloads a dataset file from a remote URL into dest_dir.
    Uses realistic User-Agent to avoid HTTP 403 Forbidden on academic/open data repos.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    parsed = urllib.parse.urlparse(url)
    filename = Path(parsed.path).name or "downloaded_data.csv"
    target_path = dest_dir / filename

    print(f"[*] Downloading from: {url}")
    print(f"[*] Saving to: {target_path}")

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response, open(target_path, "wb") as out_file:
            chunk_size = 64 * 1024
            total_bytes = 0
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
                total_bytes += len(chunk)
        print(f"[+] Download complete: {format_bytes(total_bytes)}\n")
        return target_path
    except urllib.error.URLError as err:
        print(f"[!] Error downloading {url}: {err}")
        raise


def format_bytes(size: int) -> str:
    """Formats raw byte count into human-readable B, KB, MB, GB."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.2f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"


def detect_delimiter(sample_text: str) -> str:
    """
    Detects delimiter for delimited files. Defaults to ',' if inconclusive.
    """
    candidate_delimiters = [",", "\t", ";", "|"]
    first_lines = [l for l in sample_text.splitlines()[:15] if l.strip()]
    if not first_lines:
        return ","

    # Try csv.Sniffer first
    try:
        dialect = csv.Sniffer().sniff("\n".join(first_lines), delimiters=",\t;|")
        if dialect.delimiter in candidate_delimiters:
            return dialect.delimiter
    except Exception:
        pass

    # Heuristic fallback: count frequency across lines
    counts = {d: [line.count(d) for line in first_lines] for d in candidate_delimiters}
    best_delim = ","
    best_score = -1

    for delim, occurrences in counts.items():
        if not occurrences:
            continue
        first_count = occurrences[0]
        if first_count > 0 and all(c == first_count for c in occurrences):
            score = first_count * 10
        else:
            score = sum(occurrences)
        if score > best_score:
            best_score = score
            best_delim = delim

    # Check for whitespace delimiter if standard delimiters fail
    if best_score <= 0:
        if any(" " in line for line in first_lines):
            return " "

    return best_delim


def parse_datetime(val_str: str) -> Optional[datetime.datetime]:
    """Tries parsing a string as a datetime object."""
    s = val_str.strip()
    if len(s) < 8 or len(s) > 35:
        return None
    try:
        return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def calculate_skewness(values: List[float], mean_val: float, std_val: float) -> Optional[float]:
    """Calculates Fisher-Pearson standardized skewness."""
    n = len(values)
    if n < 3 or std_val <= 1e-9:
        return 0.0
    factor = n / ((n - 1) * (n - 2))
    sum_cubed = sum(((x - mean_val) / std_val) ** 3 for x in values)
    return factor * sum_cubed


def extract_columns_from_names_file(names_path: Path) -> List[str]:
    """
    Heuristically extracts attribute names from a UCI .names file if present.
    """
    if not names_path.is_file():
        return []
    attrs = []
    pattern = re.compile(r"^\s*(?:--)?\s*(\d+)[\.\)]\s+([a-zA-Z0-9_\-]+)")
    with open(names_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                attr_name = match.group(2).strip()
                if attr_name.lower() not in ("the", "number", "attribute", "attributes"):
                    attrs.append(attr_name)
    return attrs


# ==============================================================================
# DATASET PROFILER CLASS
# ==============================================================================

class DataProfiler:
    """
    Analyzes, profiles, and detects patterns in a single tabular or JSON dataset.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        source_url: Optional[str] = None,
        delimiter: Optional[str] = None,
        custom_columns: Optional[List[str]] = None,
        has_header: Optional[bool] = None,
        custom_na: Optional[Sequence[str]] = None,
    ):
        self.file_path = Path(file_path)
        self.source_url = source_url
        self.delimiter = delimiter
        self.custom_columns = custom_columns
        self.has_header = has_header
        self.na_markers = set(DEFAULT_MISSING_MARKERS)
        if custom_na:
            self.na_markers.update(m.lower() for m in custom_na)

        self.file_size = 0
        self.raw_rows: List[List[str]] = []
        self.columns: List[str] = []
        self.num_rows = 0
        self.num_cols = 0
        self.duplicate_rows_count = 0
        self.is_empty_file = False

        # Profiling results
        self.col_types: Dict[str, str] = {}
        self.missing_counts: Dict[str, int] = {}
        self.unique_counts: Dict[str, int] = {}
        self.numeric_stats: Dict[str, Dict[str, Any]] = {}
        self.categorical_stats: Dict[str, Dict[str, Any]] = {}
        self.datetime_stats: Dict[str, Dict[str, Any]] = {}
        self.correlations: List[Dict[str, Any]] = []
        self.recommendations: List[str] = []
        self.overall_health_score: float = 100.0

    def load_data(self) -> "DataProfiler":
        """Loads and parses file content into structured records."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        self.file_size = self.file_path.stat().st_size
        if self.file_size == 0:
            self.is_empty_file = True
            return self

        suffix = self.file_path.suffix.lower()

        if suffix in (".json", ".jsonl"):
            self._load_json()
        else:
            self._load_delimited()

        self.num_rows = len(self.raw_rows)
        self.num_cols = len(self.columns)

        if self.num_rows > 0:
            self._count_duplicates()

        return self

    def _load_json(self):
        """Loads JSON list of objects or JSON Lines."""
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read().strip()

        data_objs: List[Dict[str, Any]] = []
        if content.startswith("["):
            try:
                data_objs = json.loads(content)
            except json.JSONDecodeError as err:
                raise ValueError(f"Failed to parse JSON file: {err}")
        else:
            for line in content.splitlines():
                line = line.strip()
                if line:
                    try:
                        data_objs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        if not data_objs:
            return

        all_keys: List[str] = []
        for obj in data_objs:
            if isinstance(obj, dict):
                for k in obj.keys():
                    if k not in all_keys:
                        all_keys.append(k)

        self.columns = self.custom_columns if self.custom_columns else all_keys
        self.raw_rows = []
        for obj in data_objs:
            if isinstance(obj, dict):
                row = [str(obj.get(k, "")) if obj.get(k) is not None else "" for k in self.columns]
                self.raw_rows.append(row)

    def _load_delimited(self):
        """Loads CSV, TSV, DATA, or plain delimited text files."""
        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            sample_lines = [f.readline() for _ in range(25)]
        sample_text = "".join(sample_lines)

        if not self.delimiter:
            self.delimiter = detect_delimiter(sample_text)

        with open(self.file_path, "r", encoding="utf-8", errors="replace") as f:
            if self.delimiter == " ":
                raw_lines = [line.strip() for line in f if line.strip()]
                parsed_rows = [re.split(r"\s+", line) for line in raw_lines]
            else:
                reader = csv.reader(f, delimiter=self.delimiter)
                parsed_rows = [row for row in reader if row and any(c.strip() for c in row)]

        if not parsed_rows:
            return

        # Check for matching .names file in the same directory if custom_columns not provided
        if not self.custom_columns:
            names_file = self.file_path.with_suffix(".names")
            if names_file.is_file():
                extracted = extract_columns_from_names_file(names_file)
                if len(extracted) == len(parsed_rows[0]):
                    self.custom_columns = extracted

        # Header detection
        if self.custom_columns:
            self.columns = self.custom_columns
            if self._looks_like_header(parsed_rows[0]):
                self.raw_rows = parsed_rows[1:]
            else:
                self.raw_rows = parsed_rows
        elif self.has_header is True:
            self.columns = [c.strip() or f"col_{idx+1}" for idx, c in enumerate(parsed_rows[0])]
            self.raw_rows = parsed_rows[1:]
        elif self.has_header is False:
            self.columns = [f"col_{i+1:02d}" for i in range(len(parsed_rows[0]))]
            self.raw_rows = parsed_rows
        else:
            if self._looks_like_header(parsed_rows[0]):
                self.columns = [c.strip() or f"col_{idx+1}" for idx, c in enumerate(parsed_rows[0])]
                self.raw_rows = parsed_rows[1:]
            else:
                # If 14 columns in a .data file, suggest/check if UCI heart disease matches
                if len(parsed_rows[0]) == 14 and "heart" in self.file_path.name.lower():
                    self.columns = UCI_HEART_COLUMNS
                else:
                    self.columns = [f"col_{i+1:02d}" for i in range(len(parsed_rows[0]))]
                self.raw_rows = parsed_rows

    def _looks_like_header(self, first_row: List[str]) -> bool:
        """Determines if the first row is a column header rather than data."""
        if not first_row:
            return False
        for val in first_row:
            s = val.strip()
            if self._is_numeric(s):
                return False
        return True

    def _is_numeric(self, s: str) -> bool:
        """Checks if a string represents an integer or float."""
        s = s.strip()
        if not s or s.lower() in self.na_markers:
            return False
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _count_duplicates(self):
        """Counts exact duplicate rows."""
        seen = set()
        duplicates = 0
        for row in self.raw_rows:
            row_tuple = tuple(row)
            if row_tuple in seen:
                duplicates += 1
            else:
                seen.add(row_tuple)
        self.duplicate_rows_count = duplicates

    # ==========================================================================
    # PROFILING & STATISTICS
    # ==========================================================================

    def profile(self) -> "DataProfiler":
        """Performs full statistical, categorical, trend, and correlation profiling."""
        if self.is_empty_file or self.num_rows == 0 or self.num_cols == 0:
            return self

        # 1. Column-by-column analysis
        col_data: Dict[str, List[str]] = {col: [] for col in self.columns}
        for row in self.raw_rows:
            for idx, col in enumerate(self.columns):
                val = row[idx].strip() if idx < len(row) else ""
                col_data[col].append(val)

        numeric_clean_values: Dict[str, List[float]] = {}

        for col in self.columns:
            values = col_data[col]
            missing_count = sum(1 for v in values if v.lower() in self.na_markers)
            self.missing_counts[col] = missing_count
            valid_values = [v for v in values if v.lower() not in self.na_markers]
            unique_vals = set(valid_values)
            self.unique_counts[col] = len(unique_vals)

            inferred_type = self._infer_column_type(valid_values)
            self.col_types[col] = inferred_type

            if inferred_type in ("Integer", "Float"):
                nums = [float(v) for v in valid_values]
                numeric_clean_values[col] = nums
                self._profile_numeric_column(col, nums, missing_count)
            elif inferred_type == "Datetime":
                self._profile_datetime_column(col, valid_values, missing_count)
            else:
                self._profile_categorical_column(col, valid_values, missing_count)

        # 2. Correlation analysis across numeric columns
        self._calculate_correlations(numeric_clean_values)

        # 3. Generate actionable findings & recommendations
        self._generate_recommendations()

        # 4. Calculate overall data health score
        self._calculate_health_score()

        return self

    def _infer_column_type(self, valid_values: List[str]) -> str:
        """Infers high-fidelity column datatype."""
        if not valid_values:
            return "Text"

        sample = valid_values[:500]

        # Check boolean
        bool_markers = {"0", "1", "true", "false", "yes", "no", "t", "f", "y", "n"}
        if all(v.lower() in bool_markers for v in sample):
            distinct_lower = set(v.lower() for v in sample)
            if distinct_lower.issubset({"true", "false"}) or distinct_lower.issubset({"yes", "no"}):
                return "Boolean"

        # Check Integer
        is_int = True
        for v in sample:
            try:
                val = float(v)
                if not val.is_integer() or "." in v and not v.endswith(".0"):
                    is_int = False
                    break
            except ValueError:
                is_int = False
                break
        if is_int:
            if set(sample).issubset({"0", "1"}):
                return "Boolean"
            return "Integer"

        # Check Float
        is_float = True
        for v in sample:
            try:
                float(v)
            except ValueError:
                is_float = False
                break
        if is_float:
            return "Float"

        # Check Datetime
        dt_matches = sum(1 for v in sample if parse_datetime(v) is not None)
        if dt_matches / len(sample) >= 0.8:
            return "Datetime"

        # Check Categorical vs Text
        distinct_ratio = len(set(valid_values)) / len(valid_values)
        if len(set(valid_values)) <= 35 or distinct_ratio < 0.05:
            return "Categorical"

        return "Text"

    def _profile_numeric_column(self, col: str, nums: List[float], missing_count: int):
        """Calculates statistical metrics for numeric columns."""
        n = len(nums)
        if n == 0:
            return

        mean_val = statistics.mean(nums)
        std_val = statistics.stdev(nums) if n > 1 else 0.0
        variance_val = statistics.variance(nums) if n > 1 else 0.0
        min_val = min(nums)
        max_val = max(nums)

        if n >= 4:
            q_list = statistics.quantiles(nums, n=4)
            q1, median_val, q3 = q_list[0], q_list[1], q_list[2]
        else:
            median_val = statistics.median(nums)
            q1 = min_val
            q3 = max_val

        iqr = q3 - q1
        lower_fence = q1 - (1.5 * iqr)
        upper_fence = q3 + (1.5 * iqr)
        outliers = [x for x in nums if x < lower_fence or x > upper_fence]
        skewness_val = calculate_skewness(nums, mean_val, std_val)
        zeros_count = sum(1 for x in nums if x == 0.0)

        self.numeric_stats[col] = {
            "count": n,
            "missing": missing_count,
            "missing_pct": (missing_count / self.num_rows) * 100,
            "mean": mean_val,
            "std": std_val,
            "var": variance_val,
            "min": min_val,
            "q25": q1,
            "median": median_val,
            "q75": q3,
            "max": max_val,
            "iqr": iqr,
            "skewness": skewness_val,
            "outliers_count": len(outliers),
            "outliers_pct": (len(outliers) / n) * 100 if n else 0,
            "zeros_count": zeros_count,
            "zeros_pct": (zeros_count / n) * 100 if n else 0,
        }

    def _profile_categorical_column(self, col: str, valid_values: List[str], missing_count: int):
        """Profiles categorical/text columns."""
        n = len(valid_values)
        counter = Counter(valid_values)
        most_common = counter.most_common(5)

        dominant_pct = (most_common[0][1] / n) * 100 if most_common and n > 0 else 0.0
        is_candidate_pk = (len(counter) == self.num_rows) and (missing_count == 0)

        self.categorical_stats[col] = {
            "count": n,
            "missing": missing_count,
            "missing_pct": (missing_count / self.num_rows) * 100,
            "distinct_count": len(counter),
            "top_values": most_common,
            "dominant_pct": dominant_pct,
            "is_candidate_pk": is_candidate_pk,
        }

    def _profile_datetime_column(self, col: str, valid_values: List[str], missing_count: int):
        """Profiles datetime columns."""
        dt_objs = []
        for v in valid_values:
            parsed = parse_datetime(v)
            if parsed:
                dt_objs.append(parsed)

        if not dt_objs:
            return

        min_dt = min(dt_objs)
        max_dt = max(dt_objs)
        timespan = max_dt - min_dt

        self.datetime_stats[col] = {
            "count": len(dt_objs),
            "missing": missing_count,
            "missing_pct": (missing_count / self.num_rows) * 100,
            "min_date": min_dt.isoformat(),
            "max_date": max_dt.isoformat(),
            "timespan_days": timespan.days,
        }

    def _calculate_correlations(self, numeric_clean_values: Dict[str, List[float]]):
        """
        Calculates Pearson correlation for all numeric pairs.
        Flags pairs with strong correlation (|r| >= 0.40).
        """
        num_cols = list(numeric_clean_values.keys())
        if len(num_cols) < 2:
            return

        for i in range(len(num_cols)):
            for j in range(i + 1, len(num_cols)):
                c1 = num_cols[i]
                c2 = num_cols[j]

                pairs = []
                for row in self.raw_rows:
                    idx1 = self.columns.index(c1)
                    idx2 = self.columns.index(c2)
                    v1_str = row[idx1].strip() if idx1 < len(row) else ""
                    v2_str = row[idx2].strip() if idx2 < len(row) else ""
                    if v1_str.lower() not in self.na_markers and v2_str.lower() not in self.na_markers:
                        try:
                            pairs.append((float(v1_str), float(v2_str)))
                        except ValueError:
                            continue

                if len(pairs) < 4:
                    continue

                x_vals = [p[0] for p in pairs]
                y_vals = [p[1] for p in pairs]

                try:
                    r = statistics.correlation(x_vals, y_vals)
                    if math.isnan(r):
                        continue
                    if abs(r) >= 0.40:
                        self.correlations.append({
                            "col1": c1,
                            "col2": c2,
                            "r": r,
                            "strength": "Strong" if abs(r) >= 0.70 else "Moderate",
                            "direction": "Positive" if r > 0 else "Negative",
                            "sample_size": len(pairs)
                        })
                except Exception:
                    continue

        self.correlations.sort(key=lambda item: abs(item["r"]), reverse=True)

    def _generate_recommendations(self):
        """Generates actionable data cleaning and modeling advice."""
        recs = []

        # Duplicates check
        if self.duplicate_rows_count > 0:
            recs.append(
                f"⚠️ **Duplicate Rows Detected**: Found {self.duplicate_rows_count} exact duplicate "
                f"row(s) ({(self.duplicate_rows_count/self.num_rows)*100:.1f}%). "
                f"Consider deduping with `.drop_duplicates()`."
            )

        # Missing values check
        high_missing = [c for c, m in self.missing_counts.items() if (m / self.num_rows) >= 0.20]
        if high_missing:
            recs.append(
                f"⚠️ **High Missingness (>20%)**: Columns {high_missing} contain substantial missing data. "
                f"Verify collection integrity or consider imputation/dropping."
            )

        # Constant check
        constant_cols = [c for c in self.columns if self.unique_counts.get(c, 0) == 1]
        if constant_cols:
            recs.append(
                f"⚠️ **Zero Variance (Constant Columns)**: Columns {constant_cols} have only 1 unique value. "
                f"They provide zero predictive power and should be dropped."
            )

        # Outlier hotspots
        high_outliers = [
            c for c, s in self.numeric_stats.items() if s.get("outliers_pct", 0) >= 5.0
        ]
        if high_outliers:
            recs.append(
                f"💡 **Outlier Hotspots**: Columns {high_outliers} exhibit >= 5% Tukey outliers. "
                f"Inspect whether these represent clinical anomalies, extreme events, or data entry errors."
            )

        # Skewness check
        skewed_cols = [
            c for c, s in self.numeric_stats.items() if abs(s.get("skewness") or 0.0) >= 1.5
        ]
        if skewed_cols:
            recs.append(
                f"💡 **Heavy Skewness**: Features {skewed_cols} are heavily skewed (|skew| >= 1.5). "
                f"Consider applying Log or Power transformations prior to linear modeling."
            )

        # Multicollinearity
        strong_pairs = [c for c in self.correlations if abs(c["r"]) >= 0.75]
        if strong_pairs:
            pair_strs = [f"{p['col1']} & {p['col2']} (r={p['r']:.2f})" for p in strong_pairs[:3]]
            recs.append(
                f"⚠️ **Multicollinearity Alert**: Very strong correlations found: {', '.join(pair_strs)}. "
                f"Consider feature selection or PCA to avoid redundant predictors."
            )

        # Candidate Primary Keys
        pk_candidates = [
            c for c, s in self.categorical_stats.items() if s.get("is_candidate_pk")
        ]
        if pk_candidates:
            recs.append(
                f"🔑 **Candidate Identifier / Primary Key**: Column(s) {pk_candidates} are 100% unique "
                f"and non-null. Exclude them from statistical model feature sets."
            )

        # Class imbalance in categoricals
        imbalanced = [
            f"{c} ({s['top_values'][0][0]}: {s['dominant_pct']:.1f}%)"
            for c, s in self.categorical_stats.items()
            if s.get("dominant_pct", 0) >= 85.0 and s.get("distinct_count", 0) > 1
        ]
        if imbalanced:
            recs.append(
                f"⚠️ **Class Imbalance Notice**: Low category diversity in: {', '.join(imbalanced)}. "
                f"Watch for majority-class bias if used as a target or predictor."
            )

        if not recs:
            recs.append("✅ **Clean Dataset**: No critical anomalies, high missingness, or duplicate rows detected.")

        self.recommendations = recs

    def _calculate_health_score(self):
        """Calculates a composite data health score (0 to 100)."""
        score = 100.0
        total_cells = self.num_rows * self.num_cols
        total_missing = sum(self.missing_counts.values())

        if total_cells > 0:
            missing_rate = total_missing / total_cells
            score -= missing_rate * 40.0

        if self.num_rows > 0:
            dup_rate = self.duplicate_rows_count / self.num_rows
            score -= dup_rate * 30.0

        constant_count = sum(1 for c in self.columns if self.unique_counts.get(c, 0) == 1)
        if self.num_cols > 0:
            score -= (constant_count / self.num_cols) * 20.0

        self.overall_health_score = max(0.0, min(100.0, round(score, 1)))

    # ==========================================================================
    # DISPLAY & REPORTING
    # ==========================================================================

    def print_console_summary(self):
        """Outputs an organized, formatted terminal report."""
        sep = "=" * 80
        thin_sep = "-" * 80

        print("\n" + sep)
        print(f" DATASET EXPLORATION & PROFILE REPORT: {self.file_path.name}")
        print(sep)
        if self.source_url:
            print(f" Source URL       : {self.source_url}")
        print(f" Local File Path  : {self.file_path.resolve()}")
        print(f" File Size        : {format_bytes(self.file_size)}")

        if self.is_empty_file or self.num_rows == 0:
            print("\n [!] Notice: This file is empty (0 rows / 0 bytes). No data to profile.")
            print(sep + "\n")
            return

        print(f" Total Rows       : {self.num_rows:,}")
        print(f" Total Columns    : {self.num_cols:,}")
        print(f" Duplicate Rows   : {self.duplicate_rows_count:,} ({(self.duplicate_rows_count/self.num_rows)*100 if self.num_rows else 0:.2f}%)")
        total_cells = self.num_rows * self.num_cols
        total_missing = sum(self.missing_counts.values())
        print(f" Missing Cells    : {total_missing:,} / {total_cells:,} ({(total_missing/total_cells)*100 if total_cells else 0:.2f}%)")
        print(f" Health Score     : {self.overall_health_score}/100.0")
        print(thin_sep)

        # 1. Column Inventory Table
        print("\n[1] COLUMN SCHEMA & DATA HYGIENE")
        print(f"{'#':<3} {'Column Name':<22} {'Data Type':<13} {'Missing (%)':<15} {'Distinct':<10} {'Flags / Special':<18}")
        print("-" * 85)
        for idx, col in enumerate(self.columns, 1):
            dtype = self.col_types.get(col, "Unknown")
            miss = self.missing_counts.get(col, 0)
            miss_pct = (miss / self.num_rows) * 100 if self.num_rows else 0
            distinct = self.unique_counts.get(col, 0)

            flags = []
            if distinct == 1:
                flags.append("CONSTANT")
            if self.categorical_stats.get(col, {}).get("is_candidate_pk"):
                flags.append("PRIMARY_KEY")
            if miss_pct >= 20.0:
                flags.append("HIGH_NULLS")
            if self.numeric_stats.get(col, {}).get("outliers_count", 0) > 0:
                flags.append(f"{self.numeric_stats[col]['outliers_count']} OUTLIERS")

            flag_str = ", ".join(flags) if flags else "-"
            print(f"{idx:<3} {col[:20]:<22} {dtype:<13} {miss:<5} ({miss_pct:5.1f}%) {distinct:<10} {flag_str:<18}")

        # 2. Numeric Statistics
        if self.numeric_stats:
            print("\n[2] NUMERICAL STATISTICAL SUMMARY")
            print(f"{'Column':<18} {'Mean':<10} {'Std':<10} {'Min':<9} {'25%':<9} {'Median':<9} {'75%':<9} {'Max':<9} {'Skew':<8} {'Outliers':<9}")
            print("-" * 102)
            for col, s in self.numeric_stats.items():
                skew_str = f"{s['skewness']:.2f}" if s['skewness'] is not None else "N/A"
                print(
                    f"{col[:16]:<18} "
                    f"{s['mean']:<10.2f} "
                    f"{s['std']:<10.2f} "
                    f"{s['min']:<9.2f} "
                    f"{s['q25']:<9.2f} "
                    f"{s['median']:<9.2f} "
                    f"{s['q75']:<9.2f} "
                    f"{s['max']:<9.2f} "
                    f"{skew_str:<8} "
                    f"{s['outliers_count']:<9}"
                )

        # 3. Categorical Distributions
        if self.categorical_stats:
            print("\n[3] CATEGORICAL & TEXT FEATURE PROFILES")
            for col, s in self.categorical_stats.items():
                top_str = ", ".join([f"'{val}' ({cnt})" for val, cnt in s["top_values"][:4]])
                print(f" • {col:<18} [Distinct: {s['distinct_count']:<3} | Dominant: {s['dominant_pct']:.1f}%] -> Top: {top_str}")

        # 4. Trends & Noticeable Patterns
        print("\n[4] NOTICEABLE TRENDS & CORRELATIONS")
        if self.correlations:
            print(" • Top Bivariate Correlations:")
            for corr in self.correlations[:5]:
                symbol = "📈" if corr["r"] > 0 else "📉"
                print(f"   {symbol} {corr['col1']} <---> {corr['col2']}: r = {corr['r']:+.3f} ({corr['strength']} {corr['direction']})")
        else:
            print(" • No strong bivariate correlations (|r| >= 0.40) detected among numeric features.")

        # Temporal trends
        if self.datetime_stats:
            for col, dts in self.datetime_stats.items():
                print(f" • Temporal Range ({col}): {dts['min_date']} to {dts['max_date']} (Timespan: {dts['timespan_days']} days)")

        # 5. Recommendations
        print("\n[5] FIRST-REVIEW RECOMMENDATIONS & ACTION ITEMS")
        for rec in self.recommendations:
            clean_rec = rec.replace("**", "").replace("`", "")
            print(f" {clean_rec}")

        print(sep + "\n")

    def generate_markdown_report(self, output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Generates a comprehensive GitHub-Flavored Markdown report.
        """
        if output_path is None:
            output_path = self.file_path.parent / f"{self.file_path.stem}_profile_report.md"
        else:
            output_path = Path(output_path)

        md = []
        md.append(f"# 📊 Data Profile & Exploratory Analysis Report")
        md.append(f"**Target Dataset:** `{self.file_path.name}`  ")
        md.append(f"**Analysis Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        if self.source_url:
            md.append(f"**Source URL / Provenance:** [{self.source_url}]({self.source_url})  ")
        md.append(f"**File Size:** {format_bytes(self.file_size)}  ")
        md.append(f"**Data Health Score:** `{self.overall_health_score}/100.0`\n")

        if self.is_empty_file or self.num_rows == 0:
            md.append("> [!WARNING]\n> This file is empty (0 bytes or 0 rows). No tabular records found.\n")
            output_path.write_text("\n".join(md), encoding="utf-8")
            return output_path

        md.append("---")
        md.append("## 1. Executive Summary\n")
        total_cells = self.num_rows * self.num_cols
        total_missing = sum(self.missing_counts.values())
        missing_pct = (total_missing / total_cells) * 100 if total_cells else 0
        dup_pct = (self.duplicate_rows_count / self.num_rows) * 100 if self.num_rows else 0

        md.append("| Metric | Value | Metric | Value |")
        md.append("| :--- | :--- | :--- | :--- |")
        md.append(f"| **Total Rows** | {self.num_rows:,} | **Total Columns** | {self.num_cols:,} |")
        md.append(f"| **Duplicate Rows** | {self.duplicate_rows_count:,} ({dup_pct:.2f}%) | **Total Cells** | {total_cells:,} |")
        md.append(f"| **Missing Data Cells** | {total_missing:,} ({missing_pct:.2f}%) | **Health Score** | {self.overall_health_score} / 100 |")
        md.append("\n---\n")

        # Column Schema Table
        md.append("## 2. Column Inventory & Data Schema\n")
        md.append("| # | Column Name | Inferred Type | Missing Count (%) | Distinct Values | Notes & Flags |")
        md.append("| :- | :--- | :--- | :--- | :--- | :--- |")
        for idx, col in enumerate(self.columns, 1):
            dtype = self.col_types.get(col, "Unknown")
            miss = self.missing_counts.get(col, 0)
            miss_p = (miss / self.num_rows) * 100 if self.num_rows else 0
            distinct = self.unique_counts.get(col, 0)

            flags = []
            if distinct == 1:
                flags.append("`CONSTANT`")
            if self.categorical_stats.get(col, {}).get("is_candidate_pk"):
                flags.append("`PRIMARY KEY`")
            if miss_p >= 20.0:
                flags.append("`HIGH NULLS`")
            if self.numeric_stats.get(col, {}).get("outliers_count", 0) > 0:
                flags.append(f"`{self.numeric_stats[col]['outliers_count']} Outliers`")

            notes = ", ".join(flags) if flags else "-"
            md.append(f"| {idx} | **{col}** | `{dtype}` | {miss} ({miss_p:.1f}%) | {distinct:,} | {notes} |")
        md.append("\n---\n")

        # Numeric Statistics
        if self.numeric_stats:
            md.append("## 3. Numerical Features Statistical Summary\n")
            md.append("| Column | Mean | Std Dev | Min | 25% (Q1) | Median | 75% (Q3) | Max | IQR | Skewness | Outliers |")
            md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
            for col, s in self.numeric_stats.items():
                skew_str = f"{s['skewness']:.2f}" if s['skewness'] is not None else "-"
                md.append(
                    f"| **{col}** | {s['mean']:.2f} | {s['std']:.2f} | {s['min']:.2f} | "
                    f"{s['q25']:.2f} | {s['median']:.2f} | {s['q75']:.2f} | {s['max']:.2f} | "
                    f"{s['iqr']:.2f} | {skew_str} | {s['outliers_count']} ({s['outliers_pct']:.1f}%) |"
                )
            md.append("\n---\n")

        # Categorical Profiles
        if self.categorical_stats:
            md.append("## 4. Categorical & Text Distributions\n")
            md.append("| Column | Distinct Values | Dominant Class (%) | Top Most Frequent Values (Count, %) |")
            md.append("| :--- | :--- | :--- | :--- |")
            for col, s in self.categorical_stats.items():
                top_formatted = ", ".join([
                    f"`{val}`: {cnt} ({(cnt/s['count'])*100:.1f}%)"
                    for val, cnt in s["top_values"][:4]
                ])
                md.append(f"| **{col}** | {s['distinct_count']} | {s['dominant_pct']:.1f}% | {top_formatted} |")
            md.append("\n---\n")

        # Noticeable Trends & Correlations
        md.append("## 5. Noticeable Trends & Associations\n")
        if self.correlations:
            md.append("### 🔗 Notable Pearson Correlations\n")
            md.append("| Feature 1 | Feature 2 | Correlation ($r$) | Relationship | Strength |")
            md.append("| :--- | :--- | :--- | :--- | :--- |")
            for corr in self.correlations[:8]:
                md.append(
                    f"| `{corr['col1']}` | `{corr['col2']}` | `{corr['r']:+.3f}` | "
                    f"{corr['direction']} | {corr['strength']} |"
                )
            md.append("\n")
        else:
            md.append("*No bivariate numerical correlations exceeding $|r| \\ge 0.40$ were identified.*\n")

        if self.datetime_stats:
            md.append("### ⏱️ Temporal Profile\n")
            for col, dts in self.datetime_stats.items():
                md.append(f"- **`{col}`**: Observed range from `{dts['min_date']}` to `{dts['max_date']}` ({dts['timespan_days']} days total span).")
            md.append("\n")

        # Recommendations Checklist
        md.append("## 6. Actionable First-Review Recommendations\n")
        for rec in self.recommendations:
            md.append(f"- {rec}")
        md.append("\n---\n")
        md.append("*Report generated automatically by `data_profiler.py`.*")

        output_path.write_text("\n".join(md), encoding="utf-8")
        print(f"[+] Markdown report saved to: {output_path.resolve()}")
        return output_path

    def to_dict(self) -> Dict[str, Any]:
        """Exports profile metrics as a JSON-serializable dictionary."""
        return {
            "file_name": self.file_path.name,
            "source_url": self.source_url,
            "file_size_bytes": self.file_size,
            "total_rows": self.num_rows,
            "total_columns": self.num_cols,
            "duplicate_rows": self.duplicate_rows_count,
            "health_score": self.overall_health_score,
            "columns": self.columns,
            "column_types": self.col_types,
            "missing_counts": self.missing_counts,
            "unique_counts": self.unique_counts,
            "numeric_stats": self.numeric_stats,
            "categorical_stats": self.categorical_stats,
            "datetime_stats": self.datetime_stats,
            "correlations": self.correlations,
            "recommendations": self.recommendations,
        }


# ==============================================================================
# MULTI-DATASET COMPARATIVE SUMMARY
# ==============================================================================

def print_multi_dataset_comparison(profilers: List[DataProfiler]):
    """Prints a comparative table comparing multiple profiled files."""
    if len(profilers) <= 1:
        return

    sep = "=" * 90
    print("\n" + sep)
    print(" 📑 MULTI-DATASET BATCH COMPARATIVE SUMMARY")
    print(sep)
    header = f"{'File Name':<28} {'Rows':<9} {'Cols':<6} {'Size':<10} {'Missing (%)':<13} {'Duplicates':<12} {'Health':<8}"
    print(header)
    print("-" * 90)

    for p in profilers:
        total_cells = p.num_rows * p.num_cols
        total_missing = sum(p.missing_counts.values())
        miss_pct = (total_missing / total_cells) * 100 if total_cells else 0.0
        dup_str = f"{p.duplicate_rows_count}"
        size_str = format_bytes(p.file_size)
        print(
            f"{p.file_path.name[:26]:<28} "
            f"{p.num_rows:<9} "
            f"{p.num_cols:<6} "
            f"{size_str:<10} "
            f"{miss_pct:5.1f}%{' '*6} "
            f"{dup_str:<12} "
            f"{p.overall_health_score:<8.1f}"
        )
    print(sep + "\n")


# ==============================================================================
# CLI & WORKFLOW ORCHESTRATION
# ==============================================================================

def profile_dataset(
    file_or_url: str,
    source_url: Optional[str] = None,
    output_dir: Optional[Path] = None,
    delimiter: Optional[str] = None,
    columns: Optional[List[str]] = None,
    save_json: bool = False,
) -> DataProfiler:
    """Convenience helper to profile a single local file or URL."""
    is_url = file_or_url.startswith("http://") or file_or_url.startswith("https://")
    cache_dir = output_dir or Path("./downloaded_data")

    if is_url:
        actual_url = file_or_url
        local_file = download_url(actual_url, cache_dir)
    else:
        local_file = Path(file_or_url)
        actual_url = source_url

    profiler = DataProfiler(
        file_path=local_file,
        source_url=actual_url,
        delimiter=delimiter,
        custom_columns=columns,
    )
    profiler.load_data()
    profiler.profile()
    profiler.print_console_summary()

    if not profiler.is_empty_file and profiler.num_rows > 0:
        report_dir = output_dir or local_file.parent
        md_path = report_dir / f"{local_file.stem}_profile_report.md"
        profiler.generate_markdown_report(md_path)

        if save_json:
            json_path = report_dir / f"{local_file.stem}_profile.json"
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(profiler.to_dict(), jf, indent=2)
            print(f"[+] JSON profile saved to: {json_path.resolve()}")

    return profiler


def main():
    parser = argparse.ArgumentParser(
        description="Automated Data Profiler & Exploratory Data Analysis (EDA) Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples of Usage:
  # 1. Profile a local CSV / DATA file
  python data_profiler.py dataset.csv

  # 2. Profile a local file and record provenance / source URL
  python data_profiler.py cleveland.data --source-url "https://archive.ics.uci.edu/dataset/45/heart+disease"

  # 3. Directly download and profile a remote dataset URL
  python data_profiler.py --url "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"

  # 4. Profile UCI Heart Disease files with preset 14 attribute schema
  python data_profiler.py processed.cleveland.data --uci-heart

  # 5. Profile a headerless dataset with custom column names
  python data_profiler.py data.txt --columns "age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal,num"

  # 6. Profile all datasets in a directory
  python data_profiler.py source_dir/

  # 7. Zero arguments: Automatically checks .env for DATA_FILES, SOURCE_FILES, or prompts
  python data_profiler.py
        """
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help="One or more local file paths, directories, or dataset URLs to analyze."
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Direct dataset URL to download and analyze."
    )
    parser.add_argument(
        "--source-url",
        type=str,
        default=None,
        help="Optional provenance / source URL metadata for locally uploaded files."
    )
    parser.add_argument(
        "-d", "--delimiter",
        type=str,
        default=None,
        help="Explicit delimiter (e.g. ',', '\\t', ';', '|', ' '). Auto-detected if omitted."
    )
    parser.add_argument(
        "-c", "--columns",
        type=str,
        default=None,
        help="Comma-separated or semicolon-separated list of column names."
    )
    parser.add_argument(
        "--uci-heart",
        action="store_true",
        help="Apply standard UCI Heart Disease 14-attribute column schema."
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="Directory to save generated markdown and JSON reports. Defaults to file's directory."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Save profile metrics as a JSON file in addition to Markdown."
    )

    args = parser.parse_args()

    # Load .env variables if present
    env_vars = load_env_variables(".env")

    # Determine custom columns
    custom_cols = None
    if args.uci_heart:
        custom_cols = UCI_HEART_COLUMNS
    elif args.columns:
        delim = ";" if ";" in args.columns else ","
        custom_cols = [c.strip() for c in args.columns.split(delim) if c.strip()]

    out_dir = Path(args.output_dir) if args.output_dir else None

    # Collect target list
    targets: List[Tuple[str, Optional[str]]] = []

    if args.url:
        targets.append((args.url, args.url))

    for item in args.inputs:
        item_path = Path(item)
        if item.startswith("http://") or item.startswith("https://"):
            targets.append((item, item))
        elif item_path.is_dir():
            valid_exts = {".csv", ".tsv", ".data", ".txt", ".json", ".jsonl"}
            matched = sorted([f for f in item_path.iterdir() if f.is_file() and f.suffix.lower() in valid_exts])
            for f in matched:
                targets.append((str(f), args.source_url))
        elif item_path.is_file():
            targets.append((str(item_path), args.source_url))
        else:
            print(f"[!] Target not found: {item}")

    # Fallback to .env configuration if no inputs were provided via CLI
    if not targets:
        source_folder = env_vars.get("SOURCE_FOLDER") or env_vars.get("TARGET_FOLDER")
        source_files = env_vars.get("SOURCE_FILES") or env_vars.get("DATA_FILES") or env_vars.get("SOURCE_FILE")
        env_url = env_vars.get("DATASET_URL") or env_vars.get("SOURCE_URL") or env_vars.get("URL")

        if env_url:
            targets.append((env_url, env_url))
        elif source_folder and source_files:
            folder_path = Path(source_folder)
            files = [f.strip() for f in source_files.split(";") if f.strip()]
            for fname in files:
                p = folder_path / fname
                if p.is_file():
                    targets.append((str(p), env_url))

    # Interactive prompt if still no inputs
    if not targets:
        print("=" * 70)
        print(" Universal Data Profiler - Interactive Setup")
        print("=" * 70)
        file_input = input("Enter local file path or dataset URL: ").strip()
        if not file_input:
            print("[!] No file or URL provided. Exiting.")
            sys.exit(1)
        url_input = ""
        if not (file_input.startswith("http://") or file_input.startswith("https://")):
            url_input = input("Enter source URL where file came from (optional, press Enter to skip): ").strip()
        targets.append((file_input, url_input if url_input else None))

    print(f"\n[+] Processing {len(targets)} dataset(s)...")

    profiled_results: List[DataProfiler] = []

    for file_or_url, src_url in targets:
        try:
            p = profile_dataset(
                file_or_url=file_or_url,
                source_url=src_url,
                output_dir=out_dir,
                delimiter=args.delimiter,
                columns=custom_cols,
                save_json=args.json,
            )
            profiled_results.append(p)
        except Exception as err:
            print(f"[!] Failed to profile '{file_or_url}': {err}")
            import traceback
            traceback.print_exc()

    # Print multi-dataset comparison table if 2 or more files were profiled
    if len(profiled_results) > 1:
        print_multi_dataset_comparison(profiled_results)


if __name__ == "__main__":
    main()
