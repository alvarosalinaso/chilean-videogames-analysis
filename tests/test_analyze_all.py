"""Integration tests for analyze_all module (chilean-videogames-analysis)."""

import pandas as pd
import pytest
from pathlib import Path

from chilean_videogames.analyze_all import load_and_enrich_data


def test_load_and_enrich_data_returns_dataframe(tmp_path, monkeypatch):
    """Test that load_and_enrich_data returns enriched DataFrame."""
    import chilean_videogames.analyze_all as aa_module
    monkeypatch.setattr(aa_module, "Path", lambda x: tmp_path / x)
    
    # Create sample games.csv
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)
    
    games_csv = processed_dir / "games.csv"
    pd.DataFrame({
        "source": ["steam", "steam", "itch"],
        "name": ["Game A", "Game B", "Game C"],
        "year": ["2020", "2021", "2022"],
        "recommendations": [100, 200, 0],
        "price": [10.0, 20.0, 5.0],
        "currency": ["USD", "USD", "USD"],
        "genres": ["Action, Adventure", "RPG", "Platformer"],
        "developers": ["Dev A", "Dev B", "Dev C"],
    }).to_csv(games_csv, index=False)
    
    result = load_and_enrich_data()
    
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    # Check enriched columns
    assert "estimated_copies" in result.columns
    assert "price_usd" in result.columns
    assert "gross_revenue_est_usd" in result.columns
    assert "primary_genre" in result.columns
    assert "dev_location" in result.columns
    # Check Boxleiter factor applied
    assert result.loc[0, "estimated_copies"] == 4000  # 100 * 40
    assert result.loc[1, "estimated_copies"] == 8000  # 200 * 40
    assert result.loc[2, "estimated_copies"] == 0  # itch game
    # Check primary genre extraction
    assert result.loc[0, "primary_genre"] == "Action"
    assert result.loc[1, "primary_genre"] == "RPG"
    assert result.loc[2, "primary_genre"] == "Platformer"


def test_load_and_enrich_data_missing_file(tmp_path, monkeypatch):
    """Test load_and_enrich_data with missing input file."""
    import chilean_videogames.analyze_all as aa_module
    monkeypatch.setattr(aa_module, "Path", lambda x: tmp_path / x)
    
    result = load_and_enrich_data()
    assert result is None


def test_load_and_enrich_data_empty(tmp_path, monkeypatch):
    """Test load_and_enrich_data with empty CSV."""
    import chilean_videogames.analyze_all as aa_module
    monkeypatch.setattr(aa_module, "Path", lambda x: tmp_path / x)
    
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)
    
    games_csv = processed_dir / "games.csv"
    pd.DataFrame(columns=["source", "name", "year", "recommendations", "price", "currency", "genres", "developers"]).to_csv(games_csv, index=False)
    
    result = load_and_enrich_data()
    assert result is not None
    assert len(result) == 0


def test_boxleiter_factor_documentation():
    """Verify Boxleiter factor is documented and reasonable."""
    import chilean_videogames.analyze_all as aa_module
    import inspect
    
    source = inspect.getsource(aa_module.load_and_enrich_data)
    assert "BOXLEITER_FACTOR = 40" in source
    assert "Boxleiter method" in source
    assert "gamedeveloper.com" in source
    assert "ESTIMACIÓN APROXIMADA" in source


def test_enrichment_pipeline_columns(tmp_path, monkeypatch):
    """Test all expected enrichment columns are created."""
    import chilean_videogames.analyze_all as aa_module
    monkeypatch.setattr(aa_module, "Path", lambda x: tmp_path / x)
    
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)
    
    games_csv = processed_dir / "games.csv"
    pd.DataFrame({
        "source": ["steam"],
        "name": ["Test Game"],
        "year": ["2020"],
        "recommendations": [50],
        "price": [15.0],
        "currency": ["USD"],
        "genres": ["Action, Adventure"],
        "developers": ["Test Studio"],
    }).to_csv(games_csv, index=False)
    
    result = load_and_enrich_data()
    
    expected_columns = {
        "estimated_copies", "price_usd", "gross_revenue_est_usd",
        "primary_genre", "dev_location", "year"
    }
    assert expected_columns.issubset(set(result.columns))