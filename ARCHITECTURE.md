# Arquitectura — chilean-videogames-analysis

## Visión general
Análisis de videojuegos desarrollados en Chile. Scraping de Steam e Itch.io, limpieza, análisis estadístico, clustering, forecasting, A/B testing y dashboard interactivo.

## Componentes principales

### Datos
- `data/raw/*.json` — Respuestas crudas de Steam API e Itch.io scraping (70+ archivos)
- `data/processed/games.csv` — Dataset consolidado y limpio
- `data/export/chilean_games_final.csv` — Dataset enriquecido con revenue estimado
- `data/export/` — Outputs: statistical_tests.json, visualizaciones

### Recolección
- `collect.py` — Steam API collection
- `collect_itch.py` — Itch.io scraping

### Limpieza
- `clean.py` — build_dataset: parsea JSONs → games.csv
- `utils.py` — Utilidades: parse_price_steam, parse_price_itch, extract_year, normalize_currency_to_usd, get_location

### Análisis (src/)
- `statistical_tests.py` — run_statistical_tests: t-test (Steam vs Itch), ANOVA (revenue por género), Pearson (recommendations vs revenue)
- `clustering_analysis.py` — run_clustering: KMeans sobre features de juegos
- `forecasting.py` — run_forecasting: predicción de lanzamientos
- `ab_testing.py` — run_ab_testing: tests A/B
- `generate_tables.py` — generate: tablas resumen
- `generate_report.py` — generate_report: reporte consolidado
- `export_visualizations.py` — export_visualizations: gráficos Plotly/Altair
- `analyze_all.py` — Orquestador

### Dashboard
- `dashboard.py` — Dash app con tabs: Overview, Distribución, Clustering, Forecasting, A/B Testing, Tablas

## Flujo de datos
```
Steam/Itch JSONs → clean.build_dataset → games.csv
games.csv → statistical_tests/clustering/forecasting/ab_testing → outputs
Todos → generate_report + dashboard
```

## Despliegue
- Render: `gunicorn dashboard:server` (ver `render.yaml`)

## Tests
- `tests/test_clean.py` — _parse_steam, _parse_itch, build_dataset
- `tests/test_utils.py` — parse_price_steam, parse_price_itch, extract_year, normalize_currency_to_usd, get_location
- `tests/test_statistical_tests.py` — run_statistical_tests
- `tests/test_analysis.py` — Smoke tests
- CI: pytest + coverage + ruff (Python 3.10, 3.11, 3.12)