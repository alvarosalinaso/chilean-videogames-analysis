"""Integration tests for forecasting module (chilean-videogames-analysis)."""

import json

import pandas as pd

from chilean_videogames.forecasting import run_forecasting


def test_run_forecasting_returns_dict(tmp_path):
    """Test that run_forecasting returns a dict."""
    data_processed = tmp_path / "data" / "processed"
    data_processed.mkdir(parents=True)

    games_csv = data_processed / "games.csv"
    pd.DataFrame(
        {
            "source": ["steam", "steam", "steam", "itch", "itch"],
            "year": ["2019", "2020", "2021", "2020", "2021"],
            "price_usd": [10.0, 15.0, 20.0, 5.0, 10.0],
            "gross_revenue_est_usd": [1000, 2000, 3000, 500, 1500],
        }
    ).to_csv(games_csv, index=False)

    result = run_forecasting(data_dir=data_processed, output_dir=tmp_path / "data" / "export")
    assert isinstance(result, dict)


def test_run_forecasting_no_data(tmp_path):
    """Test run_forecasting with missing data."""
    result = run_forecasting(
        data_dir=tmp_path / "data" / "processed", output_dir=tmp_path / "data" / "export"
    )
    assert isinstance(result, dict)
    assert result == {}


def test_run_forecasting_creates_output(tmp_path):
    """Test that run_forecasting creates output files."""
    data_processed = tmp_path / "data" / "processed"
    data_processed.mkdir(parents=True)

    games_csv = data_processed / "games.csv"
    pd.DataFrame(
        {
            "source": ["steam", "steam", "steam"],
            "year": ["2019", "2020", "2021"],
            "price_usd": [10.0, 15.0, 20.0],
            "gross_revenue_est_usd": [1000, 2000, 3000],
        }
    ).to_csv(games_csv, index=False)

    run_forecasting(data_dir=data_processed, output_dir=tmp_path / "data" / "export")
    output_file = tmp_path / "data" / "export" / "forecasting_results.json"
    assert output_file.exists()

    with open(output_file) as f:
        content = json.load(f)
    assert isinstance(content, dict)


def test_run_forecasting_unknown_year_and_mixed_case_source(tmp_path):
    """Años 'Unknown' no rompen el filtro numérico y source se normaliza con casefold."""
    data_processed = tmp_path / "data" / "processed"
    data_processed.mkdir(parents=True)

    games_csv = data_processed / "games.csv"
    pd.DataFrame(
        {
            "source": [
                "Steam",
                "STEAM",
                "itch",
                "Itch",
                "steam",
                "ITCH",
                "steam",
                "itch",
                "Steam",
                "itch",
            ],
            "year": [
                "2010",
                "2010",
                "2011",
                "2012",
                "2013",
                "2014",
                "2015",
                "2016",
                "Unknown",
                "Unknown",
            ],
            "gross_revenue_est_usd": [1000, 2000, 0, 0, 3000, 0, 4000, 0, 0, 0],
        }
    ).to_csv(games_csv, index=False)

    result = run_forecasting(data_dir=data_processed, output_dir=tmp_path / "data" / "export")

    assert "releases_arima" in result
    historical = result["releases_arima"]["historical"]
    assert historical, "el histórico no debe quedar vacío"
    assert all(isinstance(y, int) for y in historical)
    assert historical[2010] == 2
    assert 2016 in historical
    assert "Unknown" not in historical
