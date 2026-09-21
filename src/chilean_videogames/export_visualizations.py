"""Export CSV files optimized for visualization platforms.

Reads data/export/chilean_games_final.csv and generates:
- dw_quadrant_rentabilidad.csv  → Datawrapper Quadrant Chart
- flourish_treemap_genero.csv   → Flourish Treemap
- observable_distribucion.csv   → Observable Plot distribution
- embed_snippets.md             → HTML embed snippets
"""

from pathlib import Path

import pandas as pd


def load_final_data(input_path: Path) -> pd.DataFrame:
    """Load the final Chilean games dataset."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    return pd.read_csv(input_path)


def prepare_dw_quadrant(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """Prepare quadrant chart data: avg revenue vs saturation (count) per genre.

    Datawrapper quadrant chart expects:
      - Y-axis: average estimated revenue (USD)
      - X-axis: saturation = number of games in the genre
    """
    grouped = (
        df.groupby("primary_genre")
        .agg(
            avg_revenue_usd=("gross_revenue_est_usd", "mean"),
            total_revenue_usd=("gross_revenue_est_usd", "sum"),
            num_games=("name", "count"),
        )
        .reset_index()
    )
    grouped = grouped.sort_values("num_games", ascending=False)

    # Quadrant midpoints (median of axes)
    mid_x = grouped["num_games"].median()
    mid_y = grouped["avg_revenue_usd"].median()

    grouped["quadrant"] = grouped.apply(
        lambda row: (
            "★ Líderes"
            if row["num_games"] >= mid_x and row["avg_revenue_usd"] >= mid_y
            else (
                "Emergentes"
                if row["num_games"] < mid_x and row["avg_revenue_usd"] >= mid_y
                else ("Nicho Rentable" if row["num_games"] >= mid_x else "Explorar")
            )
        ),
        axis=1,
    )

    grouped.to_csv(output_path, index=False)
    return grouped


def prepare_flourish_treemap(df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
    """Prepare treemap data with Platform > Genre > Game hierarchy.

    Flourish treemap expects columns that define the nesting hierarchy.
    """
    # Expand genres so each game appears once per genre
    rows: list[dict[str, object]] = []
    for _, row in df.iterrows():
        genres_str = str(row.get("genres", ""))
        genres = [g.strip() for g in genres_str.split(",") if g.strip()]
        primary_genre = str(row.get("primary_genre", "Unknown"))
        if primary_genre not in genres:
            genres.insert(0, primary_genre)
        for genre in genres:
            rows.append(
                {
                    "Platform": "Steam Chile",
                    "Genre": genre,
                    "Game": row.get("name", "Unknown"),
                    "Revenue_USD": float(row.get("gross_revenue_est_usd", 0)),
                    "Copies": int(row.get("estimated_copies", 0)),
                    "Metacritic": (
                        int(row["metacritic"]) if pd.notna(row.get("metacritic")) else 0
                    ),
                    "Year": str(row.get("year", "Unknown")),
                }
            )

    treemap_df = pd.DataFrame(rows)

    # Keep only top genres (by total revenue) for readability
    genre_totals = treemap_df.groupby("Genre")["Revenue_USD"].sum()
    top_genres = genre_totals.nlargest(15).index.tolist()
    treemap_df.loc[~treemap_df["Genre"].isin(top_genres), "Genre"] = "Otros"

    treemap_df.to_csv(output_path, index=False)
    return treemap_df


def prepare_observable_distribution(
    df: pd.DataFrame, output_path: Path
) -> pd.DataFrame:
    """Prepare data for Observable Plot distribution analysis by platform/genre."""
    obs_df = df[
        [
            "name",
            "primary_genre",
            "price_usd",
            "estimated_copies",
            "gross_revenue_est_usd",
            "metacritic",
            "year",
            "developers",
            "is_free",
        ]
    ].copy()

    obs_df = obs_df.rename(
        columns={
            "name": "game",
            "primary_genre": "genre",
            "price_usd": "price_usd",
            "estimated_copies": "copies_sold",
            "gross_revenue_est_usd": "revenue_usd",
        }
    )

    # Add derived columns
    obs_df["is_paid"] = ~obs_df["is_free"].astype(str).str.lower().eq("true")
    obs_df["has_metacritic"] = obs_df["metacritic"].notna()

    obs_df.to_csv(output_path, index=False)
    return obs_df


def generate_embed_snippets(output_path: Path) -> None:
    """Write HTML embed snippets to a markdown file."""
    content = """# Visualización: Embed Snippets

Snippets listos para pegar. Cada uno apunta a un CSV generado por `src/export_visualizations.py`.

---

## 1. Datawrapper — Cuadrante de Rentabilidad

**Archivo de datos:** `data/export/dw_quadrant_rentabilidad.csv`

<!-- Reemplaza DATAWRAPPER_ID con el ID de tu gráfico creado en Datawrapper -->
<div id="dw-quadrant" style="max-width:100%; overflow:hidden;">
  <noscript>
    <p>Gráfico de cuadrante: Rentabilidad vs Saturación por género.
       Consulta <code>data/export/dw_quadrant_rentabilidad.csv</code> para los datos.</p>
  </noscript>
  <iframe
    title="Cuadrante de Rentabilidad — Géneros de Videojuegos Chilenos"
    aria-label="Gráfico de cuadrante mostrando ingresos promedio vs cantidad de juegos por género"
    src="https://datawrapper.dwcdn.net/DATAWRAPPER_ID/"
    style="width:100%; border:none; min-height:520px;"
    loading="lazy"
  ></iframe>
</div>

---

## 2. Flourish — Treemap de Géneros

**Archivo de datos:** `data/export/flourish_treemap_genero.csv`

<!-- Reemplaza FLOURISH_ID con el ID de tu visualización en Flourish -->
<div id="flourish-treemap" style="max-width:100%; overflow:hidden;">
  <noscript>
    <p>Mapa de árbol: Jerarquía Plataforma → Género → Juego.
       Consulta <code>data/export/flourish_treemap_genero.csv</code> para los datos.</p>
  </noscript>
  <div
    class="flourish-embed flourish-type-hierarchy"
    data-src="visualisation/FLOURISH_ID"
    style="width:100%; max-width:100%;"
  >
    <noscript>
      <a href="https://public.flourish.studio/visualisation/FLOURISH_ID/">Ver visualización</a>
    </noscript>
  </div>
  <script src="https://public.flourish.studio/resources/embed.js" async></script>
</div>

---

## 3. Observable Plot — Distribución de Ingresos

**Archivo de datos:** `data/export/observable_distribucion.csv`

<!-- Este snippet usa Observable Plot desde CDN. Carga el CSV vía fetch. -->
<div id="observable-dist" style="max-width:100%; overflow:hidden;">
  <noscript>
    <p>Distribución de ingresos por género.
       Consulta <code>data/export/observable_distribucion.csv</code> para los datos.</p>
  </noscript>
  <figure
    id="observable-figure"
    role="img"
    aria-label="Distribución de ingresos estimados por género de videojuegos chilenos"
    style="width:100%; overflow-x:auto;"
  >
    <figcaption>Distribución de ingresos por género — Observable Plot</figcaption>
    <div id="observable-plot" style="width:100%; min-height:300px;">
      <noscript>Gráfico interactivo. Activa JavaScript para verlo.</noscript>
    </div>
  </figure>
  <script type="module">
    import * as Plot from "https://cdn.jsdelivr.net/npm/@observablehq/plot@0.6/+esm";

    const res = await fetch("../data/export/observable_distribucion.csv");
    const text = await res.text();
    const rows = text.split("\\n").slice(1).map(line => {
      const [game, genre, price, copies, revenue, mc, year, dev, is_free, is_paid, has_mc] = line.split(",");
      return {
        game,
        genre,
        price_usd: +price,
        copies_sold: +copies,
        revenue_usd: +revenue,
        metacritic: mc ? +mc : null,
        year,
        is_paid: is_paid === "True",
      };
    }).filter(d => d.genre && d.revenue_usd > 0);

    const chart = Plot.plot({
      width: 800,
      marginLeft: 140,
      marginBottom: 40,
      x: { label: "Revenue estimado (USD)", grid: true },
      y: { label: null },
      color: { legend: true },
      marks: [
        Plot.barX(rows, Plot.groupY({ x: "sum" }, { y: "genre", x: "revenue_usd", fill: "genre", sort: { y: "-x" } })),
        Plot.ruleX([0]),
      ],
    });

    document.getElementById("observable-plot").appendChild(chart);
  </script>
</div>
"""
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    """Generate all visualization export files."""
    base = Path(__file__).resolve().parent.parent
    input_path = base / "data" / "export" / "chilean_games_final.csv"
    export_dir = base / "data" / "export"
    export_dir.mkdir(parents=True, exist_ok=True)

    try:
        df = load_final_data(input_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    try:
        dw_df = prepare_dw_quadrant(df, export_dir / "dw_quadrant_rentabilidad.csv")
        print(f"[OK] dw_quadrant_rentabilidad.csv — {len(dw_df)} géneros")
    except (OSError, ValueError, KeyError) as exc:
        print(f"[FAIL] Datawrapper: {exc}")

    try:
        fl_df = prepare_flourish_treemap(df, export_dir / "flourish_treemap_genero.csv")
        print(f"[OK] flourish_treemap_genero.csv — {len(fl_df)} filas")
    except (OSError, ValueError, KeyError) as exc:
        print(f"[FAIL] Flourish treemap: {exc}")

    try:
        ob_df = prepare_observable_distribution(
            df, export_dir / "observable_distribucion.csv"
        )
        print(f"[OK] observable_distribucion.csv — {len(ob_df)} filas")
    except (OSError, ValueError, KeyError) as exc:
        print(f"[FAIL] Observable: {exc}")

    try:
        generate_embed_snippets(export_dir / "embed_snippets.md")
        print("[OK] embed_snippets.md")
    except (OSError, ValueError) as exc:
        print(f"[FAIL] Embed snippets: {exc}")

    print("Exportación completada.")


if __name__ == "__main__":
    main()
