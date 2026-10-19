"""Test de humo: pipeline completo (clean → analyze → exports) sobre una muestra.

No toca la data real del repo: todo se ejecuta en tmp_path.
"""

import json
from pathlib import Path

import pandas as pd

from chilean_videogames import analyze_all, export_visualizations
from chilean_videogames.clean import main as clean_main

STEAM_GAMES = [
    # (name, year, recommendations, price_usd, genre, metacritic)
    ("Sample Alpha", "2010", 50, 9.99, "Action", 70),
    ("Sample Beta", "2010", 120, 19.99, "RPG", 82),
    ("Sample Gamma", "2011", 0, 0.0, "Adventure", None),
    ("Sample Delta", "2012", 30, 4.99, "Platformer", 65),
    ("Sample Epsilon", "2013", 80, 14.99, "Action", 75),
    ("Sample Zeta", "2014", 0, 0.0, "Puzzle", None),
    ("Sample Eta", "2015", 200, 29.99, "Simulation", 88),
    ("Sample Theta", "2016", 10, 7.99, "Strategy", None),
]

ITCH_GAMES = [
    ("Itch Sample 1", "2017", "$5.00", "Action"),
    ("Itch Sample 2", "2018", "Free", "Puzzle"),
    ("Itch Sample 3", "Unknown", "$9.99", "Adventure"),
    ("Itch Sample 4", "2019", "$0.99", "RPG"),
]


def _write_sample_raw(raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for i, (name, year, recs, price, genre, mc) in enumerate(STEAM_GAMES):
        payload = {
            "steam_appid": 1000 + i,
            "name": name,
            "release_date": {"date": f"1 Jan, {year}"} if year != "Unknown" else {"date": ""},
            "is_free": price == 0,
            "price_overview": {"final": int(round(price * 100)), "currency": "USD"},
            "metacritic": {"score": mc} if mc else None,
            "recommendations": {"total": recs} if recs else None,
            "genres": [{"description": genre}],
            "developers": [f"Studio {i}"],
            "publishers": [f"Pub {i}"],
        }
        (raw_dir / f"{1000 + i}.json").write_text(json.dumps(payload), encoding="utf-8")

    for i, (name, year, price_text, genre) in enumerate(ITCH_GAMES):
        payload = {
            "source": "itch",
            "id": 9000 + i,
            "name": name,
            "url": f"https://sample{i}.itch.io/game",
            "author": f"Itch Dev {i}",
            "genre": genre,
            "price_text": price_text,
            "release_date": year,
        }
        (raw_dir / f"itch_{9000 + i}.json").write_text(json.dumps(payload), encoding="utf-8")


def test_full_pipeline_on_sample(tmp_path, monkeypatch):
    """clean + analyze_all + export_visualizations corren de punta a punta."""
    monkeypatch.chdir(tmp_path)
    _write_sample_raw(tmp_path / "data" / "raw")

    # 1. Limpieza: raw → data/processed/games.csv
    clean_main(tmp_path / "data" / "raw", tmp_path / "data" / "processed")
    processed = tmp_path / "data" / "processed" / "games.csv"
    assert processed.exists()
    assert len(pd.read_csv(processed)) == len(STEAM_GAMES) + len(ITCH_GAMES)

    # 2. Análisis completo: figuras, CSV enriquecido, clustering, forecast, A/B,
    #    tests estadísticos, tabla ejecutiva y reporte
    analyze_all.main()

    final_csv = tmp_path / "data" / "export" / "chilean_games_final.csv"
    assert final_csv.exists()
    enriched = pd.read_csv(final_csv)
    for col in ("price_usd", "gross_revenue_est_usd", "primary_genre", "dev_location"):
        assert col in enriched.columns

    figures = sorted((tmp_path / "assets").rglob("*.png"))
    assert len(figures) >= 4, f"se esperaban >=4 figuras, hay {len(figures)}"

    export_dir = tmp_path / "data" / "export"
    for json_name in (
        "forecasting_results.json",
        "ab_testing_results.json",
        "statistical_tests.json",
        "clustering_results.json",
    ):
        assert (export_dir / json_name).exists(), f"falta {json_name}"

    assert (tmp_path / "assets" / "executive_table.html").exists()
    assert (tmp_path / "docs" / "paper_report.md").exists()

    # 3. Export para visualizaciones externas (Observable, Datawrapper, Flourish)
    export_visualizations.main(base=tmp_path)
    assert (export_dir / "observable_distribucion.csv").exists()
    assert (export_dir / "dw_quadrant_rentabilidad.csv").exists()
    assert (export_dir / "flourish_treemap_genero.csv").exists()
    assert len(pd.read_csv(export_dir / "observable_distribucion.csv")) == len(enriched)
