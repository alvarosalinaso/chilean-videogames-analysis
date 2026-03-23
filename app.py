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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #0d1117; color: #e6edf3; }
    
    /* Headers de Sección con Estilo Narrativo */
    .section-header {
        font-weight: 800;
        font-size: 1.8rem;
        color: #DA291C;
        margin-top: 3rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #30363d;
        padding-bottom: 0.5rem;
    }
    .section-text { font-size: 1.05rem; color: #8b949e; margin-bottom: 1.5rem; line-height: 1.6; }
    
    /* KPIs y Tarjetas */
    [data-testid="metric-container"] { background: #161b22 !important; border: 1px solid #30363d; border-radius: 12px; padding: 1rem; }
    [data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 800 !important; }
    
    /* Panel IA */
    .ia-panel { background: #161b22; padding: 2rem; border-radius: 12px; border: 1px solid #30363d; }
    .status-ok { color: #2ea043; font-weight: 800; font-size: 1.4rem; background: rgba(46,160,67,0.1); padding: 5px 15px; border-radius: 20px;}
    .status-bad { color: #da3633; font-weight: 800; font-size: 1.4rem; background: rgba(218,54,51,0.1); padding: 5px 15px; border-radius: 20px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────── CARGA DE DATOS ───────────────────────────────
df = cargar_datos_historicos()
kpis = calcular_kpis_globales(df)

# ─────────────────────────────── SIDEBAR ───────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;margin-bottom:1.2rem;'>
      <div style='font-size:3rem;'>🎮</div>
      <div style='font-weight:800;font-size:1.2rem;color:#DA291C;'>GameDev Chile</div>
      <div style='font-size:.8rem;color:#8b949e;'>Market Intelligence Report</div>
    </div>
    <hr>
    """, unsafe_allow_html=True)
    
    st.markdown("**🎛️ Filtros Globales del Reporte**")
    gen_list = ["Todos"] + sorted(list(df['genre'].unique()))
    sel_genre = st.selectbox("Género", gen_list)
    sel_f2p = st.radio("Modelo de Negocio", ["Ambos", "Solo Premium", "Solo Free-to-Play"])
    
    st.markdown("---")
    st.markdown("<div style='font-size:0.8rem; color:#8b949e;'>Usa estos filtros para recalcular instantáneamente todas las métricas y gráficos del informe.</div>", unsafe_allow_html=True)

df_f = df.copy()
if sel_genre != "Todos":
    df_f = df_f[df_f['genre'] == sel_genre]
if sel_f2p == "Solo Premium":
    df_f = df_f[~df_f['is_f2p']]
elif sel_f2p == "Solo Free-to-Play":
    df_f = df_f[df_f['is_f2p']]

# ─────────────────────────────── HERO SECTION ───────────────────────────────
st.title("🇨🇱 Análisis de Mercado: Industria Chilena de Videojuegos")
st.markdown("<p style='font-size:1.1rem; color:#8b949e;'>Un informe de <b>Inteligencia de Negocios (BI)</b> y analítica descriptiva para entender empíricamente qué juegos triunfan comercialmente, por qué fallan, y qué lecciones puede darnos el mercado real de Steam.</p>", unsafe_allow_html=True)

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Proyectos Analizados", f"{len(df_f)}", "Del ecosistema chileno")
c2.metric("Gross Revenue Est.", f"${df_f['revenue_est'].sum():,.0f}", f"{(df_f['revenue_est'].sum() / (kpis['total_revenue'] or 1)) * 100:.1f}% de la torta", delta_color="normal" if len(df_f)==len(df) else "off")
c3.metric("Score Promedio (Metacritic)", f"{df_f['score'].mean():.1f}/100")
c4.metric("Sentimiento del Jugador", f"{df_f['sentiment'].mean():.2f}", "Rango [-1 a +1]")

st.info("💡 **Metodología de los datos:** Las ventas (Revenue) y las copias se estiman usando el modelo *Boxleiter* a partir de reseñas públicas. El Índice de Sentimiento (-1 a +1) fue extraído procesando el texto de miles de reseñas con Natural Language Processing (NLP).")

# ─────────────────────────────── SECCIÓN 1 ───────────────────────────────
st.markdown("<div class='section-header'>1. Volumen y Estacionalidad 📅</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>El primer paso para entender la industria es mirar su volumen de producción. A continuación puedes ver qué géneros predominan en Chile históricamente, y en qué meses los estudios prefieren publicar sus títulos para evitar a los colosos Triple-A internacionales.</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(graficar_lanzamientos(df_f), use_container_width=True)
with col2:
    st.plotly_chart(graficar_heatmap_mes(df_f), use_container_width=True)

# ─────────────────────────────── SECCIÓN 2 ───────────────────────────────
st.markdown("<div class='section-header'>2. Sentimiento y Recepción del Público 🗣️</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>No basta con publicarlo, el juego debe gustar. Utilizamos Inteligencia Artificial para leer las reseñas de los jugadores y asignarles una <b>puntuación de sentimiento</b>. Una caja alta significa opiniones divididas (alto riesgo). Una caja aplastada significa consenso (los jugadores están de acuerdo en si el juego es bueno o malo).</div>", unsafe_allow_html=True)

cc1, cc2 = st.columns(2)
with cc1:
    st.plotly_chart(graficar_sentiment_box(df_f, False), use_container_width=True)
with cc2:
    st.plotly_chart(graficar_sentiment_box(df_f, True), use_container_width=True)

# ─────────────────────────────── SECCIÓN 3 ───────────────────────────────
st.markdown("<div class='section-header'>3. Retorno Comercial vs Calidad 🎯</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>El gráfico definitivo de la inteligencia comercial. ¿Un juego extraordinario siempre es rentable? ¿Un juego mediocre está condenado al fracaso? Aquí cruzamos el diagnóstico financiero contra la satisfacción validada por el mercado. <b>Pasa el cursor sobre las esferas para explorar los datos subyacentes.</b></div>", unsafe_allow_html=True)

st.plotly_chart(graficar_cuadrante_oportunidad(df_f), use_container_width=True)

sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.markdown("🟢 **Arriba a la Derecha (La Meca):**<br>Juegos muy buenos que vendieron muchísimo (Ej. *Tormented Souls*, *Rock of Ages*). Encontraron su nicho y lo conquistaron.", unsafe_allow_html=True)
with sc2:
    st.markdown("🟡 **Abajo a la Derecha (Joyas Ocultas):**<br>Excelente recepción de jugadores, pero pésimas ventas financieras. Suele deberse a falta de presupuesto de Marketing.", unsafe_allow_html=True)
with sc3:
    st.markdown("🔴 **Izquierda (Fracasos o *Clickbaits*):**<br>Sentimiento tóxico (-1). Si tienen ventas altas, probablemente atraparon a jugadores con marketing falso, destruyendo la confianza en el estudio a futuro.", unsafe_allow_html=True)

# ─────────────────────────────── SECCIÓN 4: MODELO PREDICTIVO ───────────────────────────────
st.markdown("<div class='section-header'>4. Simulador Estadístico de Viabilidad Comercial 📊</div>", unsafe_allow_html=True)
st.markdown("<div class='section-text'>Extrayendo el valor analítico del procesamiento de lenguaje natural de nuestro catálogo, hemos desarrollado un modelo probabilístico (Algoritmo de Bosques Aleatorios). Describe de qué trata tu juego (su género, temática, <i>pitch</i>) en <b>inglés</b> y la herramienta calculará una estimación de viabilidad basada estrictamente en los datos estadísticos vigentes.</div>", unsafe_allow_html=True)

st.markdown("<div class='ia-panel'>", unsafe_allow_html=True)
pitch = st.text_area("🕹️ Pitch o Sinopsis de tu juego (en inglés)", placeholder="Example: A dark suspense horror game with puzzle mechanics, isometric view and pixel art graphics.", height=120)

col_btn, col_empty = st.columns([1, 4])
with col_btn:
    submit = st.button("🔮 Predecir Viabilidad", type="primary", use_container_width=True)

if submit:
    if len(pitch) < 10:
        st.warning("⚠️ Escribe un pitch más largo (al menos un par de frases) para que el modelo NLP tenga suficiente contexto.")
    else:
        with st.spinner("Analizando matrices TF-IDF y conectando Random Forest..."):
            res = run_prediction(pitch)
            if "error" in res:
                st.error(res["error"])
            else:
                st.markdown("<hr style='border-color:#30363d;'>", unsafe_allow_html=True)
                st.markdown("### 📊 Resultado de Inferencia ML")
                
                rm1, rm2, rm3 = st.columns(3)
                rev_str = f"${res['revenue']:,.0f} USD"
                rm1.metric("💰 Estimación Vitalicia Promedio", rev_str, "Proyección gross")
                
                estado = "<span class='status-ok'>Proyecto Viable / Rentable</span>" if res["is_success"] else "<span class='status-bad'>Dificultad Comercial / Nicho riesgoso</span>"
                rm2.markdown(f"**Veredicto IA:**<br>{estado}", unsafe_allow_html=True)
                
                rm3.metric("📊 Exactitud Predictiva Estimada", f"{res['probability']*100:.1f}%", help="Probabilidad asignada por los árboles de decisión sobre la clase ganadora.")
st.markdown("</div>", unsafe_allow_html=True)
