# Inteligencia de Mercado para la Industria de Videojuegos Chilenos: Análisis Comparativo Steam vs Itch.io (2009–2025)

[![CI](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org) [![Ruff](https://img.shields.io/badge/Ruff-linting-blueviolet)](https://docs.astral.sh/ruff/)

Análisis cuantitativo de la industria de videojuegos chilenos combinando datos de **Steam** (mercado comercial) e **Itch.io** (escena indie). Genera inteligencia de mercado accionable para estudios, inversores y política pública.

---

## 1. Contexto Estratégico y Problema de Negocio

La industria chilena de videojuegos carece de inteligencia competitiva estructurada. Los estudios indie y fondos de fomento (CORFO, INDIE AWARD) deciden sin datos sobre rentabilidad por género, plataforma óptima y ventana temporal. Este pipeline ETL extrae datos reales de Steam e Itch.io, normaliza moneda, estima copias (factor BoxLeiter 40x) y calcula un índice HHI de concentración.

**Mercado:** 155 juegos chilenos (89 Steam, 66 Itch.io), período 2009–2025.

---

## 2. Preguntas de Investigación e Hipótesis

| ID | Pregunta | Variables | Hipótesis |
|----|----------|-----------|-----------|
| RQ1 | Evolución de lanzamientos por año y plataforma | `year`, `source` | Crecimiento exponencial post-2020 (COVID-19) |
| RQ2 | Diferencias en distribución de precios | `price_usd`, `source` | Steam: $4–15 USD; Itch.io: mayoritariamente gratuito |
| RQ3 | Géneros con mayor revenue estimado | `primary_genre`, `gross_revenue_est_usd` | Acción/Aventura dominan; Horror mayor rev/título |
| RQ4 | Concentración de mercado por género (HHI) | `HHI`, `primary_genre` | Baja concentración (HHI < 1500) |
| RQ5 | Relación recomendaciones vs revenue | `recommendations`, `gross_revenue_est_usd` | Correlación positiva fuerte (r > 0.85) |

---

## 3. Pipeline Metodológico y Arquitectura de Datos

### 3.1 Extracción

| Fuente | Método | Registros |
|--------|--------|-----------|
| Steam API (`appdetails`) | `requests` + `BeautifulSoup` | 89 juegos |
| Itch.io (`/games/tag-chile`) | Scraping HTML con paginación | 66 juegos |

**Scripts:** `src/collect.py` (Steam), `src/collect_itch.py` (Itch.io)

### 3.2 Transformación y Limpieza

- **Deduplicación:** por (`name`, `source`) — 0 duplicados
- **Normalización USD:** tasas fijas (CLP/USD = 1/950, EUR = 1.10, GBP = 1.27)
- **Extracción de año:** regex `\b(19|20)\d{2}\b` sobre fechas heterogéneas
- **Geolocalización:** 20 estudios → Santiago (14), Valparaíso (3), General (resto)

**Script:** `src/clean.py` → `data/processed/games.csv`

### 3.3 Modelado e Indicadores

| Indicador | Fórmula | Aplicación |
|-----------|---------|------------|
| Copias estimadas | `recommendations × 40` (BoxLeiter) | Proxy de ventas Steam |
| Revenue bruto | `estimated_copies × price_usd` | Ingresos totales por título |
| HHI | `Σ(s_i²)` donde `s_i` = share de género | Concentración de mercado |
| Normalización USD | `price × factor_moneda` | Comparabilidad cross-plataforma |

### 3.4 Sesgos y Limitaciones

- **Supervivencia:** Solo juegos publicados; cancelados no aparecen en APIs
- **BoxLeiter fijo:** Relación recomendaciones/copias varía por género
- **Itch.io:** 100% gratuito/name-your-price, sin revenue confiable
- **Incompleto:** ~35% de títulos Steam sin `recommendations` > 0

---

## 4. Hallazgos Clave y Business Insights

### 4.1 Tendencia Temporal

| Período | Steam | Itch.io | Total |
|---------|-------|---------|-------|
| 2009–2019 | 18 | 3 | 21 |
| 2020–2025 | 51 | 63 | 114 |

**Insight:** Crecimiento **5.4x** post-2020. COVID-19 aceleró entrada de nuevos estudios.

### 4.2 Distribución de Precios

| Plataforma | Mediana | % Gratuitos |
|------------|---------|-------------|
| Steam | $7.68 USD | 21% |
| Itch.io | $0.00 USD | 100% |

**Insight:** Steam = premium ($5–15); Itch.io = vitrina experimental.

### 4.3 Top Revenue Estimado (Steam)

| Título | Revenue (USD) | Recomendaciones | Género |
|--------|---------------|-----------------|--------|
| Microsoft Flight Simulator | $127.3M | 67,213 | Simuladores |
| MENACE | $2.5M | 4,048 | Rol |
| The Rise of the Golden Idol | $1.5M | 3,390 | Aventura |
| Tormented Souls 2 | $867K | 1,329 | Acción |
| Tormented Souls | $2.5M | 5,707 | Acción |

### 4.4 Revenue por Género (Mediana)

| Género | Revenue Med. (USD) | Títulos |
|--------|-------------------|---------|
| Simuladores | $6,132 | 4 |
| Acción | $4,716 | 48 |
| Aventura | $3,201 | 18 |
| Estrategia | $1,286 | 6 |

**Insight:** Horror ($2.5M Tormented Souls) = nicho subexplotado con alta rentabilidad.

### 4.5 Concentración de Mercado (HHI)

HHI < 1000 → mercado **altamente fragmentado**. Ningún género domina; diversificación creativa saludable; baja barrera de entrada.

---

## Tabla Ejecutiva

Tabla ejecutiva estilo ejecutivo con `great_tables`. Ejecutar `src/generate_tables.py` para regenerar.

<details>
<summary><strong>Ver tabla ejecutiva</strong></summary>

| Métrica | Valor | Benchmark | Δ |
|---------|-------|-----------|---|
| Total juegos analizados | 155 | — | — |
| Revenue promedio Steam | $7.68 USD | Industria global: $15 USD | -49% |
| Revenue mediano género top | $6,132 USD | Simuladores | — |
| HHI concentración | <1000 | Altamente fragmentado | — |
| Crecimiento post-2020 | 5.4x | Pre-COVID: 21 juegos | +443% |

*Generado con great_tables — Ejecutar `python src/generate_tables.py` para actualizar*
</details>

---

## 5. Dashboard y Visualizaciones Interactivas

### 5.1 Dashboard Principal

**[Portfolio Web](https://alvarosalinaso.github.io/portfolio-web/)** → Tab "Industria Gamer Chilena" · Plotly.js · 4 tabs

### 5.2 Visualizaciones Embebidas

**Evolución de lanzamientos (Datawrapper):**

<div style="width:100%;max-width:800px;margin:0 auto;">
<iframe src="https://datawrapper/embed/PLACEHOLDER_TIMELINE" style="width:100%;border:none;height:400px;" title="Evolución Lanzamientos Chile 2009-2025"></iframe>
</div>

**Cuadrante de oportunidad (Flourish):**

<div style="width:100%;max-width:800px;margin:0 auto;">
<iframe src="https://public.flourish.studio/visualisation/PLACEHOLDER_OPPORTUNITY/embed" style="width:100%;border:none;height:500px;" title="Cuadrante de Oportunidad"></iframe>
</div>

**Sentimientos por plataforma (Observable):**

<div style="width:100%;max-width:800px;margin:0 auto;">
<iframe src="https://observablehq.com/embed/PLACEHOLDER_SENTIMENT" style="width:100%;border:none;height:400px;" title="Sentimientos Steam vs Itch.io"></iframe>
</div>

### 5.3 Figures Estáticas (`assets/figures_v2/`)

- `1_timeline_releases.png` — Lanzamientos por año
- `2_price_distribution.png` — Precios por plataforma
- `3_top_revenue.png` — Top 10 revenue
- `4_revenue_genre.png` — Revenue por género (log scale)

---

## Visual Analytics

Interactividad multinivel para exploración de datos y presentación ejecutiva.

<details>
<summary><strong>Datawrapper — Gráfico interactivo</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://datawrapper.dwcdn.net/MBqIQ/" title="Cuadrante de Saturación vs Revenue — Géneros de Videojuegos" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Flourish — Visualización animada</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://flo.uri.sh/visualisation/1444147/embed" title="Distribución de Revenue por Plataforma y Género" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

<details>
<summary><strong>Observable — Notebook interactivo</strong></summary>

<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;max-width:100%;">
  <iframe src="https://observablehq.com/@alvarosalinaso/chilean-distribution" title="Distribución Bimodal de Precios" style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" loading="lazy" allowfullscreen></iframe>
</div>
</details>

**Hallazgos clave**: Los videojuegos chilenos muestran una distribución bimodal de precios con clusters en $5.000-$15.000 y $25.000-$45.000 CLP, sugiriendo segmentación de mercado.

---

## 6. Reproducibilidad y Entorno Técnico

### 6.1 Instalación

```bash
git clone https://github.com/alvarosalinaso/chilean-videogames-analysis.git
cd chilean-videogames-analysis
pip install -r requirements.txt
```

### 6.2 Ejecución del Pipeline

```bash
python src/collect.py          # Extracción Steam
python src/collect_itch.py     # Extracción Itch.io
python src/clean.py            # Limpieza
python src/analyze_all.py      # Análisis + visualizaciones
```

### 6.3 Dependencias

| Paquete | Versión | Uso |
|---------|---------|-----|
| plotly | >= 5.19.0 | Visualizaciones interactivas |
| pandas | >= 2.1.0 | Manipulación de datos |
| numpy | >= 1.26.0 | Operaciones numéricas |
| scipy | >= 1.22.0 | Análisis estadístico |
| matplotlib | >= 3.8.0 | Figuras estáticas |
| requests | >= 2.31.0 | APIs HTTP |
| beautifulsoup4 | >= 4.12.0 | Parsing HTML |
| scikit-learn | >= 1.3.0 | Clusterización K-Means |

### 6.4 Calidad de Código

```bash
ruff check .                  # Linting
ruff format --check .         # Formato
python -m compileall -q src          # Compilación
```

### 6.5 Estructura

```
chilean-videogames-analysis/
├── src/
│   ├── collect.py          # Extracción Steam
│   ├── collect_itch.py     # Extracción Itch.io
│   ├── clean.py            # Limpieza
│   ├── analyze_all.py      # Análisis + orchestrador
│   ├── clustering_analysis.py  # Clusterización K-Means
│   └── utils.py            # Utilidades
├── data/
│   ├── raw/                # JSONs crudos
│   ├── processed/          # CSV consolidado
│   └── export/             # Dataset final
├── assets/figures_v2/      # Visualizaciones
├── requirements.txt
└── .github/workflows/ci.yml
```

---

**Autor:** Álvaro Salinas Ortiz — [LinkedIn](https://linkedin.com/in/alvaro-salinas-ortiz) · [Portfolio](https://alvarosalinaso.github.io/portfolio-web/) · [GitHub](https://github.com/alvarosalinaso)
