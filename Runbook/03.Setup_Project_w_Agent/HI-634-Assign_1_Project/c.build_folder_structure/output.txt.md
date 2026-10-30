
## Project Directory Structure & Git Configuration

All requested folders and files have been set up:

text
HI-634-Assign_1_Project/
├── .gitignore                       <-- Configured (.venv/, caches, checkpoints)
├── requirements.txt                 <-- Pinned dependencies
├── README.md                        <-- Complete documentation & reproduction guide
├── heart_disease_sample.csv         <-- Sample dataset
├── data/
│   ├── raw/
│   │   └── heart_disease.csv        <-- Raw dataset copy
│   └── processed/
│       └── heart_disease_cleaned.csv <-- Processed dataset with engineered target
├── notebooks/
│   └── exploratory_data_analysis.ipynb <-- Interactive exploration notebook
├── src/
│   ├── download_data.py             <-- Ingestion script (UCI Repo ID 45)
│   └── generate_figures.py          <-- Pipeline script to reproduce tables/figures
└── reports/
    └── figures/
        ├── summary_statistics.csv   <-- Descriptive statistics table
        ├── age_distribution.png     <-- Figure 1: Age distribution plot
        └── correlation_matrix.png   <-- Figure 2: Correlation heatmap

<br>

