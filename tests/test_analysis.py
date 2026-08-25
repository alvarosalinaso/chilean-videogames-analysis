"""Smoke tests for chilean-videogames-analysis."""
import pytest


def test_imports():
    from src.clustering_analysis import run_clustering
    from src.ab_testing import run_ab_testing
    from src.forecasting import run_forecasting
    from src.statistical_tests import run_statistical_tests
    from src.generate_tables import generate
    from src.generate_report import generate_report
    assert callable(run_clustering)
    assert callable(run_ab_testing)
    assert callable(run_forecasting)
    assert callable(run_statistical_tests)
    assert callable(generate)
    assert callable(generate_report)


def test_statistical_tests_has_return():
    from src.statistical_tests import run_statistical_tests
    result = run_statistical_tests()
    assert isinstance(result, dict)
