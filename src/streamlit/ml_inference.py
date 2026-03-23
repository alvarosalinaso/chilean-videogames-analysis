import pickle
import re
from pathlib import Path
import streamlit as st
import traceback

@st.cache_resource
def load_models():
    """Carga los modelos NLP en caché para no saturar memoria en cada interacción."""
    base_dir = Path("src/ml/models")
    try:
        with open(base_dir / "tfidf_vectorizer.pkl", "rb") as f:
            tfidf = pickle.load(f)
        with open(base_dir / "rf_regressor.pkl", "rb") as f:
            reg = pickle.load(f)
        with open(base_dir / "rf_classifier.pkl", "rb") as f:
            clf = pickle.load(f)
        return tfidf, reg, clf
    except Exception as e:
        return None, None, None

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^a-záéíóúñ0-9\s]', '', text)
    return text.strip()

def run_prediction(pitch_text):
    tfidf, reg, clf = load_models()
    if tfidf is None:
        return {"error": "Modelos no encontrados en src/ml/models/"}
    
    clean_pitch = clean_text(pitch_text)
    if not clean_pitch:
        return {"error": "Por favor escribe una descripción válida."}
        
    vec = tfidf.transform([clean_pitch])
    
    rev = reg.predict(vec)[0]
    cls = clf.predict(vec)[0]
    prob = clf.predict_proba(vec)[0][1]
    
    return {
        "revenue": float(rev),
        "is_success": bool(cls == 1),
        "probability": float(prob)
    }
