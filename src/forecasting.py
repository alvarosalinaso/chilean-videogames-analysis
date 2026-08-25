"""
Forecasting de lanzamientos y revenue de videojuegos chilenos.
ARIMA + Exponential Smoothing + Prophet (si disponible).
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

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False


def run_forecasting(data_dir: Path = Path("data/processed"), output_dir: Path = Path("data/export")) -> dict:
    """
    Forecast de lanzamientos y revenue por año.
    
    Returns:
        dict con predicciones 2026-2028 y métricas de error
    """
    if not PANDAS_AVAILABLE or not STATSMODELS_AVAILABLE:
        print("[FORECAST] pandas/statsmodels no instalados")
        return {}

    df = pd.read_csv(data_dir / "games.csv", encoding="utf-8")
    
    if "year" not in df.columns:
        print("[FORECAST] Columna 'year' no encontrada")
        return {}
    
    results = {}
    
    # 1. Forecast de lanzamientos por año
    yearly = df.groupby("year").size().reset_index(name="releases")
    yearly = yearly[yearly["year"] >= 2010].sort_values("year")
    
    if len(yearly) >= 5:
        ts = yearly.set_index("year")["releases"]
        
        # Augmented Dickey-Fuller test
        adf_result = adfuller(ts.dropna())
        
        # ARIMA forecast
        try:
            model_arima = ARIMA(ts, order=(1, 1, 1))
            fit_arima = model_arima.fit()
            forecast_arima = fit_arima.forecast(steps=3)
            
            # In-sample fit
            fitted = fit_arima.fittedvalues
            mae = np.mean(np.abs(ts.values - fitted.values[:len(ts)]))
            mape = np.mean(np.abs((ts.values - fitted.values[:len(ts)]) / (ts.values + 1e-8))) * 100
            
            results["releases_arima"] = {
                "model": "ARIMA(1,1,1)",
                "adf_statistic": round(adf_result[0], 4),
                "adf_p_value": round(adf_result[1], 4),
                "stationary": adf_result[1] < 0.05,
                "forecast_2026_2028": [round(max(0, v), 0) for v in forecast_arima.values],
                "mae": round(mae, 2),
                "mape": round(mape, 2),
                "historical": {int(k): int(v) for k, v in ts.items()},
            }
            print(f"[FORECAST] ARIMA releases: 2026={forecast_arima.values[0]:.0f}, 2027={forecast_arima.values[1]:.0f}, 2028={forecast_arima.values[2]:.0f}")
        except Exception as e:
            print(f"[FORECAST] ARIMA error: {e}")
        
        # Exponential Smoothing
        try:
            model_es = ExponentialSmoothing(ts, trend="add", seasonal=None, initialization_method="estimated")
            fit_es = model_es.fit(optimized=True)
            forecast_es = fit_es.forecast(steps=3)
            
            results["releases_exponential_smoothing"] = {
                "model": "Holt's Linear Exponential Smoothing",
                "forecast_2026_2028": [round(max(0, v), 0) for v in forecast_es.values],
                "alpha": round(fit_es.params.get("smoothing_level", 0), 4),
                "beta": round(fit_es.params.get("smoothing_trend", 0), 4),
            }
            print(f"[FORECAST] ES releases: 2026={forecast_es.values[0]:.0f}, 2027={forecast_es.values[1]:.0f}, 2028={forecast_es.values[2]:.0f}")
        except Exception as e:
            print(f"[FORECAST] ES error: {e}")
    
    # 2. Forecast de revenue por año (Steam only)
    steam = df[df["source"] == "Steam"].copy()
    if "gross_revenue_est_usd" in steam.columns and len(steam) >= 10:
        rev_yearly = steam.groupby("year")["gross_revenue_est_usd"].sum().reset_index()
        rev_yearly = rev_yearly[rev_yearly["year"] >= 2015].sort_values("year")
        
        if len(rev_yearly) >= 5:
            ts_rev = rev_yearly.set_index("year")["gross_revenue_est_usd"]
            
            try:
                model_rev = ARIMA(ts_rev, order=(1, 1, 0))
                fit_rev = model_rev.fit()
                forecast_rev = fit_rev.forecast(steps=3)
                
                results["revenue_arima"] = {
                    "model": "ARIMA(1,1,0)",
                    "forecast_2026_2028": [round(max(0, v), 2) for v in forecast_rev.values],
                    "historical_total": round(ts_rev.sum(), 2),
                }
                print(f"[FORECAST] ARIMA revenue: 2026=${forecast_rev.values[0]:,.0f}, 2027=${forecast_rev.values[1]:,.0f}")
            except Exception as e:
                print(f"[FORECAST] Revenue ARIMA error: {e}")
    
    # 3. Trend analysis
    if len(yearly) >= 3:
        x = yearly["year"].values
        y = yearly["releases"].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        results["trend_analysis"] = {
            "slope": round(slope, 3),
            "r_squared": round(r_value**2, 4),
            "p_value": round(p_value, 6),
            "annual_growth_rate": round(slope, 2),
            "interpretation": f"Crecimiento de {slope:.1f} lanzamientos por año (R²={r_value**2:.3f})",
        }
        print(f"[FORECAST] Trend: +{slope:.1f} games/year, R²={r_value**2:.3f}, p={p_value:.4f}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "forecasting_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results


if __name__ == "__main__":
    run_forecasting()