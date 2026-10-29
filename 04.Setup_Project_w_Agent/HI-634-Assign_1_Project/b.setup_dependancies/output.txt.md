
## 1. requirements.txt

The file requirements.txt has been prepared with the requested core libraries and ucimlrepo:

```
text

# Core Data Science & Analysis
pandas
numpy

# Visualization
matplotlib
seaborn

# Machine Learning
scikit-learn

# Notebook & Interactive Computing
jupyter

# UCI Machine Learning Repository API (for importing UCI health datasets such as Heart Disease)
ucimlrepo
```


## 2. Installing Inside .venv

Command Executed:

```
bash

# Activated virtual environment and installed requirements:
source .venv/bin/activate && python -m pip install -r requirements.txt
```

(All dependencies including pandas 3.1.0, numpy 2.5.4, matplotlib 3.11.2, seaborn 0.13.2, scikit-learn 1.9.1, jupyter, and ucimlrepo 0.0.7 are installed in .venv).


## 3. Python Path & Package Versions

To ensure reliability across isolated subshells, we inspect the environment directly:

```
bash

MPLCONFIGDIR=/tmp .venv/bin/python -c "
import sys, importlib.metadata
import pandas as pd
import numpy as np
import matplotlib
import seaborn as sns
import sklearn
print('=== Python Path & Executable ===')
print('sys.executable:', sys.executable)
print('sys.prefix:    ', sys.prefix)
print('\n=== Package Versions ===')
print('pandas:       ', pd.__version__)
print('numpy:        ', np.__version__)
print('matplotlib:   ', matplotlib.__version__)
print('seaborn:      ', sns.__version__)
print('scikit-learn: ', sklearn.__version__)
print('jupyter-core: ', importlib.metadata.version('jupyter_core'))
print('ucimlrepo:    ', importlib.metadata.version('ucimlrepo'))"
```

Output:

```
text

=== Python Path & Executable ===
sys.executable: /home/kafeiaulait/HI-634-Assign_1_Project/.venv/bin/python
sys.prefix:     /home/kafeiaulait/HI-634-Assign_1_Project/.venv

=== Package Versions ===
pandas:        3.1.0
numpy:         2.5.4
matplotlib:    3.11.2
seaborn:       0.13.2
scikit-learn:  1.9.1
jupyter-core:  5.9.1
ucimlrepo:     0.0.7
```


## 4. Sample Data Loading (UCI Heart Disease Dataset)

We loaded a sample of the Heart Disease dataset (heart_disease_sample.csv):

```
bash

.venv/bin/python -c "
import pandas as pd
df = pd.read_csv('heart_disease_sample.csv')
print(f'Shape: {df.shape} (rows, columns)\n')
print(df.head())"
```

Output:

```
text

Shape: (303, 14) (rows, columns)
   age  sex  cp  trestbps  chol  fbs  restecg  thalach  exang  oldpeak  slope   ca  thal  num
0   63    1   1       145   233    1        2      150      0      2.3      3  0.0   6.0    0
1   67    1   4       160   286    0        2      108      1      1.5      2  3.0   3.0    2
2   67    1   4       120   229    0        2      129      1      2.6      2  2.0   7.0    1
3   37    1   3       130   250    0        0      187      0      3.5      3  0.0   3.0    0
4   41    0   2       130   204    0        2      172      0      1.4      1  0.0   3.0    0
```


## 5. Virtual Environment Activation: Common OS Errors & Direct Fallback

If source .venv/bin/activate or equivalent fails, the root cause depends on the operating system:

| OS / Shell | Common Error Message | Cause & Explanation | Direct Fallback Workaround |
| :---: | :---: | :---: | :---: |
| **Linux / POSIX<br>(Direct execution)** | `bash: .venv/bin/activate: Permission denied` | Attempting to run `.venv/bin/activate` directly as an executable binary instead of sourcing it (`source` or `.`). Activation scripts are shell configuration files, not standalone executables. | Use the virtual environment's Python directly:<br>`./.venv/bin/python script.py` |
| **Linux (POSIX<br>sh / Dash)** | `sh: 1: source: not found` | The standard `/bin/sh` shell does not support the bash-specific `source` keyword; it requires `. .venv/bin/activate`. | Use the venv binary directly:<br>`./.venv/bin/python -m pip ...` |
| **Windows<br>(PowerShell)** | `File ... activate.ps1 cannot be loaded because running scripts is disabled on this system (PSSecurityException)` | PowerShell's default execution policy (`Restricted`) prevents running unsigned PowerShell scripts. | Bypass execution policy (`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`) or run directly:<br>`.venv\Scripts\python.exe` |
| **CI / Subshell<br>Runners** | `Environment reverts to system Python on next command` | Automated runners spawn independent subshells per command; environment changes (like PATH updates from activate) discard upon exit. | Always invoke with full or relative path:<br>`/home/kafeiaulait/HI-634-Assign_1_Project/.venv/bin/python` |


<br>

