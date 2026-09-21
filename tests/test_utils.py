"""Tests for utils module."""

import pytest

from chilean_videogames.utils import (
    setup_logger,
    parse_price_steam,
    parse_price_itch,
    parse_date,
    extract_year,
    normalize_currency_to_usd,
    get_location,
)


def test_setup_logger():
    """Test logger setup."""
    logger = setup_logger("test_module")
    assert logger is not None
    assert logger.level == 20  # INFO level


def test_parse_price_steam_valid():
    """Test parsing Steam price from cents."""
    price_data = {"final": 2990}
    result = parse_price_steam(price_data)
    assert result == 29.90


def test_parse_price_steam_zero():
    """Test parsing zero price."""
    price_data = {"final": 0}
    result = parse_price_steam(price_data)
    assert result == 0.0


def test_parse_price_steam_empty():
    """Test parsing empty price data."""
    result = parse_price_steam({})
    assert result == 0.0
    result = parse_price_steam(None)
    assert result == 0.0


def test_parse_price_itch_dollar():
    """Test parsing Itch.io price in dollars."""
    assert parse_price_itch("$15.99") == 15.99
    assert parse_price_itch("$10") == 10.0
    assert parse_price_itch("USD 5.50") == 5.5


def test_parse_price_itch_free():
    """Test parsing free Itch.io game."""
    assert parse_price_itch("Free") == 0.0
    assert parse_price_itch("free") == 0.0
    assert parse_price_itch("FREE") == 0.0
    assert parse_price_itch("No cost") == 0.0


def test_parse_price_itch_european():
    """Test parsing European price format."""
    assert parse_price_itch("9,99€") == 9.99
    assert parse_price_itch("19,50 €") == 19.5


def test_parse_price_itch_invalid():
    """Test parsing invalid price text."""
    assert parse_price_itch("") == 0.0
    assert parse_price_itch("N/A") == 0.0
    assert parse_price_itch(None) == 0.0


def test_parse_date():
    """Test parse_date returns stripped string."""
    assert parse_date(" 2023-01-15 ") == "2023-01-15"
    assert parse_date("") == ""
    assert parse_date(None) == ""


def test_extract_year_valid():
    """Test extracting year from various date formats."""
    assert extract_year("15 Mar, 2023") == "2023"
    assert extract_year("2023-01-15") == "2023"
    assert extract_year("January 1, 2022") == "2022"
    assert extract_year("2021") == "2021"
    assert extract_year("1999-12-31") == "1999"


def test_extract_year_invalid():
    """Test extracting year from invalid strings."""
    assert extract_year("") == "Unknown"
    assert extract_year("No date") == "Unknown"
    assert extract_year(None) == "Unknown"
    assert extract_year("31 Dec") == "Unknown"


def test_normalize_currency_to_usd_clp():
    """Test CLP to USD conversion."""
    result = normalize_currency_to_usd(950, "CLP")
    assert result == 1.0  # 950 CLP / 950 = 1 USD


def test_normalize_currency_to_usd_usd():
    """Test USD to USD (no conversion)."""
    result = normalize_currency_to_usd(10.0, "USD")
    assert result == 10.0


def test_normalize_currency_to_usd_eur():
    """Test EUR to USD conversion."""
    result = normalize_currency_to_usd(10.0, "EUR")
    assert result == 11.0  # 10 * 1.10


def test_normalize_currency_to_usd_unknown():
    """Test unknown currency defaults to 1.0 rate."""
    result = normalize_currency_to_usd(100, "XYZ")
    assert result == 100.0


def test_normalize_currency_to_usd_zero():
    """Test zero price returns zero."""
    assert normalize_currency_to_usd(0, "CLP") == 0.0


def test_get_location_known_studio():
    """Test location lookup for known studios."""
    assert get_location("ACE Team") == "Santiago"
    assert get_location("Playmestudio") == "Valparaíso"
    assert get_location("Niebla Games") == "Valparaíso"


def test_get_location_multiple_devs():
    """Test location with multiple developers (first match wins)."""
    assert get_location("ACE Team, Some Other Studio") == "Santiago"
    assert get_location("Unknown Dev, Playmestudio") == "Valparaíso"


def test_get_location_unknown():
    """Test unknown developer returns default."""
    assert get_location("Completely Unknown Studio") == "Chile (General)"
    assert get_location("") == "Chile (General)"
    assert get_location(None) == "Chile (General)"