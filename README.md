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

El pipeline analítico del sistema ha sido diseñado garantizando robustez matemática, transparencia en ingeniería de características y limpieza estructural de datos:

[INSERTAR DIAGRAMA DE LA ARQUITECTURA DE DATOS: PIPELINES API -> MODELO ML -> STREAMLIT APPS AQUÍ]

1. **Pipeline de Ingesta y ETL Multi-Plataforma:** Extracción directa e integración automatizada de las APIs públicas y scrapers de Steam e Itch.io, consolidando metadatos de lanzamientos nacionales, volumetría de reseñas históricas y precios de venta normalizados a USD.
2. **Modelado Predictivo de Viabilidad (Random Forest Híbrido):** 
   - **Modelo Offline de Procesamiento de Lenguaje Natural (NLP):** En nuestro pipeline de entrenamiento (`src/ml/train.py`), implementamos una vectorización de texto por **TF-IDF (1,000 características de máxima frecuencia)** sobre las descripciones detalladas de los juegos (`cleaned_text`). Este corpus alimenta clasificadores y regresores de **Random Forest** para evaluar qué descriptores temáticos y propuestas de valor escritas se asocian históricamente a mayores niveles de venta y tracción.
   - **Simulador Interactivo en Tiempo Real:** Integrado directamente en el panel de Streamlit (`app.py`), utiliza un Random Forest entrenado sobre variables estructuradas clave: *Género Principal* (codificado categóricamente), *Modelo de Monetización* (Premium vs. Free-to-Play), *Metascore Proyectado*, *Sentimiento del Usuario* (proporción de reviews positivas en Steam) y *Año de Lanzamiento*.
3. **Marco de Validación Financiera de Dos Niveles:** 
   - **Umbral de Validación Micro-Indie (> $1,000 USD netos):** Implementado en el pipeline ETL para filtrar proyectos de pasatiempo, proyectos escolares o jam submissions en Itch.io que distorsionan el benchmark comercial del mercado profesional.
   - **Umbral de Sostenibilidad Comercial (> $10,000 USD netos):** Utilizado en el clasificador de viabilidad del simulador interactivo como proxy de costo de recuperación operativo mínimo (capital de trabajo inicial) para micro-estudios de desarrollo de software en Chile.
4. **Infraestructura Limpia y Portable:** Estructuración modular que separa la lógica del dashboard de visualización (`app.py`), los scripts de limpieza y agregación analítica (`src/analyze_all.py`), y la orquestación del backend de aprendizaje de máquina (`src/ml/prepare.py` y `train.py`).

---

## Strategic Insights & Impact

La auditoría analítica del sector revela conclusiones críticas y objetivas sobre el comportamiento de la industria local:

- **La Realidad de la Larga Cola y Alta Mortalidad:** El análisis financiero de los 156 juegos chilenos consolidados en el dataset revela una alta concentración de mercado. Más del **75%** de los títulos fracasan en cruzar el umbral mínimo de validación micro-indie de **$1,000 USD** (principalmente proyectos de distribución gratuita en Itch.io y lanzamientos de bajo alcance en Steam). Esto demuestra que la fase de desarrollo técnico suele carecer de una estrategia de comercialización o pricing sólida.
- **Los Outliers de Éxito Comercial:** El volumen de ingresos de la industria chilena está sostenido por un puñado de casos excepcionales en los géneros de **Acción** y **Aventura**. Destacan producciones como **Tormented Souls** (Dual Effect / Abstract Digital) con ingresos netos estimados sobre los **$2.5M USD**, el catálogo histórico de **ACE Team** (liderado por sagas como **Rock of Ages** y **The Eternal Cylinder** superando cómodamente los **$500K USD** por lanzamiento), y títulos independientes sólidos como **Urbek City Builder** con más de **$530K USD** netos.
- **La Superioridad del Sentimiento del Usuario sobre la Crítica:** El modelo predictivo revela que el **Sentimiento del Usuario (Steam Positive Review Ratio)** muestra una correlación estadística sustancialmente más fuerte con el Net Revenue acumulado que el **Metascore** crítico tradicional. El mercado de nicho en Steam premia la validación directa de la comunidad y la consistencia en el soporte posventa, haciendo que el engagement comunitario sea un indicador de viabilidad comercial superior a la calificación de la prensa especializada.

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
