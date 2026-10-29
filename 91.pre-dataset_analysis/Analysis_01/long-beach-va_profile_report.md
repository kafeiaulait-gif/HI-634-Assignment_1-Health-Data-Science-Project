# 📊 Data Profile & Exploratory Analysis Report
**Target Dataset:** `long-beach-va.data`  
**Analysis Date:** 2026-10-29 01:19:04  
**File Size:** 38.96 KB  
**Data Health Score:** `79.8/100.0`

---
## 1. Executive Summary

| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 2,000 | **Total Columns** | 7 |
| **Duplicate Rows** | 561 (28.05%) | **Total Cells** | 14,000 |
| **Missing Data Cells** | 4,134 (29.53%) | **Health Score** | 79.8 / 100 |

---

## 2. Column Inventory & Data Schema

| # | Column Name | Inferred Type | Missing Count (%) | Distinct Values | Notes & Flags |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | **col_01** | `Float` | 551 (27.6%) | 212 | `HIGH NULLS`, `286 Outliers` |
| 2 | **col_02** | `Float` | 572 (28.6%) | 53 | `HIGH NULLS`, `345 Outliers` |
| 3 | **col_03** | `Float` | 468 (23.4%) | 177 | `HIGH NULLS`, `141 Outliers` |
| 4 | **col_04** | `Float` | 360 (18.0%) | 106 | `340 Outliers` |
| 5 | **col_05** | `Text` | 536 (26.8%) | 147 | `HIGH NULLS` |
| 6 | **col_06** | `Float` | 768 (38.4%) | 82 | `HIGH NULLS`, `215 Outliers` |
| 7 | **col_07** | `Float` | 879 (44.0%) | 34 | `HIGH NULLS`, `160 Outliers` |

---

## 3. Numerical Features Statistical Summary

| Column | Mean | Std Dev | Min | 25% (Q1) | Median | 75% (Q3) | Max | IQR | Skewness | Outliers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **col_01** | 29.20 | 51.59 | -0.50 | 1.00 | 1.00 | 25.00 | 202.00 | 24.00 | 1.73 | 286 (19.7%) |
| **col_02** | 19.88 | 33.30 | 0.00 | 1.00 | 1.00 | 4.00 | 139.00 | 3.00 | 1.29 | 345 (24.2%) |
| **col_03** | 37.28 | 57.87 | 0.00 | 0.75 | 1.00 | 60.00 | 220.00 | 59.25 | 1.42 | 141 (9.2%) |
| **col_04** | 9.70 | 25.31 | -9.00 | 1.00 | 1.00 | 4.20 | 162.00 | 3.20 | 2.90 | 340 (20.7%) |
| **col_06** | 12.49 | 25.63 | 0.00 | 1.00 | 1.00 | 7.00 | 100.00 | 6.00 | 2.28 | 215 (17.5%) |
| **col_07** | 15.67 | 28.78 | 0.00 | 1.00 | 1.00 | 20.00 | 87.00 | 19.00 | 1.79 | 160 (14.3%) |

---

## 4. Categorical & Text Distributions

| Column | Distinct Values | Dominant Class (%) | Top Most Frequent Values (Count, %) |
| :--- | :--- | :--- | :--- |
| **col_05** | 147 | 38.2% | `1`: 559 (38.2%), `name`: 200 (13.7%), `5`: 110 (7.5%), `2`: 109 (7.4%) |

---

## 5. Noticeable Trends & Associations

### 🔗 Notable Pearson Correlations

| Feature 1 | Feature 2 | Correlation ($r$) | Relationship | Strength |
| :--- | :--- | :--- | :--- | :--- |
| `col_04` | `col_06` | `+0.941` | Positive | Strong |
| `col_01` | `col_03` | `+0.801` | Positive | Strong |
| `col_03` | `col_04` | `+0.663` | Positive | Moderate |
| `col_03` | `col_06` | `+0.617` | Positive | Moderate |
| `col_01` | `col_04` | `+0.561` | Positive | Moderate |
| `col_01` | `col_06` | `+0.512` | Positive | Moderate |
| `col_02` | `col_04` | `+0.477` | Positive | Moderate |
| `col_02` | `col_06` | `+0.453` | Positive | Moderate |


## 6. Actionable First-Review Recommendations

- ⚠️ **Duplicate Rows Detected**: Found 561 exact duplicate row(s) (28.1%). Consider deduping with `.drop_duplicates()`.
- ⚠️ **High Missingness (>20%)**: Columns ['col_01', 'col_02', 'col_03', 'col_05', 'col_06', 'col_07'] contain substantial missing data. Verify collection integrity or consider imputation/dropping.
- 💡 **Outlier Hotspots**: Columns ['col_01', 'col_02', 'col_03', 'col_04', 'col_06', 'col_07'] exhibit >= 5% Tukey outliers. Inspect whether these represent clinical anomalies, extreme events, or data entry errors.
- 💡 **Heavy Skewness**: Features ['col_01', 'col_04', 'col_06', 'col_07'] are heavily skewed (|skew| >= 1.5). Consider applying Log or Power transformations prior to linear modeling.
- ⚠️ **Multicollinearity Alert**: Very strong correlations found: col_04 & col_06 (r=0.94), col_01 & col_03 (r=0.80). Consider feature selection or PCA to avoid redundant predictors.

---

*Report generated automatically by `data_profiler.py`.*