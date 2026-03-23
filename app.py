import streamlit as st
from src.streamlit.dashboard_data import cargar_datos_historicos, calcular_kpis_globales, cargar_market_benchmark
from src.streamlit.dashboard_plots import graficar_lanzamientos, graficar_heatmap_mes, graficar_sentiment_box, graficar_cuadrante_oportunidad, graficar_market_benchmark
from src.streamlit.ml_inference import run_prediction

st.set_page_config(page_title="Chilean Videogames | BI", page_icon="🎮", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .section-header { font-weight: 800; font-size: 1.8rem; color: #DA291C; margin-top: 3rem; border-bottom: 1px solid #30363d; padding-bottom: 0.5rem; }
    .section-text { font-size: 1.05rem; color: #8b949e; margin-bottom: 1.5rem; }
    [data-testid="metric-container"] { background: #161b22 !important; border: 1px solid #30363d; border-radius: 8px; padding: 1rem; }
    [data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 800 !important; }
    .ia-panel { background: #161b22; padding: 2rem; border-radius: 8px; border: 1px solid #30363d; }
    .status-ok { color: #2ea043; font-weight: 800; font-size: 1.3rem; }
    .status-bad { color: #da3633; font-weight: 800; font-size: 1.3rem; }
</style>
""", unsafe_allow_html=True)

raw_df = cargar_datos_historicos()
kpis_data = calcular_kpis_globales(raw_df)
bench_df = cargar_market_benchmark()

with st.sidebar:
    st.markdown("<h2 style='color:#DA291C;text-align:center;'>GameDev CL</h2><hr>", unsafe_allow_html=True)
    g_list = ["Todos"] + sorted(list(raw_df['genre'].unique()))
    target_genre = st.selectbox("Filtro Género", g_list)
    biz_model = st.radio("Modelo", ["Ambos", "Solo Premium", "Solo F2P"])
    
    st.markdown("---")
    cut_pct = st.slider("Tajada Plataforma (%)", 0, 70, 30, step=5)
    log_scale = st.toggle("Ingresos Logarítmicos", value=True)

df_active = raw_df.copy()
if target_genre != "Todos": df_active = df_active[df_active['genre'] == target_genre]
if biz_model == "Solo Premium": df_active = df_active[~df_active['is_f2p']]
elif biz_model == "Solo F2P": df_active = df_active[df_active['is_f2p']]

# Net rev
df_active['rev_net'] = df_active['revenue_est'] * (1 - (cut_pct / 100))

st.title("Market Intel: Videojuegos CL")
st.markdown("Métricas duras del mercado chileno en Steam. Rendimiento comercial vs validación de los jugadores.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Juegos", f"{len(df_active)}")
c2.metric("Net Revenue", f"${df_active['rev_net'].sum():,.0f}")
c3.metric("Metascore Promedio", f"{df_active['score'].mean():.1f}/100")
c4.metric("Sentimiento", f"{df_active['sentiment'].mean():.2f}")

st.info("Nota técnica: Revenue estimado vía Boxleiter. Sentimiento = scrape de reseñas parseadas asíncronamente.")

st.markdown("<div class='section-header'>Benchmark Global (Mediana USD)</div>", unsafe_allow_html=True)
st.plotly_chart(graficar_market_benchmark(bench_df), use_container_width=True)

st.markdown("<div class='section-header'>Histórico de Producción</div>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a: st.plotly_chart(graficar_lanzamientos(df_active), use_container_width=True)
with col_b: st.plotly_chart(graficar_heatmap_mes(df_active), use_container_width=True)

st.markdown("<div class='section-header'>Recepción Pública</div>", unsafe_allow_html=True)
c_box1, c_box2 = st.columns(2)
with c_box1: st.plotly_chart(graficar_sentiment_box(df_active, False), use_container_width=True)
with c_box2: st.plotly_chart(graficar_sentiment_box(df_active, True), use_container_width=True)

st.markdown("<div class='section-header'>Matriz de Oportunidad Comercial</div>", unsafe_allow_html=True)
st.plotly_chart(graficar_cuadrante_oportunidad(df_active, log_scale, col_y="rev_net"), use_container_width=True)

st.markdown("<div class='section-header'>Simulación ML: Viabilidad de Proyecto</div>", unsafe_allow_html=True)
st.markdown("<div class='ia-panel'>", unsafe_allow_html=True)
game_pitch = st.text_area("Pega el pitch en inglés acá", placeholder="A hardcore platformer...", height=100)

if st.button("Evaluar", type="primary"):
    if len(game_pitch) < 10:
        st.warning("Falta carnita en el texto. Dificilmente el modelo detecte algo.")
    else:
        with st.spinner("Crunching data..."):
            pred = run_prediction(game_pitch)
            if "error" in pred:
                st.error(pred["error"])
            else:
                st.markdown("### Resultados")
                r1, r2, r3 = st.columns(3)
                r1.metric("Proyección USD", f"${pred['revenue']:,.0f}")
                
                sts = "<span class='status-ok'>Viable</span>" if pred["is_success"] else "<span class='status-bad'>Riesgo Alto</span>"
                r2.markdown(f"**Veredicto:** {sts}", unsafe_allow_html=True)
                r3.metric("Acierto RF", f"{pred['probability']*100:.1f}%")
st.markdown("</div>", unsafe_allow_html=True)
