"""Tests estadísticos formales para videojuegos chilenos."""

import json
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import pandas as pd
    from scipy import stats

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


def _to_json_serializable(obj: Any) -> Any:
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, (np.bool_, np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _to_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_json_serializable(v) for v in obj]
    return obj


BOXLEITER_FACTORS = (20, 30, 40, 50, 60)


def compute_hhi(df: pd.DataFrame, category_col: str = "primary_genre") -> dict:
    """Herfindahl-Hirschman Index por género (shares de conteo, x10000).

    Umbrales del DOJ: <1500 competitivo, 1500-2500 concentrado, >2500 muy
    concentrado. Unknown cuenta como categoría.
    """
    if category_col not in df.columns:
        return {}
    counts = (
        df[category_col]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .value_counts()
    )
    if len(counts) == 0:
        return {}
    total = int(counts.sum())
    shares = counts / total
    hhi = float((shares**2).sum() * 10000)
    return {
        "category_col": category_col,
        "n_categories": int(len(counts)),
        "n_games": total,
        "hhi": round(hhi, 1),
        "top_category": str(counts.index[0]),
        "top_share_pct": round(float(shares.iloc[0]) * 100, 1),
        "interpretation": "Competitivo (<1500)"
        if hhi < 1500
        else "Concentrado (1500-2500)"
        if hhi < 2500
        else "Muy concentrado (>2500)",
    }


def _collect_p_values(results: dict, prefix: str = "") -> list:
    """(ruta, p_value, dict_ref) de todos los p-values anidados en results."""
    found = []
    for key, value in results.items():
        if not isinstance(value, dict):
            continue
        path = f"{prefix}{key}"
        p_value = value.get("p_value")
        if isinstance(p_value, (int, float)) and not isinstance(p_value, bool):
            found.append((path, float(p_value), value))
        found.extend(_collect_p_values(value, prefix=f"{path}."))
    return found


def apply_holm_correction(results: dict, alpha: float = 0.05) -> dict:
    """Corrección de Holm-Bonferroni sobre todos los p-values de results.

    Ordena los p ascendentes y ajusta p_i por (m - i + 1), forzando
    monotonicidad no decreciente y tope en 1.0. Añade p_holm y
    significant_holm a cada test y un bloque holm_correction resumen.
    """
    entries = _collect_p_values(results)
    m = len(entries)
    if m == 0:
        return results

    ordered = sorted(entries, key=lambda e: e[1])
    running_max = 0.0
    adjusted: list[float] = []
    for i, (_, p_value, _) in enumerate(ordered):
        running_max = max(running_max, min(1.0, (m - i) * p_value))
        adjusted.append(running_max)

    for (_path, _, ref), adj in zip(ordered, adjusted, strict=True):
        ref["p_holm"] = round(adj, 6)
        ref["significant_holm"] = adj < alpha

    results["holm_correction"] = {
        "method": "Holm-Bonferroni",
        "alpha": alpha,
        "n_tests": m,
        "tests": [path for path, _, _ in ordered],
        "note": "p_holm >= p_value; un test significativo tras Holm es significativo también sin corrección.",
    }
    return results


def compute_boxleiter_sensitivity(df: pd.DataFrame, factors: tuple = BOXLEITER_FACTORS) -> dict:
    """Sensibilidad del factor Boxleiter: revenue = recs × factor × precio.

    El factor solo escala los montos linealmente: rankings y shares por
    género no cambian, únicamente cambian los totales absolutos.
    """
    required = {"source", "recommendations", "price_usd", "name"}
    if not required.issubset(df.columns):
        return {}

    steam = df[df["source"].astype(str).str.casefold().str.strip() == "steam"]
    valid = steam[["name", "recommendations", "price_usd"]].dropna()
    valid = valid[(valid["recommendations"] > 0) & (valid["price_usd"] > 0)]
    if len(valid) == 0:
        return {}

    units = valid["recommendations"] * valid["price_usd"]
    factor_stats: dict = {}
    for factor in factors:
        est = units * factor
        top_idx = est.idxmax()
        factor_stats[str(factor)] = {
            "total_revenue_est_usd": round(float(est.sum()), 2),
            "median_game_revenue_usd": round(float(est.median()), 2),
            "mean_game_revenue_usd": round(float(est.mean()), 2),
            "top_game": str(valid.loc[top_idx, "name"]),
            "top_game_revenue_usd": round(float(est.loc[top_idx]), 2),
        }

    return {
        "test": "Sensibilidad del factor Boxleiter",
        "formula": "revenue_est_usd = recommendations x factor x price_usd (Steam, recs>0 y price>0)",
        "base_factor": 40,
        "n_games": int(len(valid)),
        "factors": factor_stats,
        "linear_in_factor": True,
        "note": (
            "El factor es una escala lineal: el ranking de juegos y los shares "
            "por género no cambian entre 20x y 60x; solo cambian los montos absolutos."
        ),
    }


def run_statistical_tests(
    data_dir: Path = Path("data/processed"), output_dir: Path = Path("data/export")
) -> dict:
    if not SCIPY_AVAILABLE:
        print("[STATS] scipy no instalado")
        return {}

    # Try enriched CSV first (has price_usd), fallback to processed
    enriched = data_dir.parent / "export" / "chilean_games_final.csv"
    if enriched.exists():
        df = pd.read_csv(enriched, encoding="utf-8")
    else:
        df = pd.read_csv(data_dir / "games.csv", encoding="utf-8")
    results = {}

    # Normalize source column (casefold: 'Steam', 'STEAM', 'steam' → 'steam')
    df["source"] = df["source"].astype(str).str.casefold().str.strip()

    # 1. T-test: Steam vs Itch.io prices
    if "price_usd" not in df.columns:
        print("[STATS] price_usd column not found, skipping price tests")
        return results

    steam = df[df["source"] == "steam"]["price_usd"].dropna()
    itch = df[df["source"].str.contains("itch", na=False)]["price_usd"].dropna()
    if len(steam) > 2 and len(itch) > 2:
        t_stat, p_value = stats.ttest_ind(steam, itch, equal_var=False)
        ci_steam = stats.t.interval(0.95, len(steam) - 1, loc=steam.mean(), scale=stats.sem(steam))
        ci_itch = stats.t.interval(0.95, len(itch) - 1, loc=itch.mean(), scale=stats.sem(itch))
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
            "effect_size_cohens_d": round(
                (steam.mean() - itch.mean()) / np.sqrt((steam.std() ** 2 + itch.std() ** 2) / 2),
                3,
            ),
        }
        print(
            f"[STATS] T-test: t={t_stat:.3f}, p={p_value:.4f} {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'n.s.'}"
        )

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

    # 3. Pearson: precio vs recomendaciones (solo Steam)
    # Nota: la RQ5 antigua (recomendaciones vs revenue) era circular porque
    # revenue = recommendations × 40 × price. Se correlaciona precio con
    # recomendaciones, que son variables medidas independientemente.
    if "recommendations" in df.columns and "price_usd" in df.columns:
        steam_df = df[df["source"] == "steam"]
        valid = steam_df[["recommendations", "price_usd"]].dropna()
        valid = valid[(valid["recommendations"] > 0) & (valid["price_usd"] > 0)]
        if len(valid) > 10:
            r, p_corr = stats.pearsonr(valid["price_usd"], valid["recommendations"])
            results["pearson_price_vs_recs"] = {
                "test": "Pearson correlation",
                "h0": "No hay correlación entre precio y recomendaciones (Steam)",
                "r": round(r, 4),
                "r_squared": round(r**2, 4),
                "p_value": round(p_corr, 6),
                "significant": p_corr < 0.05,
                "n_observations": len(valid),
                "interpretation": "Fuerte"
                if abs(r) > 0.7
                else "Moderada"
                if abs(r) > 0.4
                else "Débil",
            }
            print(f"[STATS] Pearson precio vs recs: r={r:.3f}, p={p_corr:.4f}, R²={r**2:.3f}")

    # 4. Sensibilidad del factor Boxleiter (20 a 60)
    sensitivity = compute_boxleiter_sensitivity(df)
    if sensitivity:
        results["boxleiter_sensitivity"] = sensitivity
        totals = sensitivity["factors"]
        print(
            "[STATS] Boxleiter total: "
            f"20x=${totals['20']['total_revenue_est_usd']:,.0f}, "
            f"40x=${totals['40']['total_revenue_est_usd']:,.0f}, "
            f"60x=${totals['60']['total_revenue_est_usd']:,.0f}"
        )

    # 5. HHI por género
    hhi = compute_hhi(df)
    if hhi:
        results["hhi_by_genre"] = hhi
        print(
            f"[STATS] HHI({hhi['category_col']}): {hhi['hhi']:.1f} "
            f"({hhi['interpretation']}; {hhi['n_categories']} categorías)"
        )

    # 6. Corrección Holm-Bonferroni sobre todos los p-values del módulo
    results = apply_holm_correction(results)
    holm = results.get("holm_correction")
    if holm:
        print(f"[STATS] Holm-Bonferroni: {holm['n_tests']} p-values corregidos")

    output_dir.mkdir(parents=True, exist_ok=True)
    results = _to_json_serializable(results)
    with open(output_dir / "statistical_tests.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results
