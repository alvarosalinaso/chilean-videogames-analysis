import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import sys
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report

# Setup paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import setup_logger

logger = setup_logger("ml_train")

def train_models():
    # 1. Cargar Dataset Procesado
    data_path = Path("data/processed/ml_dataset.csv")
    if not data_path.exists():
        logger.error("No existe ml_dataset.csv. Corre prepare.py primero.")
        return

    df = pd.read_csv(data_path)
    logger.info(f"Dataset cargado: {len(df)} registros.")
    
    # 2. Cargar Vectorizer
    model_dir = Path("src/ml/models")
    vec_path = model_dir / "tfidf_vectorizer.pkl"
    if not vec_path.exists():
        logger.error("No existe vectorizer. Corre prepare.py primero.")
        return
        
    with open(vec_path, "rb") as f:
        tfidf = pickle.load(f)
        
    # 3. Preparar X (Features) e y (Target)
    # Features: TF-IDF de 'cleaned_text'
    # TODO: Podríamos agregar OneHotEncoding de 'primary_genre'
    X_text = tfidf.transform(df['cleaned_text'].fillna(""))
    
    # Por simplicidad MVP, solo usamos texto ahora. 
    # Si quisieramos agregar género, haríamos hstack con pd.get_dummies(df['primary_genre'])
    X = X_text
    
    # Target 1: Revenue (Regresión)
    # Target 2: Éxito (Clasificación) -> is_success
    y_reg = df['gross_revenue_est_usd'].fillna(0)
    y_clf = df['is_success'].fillna(0)
    
    logger.info(f"Distribución de Clases (Éxito 1 vs 0):\n{y_clf.value_counts()}")

    # Split
    X_train, X_test, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42)
    _, _, y_train_clf, y_test_clf = train_test_split(X, y_clf, test_size=0.2, random_state=42)
    
    # --- MODELO 1: Regresor de Revenue ---
    logger.info("Entrenando Regresor de Revenue (Random Forest)...")
    regressor = RandomForestRegressor(n_estimators=100, random_state=42)
    regressor.fit(X_train, y_train_reg)
    
    # Evaluación
    y_pred_reg = regressor.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
    logger.info(f"RMSE (Error Promedio Precios): ${rmse:,.2f} USD")
    
    # --- MODELO 2: Clasificador de Éxito ---
    logger.info("Entrenando Clasificador de Éxito...")
    classifier = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    classifier.fit(X_train, y_train_clf)
    
    # Evaluación
    y_pred_clf = classifier.predict(X_test)
    acc = accuracy_score(y_test_clf, y_pred_clf)
    logger.info(f"Accuracy (Acierto): {acc*100:.1f}%")
    logger.info("\n" + classification_report(y_test_clf, y_pred_clf))
    
    # Guardar Modelos
    with open(model_dir / "rf_regressor.pkl", "wb") as f:
        pickle.dump(regressor, f)
    with open(model_dir / "rf_classifier.pkl", "wb") as f:
        pickle.dump(classifier, f)
        
    logger.info("Modelos guardados en src/ml/models/")

if __name__ == "__main__":
    train_models()
