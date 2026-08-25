"""Tests estadísticos formales para videojuegos chilenos."""
import json
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def run_statistical_tests(data_dir: Path = Path("data/processed"), output_dir: Path = Path("data/export")) -> dict:
    if not SCIPY_AVAILABLE:
        print("[STATS] scipy no instalado")
        return {}

    df = pd.read_csv(data_dir / "games.csv", encoding="utf-8")
    results = {}

    # 1. T-test: Steam vs Itch.io prices
    steam = df[df["source"] == "Steam"]["price_usd"].dropna()
    itch = df[df["source"] == "Itch.io"]["price_usd"].dropna()
    if len(steam) > 2 and len(itch) > 2:
        t_stat, p_value = stats.ttest_ind(steam, itch, equal_var=False)
        ci_steam = stats.t.interval(0.95, len(steam)-1, loc=steam.mean(), scale=stats.sem(steam))
        ci_itch = stats.t.interval(0.95, len(itch)-1, loc=itch.mean(), scale=stats.sem(itch))
        results["ttest_steam_vs_itch"] = {
            "test": "Welch's t-test",
            "h0": "No hay diferencia significativa en precios entre Steam e Itch.io",
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_value, 6),
            "significant": p_value < 0.05,
            "steam_mean": round(steam.mean(), 2),
            "steam_ci_95": [round(ci_steam[0], 2), round(ci_steam[1], 2)],
            "itch_mean": round(itch.mean(), 2),
            "itch_ci_95": [round(ci_itch[0], 2), round(ci_itch[1], 2)],
            "effect_size_cohens_d": round((steam.mean() - itch.mean()) / np.sqrt((steam.std()**2 + itch.std()**2) / 2), 3),
        }
        print(f"[STATS] T-test: t={t_stat:.3f}, p={p_value:.4f} {'***' if p_value<0.001 else '**' if p_value<0.01 else '*' if p_value<0.05 else 'n.s.'}")

    # 2. ANOVA: Revenue by genre
    if "primary_genre" in df.columns and "gross_revenue_est_usd" in df.columns:
        genres = df.groupby("primary_genre")["gross_revenue_est_usd"].apply(list).dropna()
        genres = genres[genres.apply(len) >= 3]
        if len(genres) >= 2:
            f_stat, p_anova = stats.f_oneway(*genres.values)
            eta_sq = f_stat / (f_stat + len(df) - len(genres))
            results["anova_revenue_by_genre"] = {
                "test": "One-way ANOVA",
                "h0": "El revenue promedio es igual entre todos los géneros",
                "f_statistic": round(f_stat, 4),
                "p_value": round(p_anova, 6),
                "significant": p_anova < 0.05,
                "eta_squared": round(eta_sq, 4),
                "n_genres": len(genres),
            }
            print(f"[STATS] ANOVA: F={f_stat:.3f}, p={p_anova:.4f}, η²={eta_sq:.3f}")

    # 3. Pearson: recommendations vs revenue
    if "recommendations" in df.columns and "gross_revenue_est_usd" in df.columns:
        valid = df[["recommendations", "gross_revenue_est_usd"]].dropna()
        valid = valid[(valid["recommendations"] > 0) & (valid["gross_revenue_est_usd"] > 0)]
        if len(valid) > 10:
            r, p_corr = stats.pearsonr(valid["recommendations"], valid["gross_revenue_est_usd"])
            results["pearson_rec_vs_revenue"] = {
                "test": "Pearson correlation",
                "h0": "No hay correlación entre recomendaciones y revenue",
                "r": round(r, 4),
                "r_squared": round(r**2, 4),
                "p_value": round(p_corr, 6),
                "significant": p_corr < 0.05,
                "n_observations": len(valid),
                "interpretation": "Fuerte" if abs(r) > 0.7 else "Moderada" if abs(r) > 0.4 else "Débil",
            }
            print(f"[STATS] Pearson: r={r:.3f}, p={p_corr:.4f}, R²={r**2:.3f}")

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results
