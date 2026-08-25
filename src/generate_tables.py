"""Genera tabla ejecutiva con great_tables desde games.csv"""
import pandas as pd
from pathlib import Path
from great_tables import GT

def generate():
    df = pd.read_csv("data/processed/games.csv", encoding="utf-8")
    top5 = df.nlargest(5, "gross_revenue_est_usd")[["name", "source", "price_usd", "gross_revenue_est_usd", "recommendations"]]
    top5.columns = ["Juego", "Plataforma", "Precio (USD)", "Revenue Est. (USD)", "Recomendaciones"]
    
    tbl = (
        GT(top5)
        .tab_header(title="Top 5 Revenue — Videojuegos Chilenos")
        .fmt_currency(columns=["Precio (USD)", "Revenue Est. (USD)"], currency="USD")
        .fmt_number(columns=["Recomendaciones"], use_seps=True)
        .tab_source_note("Fuente: Steam API + Itch.io scraping | Análisis: Álvaro Salinas")
    )
    Path("assets").mkdir(exist_ok=True)
    tbl.save("assets/executive_table.html")
    print("[TABLE] assets/executive_table.html generado")

if __name__ == "__main__":
    generate()
