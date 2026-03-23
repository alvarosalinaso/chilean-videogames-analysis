import pandas as pd, numpy as np, pickle, sys, os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import setup_logger

log = setup_logger("ml_train")

def run_training_pipeline():
    d_path = Path("data/processed/ml_dataset.csv")
    if not d_path.exists():
        log.error("ml_dataset.csv is missing. run prepare.py")
        return

    df = pd.read_csv(d_path)
    log.info(f"Loaded {len(df)} rows")
    
    m_dir = Path("src/ml/models")
    vec_p = m_dir / "tfidf_vectorizer.pkl"
    if not vec_p.exists():
        log.error("vectorizer is missing. run prepare.py")
        return
        
    with open(vec_p, "rb") as f: tfidf = pickle.load(f)
        
    X_txt = tfidf.transform(df['cleaned_text'].fillna(""))
    X = X_txt
    
    # labels
    y_r = df['gross_revenue_est_usd'].fillna(0)
    y_c = df['is_success'].fillna(0)
    
    X_tr, X_te, y_r_tr, y_r_te = train_test_split(X, y_r, test_size=0.2, random_state=42)
    _, _, y_c_tr, y_c_te = train_test_split(X, y_c, test_size=0.2, random_state=42)
    
    log.info("Fit RF Regressor...")
    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X_tr, y_r_tr)
    
    rmse = np.sqrt(mean_squared_error(y_r_te, reg.predict(X_te)))
    log.info(f"RMSE: ${rmse:,.2f} USD")
    
    log.info("Fit RF Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    clf.fit(X_tr, y_c_tr)
    
    y_pred_c = clf.predict(X_te)
    log.info(f"Acc: {accuracy_score(y_c_te, y_pred_c)*100:.1f}%")
    log.info("\n" + classification_report(y_c_te, y_pred_c))
    
    # store
    with open(m_dir / "rf_regressor.pkl", "wb") as f: pickle.dump(reg, f)
    with open(m_dir / "rf_classifier.pkl", "wb") as f: pickle.dump(clf, f)
    log.info("Dumped models to src/ml/models/")

if __name__ == "__main__": run_training_pipeline()
