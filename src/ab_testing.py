"""
A/B Testing: Steam vs Itch.io como grupos experimentales.
Compara métricas de rendimiento con tests de hipótesis formales.
"""
import json
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    from scipy import stats
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def compute_power(effect_size: float, n: float, alpha: float = 0.05) -> float:
    """Calcula poder estadístico aproximado."""
    from scipy.stats import norm
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(0.80)  # 80% power
    ncp = effect_size * np.sqrt(n / 2)
    power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)
    return round(power, 4)


def compute_sample_size(effect_size: float, alpha: float = 0.05, power: float = 0.80) -> int:
    """Calcula tamaño de muestra necesario."""
    from scipy.stats import norm
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
    return int(np.ceil(n))


def run_ab_testing(data_dir: Path = Path("data/processed"), output_dir: Path = Path("data/export")) -> dict:
    """
    A/B testing: Steam (control) vs Itch.io (tratamiento).

    Tests:
    1. T-test: precios entre plataformas
    2. Chi-cuadrado: distribución de géneros
    3. Mann-Whitney: revenue (no paramétrico)
    4. Effect sizes (Cohen's d, Cramér's V)
    5. Power analysis
    6. Confidence intervals
    """
    if not PANDAS_AVAILABLE:
        print("[AB] pandas/scipy no instalados")
        return {}

    df = pd.read_csv(data_dir / "games.csv", encoding="utf-8")
    results = {}

    steam = df[df["source"] == "Steam"].copy()
    itch = df[df["source"] == "Itch.io"].copy()

    results["sample_sizes"] = {
        "steam_n": len(steam),
        "itch_n": len(itch),
        "total": len(df),
    }

    # 1. Price comparison (Welch's t-test)
    if "price_usd" in df.columns:
        steam_prices = steam["price_usd"].dropna()
        itch_prices = itch["price_usd"].dropna()

        if len(steam_prices) > 2 and len(itch_prices) > 2:
            t_stat, p_value = stats.ttest_ind(steam_prices, itch_prices, equal_var=False)

            # Cohen's d
            pooled_std = np.sqrt((steam_prices.std()**2 + itch_prices.std()**2) / 2)
            cohens_d = (steam_prices.mean() - itch_prices.mean()) / pooled_std if pooled_std > 0 else 0

            # CI for difference in means
            diff_mean = steam_prices.mean() - itch_prices.mean()
            se = np.sqrt(steam_prices.var()/len(steam_prices) + itch_prices.var()/len(itch_prices))
            ci_95 = (diff_mean - 1.96*se, diff_mean + 1.96*se)

            # Power analysis
            power = compute_power(abs(cohens_d), min(len(steam_prices), len(itch_prices)))
            n_needed = compute_sample_size(abs(cohens_d))

            results["price_test"] = {
                "test": "Welch's t-test",
                "h0": "No hay diferencia de precios entre Steam e Itch.io",
                "steam_mean": round(steam_prices.mean(), 2),
                "itch_mean": round(itch_prices.mean(), 2),
                "difference": round(diff_mean, 2),
                "ci_95_lower": round(ci_95[0], 2),
                "ci_95_upper": round(ci_95[1], 2),
                "t_statistic": round(t_stat, 4),
                "p_value": round(p_value, 6),
                "significant": p_value < 0.05,
                "cohens_d": round(cohens_d, 4),
                "effect_size": "grande" if abs(cohens_d) > 0.8 else "mediano" if abs(cohens_d) > 0.5 else "pequeño",
                "power": power,
                "sample_size_needed": n_needed,
                "adequately_powered": power >= 0.80,
            }
            print(f"[AB] Price: Steam=${steam_prices.mean():.2f}, Itch=${itch_prices.mean():.2f}, d={cohens_d:.3f}, p={p_value:.4f}, power={power:.3f}")

    # 2. Genre distribution (Chi-squared)
    if "primary_genre" in df.columns:
        genre_platform = pd.crosstab(df["source"], df["primary_genre"])
        chi2, p_chi, dof, expected = stats.chi2_contingency(genre_platform)

        # Cramér's V
        n = genre_platform.sum().sum()
        min_dim = min(genre_platform.shape) - 1
        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

        results["genre_test"] = {
            "test": "Chi-squared test of independence",
            "h0": "La distribución de géneros es independiente de la plataforma",
            "chi2_statistic": round(chi2, 4),
            "p_value": round(p_chi, 6),
            "significant": p_chi < 0.05,
            "degrees_of_freedom": dof,
            "cramers_v": round(cramers_v, 4),
            "effect_size": "grande" if cramers_v > 0.5 else "mediano" if cramers_v > 0.3 else "pequeño",
            "top_steam_genres": steam["primary_genre"].value_counts().head(5).to_dict(),
            "top_itch_genres": itch["primary_genre"].value_counts().head(5).to_dict(),
        }
        print(f"[AB] Genre chi2={chi2:.2f}, p={p_chi:.4f}, Cramer's V={cramers_v:.3f}")

    # 3. Revenue comparison (Mann-Whitney, non-parametric)
    if "gross_revenue_est_usd" in df.columns:
        steam_rev = steam["gross_revenue_est_usd"].dropna()
        itch_rev = itch["gross_revenue_est_usd"].dropna()

        if len(steam_rev) > 2 and len(itch_rev) > 2:
            u_stat, p_mw = stats.mannwhitneyu(steam_rev, itch_rev, alternative="two-sided")

            # Rank-biserial correlation (effect size)
            r_rb = 1 - (2 * u_stat) / (len(steam_rev) * len(itch_rev))

            results["revenue_test"] = {
                "test": "Mann-Whitney U (non-parametric)",
                "h0": "No hay diferencia en distribucion de revenue entre plataformas",
                "steam_median": round(steam_rev.median(), 2),
                "itch_median": round(itch_rev.median(), 2),
                "u_statistic": round(u_stat, 2),
                "p_value": round(p_mw, 6),
                "significant": p_mw < 0.05,
                "rank_biserial_r": round(r_rb, 4),
                "interpretation": "Steam genera significativamente mas revenue" if p_mw < 0.05 and steam_rev.median() > itch_rev.median() else "No se puede concluir diferencia significativa",
            }
            print(f"[AB] Revenue U={u_stat:.0f}, p={p_mw:.4f}, r={r_rb:.3f}")

    # 4. Summary
    tests = [v for k, v in results.items() if isinstance(v, dict) and "p_value" in v]
    significant_tests = [t for t in tests if t.get("significant")]

    results["ab_summary"] = {
        "n_tests": len(tests),
        "n_significant": len(significant_tests),
        "conclusion": "Las plataformas difieren significativamente en multiples metricas" if len(significant_tests) >= 2 else "Las diferencias son limitadas",
        "platform_recommendation": "Steam para monetizacion, Itch.io para validacion" if len(significant_tests) >= 2 else "Ambas plataformas son viables",
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "ab_testing_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return results


if __name__ == "__main__":
    run_ab_testing()
