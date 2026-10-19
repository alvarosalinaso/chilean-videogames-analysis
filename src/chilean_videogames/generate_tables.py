"""Genera tabla ejecutiva con great_tables desde el CSV enriquecido"""

from pathlib import Path

import pandas as pd
from great_tables import GT

REQUIRED_COLUMNS = {"gross_revenue_est_usd", "price_usd", "recommendations"}


def generate():
    # La tabla necesita las columnas derivadas (price_usd, gross_revenue_est_usd),
    # que solo existen en el CSV enriquecido que escribe analyze_all.
    csv_path = Path("data/export/chilean_games_final.csv")
    if not csv_path.exists():
        print("[TABLE] Falta data/export/chilean_games_final.csv; corre analyze_all primero")
        return

    df = pd.read_csv(csv_path, encoding="utf-8")
    if not REQUIRED_COLUMNS.issubset(df.columns):
        print("[TABLE] CSV sin columnas derivadas; corre analyze_all primero")
        return

    top5 = df.nlargest(5, "gross_revenue_est_usd")[
        ["name", "source", "price_usd", "gross_revenue_est_usd", "recommendations"]
    ]
    top5.columns = [
        "Juego",
        "Plataforma",
        "Precio (USD)",
        "Revenue Est. (USD)",
        "Recomendaciones",
    ]

    tbl = (
        GT(top5)
        .tab_header(title="Top 5 Revenue — Videojuegos Chilenos")
        .fmt_currency(columns=["Precio (USD)", "Revenue Est. (USD)"], currency="USD")
        .fmt_number(columns=["Recomendaciones"], use_seps=True)
        .tab_source_note("Fuente: Steam API + Itch.io scraping | Análisis: Álvaro Salinas")
    )
    Path("assets").mkdir(exist_ok=True)
    # GT.save() exige selenium para renderizar; el HTML crudo es suficiente aquí.
    Path("assets/executive_table.html").write_text(tbl.as_raw_html(), encoding="utf-8")
    print("[TABLE] assets/executive_table.html generado")


if __name__ == "__main__":
    generate()
