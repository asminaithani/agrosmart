import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import numpy as np
from src.core.config import DATA_PATH, MODEL_PATH

def generate_mock_data(path, num_samples=1000):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    crops = ['rice', 'maize', 'sugarcane', 'wheat', 'cotton']
    
    np.random.seed(42)
    data = {
        'N': np.random.randint(0, 140, num_samples),
        'P': np.random.randint(5, 145, num_samples),
        'K': np.random.randint(5, 205, num_samples),
        'temperature': np.random.uniform(8.0, 43.0, num_samples),
        'humidity': np.random.uniform(14.0, 100.0, num_samples),
        'ph': np.random.uniform(3.5, 9.9, num_samples),
        'rainfall': np.random.uniform(20.0, 298.0, num_samples),
        'label': np.random.choice(crops, num_samples)
    }
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    print(f"Mock data generated at {path}")

def train_model():
    data_path = "crop_cleaned.xls"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"{data_path} not found!")
        
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)
    
    print("Training RandomForest model with GridSearchCV...")
    param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [None, 10, 20]
    }
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, n_jobs=-1, scoring='accuracy')
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"Best parameters: {grid_search.best_params_}")
    
    y_pred = best_model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model_artifacts = {
        "model": best_model,
        "scaler": scaler,
        "label_encoder": label_encoder,
        "feature_names": X.columns.tolist()
    }
    joblib.dump(model_artifacts, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
