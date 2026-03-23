import streamlit as st

# Modulos de Clean Architecture
from src.streamlit.dashboard_data import cargar_datos_historicos, calcular_kpis_globales
from src.streamlit.dashboard_plots import (
    graficar_lanzamientos,
    graficar_heatmap_mes,
    graficar_sentiment_box,
    graficar_cuadrante_oportunidad
)
from src.streamlit.ml_inference import run_prediction

# ─────────────────────────────── CONFIGURACIÓN INICIAL ───────────────────────────────
st.set_page_config(
    page_title="Chilean Videogames | Market Intelligence",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-value { font-size: 2.2rem !important; font-weight: 800; color: #58a6ff; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 24px; border-radius: 4px 4px 0 0; background-color: #1e1e1e; color: #8b949e; }
    .stTabs [aria-selected="true"] { background-color: #58a6ff; color: #ffffff !important; font-weight: bold; }
    .status-ok { color: #2ea043; font-weight: bold; font-size: 1.2rem; }
    .status-warn { color: #e3b341; font-weight: bold; font-size: 1.2rem; }
    .status-bad { color: #da3633; font-weight: bold; font-size: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# Cargar Datos
df = cargar_datos_historicos()
kpis = calcular_kpis_globales(df)

# ─────────────────────────────── SIDEBAR (FILTROS) ───────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Star_1_yellow.svg/1024px-Star_1_yellow.svg.png", width=60)
    st.markdown("### Market Intelligence")
    st.caption("GameDev Chile • 2024")
    st.markdown("---")
    
    st.markdown("**Filtros de Exploración**")
    gen_list = ["Todos"] + list(df['genre'].unique())
    sel_genre = st.selectbox("Seleccionar Género", gen_list)
    sel_f2p = st.radio("Modelo de Negocio", ["Ambos", "Solo Premium", "Solo Free-to-Play"])

# Filtro en memoria
df_f = df.copy()
if sel_genre != "Todos":
    df_f = df_f[df_f['genre'] == sel_genre]
if sel_f2p == "Solo Premium":
    df_f = df_f[~df_f['is_f2p']]
elif sel_f2p == "Solo Free-to-Play":
    df_f = df_f[df_f['is_f2p']]

# ─────────────────────────────── HEADER ───────────────────────────────
st.title("🎮 Chilean Videogames • Market Intelligence 📊")
st.markdown("<small>Análisis estratégico de la industria local de videojuegos - Datos simulados vs Inferencia ML</small>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────── KPI ROW ───────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Proyectos Analizados", f"{len(df_f)} / {kpis['n_juegos']}")
c2.metric("Revenue Estimado (Muestra)", f"${df_f['revenue_est'].sum():,.0f}", delta=f"{(df_f['revenue_est'].sum() / kpis['total_revenue']) * 100:.1f}% del total")
c3.metric("Score Promedio", f"{df_f['score'].mean():.1f}/100", delta_color="off")
c4.metric("Sentimiento Promedio", f"{df_f['sentiment'].mean():.2f}", help="-1 (Muy Negativo) a +1 (Muy Positivo)")

st.info("ℹ️ **Sobre Revenue Estimado y Sentimiento:** El revenue usa el *Boxleiter Factor* para estimar ventas basándose en volumen de reseñas y precio. El Sentimiento Escala la puntuación del texto NLP de reviews desde -1 (malísimo) a +1 (Obra maestra).")

# ─────────────────────────────── TABS ───────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendencias y Estacionalidad", 
    "📣 Sentiment Analysis", 
    "🎯 Matriz de Oportunidad",
    "🤖 Simulador NLP Predictivo"
])

# ══════════════════════ TAB 1 ══════════════════════
with tab1:
    col1, col2 = st.columns([6, 4])
    with col1:
        st.plotly_chart(graficar_lanzamientos(df_f), use_container_width=True)
    with col2:
        st.plotly_chart(graficar_heatmap_mes(df_f), use_container_width=True)

    with st.expander("🔍 Entendiendo las Tendencias y Estacionalidad"):
        st.markdown("""
        *   **El Gráfico de Barras Aisladas (Izquierda):** Muestra el volumen bruto de juegos lanzados por año y qué géneros dominaron históricamente. Útil para notar "burbujas" (ej. exceso de juegos de Terror en 2021).
        *   **Heatmap Estacional (Derecha):** Cruza los Meses (Y) y los Géneros (X). Detecta si hay meses estratégicos libres de competencia para lanzar un género específico, o si el mercado tiende a amontonar juegos de Aventura en Diciembre.
        """)

# ══════════════════════ TAB 2 ══════════════════════
with tab2:
    cc1, cc2 = st.columns(2)
    with cc1:
        st.plotly_chart(graficar_sentiment_box(df_f, False), use_container_width=True)
    with cc2:
        st.plotly_chart(graficar_sentiment_box(df_f, True), use_container_width=True)

    with st.expander("📊 Cómo leer la Dispersión de Sentimiento (Boxplots)"):
        st.markdown("""
        *   **Cajas largas = División de opiniones:** Significa que un juego en ese género o plataforma puede ser amado u odiado. (Alto riesgo predictivo).
        *   **Cajas cortas = Consenso general:** El sentimiento es muy consistente en esa categoría. Ideal para asegurar ventas si estás arriba del `0.0`.
        """)

# ══════════════════════ TAB 3 ══════════════════════
with tab3:
    st.plotly_chart(graficar_cuadrante_oportunidad(df_f), use_container_width=True)
    with st.expander("🎯 Mapa Cuadrante: Retorno vs Calidad"):
        st.markdown("""
        *   **Arriba a la derecha (Alto Retorno + Buen review):** La "Meca". Mercado validado y rentable. (Generalmente ocupado por simuladores de nicho exitosos).
        *   **Arriba a la izquierda (Alto Retorno + Mal review):** "Juegos Clickbait". Atrapan ventas, pero destruyen la reputación del estudio a largo plazo.
        *   **Abajo a la derecha (Bajo Retorno + Obra Maestra):** Proyectos de pasión invisibles comercialmente. Fallo drástico en Marketing o Precio.
        *   **Tamaño de los círculos:** El perímetro simboliza el "*Score Metacritic*". Círculos grandes son garantía técnica.
        """)

# ══════════════════════ TAB 4: ML INFERENCE ══════════════════════
with tab4:
    st.subheader("🤖 Predictor de Éxito de Videojuegos (NLP Pipeline)")
    st.markdown("Escribe un *Pitch* o descripción corta (en inglés) de tu idea de videojuego. Nuestros modelos **TF-IDF + Random Forest** analizarán tus palabras clave contra la base de datos de juegos chilenos en Steam y predecirán su éxito comercial.")
    
    pitch = st.text_area("Descripción de tu juego (Pitch)", placeholder="Example: A dark horror puzzle game set in rural Chile with isometric graphics...", height=150)
    
    if st.button("🔮 Lanzar Predicción de IA", type="primary"):
        with st.spinner("Procesando Tensores de NLP..."):
            res = run_prediction(pitch)
            
            if "error" in res:
                st.error(res["error"])
            else:
                st.markdown("---")
                mc1, mc2, mc3 = st.columns(3)
                
                rev_str = f"${res['revenue']:,.0f} USD"
                mc1.metric("💰 Estimación Vitalicia (Gross)", rev_str)
                
                estado = "<span class='status-ok'>✅ Proyecto Viable (>1k COP)</span>" if res["is_success"] else "<span class='status-bad'>⚠️ Alta Dificultad Comercial / Nicho</span>"
                mc2.markdown(f"**Viabilidad:**<br>{estado}", unsafe_allow_html=True)
                
                mc3.metric("📈 Probabilidad de Impacto", f"{res['probability']*100:.1f}%")
