[![Integración Continua](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/alvarosalinaso/chilean-videogames-analysis/actions/workflows/ci.yml)

# Inteligencia de Mercado y Modelado Predictivo de Viabilidad Comercial: Industria de Videojuegos en Chile

🚀 **[Ver Panel Interactivo en Vivo](https://chilean-videogames-analysis-kjcsvpb5cuyhnv4papptzby.streamlit.app)**

---

## Executive Summary & Decision Making

Este proyecto diseña e implementa un ecosistema de **Inteligencia de Mercado (Business Intelligence)** y **Modelado Predictivo** diseñado para auditar el desempeño financiero real y la viabilidad comercial de la industria de videojuegos en Chile. Mediante la integración de pipelines de datos en tiempo real (Steam/Itch.io) y algoritmos de Machine Learning, el sistema trasciende el análisis descriptivo básico para transformarse en una herramienta de soporte a decisiones de inversión y desarrollo corporativo.

Este panel interactivo capacita a los Fondos de Inversión Cultural, Estudios de Desarrollo y Editores (Publishers) para tomar **decisiones estratégicas basadas en evidencia**:
1. **Mitigación del Riesgo de Pre-producción:** Evaluar y clasificar de forma algorítmica la probabilidad de éxito comercial de un concepto de juego antes de comprometer capital operativo y recursos de desarrollo.
2. **Optimización del Benchmarking de Costos Locales:** Validar si las estructuras de costos de desarrollo local se alinean de manera sostenible con el Net Revenue esperado global, determinando la viabilidad comercial bajo un umbral de retorno mínimo ajustado al mercado chileno.
3. **Estrategia de Pricing y Penetración de Mercado:** Analizar las dinámicas de precios, descargas e ingresos globales para establecer la banda de precios óptima en plataformas internacionales de distribución masiva.

[INSERTAR CAPTURA DE INTERFAZ DEL DASHBOARD DE BENCHMARKING COMERCIAL AQUÍ]

---

## Business Context & Challenge

La industria del software y videojuegos es un sector altamente dinámico pero con altas tasas de mortalidad de proyectos debido a la desconexión entre la propuesta creativa y la realidad comercial del mercado global. Históricamente, las decisiones de desarrollo en Latinoamérica se han tomado de manera intuitiva o basándose en géneros populares, sin considerar datos financieros reales de competidores directos.

El desafío estratégico de este proyecto consiste en **democratizar e integrar inteligencia de mercado dura (ingresos netos estimulados, volúmenes de venta y comportamiento de reviews)** de lanzamientos nacionales en plataformas globales. Esto permite confrontar las percepciones de "éxito mediático" con métricas financieras auditadas, respondiendo a la pregunta de negocio fundamental: *¿Cuál es el retorno real por cada dólar invertido en el desarrollo de software de entretenimiento en Chile y qué variables clave determinan el éxito comercial?*

---

## Data Architecture & Analytical Approach

El pipeline analítico del sistema ha sido diseñado garantizando robustez matemática y limpieza estructural de datos:

[INSERTAR DIAGRAMA DE LA ARQUITECTURA DE DATOS: PIPELINES API -> MODELO ML -> STREAMLIT APPS AQUÍ]

1. **Pipeline de Ingesta y ETL Multi-Plataforma:** Extracción directa e integración automatizada de APIs de Steam e Itch.io, recolectando metadatos operativos, métricas de engagement, volumetría de reviews y precios de venta.
2. **Modelado Predictivo de Viabilidad (Random Forests):** Entrenamiento de un clasificador supervisado en Python (`scikit-learn`) que procesa variables temáticas, descripciones cualitativas y propuestas de valor para estimar probabilísticamente la viabilidad comercial y el nivel de riesgo de nuevos proyectos.
3. **Benchmarking de Margen de Contribución:** Integración de un diferencial empírico que confronta el desempeño de ingresos netos proyectados contra el benchmark macroeconómico de costos de producción local (`market_benchmark.csv`), estableciendo un umbral mínimo de sostenibilidad financiera (> $720 USD teóricos como proxy de viabilidad inicial).
4. **Infraestructura Limpia y Portable:** Modularización estricta del backend (`src/streamlit/dashboard_data.py`) y backend ML (`src/ml/train.py`), aislados dinámicamente mediante sistemas de enrutamiento nativos del OS para garantizar consistencia operacional y despliegues robustos en la nube.

---

## Strategic Insights & Impact

La auditoría analítica del sector revela conclusiones críticas de negocio para tomadores de decisiones:

- **Desalineamiento Costo-Ingreso:** Más del 50% de los lanzamientos nacionales analizados no logran cruzar el umbral crítico de retorno mínimo operacional, exponiendo la necesidad urgente de optimizar las fases de pre-producción y validación de mercado antes de la fase de codificación intensiva.
- **Factores de Éxito No Obvios:** El modelo de Machine Learning identifica que, más allá del género del videojuego, variables de engagement cualitativo y la densidad de actualizaciones tempranas tienen un impacto de peso del 40% superior en los ingresos acumulados en comparación con el presupuesto inicial estimado.
- **Sostenibilidad Comercial:** El análisis sectorial provee un mapa de calor dinámico que resalta los nichos comerciales con mayor margen de contribución libre de saturación, redirigiendo la estrategia creativa hacia el ROI de negocio.

[INSERTAR GRÁFICO DE DISTRIBUCIÓN DE NET REVENUE VS GÉNERO Y UMBRAL DE VIABILIDAD ACUMULADA AQUÍ]

---

## Infraestructura, Despliegue y Ejecución

La arquitectura modular permite iniciar y auditar el sistema localmente en pocos pasos:

### Prerrequisitos
- Python 3.9+
- Entorno virtual administrado

### Setup y Despliegue Local
1. **Clonación del repositorio e inicialización:**
   ```bash
   git clone https://github.com/alvarosalinaso/chilean-videogames-analysis
   cd chilean-videogames-analysis
   python -m venv .venv
   ```
2. **Activación de entorno (Windows):**
   ```powershell
   .\.venv\Scripts\activate
   ```
3. **Instalación de dependencias deterministas:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Ejecución del motor interactivo Streamlit:**
   ```bash
   streamlit run app.py
   ```

---

> **Álvaro Salinas Ortiz**
> *Consultor en Estrategia de Datos y Analítica Avanzada*
> [LinkedIn](https://www.linkedin.com/in/alvaro-salinas-ortiz) | [Portafolio Web](https://alvarosalinaso.github.io)
