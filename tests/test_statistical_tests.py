"""Tests for statistical_tests module."""

import json

import pandas as pd

from chilean_videogames.statistical_tests import run_statistical_tests


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
