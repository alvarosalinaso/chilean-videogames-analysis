"""Tests para scripts/readme_numbers.py: el README debe coincidir con el script."""

import importlib.util
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
README = REPO / "README.md"
EXPORT_CSV = REPO / "data" / "export" / "chilean_games_final.csv"
SCRIPT = REPO / "scripts" / "readme_numbers.py"

_spec = importlib.util.spec_from_file_location("readme_numbers", SCRIPT)
assert _spec and _spec.loader
rn = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rn)


@pytest.mark.skipif(
    not (README.exists() and EXPORT_CSV.exists()),
    reason="README.md o chilean_games_final.csv no encontrados",
)
def test_readme_block_matches_script():
    """El bloque generado del README == render del script sobre los datos del repo."""
    df = pd.read_csv(EXPORT_CSV, encoding="utf-8")
    expected = rn.render_markdown(rn.compute_numbers(df, rn.load_stats()))
    current = rn.extract_block(README.read_text(encoding="utf-8"))
    assert current is not None, "faltan los marcadores BEGIN/END GENERATED: readme_numbers"
    assert current.strip() == expected.strip(), (
        "el README no coincide con los datos actuales; "
        "ejecuta: python scripts/readme_numbers.py --write"
    )


@pytest.mark.skipif(not README.exists(), reason="README.md no encontrado")
def test_readme_has_required_sections_and_commands():
    text = README.read_text(encoding="utf-8")
    assert "Qué mide y qué no" in text
    assert "Fuentes y licencias" in text
    assert "python -m chilean_videogames.analyze_all" in text
    assert "python scripts/readme_numbers.py --check" in text
    assert rn.BEGIN_MARK in text and rn.END_MARK in text


def test_render_and_check_helpers_work_on_synthetic_data():
    """compute_numbers + render_markdown + extract/replace funcionan sin datos reales."""
    df = pd.DataFrame(
        {
            "source": ["Steam", "steam", "itch"],
            "name": ["A", "B", "C"],
            "price_usd": [10.0, 0.0, 0.0],
            "recommendations": [50, 0, 0],
            "primary_genre": ["Acción", "Acción", "Action"],
            "year": [2020, None, "Unknown"],
        }
    )
    numbers = rn.compute_numbers(df, {})
    assert numbers["n_total"] == 3
    assert numbers["n_steam"] == 2
    assert numbers["top_genre"] == "Acción"
    assert numbers["itch_paid_n"] == 0
    assert numbers["no_recs_n"] == 2

    block = rn.render_markdown(numbers)
    assert rn.BEGIN_MARK in block and rn.END_MARK in block
    assert "| Juegos en el dataset | 3 (2 Steam, 1 Itch.io) |" in block
    assert "n/a" in block  # stats vacíos -> p-values n/a

    readme = f"intro\n{rn.BEGIN_MARK}\nold\n{rn.END_MARK}\noutro"
    updated = rn.replace_block(readme, block)
    assert rn.extract_block(updated).strip() == block.strip()
    assert updated.startswith("intro")
    assert updated.endswith("outro")
