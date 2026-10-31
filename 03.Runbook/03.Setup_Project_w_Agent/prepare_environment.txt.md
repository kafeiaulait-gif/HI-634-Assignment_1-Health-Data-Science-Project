
<br>

## Documentation & Reproducibility (README.md)

	README.md has been created with all data provenance details and exact reproduction steps for a reviewer:

---


* Dataset: Heart Disease (Cleveland Database)

* Official Repository URL: https://archive.ics.uci.edu/dataset/45/heart+disease

* UCI Repository ID: 45 (ucimlrepo)

* Download / Access Date: October 29, 2026

* How a reviewer reproduces everything:

	*  Install dependencies:

  ```
		./.venv/bin/pip install -r requirements.txt
  ```    
		
	*  Fetch / Verify raw data:

  ```	
		./.venv/bin/python src/download_data.py
  ```    
		
	*  Generate all tables and figures:
	
  ```  
		MPLCONFIGDIR=/tmp ./.venv/bin/python src/generate_figures.py
  ```    
		
	*  Output files are placed directly into reports/figures/.

<br>

