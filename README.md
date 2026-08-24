# Videojuegos Chilenos — Market Intelligence

[![CI](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Plotly.js](https://img.shields.io/badge/Plotly.js-3.x-3F4F75?logo=plotly&logoColor=white)](https://plotly.com/javascript/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Pipeline ETL + Dashboard interactivo de la industria de videojuegos desarrollados en Chile (2010-2024). Combina datos de **Steam** (mercado comercial) e **Itch.io** (escena indie) para generar un panorama completo del ecosistema.

## Dashboard Integrado

👉 **Integrado en [Portfolio Web](https://alvarosalinaso.github.io/portfolio-web/)** → Tab **"🎮 Industria Gamer Chilena"**  
Desplegado en GitHub Pages (estático, sin backend Python). 4 tabs: Tendencias, Género, Sentimientos, Oportunidad.

## Hallazgos Clave

- **Crecimiento post-2020**: La escena indie chilena explotó en los últimos años
- **Dos mercados diferenciados**: Steam (Premium, $8-10 USD) vs Itch.io (Free/Experimental)
- **Top ventas estimadas**: *Rock of Ages*, *Tormented Souls*, *Zeno Clash*
- **Géneros dominantes**: Acción y Estrategia en Steam; Experimental y Narrativo en Itch.io

## Stack

| Capa | Tecnología |
|------|-----------|
| **Lenguaje** | Python 3.8+ |
| **Scraping** | BeautifulSoup, Steam API, Itch.io API |
| **Data** | Pandas, NumPy |
| **Visualización** | **Plotly.js** (integrado en Portfolio Web), Matplotlib |
| **BI** | Looker Studio (Google Data Studio) |
| **Testing** | Pytest |

## Estructura

```
chilean-videogames-analysis/
├── src/                    # Pipeline ETL
│   ├── collect.py          # Scraping Steam
│   ├── collect_itch.py     # Scraping Itch.io
│   ├── clean.py            # Limpieza y normalización
│   ├── analyze_all.py      # Generación de insights
│   └── utils.py            # Utilidades compartidas
├── data/
│   ├── raw/                # JSON crudos de APIs
│   └── export/             # CSVs listos para BI
├── assets/figures_v2/      # Visualizaciones generadas
├── docs/looker_setup.md    # Guía Looker Studio
└── requirements.txt        # Dependencias
```

## Inicio Rápido

```bash
pip install -r requirements.txt
python src/collect.py       # Scraping
python src/analyze_all.py   # Procesamiento y gráficos
```

Para ver el dashboard interactivo: **[https://alvarosalinaso.github.io/portfolio-web/](https://alvarosalinaso.github.io/portfolio-web/)** → Tab "🎮 Industria Gamer Chilena"

## Contacto

**Álvaro Salinas Ortiz** — [LinkedIn](https://linkedin.com/in/alvaro-salinas-ortiz) · [Portfolio](https://alvarosalinaso.github.io/portfolio-web/)