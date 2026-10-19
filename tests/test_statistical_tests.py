"""Tests for statistical_tests module."""

import json

import pandas as pd
import pytest

from chilean_videogames.statistical_tests import (
    compute_boxleiter_sensitivity,
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
