import joblib
import matplotlib.pyplot as plt
import os
import pandas as pd
from src.core.config import MODEL_PATH

def plot_feature_importance():
    if not os.path.exists(MODEL_PATH):
        print(f"Model not found at {MODEL_PATH}. Train the model first.")
        return
        
    artifacts = joblib.load(MODEL_PATH)
    model = artifacts["model"]
    feature_names = artifacts["feature_names"]
    
    importances = model.feature_importances_
    
    feature_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.barh(feature_importance_df['Feature'], feature_importance_df['Importance'], color='skyblue')
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.title('Random Forest Feature Importance')
    plt.gca().invert_yaxis()
    
    output_path = os.path.join(os.path.dirname(MODEL_PATH), "feature_importance.png")
    plt.savefig(output_path)
    print(f"Feature importance plot saved to {output_path}")

if __name__ == "__main__":
    plot_feature_importance()
