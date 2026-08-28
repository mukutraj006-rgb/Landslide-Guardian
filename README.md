# Landslide Guardian — SIH Prototype

Software-only landslide risk monitoring prototype using FastAPI, MongoDB Atlas, Open-Meteo and a Random Forest model.

## 1. First-time setup

From the project root:

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r backend\requirements.txt
```

Create `backend/.env` from `backend/.env.example` and add your MongoDB Atlas URI.

## 2. Verify MongoDB Atlas

```cmd
python backend\test_mongodb.py
```

Expected:

```text
SUCCESS: MongoDB Atlas is connected!
```

## 3. Start the application

```cmd
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/api/health

## 4. Test a risk assessment

Use `POST /api/risk/predict` in Swagger with:

```json
{
  "location_name": "Gangtok, Sikkim",
  "latitude": 27.3389,
  "longitude": 88.6065
}
```

A successful assessment is persisted to the `risk_assessments` collection in the `landslide_guardian` MongoDB Atlas database. High/critical assessments also create an `alerts` document.

## Prototype limitations

- Terrain slope and historical frequency use a documented prototype lookup for the predefined NER locations; custom locations use a conservative approximation.
- Soil moisture is a weather-model-derived shallow-soil proxy, not a physical sensor reading.
- The Random Forest is trained on synthetic, physics-inspired prototype data, not a validated historical landslide dataset.
- SOS is simulated; no real SMS or phone call is sent.
- If Open-Meteo is temporarily unavailable, the backend uses explicitly labelled demo weather values so the SIH demonstration can continue. MongoDB failures are never silently hidden.
