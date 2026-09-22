"""Smoke tests for chilean-videogames-analysis."""

from pathlib import Path

import pytest

DATA_CSV = Path(__file__).parent.parent / "data" / "processed" / "games.csv"


def test_imports():
    from chilean_videogames.ab_testing import run_ab_testing
    from chilean_videogames.clustering_analysis import run_clustering
    from chilean_videogames.forecasting import run_forecasting
    from chilean_videogames.generate_report import generate_report
    from chilean_videogames.generate_tables import generate
    from chilean_videogames.statistical_tests import run_statistical_tests

    assert callable(run_clustering)
    assert callable(run_ab_testing)
    assert callable(run_forecasting)
    assert callable(run_statistical_tests)
    assert callable(generate)
    assert callable(generate_report)


def test_statistical_tests_has_return():
    if not DATA_CSV.exists():
        pytest.skip("games.csv not found")
    from chilean_videogames.statistical_tests import run_statistical_tests

    result = run_statistical_tests()
    assert isinstance(result, dict)
