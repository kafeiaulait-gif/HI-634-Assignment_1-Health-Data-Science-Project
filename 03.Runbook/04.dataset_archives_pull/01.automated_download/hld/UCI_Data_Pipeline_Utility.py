import pandas as pd
from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

class UCIDataPipeline:
    """
    A utility class to download, clean, preprocess, and split 
    datasets from the UCI Machine Learning Repository.
    """
    def __init__(self, dataset_id: int):
        self.dataset_id = dataset_id
        self.repo_object = None
        self.X = None
        self.y = None
        self.preprocessor = None

    def fetch_data(self):
        """Downloads the dataset and splits it into raw X and y."""
        print(f"📡 Fetching dataset ID {self.dataset_id} from UCI Repository...")
        self.repo_object = fetch_ucirepo(id=self.dataset_id)
        
        # Extract features and targets as pandas DataFrames
        self.X = self.repo_object.data.features
        self.y = self.repo_object.data.targets
        
        print(f"✅ Successfully loaded. Shape: {self.X.shape}")
        return self

    def get_variable_summary(self):
        """Returns the variable information dataframe."""
        if self.repo_object is None:
            raise ValueError("Data not fetched yet. Call fetch_data() first.")
        return self.repo_object.variables

    def prepare_splits(self, test_size=0.2, random_state=42):
        """
        Builds a preprocessing pipeline automatically based on column types,
        handles missing values, scales numerical data, and returns train/test splits.
        """
        if self.X is None or self.y is None:
            raise ValueError("Data not fetched yet. Call fetch_data() first.")

        # Identify numeric columns automatically
        numeric_features = self.X.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Build an automated preprocessing pipeline for numeric data
        # (Handles missing values with the median, then scales the data)
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        self.preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features)
            ],
            remainder='passthrough' # Leave categorical columns as-is or handle separately
        )

        # Split into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=random_state
        )

        # Flatten target arrays to 1D arrays for scikit-learn compatibility
        y_train = y_train.values.ravel()
        y_test = y_test.values.ravel()

        return X_train, X_test, y_train, y_test



# ==========================================
# Main
# ==========================================

if __name__ == "__main__":
    # 1. Initialize the utility for Heart Disease (ID 45)
    pipeline = UCIDataPipeline(dataset_id=45)
    
    # 2. Fetch the data
    pipeline.fetch_data()
    
    # 3. View variables metadata (optional check)
    # print(pipeline.get_variable_summary())

    # 4. Automate the cleaning and splitting process
    X_train, X_test, y_train, y_test = pipeline.prepare_splits(test_size=0.2)

    # 5. Build a model pipeline combining preprocessing and a classifier
    model_pipeline = Pipeline(steps=[
        ('preprocessing', pipeline.preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    print("🏋️ Training baseline model...")
    model_pipeline.fit(X_train, y_train)

    print("📊 Evaluating model performance...")
    predictions = model_pipeline.predict(X_test)
    
    # 6. Print evaluation report
    print("\nBaseline Model Report:")
    print(classification_report(y_test, predictions))
    
    
    