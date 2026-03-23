[![Integración Continua](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml)

# Videojuegos Chilenos: Inteligencia de Mercado y Comparativas

Panel interactivo alojado en [Streamlit](https://streamlit.io/) enfocado en auditar el desempeño financiero real de la industria chilena de videojuegos. A diferencia de un análisis clásico de géneros, este proyecto compara la percepción pública con las métricas estimadas de negocio.

## Funcionalidades Principales
- **Extracción de Datos**: Flujos directos para obtener información de Steam e Itch.io.
- **Predicción (Bosques Aleatorios)**: Un motor predictivo que evalúa la propuesta comercial y categoriza la probabilidad de éxito y la viabilidad técnica del desarrollo.
- **Comparativa América Latina/Global**: Se inyectaron datos de la mediana de ingresos mundial. Comparamos el bajo costo operativo de Chile contra el retorno esperado (> $720 USD) para determinar si es financieramente seguro invertir localmente.
- **Motor Refactorizado**: Rutas relativas aisladas mediante bibliotecas del sistema operativo para evitar caídas de la aplicación de manera independiente del entorno de uso.

## Archivos Críticos
1. `app.py`: El núcleo visual del panel de control.
2. `src/streamlit/dashboard_data.py`: Donde el código une la información local con el cruce comparativo del mercado externo (`market_benchmark.csv`).
3. `src/ml/train.py`: El algoritmo de aprendizaje automático, sin redundancias y directo al punto.

## Configuración Inicial
Clona el repositorio, activa el entorno virtual y dispara la interfaz gráfica:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

> Álvaro Salinas Ortiz | alvarosalinasortiz@gmail.com | [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)
