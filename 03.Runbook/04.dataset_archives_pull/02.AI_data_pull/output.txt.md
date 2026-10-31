

## 1. Locating processed.cleveland.data and Documentation

* Official UCI Dataset URL: https://archive.ics.uci.edu/dataset/45/heart+disease

* Dataset Identifier: UCI ID 45

* Raw Data File: In the UCI distribution archive, the Cleveland Clinic dataset is stored as processed.cleveland.data. It contains 303 patient records, comma-delimited, without a header row, and represents missing entries with a question mark (?).

* Documentation File: In the UCI archive, feature definitions and column orders are detailed in heart-disease.names.

* Local Raw Location in Project: Placed directly at data/raw/processed.cleveland.data.


## 2. The 14 Attributes: Descriptions and Verified Order

According to the UCI documentation (heart-disease.names), while the full database contains 76 raw attributes, all published machine learning experiments utilize this specific subset of 14 attributes in the following exact order (Columns 1–14):

| Col # | Attribute Name | Type | Description, Clinical Units & Value Codes |
| :---: | :---: | :---: | :---: |
| 1 | age | Continuous | Age in years |
| 2 | sex | Binary | Biological sex (1 = male; 0 = female) |
| 3 | cp | Nominal | Chest pain type:<br>• 1: Typical angina<br>• 2: Atypical angina<br>• 3: Non-anginal pain<br>• 4: Asymptomatic |
| 4 | trestbps | Continuous | Resting blood pressure in mm Hg on admission |
| 5 | chol | Continuous | Serum cholesterol in mg/dl |
| 6 | fbs | Binary | Fasting blood sugar > 120 mg/dl (1 = true; 0 = false) |
| 7 | restecg | Nominal | Resting electrocardiographic results:<br>• 0: Normal<br>• 1: Having ST-T wave abnormality (T wave inversions / ST elevation or depression > 0.05 mV)<br>• 2: Showing probable or definite left ventricular hypertrophy by Estes' criteria |
| 8 | thalach | Continuous | Maximum heart rate achieved during exercise stress test |
| 9 | exang | Binary | Exercise-induced angina (1 = yes; 0 = no) |
| 10 | oldpeak | Continuous | ST depression induced by exercise relative to rest |
| 11 | slope | Ordinal | The slope of the peak exercise ST segment:<br>• 1: Upsloping<br>• 2: Flat<br>• 3: Downsloping |
| 12 | ca | Discrete | Number of major vessels (0-3) colored by fluoroscopy *(Contains 4 missing ? values)* |
| 13 | thal | Nominal | Thallium heart scan / Thalassemia:<br>• 3: Normal<br>• 6: Fixed defect<br>• 7: Reversible defect<br>*(Contains 2 missing ? values)* |
| 14 | num | Discrete<br>(Target) | Diagnosis of heart disease (angiographic disease status):<br>• 0: Absence of disease (< 50% diameter narrowing)<br>• 1, 2, 3, 4: Presence of disease (> 50% diameter narrowing, ordered by severity) |


## 3. Loading the Headerless File & Verifying with pandas

Because processed.cleveland.data has no header row and encodes missing entries as ?, load it with header=None, names=column_names, and na_values='?':

```
python

import pandas as pd
column_names = [
    'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
    'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'num'
]
# Load headerless file with designated column names and missing value handling
df = pd.read_csv(
    'data/raw/processed.cleveland.data',
    header=None,
    names=column_names,
    na_values='?'
)
```

__Verification Results:__

* Shape: (303, 14) (303 patient rows, exactly 14 columns)
* Missing Value Audit: Exactly matches the UCI documentation (4 missing values in ca, 2 missing values in thal):

```
text

age: 0, sex: 0, cp: 0, trestbps: 0, chol: 0, fbs: 0, restecg: 0
thalach: 0, exang: 0, oldpeak: 0, slope: 0, ca: 4, thal: 2, num: 0
```

* First 5 Sample Records:

```
text

   age  sex  cp  trestbps  chol  fbs  restecg  thalach  exang  oldpeak  slope   ca  thal  num
0   63    1   1       145   233    1        2      150      0      2.3      3  0.0   6.0    0
1   67    1   4       160   286    0        2      108      1      1.5      2  3.0   3.0    2
2   67    1   4       120   229    0        2      129      1      2.6      2  2.0   7.0    1
3   37    1   3       130   250    0        0      187      0      3.5      3  0.0   3.0    0
4   41    0   2       130   204    0        2      172      0      1.4      1  0.0   3.0    0
```


## 4. Project Files Updated

* data/raw/processed.cleveland.data: Raw, authentic headerless file matching UCI specifications.
* src/download_data.py: Updated with the ordered COLUMN_NAMES and automated loader.
* src/generate_figures.py: Configured to ingest processed.cleveland.data.
* notebooks/exploratory_data_analysis.ipynb: Updated with interactive loading and missing value analysis.
* README.md: Documented with the complete data dictionary table.


<br>
<br>





<br>

