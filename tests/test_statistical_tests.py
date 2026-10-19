"""Tests for statistical_tests module."""

import json

import pandas as pd
import pytest

from chilean_videogames.statistical_tests import (
    apply_holm_correction,
    compute_boxleiter_sensitivity,
    compute_hhi,
    run_statistical_tests,
)


def test_run_statistical_tests_returns_dict(tmp_path):
    """Test that run_statistical_tests returns a dict."""
    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    # Create minimal games.csv with required columns
    games_csv = data_dir / "games.csv"
    pd.DataFrame(
        {
            "source": ["steam", "steam", "itch", "itch"],
            "price_usd": [10.0, 20.0, 5.0, 15.0],
            "primary_genre": ["Action", "Action", "RPG", "RPG"],
            "gross_revenue_est_usd": [1000, 2000, 500, 1500],
            "recommendations": [100, 200, 50, 150],
        }
    ).to_csv(games_csv, index=False)

    result = run_statistical_tests(data_dir=data_dir, output_dir=output_dir)
    assert isinstance(result, dict)


def test_run_statistical_tests_creates_output(tmp_path):
    """Test that run_statistical_tests creates statistical_tests.json."""
    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    games_csv = data_dir / "games.csv"
    pd.DataFrame(
        {
            "source": ["steam", "steam", "itch", "itch"],
            "price_usd": [10.0, 20.0, 5.0, 15.0],
            "primary_genre": ["Action", "Action", "RPG", "RPG"],
            "gross_revenue_est_usd": [1000, 2000, 500, 1500],
            "recommendations": [100, 200, 50, 150],
        }
    ).to_csv(games_csv, index=False)

    run_statistical_tests(data_dir=data_dir, output_dir=output_dir)
    output_file = output_dir / "statistical_tests.json"
    assert output_file.exists()

    with open(output_file) as f:
        content = json.load(f)
    assert isinstance(content, dict)


def test_run_statistical_tests_no_scipy(tmp_path, monkeypatch):
    """Test run_statistical_tests when scipy not available."""
    import chilean_videogames.statistical_tests as stats_module

    monkeypatch.setattr(stats_module, "SCIPY_AVAILABLE", False)

    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    result = run_statistical_tests(data_dir=data_dir, output_dir=output_dir)
    assert result == {}


def test_run_statistical_tests_insufficient_data(tmp_path):
    """Test run_statistical_tests with insufficient data."""
    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    games_csv = data_dir / "games.csv"
    pd.DataFrame(
        {
            "source": ["steam"],
            "price_usd": [10.0],
        }
    ).to_csv(games_csv, index=False)

    result = run_statistical_tests(data_dir=data_dir, output_dir=output_dir)
    assert isinstance(result, dict)
    # Should not have ttest with only 1 sample per group
    assert "ttest_steam_vs_itch" not in result


def test_run_statistical_tests_mixed_case_source(tmp_path):
    """source con mayúsculas distintas se normaliza con casefold antes de agrupar."""
    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    games_csv = data_dir / "games.csv"
    pd.DataFrame(
        {
            "source": ["Steam", "STEAM", "steam", "Itch", "ITCH", "itch"],
            "price_usd": [10.0, 15.0, 20.0, 5.0, 8.0, 11.0],
        }
    ).to_csv(games_csv, index=False)

    result = run_statistical_tests(data_dir=data_dir, output_dir=output_dir)

    assert "ttest_steam_vs_itch" in result
    assert result["ttest_steam_vs_itch"]["steam_mean"] == 15.0
    assert result["ttest_steam_vs_itch"]["itch_mean"] == 8.0


def test_pearson_price_vs_recs_replaces_circular_rq5(tmp_path):
    """La RQ5 circular (recs vs revenue) se reemplaza por precio vs recs."""
    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    # 15 juegos Steam: precio y recomendaciones variables independientes
    n = 15
    pd.DataFrame(
        {
            "source": ["steam"] * n,
            "price_usd": [float(5 + i) for i in range(n)],
            "recommendations": [10 * ((i % 3) + 1) for i in range(n)],
            "gross_revenue_est_usd": [float(100 * (i + 1)) for i in range(n)],
        }
    ).to_csv(data_dir / "games.csv", index=False)

    result = run_statistical_tests(data_dir=data_dir, output_dir=output_dir)

    assert "pearson_rec_vs_revenue" not in result, "RQ5 circular aún presente"
    assert "pearson_price_vs_recs" in result
    pearson = result["pearson_price_vs_recs"]
    assert pearson["n_observations"] == n
    assert pearson["test"] == "Pearson correlation"


def test_boxleiter_sensitivity_linear_scaling():
    """Los totales 20x/40x/60x escalan linealmente (proporción 1:2:3)."""
    df = pd.DataFrame(
        {
            "source": ["steam", "steam", "steam", "itch"],
            "name": ["A", "B", "C", "D"],
            "recommendations": [100, 50, 20, 999],
            "price_usd": [10.0, 5.0, 2.5, 99.0],
        }
    )

    result = compute_boxleiter_sensitivity(df)

    assert result["base_factor"] == 40
    assert result["n_games"] == 3  # solo Steam con recs>0 y price>0
    factors = result["factors"]
    t20 = factors["20"]["total_revenue_est_usd"]
    t40 = factors["40"]["total_revenue_est_usd"]
    t60 = factors["60"]["total_revenue_est_usd"]
    assert t40 == pytest.approx(2 * t20)
    assert t60 == pytest.approx(3 * t20)
    assert factors["40"]["top_game"] == "A"
    assert factors["40"]["top_game_revenue_usd"] == pytest.approx(100 * 40 * 10.0)
    assert result["linear_in_factor"] is True


def test_boxleiter_sensitivity_in_run(tmp_path):
    """run_statistical_tests incluye la sensibilidad Boxleiter con fórmula correcta."""
    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    pd.DataFrame(
        {
            "source": ["steam", "steam"],
            "name": ["Alpha", "Beta"],
            "price_usd": [10.0, 4.0],
            "recommendations": [30, 10],
        }
    ).to_csv(data_dir / "games.csv", index=False)

    result = run_statistical_tests(data_dir=data_dir, output_dir=output_dir)

    assert "boxleiter_sensitivity" in result
    sens = result["boxleiter_sensitivity"]
    expected_40 = (30 * 10.0 + 10 * 4.0) * 40
    assert sens["factors"]["40"]["total_revenue_est_usd"] == pytest.approx(expected_40)
    assert sens["factors"]["20"]["total_revenue_est_usd"] == pytest.approx(expected_40 / 2)


def test_boxleiter_sensitivity_empty_without_columns():
    """Sin columnas requeridas devuelve {} sin lanzar error."""
    assert compute_boxleiter_sensitivity(pd.DataFrame({"x": [1]})) == {}


def test_compute_hhi_known_shares():
    """HHI de shares conocidos: 50/50 -> 5000; 10 categorías iguales -> 1000."""
    df = pd.DataFrame({"primary_genre": ["A"] * 5 + ["B"] * 5})
    result = compute_hhi(df)
    assert result["hhi"] == pytest.approx(5000.0)
    assert result["n_categories"] == 2
    assert result["n_games"] == 10
    assert result["interpretation"] == "Muy concentrado (>2500)"

    df10 = pd.DataFrame({"primary_genre": [f"G{i}" for i in range(10)] * 3})
    result10 = compute_hhi(df10)
    assert result10["hhi"] == pytest.approx(1000.0)
    assert result10["interpretation"] == "Competitivo (<1500)"


def test_compute_hhi_unknown_as_category_and_missing_col():
    """None/vacío se cuentan como Unknown; columna ausente devuelve {}."""
    df = pd.DataFrame({"primary_genre": ["Action", None, "", "Action"]})
    result = compute_hhi(df)
    assert result["n_games"] == 4
    assert result["n_categories"] == 2  # Action(2) + Unknown(2)
    assert result["hhi"] == pytest.approx(5000.0)
    assert compute_hhi(pd.DataFrame({"otra": [1]})) == {}


def test_apply_holm_correction_known_example():
    """Ejemplo known: p=[0.01, 0.03, 0.04] -> Holm [0.03, 0.06, 0.06]."""
    results = {
        "t1": {"p_value": 0.01},
        "t2": {"p_value": 0.04},
        "t3": {"p_value": 0.03},
        "sin_p": {"x": 1},
    }
    out = apply_holm_correction(results)
    assert out["t1"]["p_holm"] == pytest.approx(0.03)
    assert out["t3"]["p_holm"] == pytest.approx(0.06)
    assert out["t2"]["p_holm"] == pytest.approx(0.06)
    assert out["t1"]["significant_holm"] is True
    assert out["t2"]["significant_holm"] is False
    holm = out["holm_correction"]
    assert holm["n_tests"] == 3
    assert holm["tests"][0] == "t1"
    for entry in out.values():
        if isinstance(entry, dict) and "p_value" in entry:
            assert entry["p_holm"] >= entry["p_value"]


def test_apply_holm_correction_no_p_values():
    """Sin p-values no añade bloque ni modifica nada."""
    results = {"a": {"x": 1}}
    assert apply_holm_correction(results) == {"a": {"x": 1}}


def test_run_statistical_tests_includes_hhi_and_holm(tmp_path):
    """run_statistical_tests expone HHI por género y Holm sobre los p-values."""
    data_dir = tmp_path / "processed"
    output_dir = tmp_path / "export"
    data_dir.mkdir()
    output_dir.mkdir()

    rows = {
        "source": ["steam"] * 15 + ["itch"] * 5,
        "name": [f"G{i}" for i in range(20)],
        "price_usd": [float(5 + (i % 8)) for i in range(20)],
        "recommendations": [10 * ((i % 4) + 1) for i in range(20)],
        "primary_genre": (["Action"] * 8 + ["RPG"] * 7) + ["Casual"] * 5,
        "gross_revenue_est_usd": [float(200 * (i + 1)) for i in range(20)],
    }
    pd.DataFrame(rows).to_csv(data_dir / "games.csv", index=False)

    result = run_statistical_tests(data_dir=data_dir, output_dir=output_dir)

    assert "hhi_by_genre" in result
    # Action 8, RPG 7, Casual 5 de 20 -> shares .4/.35/.25
    expected_hhi = (0.4**2 + 0.35**2 + 0.25**2) * 10000
    assert result["hhi_by_genre"]["hhi"] == pytest.approx(expected_hhi, abs=0.1)

    assert "holm_correction" in result
    tested = ["ttest_steam_vs_itch", "anova_revenue_by_genre", "pearson_price_vs_recs"]
    for key in tested:
        assert key in result
        assert "p_holm" in result[key], f"{key} sin corrección Holm"
    assert result["holm_correction"]["n_tests"] == len(tested)
