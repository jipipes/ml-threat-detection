from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

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
    confidence = round(float(max(probability)), 3)
    label = "attack" if prediction == 1 else "normal"

    # Gemini로 탐지 결과 요약
    prompt = f"""
    네트워크 이벤트 분석 결과:
    - 판정: {label}
    - 신뢰도: {confidence * 100:.1f}%
    
    보안 분석가에게 이 결과를 2문장으로 간결하게 설명해주세요.
    한국어로 답변해주세요.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        summary = f"요약 생성 실패: {str(e)}"

    return {
        "prediction": int(prediction),
        "label": label,
        "confidence": confidence,
        "summary": summary
    }