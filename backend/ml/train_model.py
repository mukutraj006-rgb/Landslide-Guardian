"""
LANDSLIDE GUARDIAN — Machine Learning Training Pipeline
Trains an explainable Random Forest Classifier using North-Eastern geological features.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def generate_synthetic_ner_dataset(n_samples=2000):
    """
    Generates synthetic training dataset modeling realistic North-Eastern India
    topography, precipitation patterns, and slope stability relationships.
    """
    rng = np.random.default_rng(42)

    # 1. 24h Accumulated Rainfall (mm) [0 - 250mm]
    rainfall_24h = rng.uniform(5, 220, n_samples)
    # 2. Rainfall Intensity (mm/h)
    rainfall_intensity = rainfall_24h * rng.uniform(0.08, 0.25, n_samples)
    # 3. Soil Moisture (%) [30% - 98%]
    soil_moisture = np.clip(30 + (rainfall_24h * 0.3) + rng.normal(0, 5, n_samples), 30, 98)
    # 4. Humidity (%)
    humidity = np.clip(60 + (rainfall_24h * 0.15) + rng.normal(0, 4, n_samples), 50, 100)
    # 5. Temperature (°C)
    temperature = rng.uniform(14, 30, n_samples)
    # 6. Slope (degrees) [5° to 60°]
    slope = rng.uniform(8, 55, n_samples)
    # 7. Elevation (meters) [100m to 2500m]
    elevation = rng.uniform(100, 2200, n_samples)
    # 8. Historical Landslide Frequency (count in region)
    historical_freq = rng.integers(0, 12, n_samples)

    # Geotechnical Ground Truth Rule (Physics-inspired trigger logic)
    # Landslide trigger depends on: High Rainfall + Saturated Soil + Steep Slope (>30 deg)
    risk_index = (
        (rainfall_24h * 0.35) +
        (soilMoistureFactor := soil_moisture * 0.30) +
        (slopeFactor := slope * 0.85) +
        (historical_freq * 2.5)
    )

    # Label: 1 if landslide triggered under extreme factors, else 0
    y = (risk_index > 75).astype(int)

    df = pd.DataFrame({
        "rainfall_24h": rainfall_24h,
        "rainfall_intensity": rainfall_intensity,
        "soil_moisture": soil_moisture,
        "humidity": humidity,
        "temperature": temperature,
        "slope": slope,
        "elevation": elevation,
        "historical_freq": historical_freq
    })

    return df, y

def train_and_save():
    print("Generating NER Geological & Meteorological Training Dataset...")
    X, y = generate_synthetic_ner_dataset(n_samples=3000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Simple, explainable Random Forest Classifier
    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=6,             # Kept shallow for high explainability and low overfitting
        random_state=42
    )

    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    print(f"Model Training Accuracy: {accuracy_score(y_train, clf.predict(X_train)):.4f}")
    print(f"Model Testing Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    model_dir = os.path.dirname(__file__)
    model_path = os.path.join(model_dir, "model.pkl")
    joblib.dump(clf, model_path)
    print(f"Model saved successfully to: {model_path}")

if __name__ == "__main__":
    train_and_save()