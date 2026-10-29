
from lib.uci_utility import UCIDataPipeline

# Easily swap to a different dataset by changing the ID 
# (e.g., ID 45 is the Heart Disease Dataset)
heartdisease_pipeline = UCIDataPipeline(dataset_id=45)
heartdisease_pipeline.fetch_data()
X_train, X_test, y_train, y_test = wine_pipeline.prepare_splits()

