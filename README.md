[![CI](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml)

# Chilean Videogames: Market Intelligence & Benchmarking

Dashboard interactivo alojado en [Streamlit](https://streamlit.io/) enfocado en auditar el desempeño financiero real de la industria chilena de videojuegos. A diferencia de un análisis clásico de géneros, este proyecto cruza sentimiento de Steam con métricas estimadas de negocio ($).

## Features Implementados (Última Actualización)
- **Scraping Crudo**: Pipelines directos para minar Steam e Itch.io.
- **Predicción (Random Forest)**: Un motor que evalúa tu pitch y categoriza la probabilidad de éxito y la viabilidad del proyecto.
- **Benchmark LatAm/Global**: Se inyectó data estática de la mediana de ingresos independiente de LatAm y el mundo. Comparamos el costo operativo bajísimo de Chile contra el retorno esperado cercano a la media mundial (>$720 USD) para argumentar por qué es financieramente más seguro invertir aquí que en USA.
- **Engine Refactorizado**: Rutas relativas aisladas con `pathlib.Path` para blindar crashes de Streamlit sin importar desde dónde montes el entorno.

## Archivos Críticos
1. `app.py`: El core visual del dashboard.
2. `src/streamlit/dashboard_data.py`: Donde el pipeline inyecta y une los datos locales con el cruce del Benchmark del mercado externo (`market_benchmark.csv`).
3. `src/ml/train.py`: El motor de Random Forest, sin redundancias y directo al punto.

## Setup Inicial (Local)
Para levantar el servidor web tú mismo, clona, actívate el enviroment y dispara la interfaz gráfica:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

> Álvaro Salinas Ortiz | alvarosalinasortiz@gmail.com | [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)
