"""
Clusterización de videojuegos chilenos con scikit-learn.
Identifica segmentos de mercado usando K-Means + elbow method.
"""

import json
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def run_clustering(
    data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")
) -> dict:
    """Clusterización robusta con validación cruzada y métricas avanzadas."""
    if not SKLEARN_AVAILABLE:
        print("[CLUSTER] scikit-learn no instalado. pip install scikit-learn")
        return {}

    csv_file = data_dir / "games.csv"
    if not csv_file.exists():
        alt = Path("data/processed/games.csv")
        if alt.exists():
            csv_file = alt
        else:
            print(f"[CLUSTER] {csv_file} not found")
            return {}

    df = pd.read_csv(csv_file, encoding="utf-8")

    feature_cols = [
        c
        for c in ["price_usd", "gross_revenue_est_usd", "recommendations", "metacritic"]
        if c in df.columns
    ]
    if len(feature_cols) < 2:
        print("[CLUSTER] Need at least 2 numeric columns")
        return {}

    X = df[feature_cols].fillna(0).replace([np.inf, -np.inf], 0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Elbow + silhouette
    inertias, silhouettes, ch_scores, db_scores = [], [], [], []
    K_range = range(2, min(8, len(df) // 5 + 1))

    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X_scaled, labels))
        from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score

        ch_scores.append(calinski_harabasz_score(X_scaled, labels))
        db_scores.append(davies_bouldin_score(X_scaled, labels))

    optimal_k = list(K_range)[np.argmax(silhouettes)]

    # Cross-validation: stability across folds
    from sklearn.model_selection import KFold

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    fold_silhouettes = []

    for train_idx, _ in kf.split(X_scaled):
        X_fold = X_scaled[train_idx]
        km_cv = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
        labels_cv = km_cv.fit_predict(X_fold)
        fold_silhouettes.append(silhouette_score(X_fold, labels_cv))

    # PCA feature importance
    from sklearn.decomposition import PCA

    pca = PCA(n_components=len(feature_cols))
    pca.fit(X_scaled)
    feature_importance = {
        col: round(imp, 4)
        for col, imp in zip(feature_cols, pca.explained_variance_ratio_)
    }

    # Final clustering
    km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df["cluster"] = km_final.fit_predict(X_scaled)

    cluster_profiles = {}
    for c in range(optimal_k):
        cluster_df = df[df["cluster"] == c]
        profile = {
            "size": len(cluster_df),
            "pct": round(len(cluster_df) / len(df) * 100, 1),
        }
        for col in feature_cols:
            profile[f"{col}_mean"] = round(cluster_df[col].mean(), 2)
        if "name" in cluster_df.columns:
            profile["top_games"] = cluster_df.nlargest(3, feature_cols[0])[
                "name"
            ].tolist()
        cluster_profiles[f"cluster_{c}"] = profile

    results = {
        "optimal_k": optimal_k,
        "silhouette_score": round(max(silhouettes), 3),
        "calinski_harabasz": round(max(ch_scores), 2),
        "davies_bouldin": round(min(db_scores), 3),
        "cv_stability": round(np.mean(fold_silhouettes), 3),
        "cv_std": round(np.std(fold_silhouettes), 3),
        "feature_importance": feature_importance,
        "features_used": feature_cols,
        "cluster_profiles": cluster_profiles,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "clustering_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(
        f"[CLUSTER] Óptimo: {optimal_k} clusters (silhouette: {max(silhouettes):.3f})"
    )
    print(
        f"  CV stability: {np.mean(fold_silhouettes):.3f} ± {np.std(fold_silhouettes):.3f}"
    )
    print(
        f"  Calinski-Harabasz: {max(ch_scores):.1f} | Davies-Bouldin: {min(db_scores):.3f}"
    )
    return results


if __name__ == "__main__":
    run_clustering()
