# 📊 Data Profile & Exploratory Analysis Report
**Target Dataset:** `hungarian.data`  
**Analysis Date:** 2026-10-29 01:19:03  
**File Size:** 60.73 KB  
**Data Health Score:** `73.9/100.0`

---
## 1. Executive Summary

| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 2,940 | **Total Columns** | 7 |
| **Duplicate Rows** | 1,092 (37.14%) | **Total Cells** | 20,580 |
| **Missing Data Cells** | 7,713 (37.48%) | **Health Score** | 73.9 / 100 |

---

## 2. Column Inventory & Data Schema

| # | Column Name | Inferred Type | Missing Count (%) | Distinct Values | Notes & Flags |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | **col_01** | `Float` | 881 (30.0%) | 400 | `HIGH NULLS`, `294 Outliers` |
| 2 | **col_02** | `Integer` | 1030 (35.0%) | 60 | `HIGH NULLS` |
| 3 | **col_03** | `Float` | 879 (29.9%) | 140 | `HIGH NULLS` |
| 4 | **col_04** | `Float` | 790 (26.9%) | 58 | `HIGH NULLS`, `316 Outliers` |
| 5 | **col_05** | `Text` | 1095 (37.2%) | 195 | `HIGH NULLS` |
| 6 | **col_06** | `Float` | 1396 (47.5%) | 59 | `HIGH NULLS`, `292 Outliers` |
| 7 | **col_07** | `Float` | 1642 (55.9%) | 36 | `HIGH NULLS`, `295 Outliers` |

---

## 3. Numerical Features Statistical Summary

| Column | Mean | Std Dev | Min | 25% (Q1) | Median | 75% (Q3) | Max | IQR | Skewness | Outliers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **col_01** | 193.34 | 438.48 | 0.00 | 0.00 | 1.00 | 122.00 | 5002.00 | 122.00 | 3.41 | 294 (14.3%) |
| **col_02** | 26.33 | 38.36 | 0.00 | 0.00 | 2.00 | 74.00 | 134.00 | 74.00 | 0.92 | 0 (0.0%) |
| **col_03** | 53.18 | 70.07 | -9.00 | 0.00 | 14.00 | 120.00 | 240.00 | 120.00 | 0.97 | 0 (0.0%) |
| **col_04** | 13.94 | 33.39 | -9.00 | 0.00 | 0.00 | 8.00 | 134.00 | 8.00 | 2.06 | 316 (14.7%) |
| **col_06** | 21.36 | 31.62 | 0.00 | 1.00 | 7.00 | 21.00 | 110.00 | 20.00 | 1.46 | 292 (18.9%) |
| **col_07** | 20.39 | 35.20 | 0.00 | 0.00 | 1.00 | 10.00 | 87.00 | 10.00 | 1.29 | 295 (22.7%) |

---

## 4. Categorical & Text Distributions

| Column | Distinct Values | Dominant Class (%) | Top Most Frequent Values (Count, %) |
| :--- | :--- | :--- | :--- |
| **col_05** | 195 | 16.6% | `1`: 306 (16.6%), `name`: 294 (15.9%), `2`: 100 (5.4%), `100`: 77 (4.2%) |

---

## 5. Noticeable Trends & Associations

### 🔗 Notable Pearson Correlations

| Feature 1 | Feature 2 | Correlation ($r$) | Relationship | Strength |
| :--- | :--- | :--- | :--- | :--- |
| `col_04` | `col_06` | `+0.963` | Positive | Strong |
| `col_02` | `col_04` | `+0.922` | Positive | Strong |
| `col_03` | `col_06` | `+0.900` | Positive | Strong |
| `col_02` | `col_06` | `+0.840` | Positive | Strong |
| `col_03` | `col_04` | `+0.735` | Positive | Strong |
| `col_01` | `col_07` | `-0.455` | Negative | Moderate |
| `col_04` | `col_07` | `-0.412` | Negative | Moderate |


## 6. Actionable First-Review Recommendations

- ⚠️ **Duplicate Rows Detected**: Found 1092 exact duplicate row(s) (37.1%). Consider deduping with `.drop_duplicates()`.
- ⚠️ **High Missingness (>20%)**: Columns ['col_01', 'col_02', 'col_03', 'col_04', 'col_05', 'col_06', 'col_07'] contain substantial missing data. Verify collection integrity or consider imputation/dropping.
- 💡 **Outlier Hotspots**: Columns ['col_01', 'col_04', 'col_06', 'col_07'] exhibit >= 5% Tukey outliers. Inspect whether these represent clinical anomalies, extreme events, or data entry errors.
- 💡 **Heavy Skewness**: Features ['col_01', 'col_04'] are heavily skewed (|skew| >= 1.5). Consider applying Log or Power transformations prior to linear modeling.
- ⚠️ **Multicollinearity Alert**: Very strong correlations found: col_04 & col_06 (r=0.96), col_02 & col_04 (r=0.92), col_03 & col_06 (r=0.90). Consider feature selection or PCA to avoid redundant predictors.

---

*Report generated automatically by `data_profiler.py`.*