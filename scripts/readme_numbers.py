#!/usr/bin/env python
"""Genera/verifica el bloque de cifras del README desde los datos del repo.

Uso:
    python scripts/readme_numbers.py           # imprime el bloque generado
    python scripts/readme_numbers.py --write   # reescribe el bloque en README.md
    python scripts/readme_numbers.py --check   # exit 1 si README.md no coincide

El número autoritativo es el que arroja este script sobre
data/export/chilean_games_final.csv (y statistical_tests del paquete).
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from chilean_videogames.statistical_tests import (  # noqa: E402
    compute_boxleiter_sensitivity,
    compute_hhi,
    run_statistical_tests,
)

README_PATH = REPO_ROOT / "README.md"
EXPORT_CSV = REPO_ROOT / "data" / "export" / "chilean_games_final.csv"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
EXPORT_DIR = REPO_ROOT / "data" / "export"
BEGIN_MARK = "<!-- BEGIN GENERATED: readme_numbers -->"
END_MARK = "<!-- END GENERATED: readme_numbers -->"


def compute_numbers(df: pd.DataFrame, stats: dict) -> dict:
    """Extrae todas las cifras del README desde el dataset + stats."""
    df = df.copy()
    df["source"] = df["source"].astype(str).str.casefold().str.strip()
    df["primary_genre"] = df["primary_genre"].fillna("Unknown").astype(str).str.strip()

    steam = df[df["source"] == "steam"]
    itch = df[df["source"] == "itch"]

    genre_counts = df["primary_genre"].value_counts()
    top_genre = str(genre_counts.index[0])
    top_genre_n = int(genre_counts.iloc[0])

    year_num = pd.to_numeric(df["year"], errors="coerce")
    year_unknown_n = int(year_num.isna().sum())

    no_recs_n = int((pd.to_numeric(df["recommendations"], errors="coerce").fillna(0) <= 0).sum())

    hhi = compute_hhi(df)
    box = compute_boxleiter_sensitivity(df, factors=(20, 40, 60))
    box_f = box.get("factors", {}) if box else {}

    ttest = stats.get("ttest_steam_vs_itch", {})
    anova = stats.get("anova_revenue_by_genre", {})
    pearson = stats.get("pearson_price_vs_recs", {})

    steam_price = pd.to_numeric(steam["price_usd"], errors="coerce")
    itch_price = pd.to_numeric(itch["price_usd"], errors="coerce")
    paid_steam = steam_price[steam_price > 0]

    return {
        "n_total": len(df),
        "n_steam": len(steam),
        "n_itch": len(itch),
        "top_genre": top_genre,
        "top_genre_n": top_genre_n,
        "top_genre_pct": round(top_genre_n / len(df) * 100, 1),
        "n_genres": int(len(genre_counts)),
        "steam_median_price": round(float(steam_price.median()), 2),
        "steam_free_pct": round(float((steam_price <= 0).mean() * 100), 1),
        "steam_paid_median": round(float(paid_steam.median()), 2) if len(paid_steam) else None,
        "itch_paid_n": int((itch_price > 0).sum()),
        "itch_median_price": round(float(itch_price.median()), 2) if len(itch_price) else None,
        "no_recs_n": no_recs_n,
        "no_recs_pct": round(no_recs_n / len(df) * 100, 1),
        "year_unknown_n": year_unknown_n,
        "year_unknown_pct": round(year_unknown_n / len(df) * 100, 1),
        "year_min": int(year_num.min()) if year_num.notna().any() else None,
        "year_max": int(year_num.max()) if year_num.notna().any() else None,
        "hhi": hhi.get("hhi"),
        "hhi_n_categories": hhi.get("n_categories"),
        "hhi_interpretation": hhi.get("interpretation"),
        "box_total_20": box_f.get("20", {}).get("total_revenue_est_usd"),
        "box_total_40": box_f.get("40", {}).get("total_revenue_est_usd"),
        "box_total_60": box_f.get("60", {}).get("total_revenue_est_usd"),
        "box_top_game": box_f.get("40", {}).get("top_game"),
        "box_top_game_40": box_f.get("40", {}).get("top_game_revenue_usd"),
        "ttest_p": ttest.get("p_value"),
        "ttest_p_holm": ttest.get("p_holm"),
        "anova_p": anova.get("p_value"),
        "anova_p_holm": anova.get("p_holm"),
        "pearson_r": pearson.get("r"),
        "pearson_p": pearson.get("p_value"),
        "pearson_p_holm": pearson.get("p_holm"),
        "pearson_n": pearson.get("n_observations"),
        "holm_n_tests": stats.get("holm_correction", {}).get("n_tests"),
    }


def _fmt_money(value) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"${value:,.2f}" if value < 100 else f"${value:,.0f}"


def _fmt_p(value, label: str = "p") -> str:
    if value is None or pd.isna(value):
        return "n/a"
    if value < 0.001:
        return f"{label}<0.001"
    return f"{label}={value:.3f}"


def _sig(p_holm) -> str:
    if p_holm is None or pd.isna(p_holm):
        return "n/a"
    return "significativo" if p_holm < 0.05 else "n.s."


def render_markdown(n: dict) -> str:
    """Renderiza el bloque generado (hero + tabla de hallazgos)."""
    hero = (
        f"> **Hallazgo principal:** de {n['n_total']} juegos chilenos en Steam e Itch.io "
        f"({n['n_steam']} Steam, {n['n_itch']} Itch.io), el género dominante es "
        f"**{n['top_genre']}** ({n['top_genre_n']} juegos, {n['top_genre_pct']}%) y la "
        f"mediana de precio en Steam es **{_fmt_money(n['steam_median_price'])} USD**; "
        f"el **{n['no_recs_pct']}%** no tiene recomendaciones registradas "
        f"({n['no_recs_n']} de {n['n_total']})."
    )
    year_range = (
        f"{n['year_min']}–{n['year_max']} conocidos; "
        f"{n['year_unknown_n']} Unknown ({n['year_unknown_pct']}%)"
        if n["year_min"] is not None
        else f"{n['year_unknown_n']} Unknown ({n['year_unknown_pct']}%)"
    )
    steam_vs_itch = (
        f"{_fmt_p(n['ttest_p'])}, {_fmt_p(n['ttest_p_holm'], 'p_Holm')} ({_sig(n['ttest_p_holm'])})"
    )
    anova_vs = (
        f"{_fmt_p(n['anova_p'])}, {_fmt_p(n['anova_p_holm'], 'p_Holm')} ({_sig(n['anova_p_holm'])})"
    )
    pearson_vs = (
        f"r={n['pearson_r'] if n['pearson_r'] is not None else 'n/a'}, "
        f"{_fmt_p(n['pearson_p'])}, {_fmt_p(n['pearson_p_holm'], 'p_Holm')} "
        f"(n={n['pearson_n']}, {_sig(n['pearson_p_holm'])})"
    )
    paid_steam = f"{n['steam_free_pct']}% gratis; mediana pago {_fmt_money(n['steam_paid_median'])}"

    lines = [
        BEGIN_MARK,
        hero,
        "",
        "### Hallazgos clave",
        "",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| Juegos en el dataset | {n['n_total']} ({n['n_steam']} Steam, {n['n_itch']} Itch.io) |",
        f"| Género dominante | {n['top_genre']} ({n['top_genre_n']} juegos, {n['top_genre_pct']}%) |",
        f"| Categorías de género | {n['n_genres']} |",
        f"| Mediana de precio Steam | {_fmt_money(n['steam_median_price'])} USD |",
        f"| Steam gratis/pago | {paid_steam} |",
        f"| Itch.io con precio > 0 | {n['itch_paid_n']} de {n['n_itch']} |",
        f"| Sin recomendaciones registradas | {n['no_recs_n']}/{n['n_total']} ({n['no_recs_pct']}%) |",
        f"| Años | {year_range} |",
        f"| HHI por género (primary_genre) | {n['hhi']}, {n['hhi_interpretation']} ({n['hhi_n_categories']} categorías) |",
        f"| Revenue estimado Steam (Boxleiter) | 20x: {_fmt_money(n['box_total_20'])} · 40x: {_fmt_money(n['box_total_40'])} · 60x: {_fmt_money(n['box_total_60'])} |",
        f"| Mayor revenue estimado (40x) | {n['box_top_game']} ({_fmt_money(n['box_top_game_40'])}) |",
        f"| Precio vs recomendaciones (Steam) | {pearson_vs} |",
        f"| Precios Steam vs Itch.io (Welch t-test) | {steam_vs_itch} |",
        f"| ANOVA revenue por género | {anova_vs} |",
        f"| Corrección Holm-Bonferroni | {n['holm_n_tests'] if n['holm_n_tests'] is not None else 'n/a'} p-values ajustados |",
        "",
        "*Cifras generadas por `python scripts/readme_numbers.py` sobre "
        "`data/export/chilean_games_final.csv`. Verificación: "
        "`python scripts/readme_numbers.py --check`.*",
        END_MARK,
    ]
    return "\n".join(lines)


def extract_block(readme_text: str) -> str | None:
    """Devuelve el bloque generado actual del README, o None si falta."""
    try:
        start = readme_text.index(BEGIN_MARK)
        end = readme_text.index(END_MARK) + len(END_MARK)
    except ValueError:
        return None
    return readme_text[start:end]


def replace_block(readme_text: str, block: str) -> str:
    """Reemplaza (o inserta al final) el bloque generado en el README."""
    existing = extract_block(readme_text)
    if existing is None:
        return readme_text.rstrip() + "\n\n" + block + "\n"
    return readme_text.replace(existing, block)


def load_stats() -> dict:
    """Ejecuta los tests estadísticos del paquete sobre los datos del repo."""
    return run_statistical_tests(data_dir=PROCESSED_DIR, output_dir=EXPORT_DIR)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="reescribe el bloque en README.md")
    mode.add_argument("--check", action="store_true", help="verifica que README.md coincide")
    args = parser.parse_args(argv)

    df = pd.read_csv(EXPORT_CSV, encoding="utf-8")
    block = render_markdown(compute_numbers(df, load_stats()))

    if args.write:
        README_PATH.write_text(
            replace_block(README_PATH.read_text(encoding="utf-8"), block), encoding="utf-8"
        )
        print(f"[README] Bloque generado actualizado en {README_PATH}")
        return 0

    if args.check:
        current = extract_block(README_PATH.read_text(encoding="utf-8"))
        if current is None:
            print("[README] ERROR: no se encontró el bloque generado (marcadores readme_numbers)")
            return 1
        if current.strip() != block.strip():
            print("[README] ERROR: el README no coincide con los datos actuales. Ejecuta:")
            print("         python scripts/readme_numbers.py --write")
            return 1
        print("[README] OK: cifras del README == script sobre los datos del repo")
        return 0

    print(block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
