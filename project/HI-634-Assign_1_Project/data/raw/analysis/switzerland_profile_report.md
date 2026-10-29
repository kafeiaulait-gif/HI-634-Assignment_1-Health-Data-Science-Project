# 📊 Data Profile & Exploratory Analysis Report
**Target Dataset:** `switzerland.data`  
**Analysis Date:** 2026-10-29 01:36:10  
**File Size:** 24.10 KB  
**Data Health Score:** `81.0/100.0`

---
## 1. Executive Summary

| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 1,230 | **Total Columns** | 7 |
| **Duplicate Rows** | 333 (27.07%) | **Total Cells** | 8,610 |
| **Missing Data Cells** | 2,351 (27.31%) | **Health Score** | 81.0 / 100 |

---

## 2. Column Inventory & Data Schema

| # | Column Name | Inferred Type | Missing Count (%) | Distinct Values | Notes & Flags |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | **col_01** | `Float` | 356 (28.9%) | 253 | `HIGH NULLS`, `123 Outliers` |
| 2 | **col_02** | `Integer` | 281 (22.8%) | 56 | `HIGH NULLS`, `236 Outliers` |
| 3 | **col_03** | `Float` | 327 (26.6%) | 94 | `HIGH NULLS` |
| 4 | **col_04** | `Float` | 167 (13.6%) | 38 | `341 Outliers` |
| 5 | **col_05** | `Categorical` | 222 (18.0%) | 34 | - |
| 6 | **col_06** | `Float` | 464 (37.7%) | 52 | `HIGH NULLS`, `121 Outliers` |
| 7 | **col_07** | `Float` | 534 (43.4%) | 41 | `HIGH NULLS`, `138 Outliers` |

---

## 3. Numerical Features Statistical Summary

| Column | Mean | Std Dev | Min | 25% (Q1) | Median | 75% (Q3) | Max | IQR | Skewness | Outliers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **col_01** | 529.84 | 1268.20 | -2.60 | 1.00 | 1.00 | 100.00 | 4074.00 | 99.00 | 2.15 | 123 (14.1%) |
| **col_02** | 20.20 | 33.25 | 0.00 | 1.00 | 2.00 | 4.00 | 110.00 | 3.00 | 1.26 | 236 (24.9%) |
| **col_03** | 55.57 | 62.74 | -9.00 | 1.00 | 45.00 | 105.00 | 230.00 | 104.00 | 0.83 | 0 (0.0%) |
| **col_04** | 10.16 | 27.69 | -9.00 | 0.00 | 1.00 | 2.00 | 115.00 | 2.00 | 2.40 | 341 (32.1%) |
| **col_06** | 17.17 | 29.15 | 0.00 | 1.00 | 2.00 | 14.00 | 120.00 | 13.00 | 1.80 | 121 (15.8%) |
| **col_07** | 16.57 | 31.65 | 0.00 | 1.00 | 1.00 | 6.00 | 85.00 | 5.00 | 1.66 | 138 (19.8%) |

---

## 4. Categorical & Text Distributions

| Column | Distinct Values | Dominant Class (%) | Top Most Frequent Values (Count, %) |
| :--- | :--- | :--- | :--- |
| **col_05** | 34 | 30.8% | `1`: 310 (30.8%), `0`: 155 (15.4%), `2`: 138 (13.7%), `name`: 123 (12.2%) |

---

## 5. Noticeable Trends & Associations

### 🔗 Notable Pearson Correlations

| Feature 1 | Feature 2 | Correlation ($r$) | Relationship | Strength |
| :--- | :--- | :--- | :--- | :--- |
| `col_04` | `col_06` | `+0.961` | Positive | Strong |
| `col_03` | `col_06` | `+0.853` | Positive | Strong |
| `col_03` | `col_04` | `+0.683` | Positive | Moderate |
| `col_02` | `col_04` | `+0.557` | Positive | Moderate |
| `col_02` | `col_06` | `+0.493` | Positive | Moderate |


## 6. Actionable First-Review Recommendations

- ⚠️ **Duplicate Rows Detected**: Found 333 exact duplicate row(s) (27.1%). Consider deduping with `.drop_duplicates()`.
- ⚠️ **High Missingness (>20%)**: Columns ['col_01', 'col_02', 'col_03', 'col_06', 'col_07'] contain substantial missing data. Verify collection integrity or consider imputation/dropping.
- 💡 **Outlier Hotspots**: Columns ['col_01', 'col_02', 'col_04', 'col_06', 'col_07'] exhibit >= 5% Tukey outliers. Inspect whether these represent clinical anomalies, extreme events, or data entry errors.
- 💡 **Heavy Skewness**: Features ['col_01', 'col_04', 'col_06', 'col_07'] are heavily skewed (|skew| >= 1.5). Consider applying Log or Power transformations prior to linear modeling.
- ⚠️ **Multicollinearity Alert**: Very strong correlations found: col_04 & col_06 (r=0.96), col_03 & col_06 (r=0.85). Consider feature selection or PCA to avoid redundant predictors.

---

*Report generated automatically by `data_profiler.py`.*