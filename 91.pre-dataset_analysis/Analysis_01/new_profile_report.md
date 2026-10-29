# 📊 Data Profile & Exploratory Analysis Report
**Target Dataset:** `new.data`  
**Analysis Date:** 2026-10-29 01:19:04  
**File Size:** 380.64 KB  
**Data Health Score:** `69.7/100.0`

---
## 1. Executive Summary

| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Total Rows** | 18,492 | **Total Columns** | 7 |
| **Duplicate Rows** | 8,361 (45.21%) | **Total Cells** | 129,444 |
| **Missing Data Cells** | 54,286 (41.94%) | **Health Score** | 69.7 / 100 |

---

## 2. Column Inventory & Data Schema

| # | Column Name | Inferred Type | Missing Count (%) | Distinct Values | Notes & Flags |
| :- | :--- | :--- | :--- | :--- | :--- |
| 1 | **col_01** | `Float` | 5586 (30.2%) | 1,604 | `HIGH NULLS`, `2883 Outliers` |
| 2 | **col_02** | `Integer` | 4916 (26.6%) | 1,416 | `HIGH NULLS`, `2538 Outliers` |
| 3 | **col_03** | `Text` | 7233 (39.1%) | 1,213 | `HIGH NULLS` |
| 4 | **col_04** | `Integer` | 8134 (44.0%) | 132 | `HIGH NULLS`, `2120 Outliers` |
| 5 | **col_05** | `Integer` | 7964 (43.1%) | 468 | `HIGH NULLS`, `211 Outliers` |
| 6 | **col_06** | `Float` | 10569 (57.2%) | 143 | `HIGH NULLS`, `1384 Outliers` |
| 7 | **col_07** | `Float` | 9884 (53.5%) | 100 | `HIGH NULLS`, `1830 Outliers` |

---

## 3. Numerical Features Statistical Summary

| Column | Mean | Std Dev | Min | 25% (Q1) | Median | 75% (Q3) | Max | IQR | Skewness | Outliers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **col_01** | 193.73 | 559.48 | -27.00 | 0.00 | 1.00 | 21.00 | 3107.00 | 21.00 | 3.21 | 2883 (22.3%) |
| **col_02** | 365812.56 | 2410624.84 | -1.00 | 0.00 | 1.00 | 72.00 | 17541960.00 | 72.00 | 6.57 | 2538 (18.7%) |
| **col_04** | 13.37 | 30.93 | -1.00 | 0.00 | 1.00 | 2.00 | 160.00 | 2.00 | 2.25 | 2120 (20.5%) |
| **col_05** | 56.78 | 89.71 | -1.00 | 1.00 | 2.00 | 120.00 | 603.00 | 119.00 | 1.57 | 211 (2.0%) |
| **col_06** | 19.16 | 30.48 | -1.00 | 1.00 | 3.00 | 19.00 | 122.00 | 18.00 | 1.60 | 1384 (17.5%) |
| **col_07** | 323.73 | 730.33 | -1.00 | 0.00 | 1.00 | 6.00 | 1989.00 | 6.00 | 1.84 | 1830 (21.3%) |

---

## 4. Categorical & Text Distributions

| Column | Distinct Values | Dominant Class (%) | Top Most Frequent Values (Count, %) |
| :--- | :--- | :--- | :--- |
| **col_03** | 1213 | 18.9% | `0`: 2123 (18.9%), `1`: 1261 (11.2%), `-1`: 412 (3.7%), `140`: 304 (2.7%) |

---

## 5. Noticeable Trends & Associations

### 🔗 Notable Pearson Correlations

| Feature 1 | Feature 2 | Correlation ($r$) | Relationship | Strength |
| :--- | :--- | :--- | :--- | :--- |
| `col_04` | `col_06` | `+0.958` | Positive | Strong |
| `col_05` | `col_06` | `+0.586` | Positive | Moderate |


## 6. Actionable First-Review Recommendations

- ⚠️ **Duplicate Rows Detected**: Found 8361 exact duplicate row(s) (45.2%). Consider deduping with `.drop_duplicates()`.
- ⚠️ **High Missingness (>20%)**: Columns ['col_01', 'col_02', 'col_03', 'col_04', 'col_05', 'col_06', 'col_07'] contain substantial missing data. Verify collection integrity or consider imputation/dropping.
- 💡 **Outlier Hotspots**: Columns ['col_01', 'col_02', 'col_04', 'col_06', 'col_07'] exhibit >= 5% Tukey outliers. Inspect whether these represent clinical anomalies, extreme events, or data entry errors.
- 💡 **Heavy Skewness**: Features ['col_01', 'col_02', 'col_04', 'col_05', 'col_06', 'col_07'] are heavily skewed (|skew| >= 1.5). Consider applying Log or Power transformations prior to linear modeling.
- ⚠️ **Multicollinearity Alert**: Very strong correlations found: col_04 & col_06 (r=0.96). Consider feature selection or PCA to avoid redundant predictors.

---

*Report generated automatically by `data_profiler.py`.*