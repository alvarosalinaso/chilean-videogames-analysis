import pandas as pd
import numpy as np
import pickle
import sys
import os
import re
from pathlib import Path

# Setup paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import setup_logger

logger = setup_logger("ml_predict")

def clean_text(text):
    # Duplicado de prepare.py por simplicidad de import
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[^a-záéíóúñ0-9\s]', '', text)
    return text.strip()

def predict_success(game_pitch):
    model_dir = Path("src/ml/models")
    
    # Cargar Artifacts
    try:
        with open(model_dir / "tfidf_vectorizer.pkl", "rb") as f:
            tfidf = pickle.load(f)
        with open(model_dir / "rf_regressor.pkl", "rb") as f:
            regressor = pickle.load(f)
        with open(model_dir / "rf_classifier.pkl", "rb") as f:
            classifier = pickle.load(f)
    except FileNotFoundError:
        print("Error: No se encontraron los modelos. Entrena primero con src/ml/train.py")
        return

    # Preprocesar Input
    clean_pitch = clean_text(game_pitch)
    vectorized_pitch = tfidf.transform([clean_pitch])
    
    # Predicción
    pred_revenue = regressor.predict(vectorized_pitch)[0]
    pred_class = classifier.predict(vectorized_pitch)[0]
    
    # Probabilidad
    pred_proba = classifier.predict_proba(vectorized_pitch)[0][1]
    
    print("\n" + "="*40)
    print("🔮 LA BOLA DE CRISTAL DE VIDEOJUEGOS CHILENOS 🔮")
    print("="*40)
    print(f"Input: \"{game_pitch[:50]}...\"")
    print("-" * 40)
    
    print(f"💰 Revenue Estimado (Lifetime): ${pred_revenue:,.2f} USD")
    
    success_label = "✅ ÉXITO (>1k copias)" if pred_class == 1 else "⚠️ NICHO / DIFÍCIL"
    print(f"📊 Potencial de Éxito: {success_label}")
    print(f"📈 Probabilidad: {pred_proba*100:.1f}%")

    # 5. Buscar Juegos Similares (Nearest Neighbors)
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Cargar dataset original para buscar
        df_path = "data/processed/ml_dataset.csv"
        if os.path.exists(df_path):
            df = pd.read_csv(df_path)
            
            # Vectorizar todos los juegos (idealmente guardar matriz, pero recalculamos rápido)
            X_all = tfidf.transform(df['cleaned_text'].fillna(""))
            
            # Calcular similitud
            similarities = cosine_similarity(vectorized_pitch, X_all).flatten()
            
            # Top 3 índices
            top_indices = similarities.argsort()[-3:][::-1]
            
            print("-" * 40)
            print("🔍 JUEGOS CHILENOS SIMILARES:")
            for idx in top_indices:
                game = df.iloc[idx]
                sim_score = similarities[idx]
                is_suc = game['is_success'] == 1
                status = "✅ ÉXITO" if is_suc else "⚠️ NICHO"
                revenue = game['gross_revenue_est_usd']
                print(f"  • {game['name']} ({status}, ${revenue:,.0f})")
                print(f"    [Similitud: {sim_score*100:.0f}%]")
    except Exception as e:
        print(f"ERROR en Similitud: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*40 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        predict_success(user_input)
    else:
        print("\nEscribe el concepto de tu juego (en inglés o español) y presiona Enter:")
        user_input = input("> ")
        predict_success(user_input)
