import os
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

# Load model if exists, otherwise train it immediately
if not os.path.exists(MODEL_PATH):
    from .train_model import train_and_save
    train_and_save()

_model = joblib.load(MODEL_PATH)

def predict_landslide_probability(features_dict: dict) -> float:
    """
    Accepts feature dictionary and outputs risk probability [0.0 to 1.0].
    """
    feature_cols = [
        "rainfall_24h", "rainfall_intensity", "soil_moisture",
        "humidity", "temperature", "slope", "elevation", "historical_freq"
    ]
    
    row = {col: features_dict.get(col, 0.0) for col in feature_cols}
    df = pd.DataFrame([row])
    
    probs = _model.predict_proba(df)[0]
    # Class 1 probability (Landslide Risk)
    return float(probs[1])