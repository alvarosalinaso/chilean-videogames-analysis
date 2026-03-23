import json
import pandas as pd
import numpy as np
from pathlib import Path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import sys
import os

# Ajustar path para importar utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import setup_logger

logger = setup_logger("ml_prepare")

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Lowercase
    text = text.lower()
    # Remove html tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special chars but keep words
    text = re.sub(r'[^a-záéíóúñ0-9\s]', '', text)
    return text.strip()

def load_raw_data():
    raw_dir = Path("data/raw")
    games = []
    
    logger.info("Cargando JSONs raw...")
    # Cargar Steam y Itch (aunque Itch tiene menos data rica, nos enfocaremos en Steam para training fuerte)
    # Pero para generalizar, carguemos todo lo que tenga 'description' o similar.
    
    for f in raw_dir.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                
                # Normalizar Steam vs Itch
                game_info = {}
                
                # STEAM
                if "steam_appid" in data:
                    game_info['source'] = 'steam'
                    game_info['name'] = data.get('name', '')
                    game_info['description'] = data.get('detailed_description', '') + " " + data.get('short_description', '')
                    
                    # Target: Estimated Revenue (Usaremos recommendations como proxy de éxito por ahora si revenue no está calculado aquí)
                    # Mejor cruzar con el CSV procesado que ya tiene revenue estimado.
                    game_info['id'] = str(data.get('steam_appid'))
                    
                # ITCH
                elif "source" in data and data["source"] == "itch":
                    game_info['source'] = 'itch'
                    game_info['name'] = data.get('name', '')
                    game_info['description'] = data.get('name', '') + " " + data.get('genre', '') # Itch es pobre en descripciones en este scraper
                    game_info['id'] = str(data.get('id'))
                
                games.append(game_info)
        except Exception as e:
            logger.warning(f"Error leyendo {f}: {e}")

    return pd.DataFrame(games)

def prepare_dataset():
    # 1. Cargar Data Cruda (Texto)
    df_raw = load_raw_data()
    
    # 2. Cargar Data Procesada (Targets: Revenue/Copia)
    processed_path = Path("data/export/chilean_games_final.csv")
    if not processed_path.exists():
        logger.error("No se encontró data procesada final. Corre analyze_all.py primero.")
        return
    
    df_metrics = pd.read_csv(processed_path)
    # Asegurar IDs string para merge
    df_metrics['steam_id'] = df_metrics['steam_id'].fillna(0).astype(int).astype(str)
    
    # Merge para pegar el Target (Revenue/Recommendations) al Texto
    # Ojo: El CSV final puede tener IDs de itch.
    # Vamos a usar 'name' como llave de fallback o 'steam_id' si existe.
    
    # Estrategia: Usar Steam ID para cruce exacto en Steam
    df_steam = df_raw[df_raw['source'] == 'steam'].copy()
    df_steam = df_steam.merge(df_metrics[['steam_id', 'gross_revenue_est_usd', 'recommendations', 'primary_genre']], 
                              left_on='id', right_on='steam_id', how='inner')
    
    logger.info(f"Juegos de Steam con data completa: {len(df_steam)}")
    
    # Limpieza de Texto
    df_steam['cleaned_text'] = df_steam['description'].apply(clean_text)
    
    # Definir Target: "Éxito" = > $1,000 USD revenue estimado (Umbral más bajo para indie)
    # O usar Regresión directa. Preparemos ambos.
    
    dataset = df_steam[['name', 'cleaned_text', 'primary_genre', 'gross_revenue_est_usd', 'recommendations']].copy()
    dataset['is_success'] = (dataset['gross_revenue_est_usd'] > 1000).astype(int)
    
    # Guardar CSV intermedio para debug
    dataset.to_csv("data/processed/ml_dataset.csv", index=False)
    logger.info("Dataset ML guardado en data/processed/ml_dataset.csv")
    
    # Entrenar Vectorizer (TF-IDF) y guardarlo
    logger.info("Entrenando TF-IDF...")
    tfidf = TfidfVectorizer(max_features=1000, stop_words='english') # English porque Steam suele estar en inglés o español mixto, pero stop words english ayuda technical terms.
    # Nota: Muchos juegos chilenos tienen descripción en español. Deberíamos usar stop words 'spanish' si detectamos eso. 
    # Por simplicidad, usaremos sin stop words o lista custom si vemos mucho ruido.
    
    matrix = tfidf.fit_transform(dataset['cleaned_text'])
    
    # Guardar artefactos
    model_dir = Path("src/ml/models")
    model_dir.mkdir(parents=True, exist_ok=True)
    
    with open(model_dir / "tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(tfidf, f)
        
    logger.info("Vectorizer guardado.")
    return dataset

if __name__ == "__main__":
    prepare_dataset()
