import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "models", "rf_crop_model.joblib")
DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "Crop_recommendation.csv")
