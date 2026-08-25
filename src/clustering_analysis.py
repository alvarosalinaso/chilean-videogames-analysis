"""
Clusterización de videojuegos chilenos con scikit-learn.
Identifica segmentos de mercado usando K-Means + elbow method.
"""
import json
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def run_clustering(data_dir: Path = Path("data/export"), output_dir: Path = Path("data/export")) -> dict:
    """
    Clusteriza videojuegos chilenos por revenue, precio y Metacritic.

    Returns:
        dict con clusters encontrados y métricas
    """
    if not SKLEARN_AVAILABLE:
        print("[CLUSTER] scikit-learn no instalado. pip install scikit-learn")
        return {}

    csv_file = data_dir / "games.csv"
    if not csv_file.exists():
        # Try alternative paths
        alt = Path("data/processed/games.csv")
        if alt.exists():
            csv_file = alt
        else:
            print(f"[CLUSTER] {csv_file} not found")
            return {}

    df = pd.read_csv(csv_file, encoding="utf-8")

    # Features for clustering
    feature_cols = []
    if "price_usd" in df.columns:
        feature_cols.append("price_usd")
    if "gross_revenue_est_usd" in df.columns:
        feature_cols.append("gross_revenue_est_usd")
    if "recommendations" in df.columns:
        feature_cols.append("recommendations")
    if "metacritic" in df.columns:
        feature_cols.append("metacritic")

    if len(feature_cols) < 2:
        print("[CLUSTER] Need at least 2 numeric columns for clustering")
        return {}

    # Prepare data
    X = df[feature_cols].fillna(0).replace([np.inf, -np.inf], 0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Elbow method + silhouette
    inertias = []
    silhouettes = []
    K_range = range(2, min(8, len(df) // 5 + 1))

    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X_scaled, labels))

    # Optimal k (highest silhouette)
    optimal_k = list(K_range)[np.argmax(silhouettes)]

    # Final clustering
    km_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df["cluster"] = km_final.fit_predict(X_scaled)

    # Cluster profiles
    cluster_profiles = {}
    for c in range(optimal_k):
        cluster_df = df[df["cluster"] == c]
        profile = {
            "size": len(cluster_df),
            "pct": round(len(cluster_df) / len(df) * 100, 1),
        }
        for col in feature_cols:
            profile[f"{col}_mean"] = round(cluster_df[col].mean(), 2)
            profile[f"{col}_median"] = round(cluster_df[col].median(), 2)

        # Top games in cluster
        if "name" in cluster_df.columns:
            profile["top_games"] = cluster_df.nlargest(3, feature_cols[0])["name"].tolist()

        cluster_profiles[f"cluster_{c}"] = profile

    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "clustering_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "optimal_k": optimal_k,
            "silhouette_score": round(max(silhouettes), 3),
            "features_used": feature_cols,
            "cluster_profiles": cluster_profiles,
        }, f, ensure_ascii=False, indent=2)

    print(f"[CLUSTER] Óptimo: {optimal_k} clusters (silhouette: {max(silhouettes):.3f})")
    for name, profile in cluster_profiles.items():
        print(f"  {name}: {profile['size']} juegos ({profile['pct']}%) — revenue medio: ${profile.get('gross_revenue_est_usd_mean', 'N/A')}")

    return {"optimal_k": optimal_k, "profiles": cluster_profiles}


if __name__ == "__main__":
    run_clustering()
