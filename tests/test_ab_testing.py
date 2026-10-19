"""Tests for ab_testing module (chilean-videogames-analysis)."""

from pathlib import Path

import pytest

REPO_EXPORT = Path(__file__).resolve().parents[1] / "data" / "export"


def test_ab_testing_missing_csv_returns_empty(tmp_path):
    """Sin CSV enriquecido devuelve {} en vez de explotar."""
    from chilean_videogames.ab_testing import run_ab_testing

    result = run_ab_testing(export_dir=tmp_path, output_dir=tmp_path / "out")
    assert result == {}


@pytest.mark.skipif(
    not (REPO_EXPORT / "chilean_games_final.csv").exists(),
    reason="chilean_games_final.csv no encontrado (corre analyze_all)",
)
def test_ab_testing_runs_at_least_one_statistical_test(tmp_path):
    """Al menos un test estadístico se ejecuta sobre el CSV enriquecido real."""
    from chilean_videogames.ab_testing import run_ab_testing

    results = run_ab_testing(export_dir=REPO_EXPORT, output_dir=tmp_path)

    tests_with_p = [
        key for key, value in results.items() if isinstance(value, dict) and "p_value" in value
    ]
    assert len(tests_with_p) >= 1, f"ningún test corrió: {list(results)}"
    assert results["ab_summary"]["n_tests"] >= 1
    assert (tmp_path / "ab_testing_results.json").exists()
