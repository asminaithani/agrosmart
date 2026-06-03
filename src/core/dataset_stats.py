import pandas as pd
import joblib
import os
import numpy as np

DATASET_PATH = "crop_cleaned.xls"
MODEL_PATH = "models/rf_crop_model.joblib"

_cached_context = None

def get_dataset_context() -> str:
    global _cached_context
    if _cached_context is not None:
        return _cached_context
        
    try:
        # Load Dataset
        df = pd.read_csv(DATASET_PATH)
        total_records = len(df)
        most_frequent_crop = df['label'].mode()[0]
        avg_rainfall = df['rainfall'].mean()
        
        # High Humidity Crops
        # Find crops where average humidity is > 80%
        crop_humidity = df.groupby('label')['humidity'].mean()
        high_humidity_crops = crop_humidity[crop_humidity > 80].index.tolist()
        
        # Load Model
        artifacts = joblib.load(MODEL_PATH)
        model = artifacts["model"]
        features = artifacts["feature_names"]
        
        # Top Feature
        importances = model.feature_importances_
        top_feature_idx = np.argmax(importances)
        top_feature = features[top_feature_idx]
        
        # Format the context string
        context = (
            "--- GLOBAL DATASET KNOWLEDGE ---\n"
            "You have access to the global dataset statistics. If the user asks about the dataset, use these exact facts:\n"
            f"Total Records: {total_records}\n"
            f"Most Frequent Crop: {most_frequent_crop.capitalize()}\n"
            f"Average Rainfall: {avg_rainfall:.2f} mm\n"
            f"Highest Impact Feature on Prediction: {top_feature}\n"
            f"Crops suitable for high humidity (>80%): {', '.join(high_humidity_crops)}\n"
            "Dataset Trends: High rainfall correlates strongly with Rice and Papaya. High nitrogen levels are crucial for Cotton and Coffee. "
            "Apples and Grapes require lower temperatures compared to tropical crops like Mango and Banana.\n"
            "--- END DATASET KNOWLEDGE ---\n"
        )
        
        _cached_context = context
        return _cached_context
        
    except Exception as e:
        print(f"Error loading dataset stats: {e}")
        return "Dataset stats unavailable."
