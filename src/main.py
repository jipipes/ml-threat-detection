from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib
import os

# 모델 & 스케일러 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model = joblib.load(os.path.join(BASE_DIR, "models/xgb_model.joblib"))
scaler = joblib.load(os.path.join(BASE_DIR, "data/processed/scaler.joblib"))

app = FastAPI(title="ML Threat Detection API")

class NetworkEvent(BaseModel):
    features: list[float]

@app.get("/")
def root():
    return {"message": "ML Threat Detection API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(event: NetworkEvent):
    features = np.array(event.features).reshape(1, -1)
    scaled = scaler.transform(features)
    prediction = model.predict(scaled)[0]
    probability = model.predict_proba(scaled)[0]
    
    return {
        "prediction": int(prediction),
        "label": "attack" if prediction == 1 else "normal",
        "confidence": round(float(max(probability)), 3)
    }