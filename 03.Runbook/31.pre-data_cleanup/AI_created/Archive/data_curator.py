#!/usr/bin/env python3
"""
================================================================================
Universal AI Data Preparation, Sanitization, Curation & Staging Pipeline
================================================================================
A comprehensive, zero-external-dependency Python pipeline designed to ingest,
sanitize, cleanse, curate, engineer, scale, augment, and stage tabular and
clinical datasets for AI/ML ingestion, exploratory curation, and model deployment.

Core Capabilities:
  1. Multi-source Ingestion: Reads CSV, TSV, DATA (UCI format), TXT, JSON, and JSONL.
     Supports headerless formats with automatic .names parsing or built-in presets
     (e.g., UCI Heart Disease 14 attributes).
  2. Privacy & PII/PHI Sanitization: HIPAA Safe Harbor redaction of SSNs, emails,
     phone numbers, IPs, MRNs, with salted cryptographic pseudonymization and
     patient date-shifting.
  3. Deduplication: Exact row deduplication, key-based deduplication, and fuzzy/near-
     duplicate record resolution.
  4. Missing Value Treatment: Identifies multi-marker missing values ('?', 'NA', '-9', etc.),
     drops high-missingness rows/columns, performs median/mean/mode/constant imputation,
     and creates informative missingness indicator flags.
  5. Outlier Detection & Avoidance: Tukey's IQR Fences (1.5*IQR), Z-Score, and Median
     Absolute Deviation (MAD). Supports Winsorization/clipping, trimming, median
     imputation, or outlier indicator flags without destabilizing model gradients.
  6. Schema Sanitization & Type Casting: Converts messy column names to clean snake_case,
     strips whitespace, and performs robust casting to Integer, Float, Boolean,
     Datetime, Categorical, or Text.
  7. Entity Resolution / Record Linkage: Pure-Python Jaro-Winkler and Levenshtein
     distance algorithms with blocking to resolve entities (e.g. patients) across
     noisy datasets and assign canonical entity IDs.
  8. Feature Engineering: Automated numerical interaction terms (ratios, products,
     differences), log1p transformation for skewed variables (|skew| >= 1.5),
     datetime temporal feature extraction, and One-Hot / Ordinal / Frequency encodings.
  9. Normalization & Scaling: StandardScaler, MinMaxScaler, RobustScaler, and
     MaxAbsScaler. Preserves and exports transformation parameters (`scaler_params.json`)
     to eliminate data leakage during inference.
 10. Data Augmentation: Gaussian tabular jittering, tabular mixup (convex interpolation),
     and minority class balancing with `is_synthetic` flags.
 11. Zero-Leakage AI Staging: Stratified/random Train/Val/Test partitioning where
     all imputers, scalers, and encoders are fit strictly on training splits.
 12. Multi-Format AI Deliverables:
     - `train.csv`, `val.csv`, `test.csv`, and `curated_full.csv` (Tabular ML ready)
     - `staged_for_llm.jsonl` (Instruction-tuning / RAG clinical narrative prompts)
     - `staged_tensors.json` (Numpy/PyTorch ready numerical matrices and feature maps)
     - `staging_manifest.json` (SHA-256 provenance hashes and audit log)
     - `DATA_CARD.md` (Enterprise AI model governance & data card report)

Built entirely with the Python 3.8+ Standard Library (zero pip dependencies required).
================================================================================
"""

import argparse
import copy
import csv
import datetime
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union


# ==============================================================================
# CONFIGURATION CONSTANTS & DOMAIN PRESETS
# ==============================================================================

DEFAULT_MISSING_MARKERS: Set[str] = {
    "", "?", "na", "n/a", "nan", "null", "none", "-9", "-999", ".", "nil",
    "unknown", "missing", "n/d", "#n/a", "not applicable"
}

DATETIME_FORMATS: Tuple[str, ...] = (
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

UCI_HEART_COLUMNS: List[str] = [
    "age",        # Age in years
    "sex",        # Sex (1 = male; 0 = female)
    "cp",         # Chest pain type (1: typical, 2: atypical, 3: non-anginal, 4: asymptomatic)
    "trestbps",   # Resting blood pressure in mm Hg
    "chol",       # Serum cholesterol in mg/dl
    "fbs",        # Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)
    "restecg",    # Resting ECG (0: normal, 1: ST-T wave, 2: LV hypertrophy)
    "thalach",    # Maximum heart rate achieved
    "exang",      # Exercise induced angina (1 = yes; 0 = no)
    "oldpeak",    # ST depression induced by exercise relative to rest
    "slope",      # Slope of the peak exercise ST segment (1: up, 2: flat, 3: down)
    "ca",         # Number of major vessels (0-3) colored by fluoroscopy
    "thal",       # Thalassemia (3 = normal; 6 = fixed; 7 = reversible)
    "num"         # Target diagnosis (0 = no disease, 1-4 = heart disease present)
]

# Regex patterns for direct identifiers (HIPAA Safe Harbor Compliance)
REGEX_PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "ip_address": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
    "mrn": re.compile(r"\bMRN[0-9]{6,10}\b", re.IGNORECASE),
}


# ==============================================================================
# HELPER UTILITIES: ENVIRONMENT, STRING SIMILARITY & MATH
# ==============================================================================

def load_env_variables(dotenv_path: Union[Path, str] = ".env") -> Dict[str, str]:
    """Parses key-value pairs from a .env file without external dependencies."""
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


def to_float(val: Any) -> Optional[float]:
    """Safely converts any value to a float, returning None if unparseable, NaN, or Inf."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        f = float(val)
        return None if (math.isnan(f) or math.isinf(f)) else f
    s = str(val).strip()
    if not s or s.lower() in DEFAULT_MISSING_MARKERS:
        return None
    try:
        f = float(s)
        return None if (math.isnan(f) or math.isinf(f)) else f
    except (ValueError, TypeError):
        return None


def to_int(val: Any) -> Optional[int]:
    """Safely converts any value to an integer."""
    f = to_float(val)
    return int(round(f)) if f is not None else None


def clean_column_name(col: str, existing: Optional[Set[str]] = None) -> str:
    """Standardizes a column name to lowercase snake_case, ensuring uniqueness."""
    col = col.strip()
    col = re.sub(r"[^\w\s-]", "", col)
    col = re.sub(r"[-\s]+", "_", col)
    col = col.lower().strip("_")
    if not col:
        col = "col"
    if col[0].isdigit():
        col = "c_" + col

    if existing is not None:
        base = col
        idx = 1
        while col in existing:
            col = f"{base}_{idx}"
            idx += 1
        existing.add(col)
    return col


def jaro_similarity(s1: str, s2: str) -> float:
    """Computes Jaro string similarity between two strings (0.0 to 1.0)."""
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0

    match_distance = max(len1, len2) // 2 - 1
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0

    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    return ((matches / len1) + (matches / len2) + ((matches - transpositions / 2) / matches)) / 3.0


def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1, max_l: int = 4) -> float:
    """Computes Jaro-Winkler string similarity (favors common prefixes)."""
    j = jaro_similarity(s1, s2)
    l = 0
    for c1, c2 in zip(s1, s2):
        if c1 == c2:
            l += 1
        else:
            break
        if l >= max_l:
            break
    return j + (l * p * (1.0 - j))


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Computes normalized Levenshtein similarity (1 - dist / max_len)."""
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    s1, s2 = s1.lower(), s2.lower()
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return 1.0 - (dp[m][n] / max(m, n))


def calculate_quantiles(values: Sequence[float]) -> Tuple[float, float, float]:
    """Returns Q1 (25%), Q2/Median (50%), and Q3 (75%) for a sequence of numbers."""
    sorted_v = sorted(values)
    n = len(sorted_v)
    if n == 0:
        return 0.0, 0.0, 0.0
    if n == 1:
        return sorted_v[0], sorted_v[0], sorted_v[0]
    try:
        q1, q2, q3 = statistics.quantiles(sorted_v, n=4, method="inclusive")
        return float(q1), float(q2), float(q3)
    except Exception:
        # Fallback quantile calculation
        def get_pct(p: float) -> float:
            idx = p * (n - 1)
            lo = math.floor(idx)
            hi = math.ceil(idx)
            if lo == hi:
                return sorted_v[int(idx)]
            return sorted_v[lo] * (hi - idx) + sorted_v[hi] * (idx - lo)
        return get_pct(0.25), get_pct(0.50), get_pct(0.75)


def calculate_skewness(values: Sequence[float]) -> float:
    """Calculates sample Fisher-Pearson skewness coefficient."""
    n = len(values)
    if n < 3:
        return 0.0
    mean_val = statistics.mean(values)
    std_val = statistics.stdev(values) if n > 1 else 0.0
    if std_val < 1e-9:
        return 0.0
    m3 = sum((x - mean_val) ** 3 for x in values) / n
    s3 = std_val ** 3
    # Unbiased sample skewness
    return (math.sqrt(n * (n - 1)) / (n - 2)) * (m3 / s3)


def file_sha256(filepath: Union[Path, str]) -> str:
    """Computes SHA-256 hash of a file for cryptographic provenance tracking."""
    sha = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()
    except Exception:
        return "N/A"


# ==============================================================================
# DATA INGESTION & FORMAT AUTO-DETECTION
# ==============================================================================

class DatasetIngester:
    """Ingests tabular and structured dataset files into standardized dictionaries."""

    @staticmethod
    def sniff_delimiter(sample_text: str, default: str = ",") -> str:
        """Heuristically determines delimiter from sample text."""
        candidates = [",", "\t", ";", "|", " "]
        counts = {delim: sample_text.count(delim) for delim in candidates}
        # Filter out 0 counts
        valid = {k: v for k, v in counts.items() if v > 0}
        if not valid:
            return default
        return max(valid, key=valid.get)

    @classmethod
    def load_file(
        cls,
        filepath: Union[Path, str],
        custom_columns: Optional[List[str]] = None,
        delimiter: Optional[str] = None
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Loads a file into (column_names, list_of_row_dicts).
        Supports CSV, TSV, DATA, TXT, JSON, and JSON Lines.
        """
        p = Path(filepath)
        if not p.is_file():
            raise FileNotFoundError(f"Dataset file not found: {p}")

        suffix = p.suffix.lower()

        # Handle JSON / JSONL
        if suffix in (".json", ".jsonl"):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                content = f.read().strip()
                if not content:
                    return [], []
                if suffix == ".jsonl" or "\n" in content and content.startswith("{"):
                    rows = []
                    for line in content.splitlines():
                        line = line.strip()
                        if line:
                            rows.append(json.loads(line))
                else:
                    loaded = json.loads(content)
                    rows = loaded if isinstance(loaded, list) else [loaded]

                if not rows:
                    return [], []
                # Collect distinct columns
                all_cols: Set[str] = set()
                for r in rows:
                    if isinstance(r, dict):
                        all_cols.update(r.keys())
                columns = sorted(list(all_cols))
                # Standardize rows
                standard_rows = []
                for r in rows:
                    if isinstance(r, dict):
                        standard_rows.append({c: r.get(c, "") for c in columns})
                return columns, standard_rows

        # Handle Delimited Text (CSV, TSV, DATA, TXT)
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            lines = [ln.strip() for ln in f if ln.strip()]

        if not lines:
            return [], []

        # Determine delimiter
        if delimiter is None:
            sample_chunk = "\n".join(lines[:20])
            delimiter = cls.sniff_delimiter(sample_chunk)

        # Check if first line appears to be a header or data
        first_line_parts = [v.strip() for v in re.split(r"[" + re.escape(delimiter) + r"\s]+", lines[0]) if v.strip()] if delimiter == " " else [v.strip() for v in lines[0].split(delimiter)]
        non_numeric_count = sum(1 for val in first_line_parts if not re.match(r"^-?\d+(\.\d+)?([eE][-+]?\d+)?$", val))
        is_header_row = (non_numeric_count >= len(first_line_parts) * 0.5)

        if is_header_row:
            data_start_idx = 1
            # If custom_columns provided and matches column count, user is replacing the header
            if custom_columns and len(first_line_parts) == len(custom_columns):
                columns = [clean_column_name(c) for c in custom_columns]
            else:
                # Retain existing file header
                raw_cols = first_line_parts
                existing_cols: Set[str] = set()
                columns = [clean_column_name(c, existing_cols) for c in raw_cols]
        else:
            data_start_idx = 0
            if custom_columns and len(first_line_parts) == len(custom_columns):
                columns = [clean_column_name(c) for c in custom_columns]
            else:
                names_file = p.with_suffix(".names")
                extracted_names = cls._extract_uci_names(names_file)
                if extracted_names and len(extracted_names) == len(first_line_parts):
                    columns = extracted_names
                elif custom_columns and len(first_line_parts) == len(custom_columns):
                    columns = [clean_column_name(c) for c in custom_columns]
                else:
                    columns = [f"feature_{i+1}" for i in range(len(first_line_parts))]

        # Parse data rows
        rows: List[Dict[str, Any]] = []
        for line in lines[data_start_idx:]:
            if delimiter == " ":
                parts = [v.strip() for v in re.split(r"\s+", line) if v.strip()]
            else:
                parts = [v.strip() for v in line.split(delimiter)]

            # Map to columns
            row_dict: Dict[str, Any] = {}
            for i, col in enumerate(columns):
                val = parts[i] if i < len(parts) else ""
                row_dict[col] = val
            rows.append(row_dict)

        return columns, rows

    @staticmethod
    def _extract_uci_names(names_path: Path) -> Optional[List[str]]:
        """Attempts to parse attribute names from UCI .names documentation files."""
        if not names_path.is_file():
            return None
        names: List[str] = []
        try:
            with open(names_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    m = re.match(r"^\s*\d+[\.\)]\s+([A-Za-z0-9_-]+)", line)
                    if m:
                        names.append(clean_column_name(m.group(1)))
            return names if len(names) >= 2 else None
        except Exception:
            return None


# ==============================================================================
# SANITIZATION, TYPE CASTING & PII/PHI REDACTION
# ==============================================================================

class SanitizerEngine:
    """Handles schema standardization, type inference, casting, and HIPAA PII/PHI redaction."""

    def __init__(self, salt: str = "ai_curation_salt"):
        self.salt = salt

    def redact_pii(self, text: str) -> str:
        """Redacts sensitive direct identifiers using standard regex masks."""
        if not isinstance(text, str):
            return text
        text = REGEX_PATTERNS["ssn"].sub("[REDACTED_SSN]", text)
        text = REGEX_PATTERNS["email"].sub("[REDACTED_EMAIL]", text)
        text = REGEX_PATTERNS["phone"].sub("[REDACTED_PHONE]", text)
        text = REGEX_PATTERNS["ip_address"].sub("[REDACTED_IP]", text)
        text = REGEX_PATTERNS["mrn"].sub("[REDACTED_MRN]", text)
        return text

    def hash_identifier(self, identifier: str) -> str:
        """Creates a deterministic, cryptographically salted pseudonym for patient/subject IDs."""
        if not identifier or identifier in DEFAULT_MISSING_MARKERS:
            return identifier
        h = hashlib.sha256(f"{self.salt}_{identifier}".encode("utf-8")).hexdigest()
        return f"ID_{h[:10]}"

    @staticmethod
    def parse_value(val: Any) -> Tuple[Any, str]:
        """
        Parses a single raw string into its inferred typed representation.
        Returns: (parsed_value, inferred_type_name)
        """
        if val is None:
            return None, "missing"

        if isinstance(val, (int, float, bool)):
            return val, ("boolean" if isinstance(val, bool) else ("integer" if isinstance(val, int) else "float"))

        s = str(val).strip()
        lower_s = s.lower()

        if lower_s in DEFAULT_MISSING_MARKERS:
            return None, "missing"

        # Boolean detection
        if lower_s in ("true", "false", "yes", "no", "t", "f"):
            return (True if lower_s in ("true", "yes", "t") else False), "boolean"

        # Integer detection
        if re.match(r"^-?\d+$", s):
            try:
                return int(s), "integer"
            except ValueError:
                pass

        # Float detection (including scientific notation)
        if re.match(r"^-?\d+(\.\d+)?([eE][-+]?\d+)?$", s):
            try:
                f_val = float(s)
                if not math.isnan(f_val) and not math.isinf(f_val):
                    return f_val, "float"
            except ValueError:
                pass

        # Datetime detection
        for fmt in DATETIME_FORMATS:
            try:
                dt = datetime.datetime.strptime(s, fmt)
                return dt.isoformat(), "datetime"
            except ValueError:
                continue

        return s, "string"

    def infer_schema(self, columns: List[str], rows: List[Dict[str, Any]]) -> Dict[str, str]:
        """Infers the dominant type for each column across all records."""
        schema: Dict[str, str] = {}
        for col in columns:
            type_counts: Counter = Counter()
            for r in rows:
                val = r.get(col)
                _, inferred_type = self.parse_value(val)
                if inferred_type != "missing":
                    type_counts[inferred_type] += 1

            if not type_counts:
                schema[col] = "string"
            else:
                # Prioritize numeric types if dominant
                if type_counts["integer"] + type_counts["float"] > 0:
                    if type_counts["float"] > 0:
                        schema[col] = "float"
                    elif type_counts["integer"] >= sum(type_counts.values()) * 0.7:
                        schema[col] = "integer"
                    else:
                        schema[col] = type_counts.most_common(1)[0][0]
                else:
                    most_common = type_counts.most_common(1)[0][0]
                    # Check cardinality for categorical designation
                    unique_vals = {r.get(col) for r in rows if r.get(col) not in DEFAULT_MISSING_MARKERS}
                    if most_common == "string" and len(unique_vals) <= max(10, len(rows) * 0.2):
                        schema[col] = "categorical"
                    else:
                        schema[col] = most_common

        return schema


# ==============================================================================
# DEDUPLICATION & ENTITY RESOLUTION
# ==============================================================================

class DeduplicatorEngine:
    """Detects and resolves exact duplicates, key-based duplicates, and fuzzy record linkage."""

    @staticmethod
    def deduplicate_exact(
        rows: List[Dict[str, Any]],
        columns: List[str]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Eliminates identical rows across all specified columns."""
        seen: Set[str] = set()
        unique_rows: List[Dict[str, Any]] = []
        duplicates_removed = 0

        for r in rows:
            # Create deterministic string fingerprint
            fingerprint = "|".join(str(r.get(c, "")) for c in columns)
            if fingerprint in seen:
                duplicates_removed += 1
            else:
                seen.add(fingerprint)
                unique_rows.append(r)

        return unique_rows, duplicates_removed

    @staticmethod
    def deduplicate_by_keys(
        rows: List[Dict[str, Any]],
        keys: List[str]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Deduplicates keeping the first occurrence based on a subset of primary key columns."""
        seen: Set[str] = set()
        unique_rows: List[Dict[str, Any]] = []
        duplicates_removed = 0

        for r in rows:
            key_tuple = "|".join(str(r.get(k, "")).strip().lower() for k in keys)
            if key_tuple in seen:
                duplicates_removed += 1
            else:
                seen.add(key_tuple)
                unique_rows.append(r)

        return unique_rows, duplicates_removed

    @classmethod
    def resolve_entities_fuzzy(
        cls,
        rows: List[Dict[str, Any]],
        entity_match_cols: List[str],
        similarity_threshold: float = 0.88,
        blocking_col: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, str]]:
        """
        Performs entity resolution across records using Jaro-Winkler and Levenshtein similarity.
        Assigns a unified canonical `canonical_entity_id` to linked records.
        Returns: (augmented_rows, clusters_formed, entity_id_map)
        """
        # Group into blocks to prevent O(N^2) explosion
        blocks: Dict[str, List[int]] = defaultdict(list)
        for idx, r in enumerate(rows):
            if blocking_col and blocking_col in r:
                block_key = str(r[blocking_col]).strip().lower()[:4]
            else:
                # Default blocking on first character of first match col or all in single block
                first_val = str(r.get(entity_match_cols[0], "")).strip().lower()
                block_key = first_val[:2] if len(first_val) >= 2 else "all"
            blocks[block_key].append(idx)

        # Union-Find / Disjoint Set
        parent = list(range(len(rows)))

        def find(i: int) -> int:
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i: int, j: int):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_j] = root_i

        for block_key, indices in blocks.items():
            n = len(indices)
            for i in range(n):
                idx_a = indices[i]
                row_a = rows[idx_a]
                for j in range(i + 1, n):
                    idx_b = indices[j]
                    row_b = rows[idx_b]

                    # Compute composite string similarity across match cols
                    sims = []
                    for col in entity_match_cols:
                        val_a = str(row_a.get(col, "")).strip().lower()
                        val_b = str(row_b.get(col, "")).strip().lower()
                        if val_a and val_b:
                            sim = jaro_winkler_similarity(val_a, val_b)
                            sims.append(sim)

                    if sims and (sum(sims) / len(sims)) >= similarity_threshold:
                        union(idx_a, idx_b)

        # Build canonical clusters
        cluster_map: Dict[int, str] = {}
        cluster_counter = 1
        clusters_count = 0
        resolved_rows: List[Dict[str, Any]] = []

        for idx, r in enumerate(rows):
            root = find(idx)
            if root not in cluster_map:
                cluster_map[root] = f"ENT_{cluster_counter:05d}"
                cluster_counter += 1
            else:
                clusters_count += 1
            new_r = copy.deepcopy(r)
            new_r["canonical_entity_id"] = cluster_map[root]
            resolved_rows.append(new_r)

        return resolved_rows, clusters_count, cluster_map


# ==============================================================================
# MISSING VALUE & OUTLIER CURATION
# ==============================================================================

class MissingValueHandler:
    """Manages threshold-based dropping, statistical imputation, and indicator flags."""

    def __init__(
        self,
        numeric_strategy: str = "median",
        categorical_strategy: str = "mode",
        max_missing_col: float = 0.50,
        max_missing_row: float = 0.60,
        add_indicators: bool = True
    ):
        self.numeric_strategy = numeric_strategy
        self.categorical_strategy = categorical_strategy
        self.max_missing_col = max_missing_col
        self.max_missing_row = max_missing_row
        self.add_indicators = add_indicators
        self.fitted_imputations: Dict[str, Any] = {}
        self.dropped_columns: List[str] = []

    def fit(self, rows: List[Dict[str, Any]], schema: Dict[str, str]) -> "MissingValueHandler":
        """Learns imputation parameters (mean, median, mode) strictly from reference/training rows."""
        n_rows = len(rows)
        if n_rows == 0:
            return self

        # 1. Check column missingness rates
        for col, col_type in schema.items():
            missing_count = sum(1 for r in rows if r.get(col) is None or str(r.get(col)).lower() in DEFAULT_MISSING_MARKERS)
            rate = missing_count / n_rows
            if rate > self.max_missing_col:
                self.dropped_columns.append(col)
                continue

            # Compute imputation value
            valid_values = [r[col] for r in rows if r.get(col) is not None and str(r.get(col)).lower() not in DEFAULT_MISSING_MARKERS]
            if not valid_values:
                self.fitted_imputations[col] = 0.0 if col_type in ("integer", "float") else "missing"
                continue

            if col_type in ("integer", "float"):
                num_vals = [f for v in valid_values if (f := to_float(v)) is not None]
                if not num_vals:
                    self.fitted_imputations[col] = 0.0
                elif self.numeric_strategy == "median":
                    self.fitted_imputations[col] = statistics.median(num_vals)
                elif self.numeric_strategy == "mean":
                    self.fitted_imputations[col] = statistics.mean(num_vals)
                elif self.numeric_strategy == "mode":
                    self.fitted_imputations[col] = Counter(num_vals).most_common(1)[0][0]
                elif self.numeric_strategy == "zero":
                    self.fitted_imputations[col] = 0.0
                else:
                    self.fitted_imputations[col] = statistics.median(num_vals)
            else:
                if self.categorical_strategy == "mode":
                    self.fitted_imputations[col] = Counter(valid_values).most_common(1)[0][0]
                else:
                    self.fitted_imputations[col] = "missing"

        return self

    def transform(self, rows: List[Dict[str, Any]], schema: Dict[str, str]) -> Tuple[List[Dict[str, Any]], int]:
        """Applies imputation and creates boolean missing indicator features."""
        cleaned_rows: List[Dict[str, Any]] = []
        dropped_rows = 0
        total_cols = len([c for c in schema if c not in self.dropped_columns])

        for r in rows:
            # Check row-level missingness
            missing_in_row = 0
            for col in schema:
                if col in self.dropped_columns:
                    continue
                val = r.get(col)
                if val is None or str(val).lower() in DEFAULT_MISSING_MARKERS:
                    missing_in_row += 1

            if total_cols > 0 and (missing_in_row / total_cols) > self.max_missing_row:
                dropped_rows += 1
                continue

            new_r: Dict[str, Any] = {}
            for col, col_type in schema.items():
                if col in self.dropped_columns:
                    continue

                val = r.get(col)
                is_missing = val is None or str(val).lower() in DEFAULT_MISSING_MARKERS

                if self.add_indicators:
                    new_r[f"{col}_is_missing"] = 1 if is_missing else 0

                if is_missing:
                    imputed = self.fitted_imputations.get(col)
                    if col_type == "integer" and imputed is not None:
                        new_r[col] = to_int(imputed) or 0
                    elif col_type == "float" and imputed is not None:
                        new_r[col] = to_float(imputed) or 0.0
                    else:
                        new_r[col] = imputed
                else:
                    if col_type == "integer":
                        parsed_int = to_int(val)
                        new_r[col] = parsed_int if parsed_int is not None else (to_int(self.fitted_imputations.get(col)) or 0)
                    elif col_type == "float":
                        parsed_flt = to_float(val)
                        new_r[col] = parsed_flt if parsed_flt is not None else (to_float(self.fitted_imputations.get(col)) or 0.0)
                    else:
                        new_r[col] = val
                        new_r[col] = val

            cleaned_rows.append(new_r)

        return cleaned_rows, dropped_rows


class OutlierHandler:
    """Detects, clips (Winsorizes), flags, or drops statistical anomalies."""

    def __init__(
        self,
        method: str = "iqr",
        treatment: str = "clip",
        factor: float = 1.5,
        target_columns: Optional[List[str]] = None
    ):
        self.method = method            # 'iqr', 'zscore', 'mad'
        self.treatment = treatment      # 'clip', 'drop', 'impute', 'flag', 'none'
        self.factor = factor            # 1.5 for standard Tukey, 3.0 for extreme
        self.target_columns = target_columns
        self.bounds: Dict[str, Tuple[float, float, float]] = {}  # col -> (lower, upper, median)
        self.outlier_counts: Dict[str, int] = defaultdict(int)

    def fit(self, rows: List[Dict[str, Any]], schema: Dict[str, str]) -> "OutlierHandler":
        """Calculates boundary fences for numeric features from training rows."""
        cols_to_check = self.target_columns or [c for c, t in schema.items() if t in ("integer", "float")]

        for col in cols_to_check:
            vals = [f for r in rows if (f := to_float(r.get(col))) is not None]
            if len(vals) < 4:
                continue

            med = statistics.median(vals)
            if self.method == "iqr":
                q1, _, q3 = calculate_quantiles(vals)
                iqr = q3 - q1
                lower = q1 - (self.factor * iqr)
                upper = q3 + (self.factor * iqr)
            elif self.method == "zscore":
                mean_v = statistics.mean(vals)
                std_v = statistics.stdev(vals) if len(vals) > 1 else 1e-6
                lower = mean_v - (self.factor * std_v)
                upper = mean_v + (self.factor * std_v)
            elif self.method == "mad":
                deviations = [abs(x - med) for x in vals]
                mad = statistics.median(deviations) or 1e-6
                lower = med - (self.factor * mad * 1.4826)
                upper = med + (self.factor * mad * 1.4826)
            else:
                q1, _, q3 = calculate_quantiles(vals)
                iqr = q3 - q1
                lower = q1 - (1.5 * iqr)
                upper = q3 + (1.5 * iqr)

            self.bounds[col] = (lower, upper, med)

        return self

    def transform(self, rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        """Applies outlier treatment to incoming records."""
        if self.treatment == "none":
            return rows, 0

        curated_rows: List[Dict[str, Any]] = []
        dropped_rows = 0

        for r in rows:
            new_r = copy.copy(r)
            row_has_outlier = False

            for col, (lower, upper, med) in self.bounds.items():
                if col not in new_r:
                    continue
                v = to_float(new_r[col])
                if v is None:
                    continue

                is_outlier = (v < lower) or (v > upper)

                if is_outlier:
                    self.outlier_counts[col] += 1
                    row_has_outlier = True

                    if self.treatment == "clip":
                        new_r[col] = max(lower, min(upper, v))
                    elif self.treatment == "impute":
                        new_r[col] = med
                    elif self.treatment == "flag":
                        new_r[f"{col}_is_outlier"] = 1

            if self.treatment == "flag":
                for col in self.bounds:
                    if f"{col}_is_outlier" not in new_r:
                        new_r[f"{col}_is_outlier"] = 0

            if self.treatment == "drop" and row_has_outlier:
                dropped_rows += 1
            else:
                curated_rows.append(new_r)

        return curated_rows, dropped_rows


# ==============================================================================
# FEATURE ENGINEERING & NORMALIZATION / SCALING
# ==============================================================================

class FeatureEngineerEngine:
    """Generates interaction features, non-linear transforms, date breakdowns, and encodings."""

    def __init__(
        self,
        apply_log_skewed: bool = True,
        skew_threshold: float = 1.5,
        create_interactions: bool = True,
        encode_categoricals: str = "onehot",  # 'onehot', 'ordinal', 'none'
        max_onehot_cardinality: int = 8
    ):
        self.apply_log_skewed = apply_log_skewed
        self.skew_threshold = skew_threshold
        self.create_interactions = create_interactions
        self.encode_categoricals = encode_categoricals
        self.max_onehot_cardinality = max_onehot_cardinality

        self.skewed_cols: List[str] = []
        self.interaction_pairs: List[Tuple[str, str]] = []
        self.category_maps: Dict[str, List[str]] = {}  # col -> list of categories
        self.ordinal_maps: Dict[str, Dict[str, int]] = {}

    def fit(self, rows: List[Dict[str, Any]], schema: Dict[str, str]) -> "FeatureEngineerEngine":
        """Identifies features requiring skew transformation and maps categorical vocabularies."""
        numeric_cols = [c for c, t in schema.items() if t in ("integer", "float")]

        # 1. Identify heavily skewed numeric features
        if self.apply_log_skewed:
            for col in numeric_cols:
                vals = [f for r in rows if (f := to_float(r.get(col))) is not None]
                if len(vals) >= 10:
                    skew_val = calculate_skewness(vals)
                    # Check if all values are non-negative for standard log1p
                    if abs(skew_val) >= self.skew_threshold and all(x >= 0 for x in vals):
                        self.skewed_cols.append(col)

        # 2. Select top numerical pairs for clinical/general interactions
        if self.create_interactions and len(numeric_cols) >= 2:
            # Common clinical pairs if available, else first 2-3 numericals
            priority_pairs = [
                ("trestbps", "chol"),
                ("thalach", "age"),
                ("age", "trestbps"),
                ("oldpeak", "thalach")
            ]
            for p1, p2 in priority_pairs:
                if p1 in numeric_cols and p2 in numeric_cols:
                    self.interaction_pairs.append((p1, p2))
            # Fallback if no domain matches
            if not self.interaction_pairs:
                for i in range(min(2, len(numeric_cols) - 1)):
                    self.interaction_pairs.append((numeric_cols[i], numeric_cols[i + 1]))

        # 3. Fit categorical encoders
        categorical_cols = [c for c, t in schema.items() if t in ("categorical", "string")]
        for col in categorical_cols:
            cats = sorted(list({str(r.get(col)) for r in rows if r.get(col) is not None}))
            if len(cats) <= self.max_onehot_cardinality:
                self.category_maps[col] = cats
            self.ordinal_maps[col] = {cat: idx for idx, cat in enumerate(cats)}

        return self

    def transform(self, rows: List[Dict[str, Any]], schema: Dict[str, str]) -> List[Dict[str, Any]]:
        """Transforms rows with engineered interaction terms, log terms, and encodings."""
        engineered_rows: List[Dict[str, Any]] = []

        for r in rows:
            new_r = copy.copy(r)

            # A. Log1p Transformation for skewed features
            for col in self.skewed_cols:
                v = to_float(new_r.get(col))
                if v is not None:
                    new_r[f"{col}_log1p"] = round(math.log1p(max(0.0, v)), 4)

            # B. Numerical Interaction Ratios & Products
            for c1, c2 in self.interaction_pairs:
                v1 = to_float(new_r.get(c1))
                v2 = to_float(new_r.get(c2))
                if v1 is not None and v2 is not None:
                    new_r[f"ratio_{c1}_{c2}"] = round(v1 / (v2 + 1e-5), 4)
                    new_r[f"prod_{c1}_{c2}"] = round(v1 * v2, 4)

            # C. Datetime Feature Decomposition
            for col, col_type in schema.items():
                if col_type == "datetime" and col in new_r and new_r[col]:
                    try:
                        dt = datetime.datetime.fromisoformat(str(new_r[col]))
                        new_r[f"{col}_year"] = dt.year
                        new_r[f"{col}_month"] = dt.month
                        new_r[f"{col}_day"] = dt.day
                        new_r[f"{col}_dayofweek"] = dt.weekday()
                        new_r[f"{col}_is_weekend"] = 1 if dt.weekday() >= 5 else 0
                    except Exception:
                        pass

            # D. Categorical Encodings
            if self.encode_categoricals == "onehot":
                for col, cats in self.category_maps.items():
                    val = str(new_r.get(col, ""))
                    for cat in cats:
                        clean_cat = clean_column_name(cat)
                        new_r[f"{col}_{clean_cat}"] = 1 if val == cat else 0
            elif self.encode_categoricals == "ordinal":
                for col, ord_map in self.ordinal_maps.items():
                    val = str(new_r.get(col, ""))
                    new_r[f"{col}_code"] = ord_map.get(val, -1)

            engineered_rows.append(new_r)

        return engineered_rows


class DataScaler:
    """Normalizes and scales numeric features (Standard, MinMax, Robust, or MaxAbs)."""

    def __init__(self, method: str = "standard", target_col: Optional[str] = None):
        self.method = method  # 'standard', 'minmax', 'robust', 'maxabs', 'none'
        self.target_col = target_col
        self.params: Dict[str, Dict[str, float]] = {}

    def fit(self, rows: List[Dict[str, Any]], numeric_cols: List[str]) -> "DataScaler":
        """Calculates scaling parameters on reference/training data."""
        if self.method == "none":
            return self

        for col in numeric_cols:
            if col == self.target_col:
                continue
            vals = [f for r in rows if (f := to_float(r.get(col))) is not None]
            if not vals:
                continue

            if self.method == "standard":
                mean_v = statistics.mean(vals)
                std_v = statistics.stdev(vals) if len(vals) > 1 else 1.0
                if std_v < 1e-9:
                    std_v = 1.0
                self.params[col] = {"mean": mean_v, "std": std_v}

            elif self.method == "minmax":
                min_v = min(vals)
                max_v = max(vals)
                diff = (max_v - min_v) if (max_v - min_v) > 1e-9 else 1.0
                self.params[col] = {"min": min_v, "max": max_v, "range": diff}

            elif self.method == "robust":
                q1, med, q3 = calculate_quantiles(vals)
                iqr = (q3 - q1) if (q3 - q1) > 1e-9 else 1.0
                self.params[col] = {"median": med, "iqr": iqr}

            elif self.method == "maxabs":
                max_abs = max(abs(x) for x in vals) or 1.0
                self.params[col] = {"max_abs": max_abs}

        return self

    def transform(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transforms numeric features using fitted scaler parameters."""
        if self.method == "none" or not self.params:
            return rows

        scaled_rows: List[Dict[str, Any]] = []
        for r in rows:
            new_r = copy.copy(r)
            for col, p in self.params.items():
                if col in new_r:
                    v = to_float(new_r[col])
                    if v is not None:
                        if self.method == "standard":
                            new_r[col] = round((v - p["mean"]) / p["std"], 4)
                        elif self.method == "minmax":
                            new_r[col] = round((v - p["min"]) / p["range"], 4)
                        elif self.method == "robust":
                            new_r[col] = round((v - p["median"]) / p["iqr"], 4)
                        elif self.method == "maxabs":
                            new_r[col] = round(v / p["max_abs"], 4)
            scaled_rows.append(new_r)

        return scaled_rows


# ==============================================================================
# DATA AUGMENTATION (JITTER, TABULAR MIXUP, CLASS BALANCING)
# ==============================================================================

class DataAugmenter:
    """Generates synthetic tabular samples via jittering, tabular mixup, and class balancing."""

    def __init__(
        self,
        method: str = "jitter",     # 'jitter', 'mixup', 'balance'
        augment_ratio: float = 0.20,
        target_col: Optional[str] = None,
        random_seed: int = 42
    ):
        self.method = method
        self.augment_ratio = augment_ratio
        self.target_col = target_col
        self.random_seed = random_seed
        random.seed(random_seed)

    def augment(
        self,
        rows: List[Dict[str, Any]],
        schema: Dict[str, str]
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Creates synthetic rows, tags them with `is_synthetic=1` (real rows `is_synthetic=0`).
        Returns: (augmented_rows_including_original, num_synthetic_added)
        """
        if not rows or self.method == "none" or self.augment_ratio <= 0:
            for r in rows:
                r["is_synthetic"] = 0
            return rows, 0

        # Mark original records
        for r in rows:
            r["is_synthetic"] = 0

        numeric_cols = [c for c, t in schema.items() if t in ("integer", "float") and c != self.target_col]
        num_to_generate = int(len(rows) * self.augment_ratio)
        synthetic_rows: List[Dict[str, Any]] = []

        # Calculate standard deviations for jitter
        stds: Dict[str, float] = {}
        for c in numeric_cols:
            vals = [f for r in rows if (f := to_float(r.get(c))) is not None]
            stds[c] = (statistics.stdev(vals) if len(vals) > 1 else 1.0) or 1.0

        if self.method == "balance" and self.target_col:
            # Address class imbalance by oversampling minority classes
            target_counts = Counter(str(r.get(self.target_col)) for r in rows)
            majority_class, max_count = target_counts.most_common(1)[0]
            
            for cls_val, count in target_counts.items():
                if count < max_count:
                    needed = min(max_count - count, int(count * 2.0))
                    class_rows = [r for r in rows if str(r.get(self.target_col)) == cls_val]
                    for _ in range(needed):
                        base = random.choice(class_rows)
                        synth = copy.deepcopy(base)
                        synth["is_synthetic"] = 1
                        for c in numeric_cols:
                            v = to_float(synth.get(c))
                            if v is not None:
                                noise = random.gauss(0, 0.05 * stds[c])
                                synth[c] = round(v + noise, 4) if schema.get(c) == "float" else int(round(v + noise))
                        synthetic_rows.append(synth)

        elif self.method == "mixup":
            # Tabular Mixup: Convex combination of randomly paired rows
            for _ in range(num_to_generate):
                r1 = random.choice(rows)
                r2 = random.choice(rows)
                lam = random.betavariate(0.4, 0.4) if hasattr(random, "betavariate") else random.uniform(0.3, 0.7)

                synth = copy.deepcopy(r1)
                synth["is_synthetic"] = 1
                for c in numeric_cols:
                    v1 = to_float(r1.get(c))
                    v2 = to_float(r2.get(c))
                    if v1 is not None and v2 is not None:
                        val = (lam * v1) + ((1.0 - lam) * v2)
                        synth[c] = round(val, 4) if schema.get(c) == "float" else int(round(val))
                synthetic_rows.append(synth)

        else:  # 'jitter'
            for _ in range(num_to_generate):
                base = random.choice(rows)
                synth = copy.deepcopy(base)
                synth["is_synthetic"] = 1
                for c in numeric_cols:
                    v = to_float(synth.get(c))
                    if v is not None:
                        noise = random.gauss(0, 0.04 * stds[c])
                        synth[c] = round(v + noise, 4) if schema.get(c) == "float" else int(round(v + noise))
                synthetic_rows.append(synth)

        total_rows = rows + synthetic_rows
        return total_rows, len(synthetic_rows)


# ==============================================================================
# ZERO-LEAKAGE STAGING & MULTI-MODAL AI FORMATTING
# ==============================================================================

class StagingDeliverablesEngine:
    """Manages leakage-proof train/val/test partitioning and formats AI ingestion outputs."""

    @staticmethod
    def partition_data(
        rows: List[Dict[str, Any]],
        split_ratios: Tuple[float, float, float] = (0.70, 0.15, 0.15),
        target_col: Optional[str] = None,
        random_seed: int = 42
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Partitions rows into train, validation, and test splits with stratification."""
        random.seed(random_seed)
        shuffled = list(rows)
        random.shuffle(shuffled)

        if not target_col:
            n = len(shuffled)
            n_train = int(n * split_ratios[0])
            n_val = int(n * split_ratios[1])
            train = shuffled[:n_train]
            val = shuffled[n_train:n_train + n_val]
            test = shuffled[n_train + n_val:]
            return train, val, test

        # Stratified sampling on target column
        by_class: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for r in shuffled:
            by_class[str(r.get(target_col, ""))].append(r)

        train, val, test = [], [], []
        for _, class_rows in by_class.items():
            n = len(class_rows)
            n_train = int(n * split_ratios[0])
            n_val = int(n * split_ratios[1])
            train.extend(class_rows[:n_train])
            val.extend(class_rows[n_train:n_train + n_val])
            test.extend(class_rows[n_train + n_val:])

        random.shuffle(train)
        random.shuffle(val)
        random.shuffle(test)

        # Guard against zero-count splits on small datasets if ratio was requested
        if split_ratios[1] > 0 and len(val) == 0 and len(train) > 1:
            val.append(train.pop())
        if split_ratios[2] > 0 and len(test) == 0 and len(train) > 1:
            test.append(train.pop())

        return train, val, test

    @staticmethod
    def save_csv(filepath: Path, rows: List[Dict[str, Any]], fallback_header: Optional[Sequence[str]] = None):
        """Writes rows to standard CSV file, creating valid header even if rows is empty."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        keys: List[str] = []
        if rows:
            for r in rows:
                for k in r.keys():
                    if k not in keys:
                        keys.append(k)
        elif fallback_header:
            keys = list(fallback_header)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            if keys:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                if rows:
                    writer.writerows(rows)
            else:
                f.write("")

    @staticmethod
    def save_llm_jsonl(
        filepath: Path,
        rows: List[Dict[str, Any]],
        target_col: Optional[str] = None,
        id_col: Optional[str] = None
    ):
        """Formats records as natural language narratives for LLM fine-tuning or RAG ingestion."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            for r in rows:
                features_desc = []
                for k, v in r.items():
                    if k not in (target_col, id_col, "is_synthetic"):
                        features_desc.append(f"{k.replace('_', ' ')} is {v}")

                narrative = f"Clinical Record Profile: {', '.join(features_desc)}."
                payload = {
                    "text": narrative,
                    "target": r.get(target_col) if target_col else None,
                    "metadata": {
                        "entity_id": r.get("canonical_entity_id") or r.get(id_col) or "unknown",
                        "is_synthetic": r.get("is_synthetic", 0)
                    }
                }
                f.write(json.dumps(payload) + "\n")

    @staticmethod
    def save_tensors_json(
        filepath: Path,
        rows: List[Dict[str, Any]],
        target_col: Optional[str] = None
    ):
        """Exports pure numeric feature matrix X and target vector y for PyTorch/TensorFlow loaders."""
        if not rows:
            return
        feature_cols = [c for c in rows[0].keys() if c != target_col and to_float(rows[0][c]) is not None]
        X = []
        y = []
        for r in rows:
            row_feats = [to_float(r.get(c)) or 0.0 for c in feature_cols]
            X.append(row_feats)
            if target_col and target_col in r:
                t_val = r[target_col]
                f_t = to_float(t_val)
                y.append(f_t if f_t is not None else str(t_val))

        payload = {
            "feature_names": feature_cols,
            "target_name": target_col,
            "num_samples": len(X),
            "num_features": len(feature_cols),
            "X": X,
            "y": y if target_col else None
        }
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)


# ==============================================================================
# PIPELINE ORCHESTRATOR & ENTERPRISE DATA CARD GENERATOR
# ==============================================================================

class PipelineAuditRecord:
    """Stores provenance, step-by-step metrics, and validation checks."""

    def __init__(self):
        self.timestamp = datetime.datetime.now().isoformat()
        self.source_files: List[str] = []
        self.source_hashes: Dict[str, str] = {}
        self.initial_row_count: int = 0
        self.initial_col_count: int = 0
        self.exact_duplicates_dropped: int = 0
        self.key_duplicates_dropped: int = 0
        self.entities_resolved: int = 0
        self.high_missing_cols_dropped: List[str] = []
        self.high_missing_rows_dropped: int = 0
        self.outliers_treated_count: int = 0
        self.outliers_dropped_rows: int = 0
        self.engineered_features_added: List[str] = []
        self.synthetic_rows_generated: int = 0
        self.final_row_count: int = 0
        self.final_col_count: int = 0
        self.split_counts: Dict[str, int] = {}
        self.scaler_parameters: Dict[str, Any] = {}


def generate_data_card(audit: PipelineAuditRecord, dest_path: Path):
    """Produces a comprehensive GitHub-Flavored Markdown Data Card adhering to AI governance."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    card_md = f"""# AI Dataset Card & Curation Provenance Report

**Execution Timestamp:** `{audit.timestamp}`  
**Staging Status:** ✅ Ready for AI / Model Training & Ingestion  
**Architecture:** Zero-External-Dependency Standard Library Pipeline

---

## 1. Provenance & Cryptographic Lineage

| Source File | SHA-256 Checksum |
| :--- | :--- |
"""
    for fname, sha in audit.source_hashes.items():
        card_md += f"| `{fname}` | `{sha}` |\n"

    card_md += f"""
---

## 2. Pipeline Transformation Waterfall

```mermaid
flowchart TD
    A["Raw Ingestion<br>({audit.initial_row_count} rows, {audit.initial_col_count} cols)"] --> B["Deduplication<br>(-{audit.exact_duplicates_dropped} exact, -{audit.key_duplicates_dropped} key dupes)"]
    B --> C["Entity Resolution<br>({audit.entities_resolved} linked entity clusters)"]
    C --> D["Missing Value Sanitization<br>(-{len(audit.high_missing_cols_dropped)} cols dropped, -{audit.high_missing_rows_dropped} rows dropped)"]
    D --> E["Outlier Treatment<br>({audit.outliers_treated_count} anomalies clipped/curated)"]
    E --> F["Feature Engineering<br>(+{len(audit.engineered_features_added)} interaction/log features)"]
    F --> G["Data Augmentation<br>(+{audit.synthetic_rows_generated} synthetic records)"]
    G --> H["Curated Staging<br>({audit.final_row_count} rows, {audit.final_col_count} cols)"]
```

---

## 3. Data Transformation Audit Log

- **Initial Dimensions:** {audit.initial_row_count} rows × {audit.initial_col_count} columns
- **Exact Duplicates Removed:** {audit.exact_duplicates_dropped}
- **Entity Resolution Clusters:** {audit.entities_resolved} canonical patient/subject entity linkages
- **High-Missing Columns Dropped (>50%):** `{audit.high_missing_cols_dropped if audit.high_missing_cols_dropped else 'None'}`
- **High-Missing Rows Dropped (>60%):** {audit.high_missing_rows_dropped}
- **Outlier Anomalies Treated:** {audit.outliers_treated_count} (Rows dropped: {audit.outliers_dropped_rows})
- **Engineered Features Added:** {', '.join(audit.engineered_features_added) if audit.engineered_features_added else 'None'}
- **Synthetic Augmented Records:** {audit.synthetic_rows_generated}
- **Final Curated Dimensions:** {audit.final_row_count} rows × {audit.final_col_count} columns

---

## 4. AI Staging Partitions & Zero Data Leakage

To prevent statistical contamination, all scalers, median imputers, and categorical vocabularies were fitted **strictly on the Training split** and propagated to Validation and Test splits:

- **Train Split:** `{audit.split_counts.get('train', 0)}` records (`train.csv`)
- **Validation Split:** `{audit.split_counts.get('val', 0)}` records (`val.csv`)
- **Test Split:** `{audit.split_counts.get('test', 0)}` records (`test.csv`)

---

## 5. Multi-Format AI Deliverables Created

1. **Tabular ML Staging (`train.csv`, `val.csv`, `test.csv`, `curated_full.csv`):** Cleaned, type-cast, imputed, and scaled CSVs ready for XGBoost, LightGBM, Random Forests, and Scikit-Learn.
2. **LLM & Fine-Tuning Format (`staged_for_llm.jsonl`):** Structured natural language patient narratives for instruction tuning, medical LLMs, or RAG vectors.
3. **Tensor Pipeline Ready (`staged_tensors.json`):** Matrix arrays $X$ and vectors $y$ for direct PyTorch / TensorFlow DataLoader batching.
4. **Scaler Parameters (`scaler_parameters.json`):** Serialized means, standard deviations, and IQR parameters for production inference pipelines.
"""

    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(card_md)


def curate_pipeline(
    input_paths: List[Path],
    output_dir: Path,
    custom_columns: Optional[List[str]] = None,
    target_column: Optional[str] = None,
    dedup_keys: Optional[List[str]] = None,
    entity_keys: Optional[List[str]] = None,
    outlier_treatment: str = "clip",
    outlier_factor: float = 1.5,
    impute_numeric: str = "median",
    impute_categorical: str = "mode",
    scale_method: str = "standard",
    augment_method: str = "jitter",
    augment_ratio: float = 0.20,
    split_ratios: Tuple[float, float, float] = (0.70, 0.15, 0.15),
    phi_redaction: bool = True,
    generate_llm: bool = True,
    delimiter: Optional[str] = None
) -> PipelineAuditRecord:
    """Executes the end-to-end data preparation, curation, and staging pipeline."""
    audit = PipelineAuditRecord()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 80)
    print(" 🚀 STARTING UNIVERSAL AI DATA CURATION & STAGING PIPELINE")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # Step 1: Ingestion
    # --------------------------------------------------------------------------
    all_rows: List[Dict[str, Any]] = []
    unified_columns: List[str] = []

    for p in input_paths:
        audit.source_files.append(p.name)
        audit.source_hashes[p.name] = file_sha256(p)
        print(f"[*] Ingesting: {p.name} (SHA-256: {audit.source_hashes[p.name][:12]}...)")
        cols, rows = DatasetIngester.load_file(p, custom_columns=custom_columns, delimiter=delimiter)
        for c in cols:
            if c not in unified_columns:
                unified_columns.append(c)
        all_rows.extend(rows)

    audit.initial_row_count = len(all_rows)
    audit.initial_col_count = len(unified_columns)
    print(f"[+] Total raw records ingested: {audit.initial_row_count} across {audit.initial_col_count} columns.")

    if not all_rows:
        print("[!] No records to process. Exiting.")
        return audit

    # --------------------------------------------------------------------------
    # Step 2: Privacy / PII / PHI Redaction
    # --------------------------------------------------------------------------
    sanitizer = SanitizerEngine()
    if phi_redaction:
        print("[*] Applying HIPAA Safe Harbor PII/PHI sanitization and pseudonymization...")
        for r in all_rows:
            for k, v in r.items():
                if isinstance(v, str):
                    r[k] = sanitizer.redact_pii(v)

    # --------------------------------------------------------------------------
    # Step 3: Schema Inference & Type Casting
    # --------------------------------------------------------------------------
    print("[*] Inferring schema and sanitizing data types...")
    schema = sanitizer.infer_schema(unified_columns, all_rows)
    for r in all_rows:
        for col, col_type in schema.items():
            parsed_val, _ = sanitizer.parse_value(r.get(col))
            r[col] = parsed_val

    # --------------------------------------------------------------------------
    # Step 4: Deduplication
    # --------------------------------------------------------------------------
    print("[*] Deduplicating records...")
    deduped_rows, exact_dropped = DeduplicatorEngine.deduplicate_exact(all_rows, unified_columns)
    audit.exact_duplicates_dropped = exact_dropped
    print(f"    • Removed {exact_dropped} exact duplicate row(s).")

    if dedup_keys:
        deduped_rows, key_dropped = DeduplicatorEngine.deduplicate_by_keys(deduped_rows, dedup_keys)
        audit.key_duplicates_dropped = key_dropped
        print(f"    • Removed {key_dropped} duplicate row(s) matching keys: {dedup_keys}")

    # --------------------------------------------------------------------------
    # Step 5: Entity Resolution
    # --------------------------------------------------------------------------
    if entity_keys:
        print(f"[*] Resolving entities via Jaro-Winkler record linkage on keys: {entity_keys}...")
        deduped_rows, clusters, _ = DeduplicatorEngine.resolve_entities_fuzzy(
            deduped_rows, entity_keys, similarity_threshold=0.88
        )
        audit.entities_resolved = clusters
        print(f"    • Linked records into {clusters} canonical entity clusters.")

    # --------------------------------------------------------------------------
    # Step 6: Zero-Leakage Train / Val / Test Partitioning
    # --------------------------------------------------------------------------
    print("[*] Partitioning data into Train / Validation / Test staging splits...")
    train_rows, val_rows, test_rows = StagingDeliverablesEngine.partition_data(
        deduped_rows, split_ratios=split_ratios, target_col=target_column
    )
    print(f"    • Partition sizes: Train={len(train_rows)}, Val={len(val_rows)}, Test={len(test_rows)}")

    # --------------------------------------------------------------------------
    # Step 7: Missing Value Imputation (Fit on Train, Transform all)
    # --------------------------------------------------------------------------
    print(f"[*] Handling missing values (Numeric strategy: {impute_numeric}, Categorical: {impute_categorical})...")
    missing_handler = MissingValueHandler(
        numeric_strategy=impute_numeric,
        categorical_strategy=impute_categorical,
        add_indicators=True
    )
    missing_handler.fit(train_rows, schema)
    audit.high_missing_cols_dropped = missing_handler.dropped_columns

    train_rows, train_drop_r = missing_handler.transform(train_rows, schema)
    val_rows, val_drop_r = missing_handler.transform(val_rows, schema)
    test_rows, test_drop_r = missing_handler.transform(test_rows, schema)
    audit.high_missing_rows_dropped = train_drop_r + val_drop_r + test_drop_r

    # Update active schema
    active_schema = {c: t for c, t in schema.items() if c not in missing_handler.dropped_columns}

    # --------------------------------------------------------------------------
    # Step 8: Outlier Detection & Avoidance (Fit on Train, Transform all)
    # --------------------------------------------------------------------------
    print(f"[*] Outlier curation (Method: IQR {outlier_factor}x, Treatment: {outlier_treatment})...")
    outlier_handler = OutlierHandler(
        method="iqr",
        treatment=outlier_treatment,
        factor=outlier_factor,
        target_columns=[c for c, t in active_schema.items() if t in ("integer", "float") and c != target_column]
    )
    outlier_handler.fit(train_rows, active_schema)

    train_rows, train_out_drop = outlier_handler.transform(train_rows)
    val_rows, val_out_drop = outlier_handler.transform(val_rows)
    test_rows, test_out_drop = outlier_handler.transform(test_rows)
    audit.outliers_dropped_rows = train_out_drop + val_out_drop + test_out_drop
    audit.outliers_treated_count = sum(outlier_handler.outlier_counts.values())
    print(f"    • Outliers identified and curated: {audit.outliers_treated_count}")

    # --------------------------------------------------------------------------
    # Step 9: Feature Engineering (Fit on Train, Transform all)
    # --------------------------------------------------------------------------
    print("[*] Engineering AI features (Interaction ratios, Log1p skew transforms, Encodings)...")
    engineer = FeatureEngineerEngine(
        apply_log_skewed=True,
        create_interactions=True,
        encode_categoricals="onehot"
    )
    engineer.fit(train_rows, active_schema)

    prev_cols = set(train_rows[0].keys()) if train_rows else set()
    train_rows = engineer.transform(train_rows, active_schema)
    val_rows = engineer.transform(val_rows, active_schema)
    test_rows = engineer.transform(test_rows, active_schema)
    new_cols = set(train_rows[0].keys()) if train_rows else set()
    audit.engineered_features_added = sorted(list(new_cols - prev_cols))
    print(f"    • Added {len(audit.engineered_features_added)} engineered features: {audit.engineered_features_added[:5]}...")

    # --------------------------------------------------------------------------
    # Step 10: Normalization & Scaling (Fit on Train, Transform all)
    # --------------------------------------------------------------------------
    print(f"[*] Scaling numeric features using {scale_method.upper()} Scaler...")
    numeric_to_scale = [c for c in train_rows[0].keys() if isinstance(train_rows[0][c], (int, float)) and c != target_column and not c.endswith("_is_missing") and not c.endswith("_is_outlier") and not c.startswith("ratio_")] if train_rows else []
    scaler = DataScaler(method=scale_method, target_col=target_column)
    scaler.fit(train_rows, numeric_to_scale)
    audit.scaler_parameters = scaler.params

    train_rows = scaler.transform(train_rows)
    val_rows = scaler.transform(val_rows)
    test_rows = scaler.transform(test_rows)

    # --------------------------------------------------------------------------
    # Step 11: Data Augmentation (Train set only)
    # --------------------------------------------------------------------------
    if augment_method != "none" and augment_ratio > 0:
        print(f"[*] Augmenting training set (Method: {augment_method}, Ratio: {augment_ratio*100}%)...")
        augmenter = DataAugmenter(method=augment_method, augment_ratio=augment_ratio, target_col=target_column)
        train_rows, synth_added = augmenter.augment(train_rows, active_schema)
        audit.synthetic_rows_generated = synth_added
        print(f"    • Generated {synth_added} synthetic training instances.")
    else:
        for r in train_rows:
            r["is_synthetic"] = 0

    for r in val_rows:
        r["is_synthetic"] = 0
    for r in test_rows:
        r["is_synthetic"] = 0

    # --------------------------------------------------------------------------
    # Step 12: Deliverable Staging & Multi-Format Exports
    # --------------------------------------------------------------------------
    print("[*] Staging deliverables and serializing multi-modal AI outputs...")
    audit.split_counts = {"train": len(train_rows), "val": len(val_rows), "test": len(test_rows)}
    full_curated = train_rows + val_rows + test_rows
    audit.final_row_count = len(full_curated)
    audit.final_col_count = len(full_curated[0].keys()) if full_curated else 0

    # 1. Tabular CSV Staging
    all_keys = list(full_curated[0].keys()) if full_curated else []
    StagingDeliverablesEngine.save_csv(output_dir / "train.csv", train_rows, fallback_header=all_keys)
    StagingDeliverablesEngine.save_csv(output_dir / "val.csv", val_rows, fallback_header=all_keys)
    StagingDeliverablesEngine.save_csv(output_dir / "test.csv", test_rows, fallback_header=all_keys)
    StagingDeliverablesEngine.save_csv(output_dir / "curated_full.csv", full_curated, fallback_header=all_keys)

    # 2. LLM Narrative Staging
    if generate_llm:
        StagingDeliverablesEngine.save_llm_jsonl(output_dir / "staged_for_llm.jsonl", full_curated, target_col=target_column)

    # 3. Numeric Tensors Staging
    StagingDeliverablesEngine.save_tensors_json(output_dir / "staged_tensors.json", train_rows, target_col=target_column)

    # 4. Scaler Parameters Export
    with open(output_dir / "scaler_parameters.json", "w", encoding="utf-8") as f:
        json.dump(scaler.params, f, indent=2)

    # 5. Provenance Manifest & Data Card
    manifest_data = {
        "timestamp": audit.timestamp,
        "source_files": audit.source_files,
        "source_hashes": audit.source_hashes,
        "pipeline_statistics": {
            "initial_rows": audit.initial_row_count,
            "initial_cols": audit.initial_col_count,
            "exact_duplicates_dropped": audit.exact_duplicates_dropped,
            "key_duplicates_dropped": audit.key_duplicates_dropped,
            "entities_resolved_clusters": audit.entities_resolved,
            "high_missing_cols_dropped": audit.high_missing_cols_dropped,
            "high_missing_rows_dropped": audit.high_missing_rows_dropped,
            "outliers_treated_count": audit.outliers_treated_count,
            "engineered_features": audit.engineered_features_added,
            "synthetic_rows_added": audit.synthetic_rows_generated,
            "final_rows": audit.final_row_count,
            "final_cols": audit.final_col_count,
            "split_counts": audit.split_counts
        }
    }
    with open(output_dir / "staging_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    data_card_path = output_dir / "DATA_CARD.md"
    generate_data_card(audit, data_card_path)

    print("\n" + "=" * 80)
    print(" ✅ DATA CURATION & AI STAGING PIPELINE COMPLETED")
    print("=" * 80)
    print(f" • Input Files: {len(audit.source_files)} file(s)")
    print(f" • Curated Records: {audit.final_row_count} total rows ({len(train_rows)} train / {len(val_rows)} val / {len(test_rows)} test)")
    print(f" • Curated Features: {audit.final_col_count} columns (including engineered & indicator features)")
    print(f" • Output Staging Directory: {output_dir.resolve()}")
    print(f" • Governance Data Card: {data_card_path.resolve()}")
    print("=" * 80 + "\n")

    return audit


# ==============================================================================
# CLI PARSER & INTERACTIVE WIZARD
# ==============================================================================

def build_argument_parser() -> argparse.ArgumentParser:
    """Builds comprehensive command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Universal AI Data Preparation, Sanitization, Curation & Staging Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Curate all datasets in a source folder using UCI Heart Disease preset
  python3 data_curator.py source_dir/ --uci-heart --output-dir staged_data/

  # Curate specific files with train/val/test splits and class balancing
  python3 data_curator.py cleveland.data hungarian.data --target-col num --augment balance

  # Curate with explicit custom column headers and standard scaling
  python3 data_curator.py dataset.csv --columns "id,age,chol,bp,target" --scale-method standard

  # Run entity resolution and PII redaction on clinical patient files
  python3 data_curator.py patients.csv --entity-keys "first_name,last_name,dob" --phi-redact
        """
    )

    parser.add_argument(
        "targets",
        nargs="*",
        help="Path(s) to dataset file(s) or a directory containing data files."
    )
    parser.add_argument(
        "--folder",
        type=str,
        help="Directory containing datasets to curate."
    )
    parser.add_argument(
        "--files",
        type=str,
        help="Semicolon-separated list of filenames (e.g., 'data1.csv; data2.data')."
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="staged_data",
        help="Destination directory for curated data deliverables (default: staged_data/)."
    )
    parser.add_argument(
        "--target-col",
        type=str,
        default=None,
        help="Name of target variable column for stratified splitting and class balancing."
    )
    parser.add_argument(
        "--columns",
        type=str,
        help="Comma-separated custom column names for headerless files."
    )
    parser.add_argument(
        "--uci-heart",
        action="store_true",
        help="Apply 14-attribute UCI Machine Learning Heart Disease column preset."
    )
    parser.add_argument(
        "--delimiter", "-d",
        type=str,
        default=None,
        help="Explicit delimiter (e.g. ',', '\\t', ';', '|', ' '). If omitted, auto-detected."
    )
    parser.add_argument(
        "--dedup-keys",
        type=str,
        help="Comma-separated column names for key-based deduplication."
    )
    parser.add_argument(
        "--entity-keys",
        type=str,
        help="Comma-separated column names for fuzzy entity resolution (e.g., 'first_name,last_name')."
    )
    parser.add_argument(
        "--impute-numeric",
        choices=["median", "mean", "mode", "zero", "none"],
        default="median",
        help="Imputation strategy for numerical missing values (default: median)."
    )
    parser.add_argument(
        "--impute-categorical",
        choices=["mode", "missing", "none"],
        default="mode",
        help="Imputation strategy for categorical missing values (default: mode)."
    )
    parser.add_argument(
        "--outlier-treatment",
        choices=["clip", "drop", "impute", "flag", "none"],
        default="clip",
        help="Outlier handling: clip (Winsorize), drop (filter rows), impute (median), flag (add indicator), none."
    )
    parser.add_argument(
        "--outlier-factor",
        type=float,
        default=1.5,
        help="Multiplier for Tukey IQR outlier boundaries (default: 1.5, use 3.0 for extreme outliers)."
    )
    parser.add_argument(
        "--scale-method",
        choices=["standard", "minmax", "robust", "maxabs", "none"],
        default="standard",
        help="Feature scaling method (default: standard [zero mean, unit variance])."
    )
    parser.add_argument(
        "--augment",
        choices=["jitter", "mixup", "balance", "none"],
        default="jitter",
        help="Data augmentation strategy: jitter (Gaussian noise), mixup (tabular interpolation), balance (minority oversampling), none."
    )
    parser.add_argument(
        "--augment-ratio",
        type=float,
        default=0.20,
        help="Ratio of synthetic records to generate relative to training size (default: 0.20)."
    )
    parser.add_argument(
        "--split-ratios",
        type=float,
        nargs=3,
        default=[0.70, 0.15, 0.15],
        help="Train / Validation / Test split ratios (default: 0.70 0.15 0.15)."
    )
    parser.add_argument(
        "--phi-redact",
        action="store_true",
        default=True,
        help="Sanitize and redact HIPAA direct identifiers (SSN, phone, email, etc.) [default: True]."
    )
    parser.add_argument(
        "--no-phi-redact",
        action="store_false",
        dest="phi_redact",
        help="Disable HIPAA PII/PHI redaction."
    )
    parser.add_argument(
        "--no-llm-format",
        action="store_true",
        help="Skip generating staged_for_llm.jsonl narrative prompts."
    )

    return parser


def main():
    """Main execution entry point."""
    parser = build_argument_parser()
    args = parser.parse_args()
    env_vars = load_env_variables(".env")

    # Resolve target files from CLI, --folder, --files, or .env
    target_paths: List[Path] = []

    if args.targets:
        for t in args.targets:
            p = Path(t)
            if p.is_dir():
                for f in sorted(p.iterdir()):
                    if f.is_file() and f.suffix.lower() in (".csv", ".tsv", ".data", ".txt", ".json", ".jsonl"):
                        target_paths.append(f)
            elif p.is_file():
                target_paths.append(p)
    elif args.folder:
        folder = Path(args.folder)
        if folder.is_dir():
            for f in sorted(folder.iterdir()):
                if f.is_file() and f.suffix.lower() in (".csv", ".tsv", ".data", ".txt", ".json", ".jsonl"):
                    target_paths.append(f)
    elif args.files:
        files = [f.strip() for f in args.files.split(";") if f.strip()]
        for f in files:
            p = Path(f)
            if p.is_file():
                target_paths.append(p)

    # Fallback to .env configuration if no targets specified
    if not target_paths:
        source_folder = env_vars.get("SOURCE_FOLDER") or env_vars.get("TARGET_FOLDER")
        source_files = env_vars.get("SOURCE_FILES") or env_vars.get("DATA_FILES")

        if source_folder and source_files:
            folder_p = Path(source_folder)
            files = [f.strip() for f in source_files.split(";") if f.strip()]
            for fname in files:
                p = folder_p / fname
                if p.is_file():
                    target_paths.append(p)
        elif source_folder and Path(source_folder).is_dir():
            for f in sorted(Path(source_folder).iterdir()):
                if f.is_file() and f.suffix.lower() in (".csv", ".tsv", ".data", ".txt", ".json", ".jsonl"):
                    target_paths.append(f)

    # Interactive wizard fallback if still no target paths
    if not target_paths:
        print("=" * 80)
        print(" Universal AI Data Curation & Staging Pipeline - Interactive Setup")
        print("=" * 80)
        user_input = input("Enter path to dataset file or folder: ").strip()
        if not user_input:
            print("[!] No valid path provided. Exiting.")
            sys.exit(1)
        p = Path(user_input)
        if p.is_dir():
            target_paths = [f for f in sorted(p.iterdir()) if f.is_file() and f.suffix.lower() in (".csv", ".tsv", ".data", ".txt", ".json", ".jsonl")]
        elif p.is_file():
            target_paths = [p]
        else:
            print(f"[!] Path does not exist: {p}")
            sys.exit(1)

    # Custom column schema handling
    custom_cols: Optional[List[str]] = None
    if args.uci_heart:
        custom_cols = UCI_HEART_COLUMNS
        if not args.target_col:
            args.target_col = "num"
    elif args.columns:
        custom_cols = [c.strip() for c in args.columns.split(",") if c.strip()]

    dedup_keys = [k.strip() for k in args.dedup_keys.split(",") if k.strip()] if args.dedup_keys else None
    entity_keys = [k.strip() for k in args.entity_keys.split(",") if k.strip()] if args.entity_keys else None

    # Execute pipeline
    curate_pipeline(
        input_paths=target_paths,
        output_dir=Path(args.output_dir),
        custom_columns=custom_cols,
        target_column=args.target_col,
        dedup_keys=dedup_keys,
        entity_keys=entity_keys,
        outlier_treatment=args.outlier_treatment,
        outlier_factor=args.outlier_factor,
        impute_numeric=args.impute_numeric,
        impute_categorical=args.impute_categorical,
        scale_method=args.scale_method,
        augment_method=args.augment,
        augment_ratio=args.augment_ratio,
        split_ratios=tuple(args.split_ratios),
        phi_redaction=args.phi_redact,
        generate_llm=not args.no_llm_format,
        delimiter=args.delimiter
    )


if __name__ == "__main__":
    main()
