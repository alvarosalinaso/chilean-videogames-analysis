# Videojuegos Chilenos — Market Intelligence

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Pipeline ETL + Dashboard interactivo de la industria de videojuegos desarrollados en Chile (2010-2024). Combina datos de **Steam** (mercado comercial) e **Itch.io** (escena indie) para generar un panorama completo del ecosistema.

## Dashboard en Vivo

👉 **[chilean-videogames-analysis.streamlit.app](https://chilean-videogames-analysis.streamlit.app)**

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
| **Visualización** | Streamlit, Plotly, Matplotlib |
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
├── app.py                  # Dashboard Streamlit
├── docs/looker_setup.md    # Guía Looker Studio
└── requirements.txt        # Dependencias
```

## Inicio Rápido

```bash
pip install -r requirements.txt
streamlit run app.py        # Dashboard local
```

Para reproducir el análisis completo:
```bash
python src/collect.py       # Scraping
python src/analyze_all.py   # Procesamiento y gráficos
```

## Contacto

**Álvaro Salinas Ortiz** — [LinkedIn](https://linkedin.com/in/alvaro-salinas-ortiz) · 
