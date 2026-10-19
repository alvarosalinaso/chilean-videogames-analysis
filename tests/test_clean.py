"""Tests for clean module."""

import json

import pandas as pd

from chilean_videogames.clean import _parse_itch, _parse_steam, build_dataset


def test_parse_steam_valid():
    """Test parsing valid Steam JSON."""
    steam_data = {
        "steam_appid": 12345,
        "name": "Test Game",
        "release_date": {"date": "15 Mar, 2023"},
        "is_free": False,
        "price_overview": {"final": 2990, "currency": "CLP"},
        "metacritic": {"score": 85},
        "recommendations": {"total": 1000},
        "genres": [{"description": "Action"}, {"description": "Adventure"}],
        "developers": ["Test Studio"],
        "publishers": ["Test Publisher"],
    }
    result = _parse_steam(steam_data)
    assert result is not None
    assert result["source"] == "steam"
    assert result["steam_id"] == 12345
    assert result["name"] == "Test Game"
    assert result["year"] == "2023"
    assert result["price"] == 29.90  # 2990 cents = 29.90
    assert result["currency"] == "CLP"
    assert result["metacritic"] == 85
    assert result["recommendations"] == 1000
    assert "Action" in result["genres"]
    assert result["developers"] == "Test Studio"
    assert result["publishers"] == "Test Publisher"


def test_parse_steam_missing_id():
    """Test parsing Steam JSON without appid returns None."""
    steam_data = {"name": "Test Game"}
    result = _parse_steam(steam_data)
    assert result is None


def test_parse_steam_free_game():
    """Test parsing free Steam game."""
    steam_data = {
        "steam_appid": 67890,
        "name": "Free Game",
        "release_date": {"date": "1 Jan, 2022"},
        "is_free": True,
        "price_overview": {},
        "metacritic": None,
        "recommendations": {"total": 500},
        "genres": [{"description": "Casual"}],
        "developers": ["Indie Dev"],
        "publishers": ["Indie Dev"],
    }
    result = _parse_steam(steam_data)
    assert result is not None
    assert result["is_free"] is True
    assert result["price"] == 0.0


def test_parse_itch_valid():
    """Test parsing valid Itch.io JSON."""
    itch_data = {
        "name": "Itch Game",
        "release_date": "2023-05-20",
        "price_text": "$15.99",
        "genre": "Platformer",
        "author": "Itch Dev",
    }
    result = _parse_itch(itch_data)
    assert result is not None
    assert result["source"] == "itch"
    assert result["steam_id"] is None
    assert result["name"] == "Itch Game"
    assert result["year"] == "2023"
    assert result["price"] == 15.99
    assert result["currency"] == "USD"
    assert result["is_free"] is False
    assert result["metacritic"] is None
    assert result["recommendations"] == 0
    assert result["genres"] == "Platformer"
    assert result["developers"] == "Itch Dev"
    assert result["publishers"] == "Self-published"


def test_parse_itch_free():
    """Test parsing free Itch.io game."""
    itch_data = {
        "name": "Free Itch Game",
        "release_date": "2022-01-01",
        "price_text": "Free",
        "genre": "RPG",
        "author": "Free Dev",
    }
    result = _parse_itch(itch_data)
    assert result is not None
    assert result["is_free"] is True
    assert result["price"] == 0.0


def test_parse_itch_european_price():
    """Test parsing Itch.io price with European format."""
    itch_data = {
        "name": "EU Game",
        "release_date": "2023",
        "price_text": "9,99€",
        "genre": "Strategy",
        "author": "EU Dev",
    }
    result = _parse_itch(itch_data)
    assert result is not None
    assert result["price"] == 9.99


def test_build_dataset_empty_dir(tmp_path):
    """Test build_dataset with empty directory."""
    result = build_dataset(tmp_path)
    assert isinstance(result, pd.DataFrame)
    assert result.empty


def test_build_dataset_with_json(tmp_path):
    """Test build_dataset with sample JSON files."""
    # Create sample Steam JSON
    steam_file = tmp_path / "game1.json"
    steam_data = {
        "source": "steam",
        "steam_appid": 111,
        "name": "Steam Game",
        "release_date": {"date": "1 Jan, 2023"},
        "is_free": False,
        "price_overview": {"final": 1000, "currency": "CLP"},
        "metacritic": {"score": 80},
        "recommendations": {"total": 100},
        "genres": [{"description": "Action"}],
        "developers": ["Dev A"],
        "publishers": ["Pub A"],
    }
    steam_file.write_text(json.dumps(steam_data))

    # Create sample Itch JSON
    itch_file = tmp_path / "game2.json"
    itch_data = {
        "source": "itch",
        "name": "Itch Game",
        "release_date": "2023-06-15",
        "price_text": "$10.00",
        "genre": "Puzzle",
        "author": "Dev B",
    }
    itch_file.write_text(json.dumps(itch_data))

    result = build_dataset(tmp_path)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert set(result["source"].tolist()) == {"steam", "itch"}


def test_build_dataset_excludes_non_chilean_titles(tmp_path):
    """Los títulos de NON_CHILEAN_TITLES no entran al dataset (ver scripts/fix_data.py)."""
    msfs = {
        "source": "steam",
        "steam_appid": 1250410,
        "name": "Microsoft Flight Simulator (2020) 40th Anniversary Edition",
        "release_date": {"date": "1 Jan, 2020"},
        "price_overview": {"final": 6000, "currency": "USD"},
        "genres": [{"description": "Simulation"}],
        "developers": ["Asobo Studio"],
        "publishers": ["Xbox Game Studios"],
    }
    chileno = {
        "source": "steam",
        "steam_appid": 111,
        "name": "Juego Chileno de Prueba",
        "release_date": {"date": "1 Jan, 2023"},
        "price_overview": {"final": 1000, "currency": "USD"},
        "genres": [{"description": "Action"}],
        "developers": ["Studio Local"],
        "publishers": ["Studio Local"],
    }
    (tmp_path / "msfs.json").write_text(json.dumps(msfs))
    (tmp_path / "local.json").write_text(json.dumps(chileno))

    result = build_dataset(tmp_path)

    assert len(result) == 1
    assert result.iloc[0]["name"] == "Juego Chileno de Prueba"
