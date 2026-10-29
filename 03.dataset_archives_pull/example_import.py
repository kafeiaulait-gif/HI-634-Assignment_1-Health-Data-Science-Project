# 1. Install the package via terminal
# pip install ucimlrepo

from ucimlrepo import fetch_ucirepo, list_available_datasets

# Optional: Preview what is available
list_available_datasets()

# 2. Fetch a specific dataset (e.g., Heart Disease dataset using its ID)
heart_disease = fetch_ucirepo(id=45) 

# 3. Access data split cleanly into features and targets
X = heart_disease.data.features
y = heart_disease.data.targets

# 4. Printing documentation
print(heart_disease.metadata) 

# 4. View properties and inspecting data types for columns
print(heart_disease.variables)





