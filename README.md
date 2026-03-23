[![CI](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml)

# Videojuegos Chilenos: Inteligencia de Mercado y Comparativas

Panel interactivo alojado en [Streamlit](https://streamlit.io/) enfocado en auditar el desempeño financiero real de la industria chilena de videojuegos. A diferencia de un análisis clásico de géneros, este proyecto enfoca la percepción pública en Steam con métricas estimadas de negocio ($).

## Funcionalidades Implementadas (Última Actualización)
- **Extracción de Datos Cruda**: Flujos de datos directos para extraer información de Steam e Itch.io.
- **Predicción (Bosques Aleatorios)**: Un motor predictivo que evalúa tu propuesta comercial y categoriza la probabilidad de éxito y la viabilidad del proyecto.
- **Comparativa América Latina/Global**: Se inyectaron datos estáticos de la mediana de ingresos independiente de América Latina y el mundo. Comparamos el costo operativo bajísimo de Chile contra el retorno esperado cercano a la media mundial (>$720 USD) para argumentar por qué es financieramente más seguro invertir aquí que en Estados Unidos.
- **Motor Refactorizado**: Rutas relativas aisladas mediante bibliotecas del sistema para evitar caídas de la aplicación sin importar desde dónde montes el entorno.

## Archivos Críticos
1. `app.py`: El núcleo visual del panel de control.
2. `src/streamlit/dashboard_data.py`: Donde el flujo de código inyecta y une la información local con el cruce comparativo del mercado externo (`market_benchmark.csv`).
3. `src/ml/train.py`: El algoritmo de aprendizaje automático, sin redundancias y directo al punto.

## Configuración Inicial (Local)
Para levantar el servidor web tú mismo, clona el repositorio, activa el entorno virtual y dispara la interfaz gráfica:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

> Álvaro Salinas Ortiz | alvarosalinasortiz@gmail.com | [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz)
