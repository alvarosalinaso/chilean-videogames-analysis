[![Integración Continua](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml)

# Videojuegos Chilenos: Inteligencia de Mercado y Comparativas

🚀 **[Ver Panel Interactivo en Vivo](https://chilean-videogames-analysis-kjcsvpb5cuyhnv4papptzby.streamlit.app)**

Una herramienta de auditoría y visualización diseñada para evaluar el desempeño financiero real de la industria chilena de videojuegos. En lugar de ofrecer un recuento superficial de géneros populares, este proyecto cruza percepciones públicas de éxito con métricas de negocio duras (Net Revenue) e incorpora modelos predictivos para clasificar la viabilidad comercial de futuros desarrollos.

---

## Arquitectura y Funcionalidad

- **Extracción Directa:** Pipelines de datos integrados hacia los repositorios de metadatos de Steam e Itch.io.
- **Predicción (Bosques Aleatorios):** Motor de Machine Learning que procesa descripciones y propuestas de valor, arrojando estimaciones de éxito comercial y riesgo de desarrollo.
- **Benchmarking Económico:** Incorporación de un diferencial empírico. Se compara la media global de ingresos de la industria versus los costos operacionales en Chile, lo cual define si la inversión local cuenta con un piso financiero viable (> $720 USD teóricos).
- **Despliegue Portable:** Código base sanitizado y enrutado dinámicamente mediante módulos del OS, permitiendo la ejecución local del Dashboard sin fricciones de ruta.

---

## Estructura Central

- `app.py`: Front-end interactivo y motor visual en Streamlit.
- `src/streamlit/dashboard_data.py`: Módulo de cruce entre extracción local y datos macro globales (`market_benchmark.csv`).
- `src/ml/train.py`: Rutinas de entrenamiento y validación del algoritmo predictivo.

---

## Ejecución Local

Para levantar el entorno analítico en tu equipo:

```bash
# Entorno e instalación
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Despliegue del Dashboard
streamlit run app.py
```

> **Álvaro Salinas Ortiz** | Estrategia de Datos y Humanidades Digitales | [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)
