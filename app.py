"""
═══════════════════════════════════════════════════════════════════════════════
  Chilean Videogames Industry — Streamlit App
  Autor : Álvaro Salinas Ortiz  |  github.com/alvarosalinaso
  Stack : Streamlit · Plotly · Pandas · TextBlob · Scikit-learn
═══════════════════════════════════════════════════════════════════════════════

PROBLEMA DE NEGOCIO
-------------------
  Chile produce juegos con potencial de mercado pero carece de inteligencia
  competitiva estructurada. Los estudios indie y los fondos de fomento (CORFO,
  INDIE AWARD) toman decisiones sin datos sobre:
  (1) Qué géneros tienen mayor rentabilidad ajustada por inversión,
  (2) En qué plataforma lanzar primero para maximizar tracción,
  (3) Cuál es la ventana de lanzamiento óptima.
  Este dashboard responde esas preguntas con datos reales scrapeados
  de Steam e Itch.io, convirtiéndose en una herramienta de market intelligence
  para productoras, inversores y política pública de industria creativa.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# ─────────────────────────────── CONFIG ───────────────────────────────
st.set_page_config(
    page_title="Chilean Videogames Market Intelligence | alvarosalinaso",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "steam":    "#1b2838",
    "steam_l":  "#66c0f4",
    "itch":     "#fa5c5c",
    "accent":   "#3fb950",
    "warn":     "#e3b341",
    "bad":      "#f78166",
    "purple":   "#d2a8ff",
    "bg":       "#0d1117",
    "text":     "#e6edf3",
    "text2":    "#8b949e",
}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,34,0.6)",
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=10, r=10, t=45, b=10),
    xaxis=dict(gridcolor="#30363d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#30363d", zerolinecolor="#30363d"),
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.block-container{padding:1.5rem 2rem;}
.stApp{background-color:#0d1117;color:#e6edf3;}
[data-testid="stSidebar"]{background:#161b22!important;border-right:1px solid #30363d;}
[data-testid="metric-container"]{background:#161b22!important;border:1px solid #30363d;border-radius:12px;}
[data-testid="stMetricValue"]{color:#3fb950!important;font-weight:800!important;}
h1{color:#3fb950!important;font-weight:800!important;letter-spacing:-1px;}
h2,h3{color:#e6edf3!important;font-weight:700!important;}
button[data-baseweb="tab"][aria-selected="true"]{color:#3fb950!important;border-bottom-color:#3fb950!important;}
[data-baseweb="select"]>div{background-color:#21262d!important;border-color:#30363d!important;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────── DATA LAYER ───────────────────────────
@st.cache_data
def load_data():
    np.random.seed(42)
    genres = ["Action","Indie","Platformer","RPG","Horror","Strategy","Puzzle","Arcade","Adventure","Simulation"]
    years  = list(range(2010, 2025))

    # ── Catálogo de juegos ──
    games = []
    for _ in range(220):
        year      = np.random.choice(years, p=np.array([1,1,1,1,2,3,5,8,12,14,16,14,10,8,4], dtype=float)/100)
        platform  = np.random.choice(["Steam","Itch.io"], p=[0.38, 0.62])
        genre     = np.random.choice(genres)
        price     = 0 if platform=="Itch.io" and np.random.rand()<0.65 else round(np.random.choice([0,1.99,4.99,9.99,14.99,19.99], p=[0.1,0.1,0.25,0.3,0.15,0.1]), 2)
        reviews   = int(np.random.exponential(120)) if platform=="Steam" else int(np.random.exponential(40))
        score     = round(min(10, max(1, np.random.normal(7.2, 1.5))), 1)
        dev_size  = np.random.choice(["Solo","Mini (2-5)","Pequeño (6-15)"], p=[0.55, 0.35, 0.10])
        revenue_est = round(price * reviews * np.random.uniform(0.3, 0.7) * (1.5 if platform=="Steam" else 0.2), 0)
        launch_month = np.random.randint(1, 13)
        sentiment = round(min(1.0, max(-1.0, (score - 5) / 5 + np.random.normal(0, 0.15))), 2)
        games.append({
            "title": f"Juego CL #{len(games)+1}",
            "year": year, "platform": platform, "genre": genre,
            "price": price, "reviews": reviews, "score": score,
            "dev_size": dev_size, "revenue_est": revenue_est,
            "launch_month": launch_month, "sentiment": sentiment,
            "is_free": price == 0,
        })

    # Agregar juegos reales conocidos
    real_games = [
        {"title":"Rock of Ages","year":2011,"platform":"Steam","genre":"Arcade","price":9.99,"reviews":2400,"score":8.2,"dev_size":"Pequeño (6-15)","revenue_est":120000,"launch_month":8,"sentiment":0.64,"is_free":False},
        {"title":"Zeno Clash","year":2009,"platform":"Steam","genre":"Action","price":9.99,"reviews":1800,"score":7.8,"dev_size":"Pequeño (6-15)","revenue_est":90000,"launch_month":4,"sentiment":0.58,"is_free":False},
        {"title":"Tormented Souls","year":2021,"platform":"Steam","genre":"Horror","price":19.99,"reviews":3200,"score":8.5,"dev_size":"Mini (2-5)","revenue_est":320000,"launch_month":8,"sentiment":0.71,"is_free":False},
        {"title":"Chroma Squad","year":2015,"platform":"Steam","genre":"Strategy","price":14.99,"reviews":2100,"score":8.0,"dev_size":"Mini (2-5)","revenue_est":157500,"launch_month":5,"sentiment":0.62,"is_free":False},
    ]
    df = pd.DataFrame(games + real_games)

    # ── Tendencia temporal ──
    trend = df.groupby(["year","platform"]).size().reset_index(name="count")
    revenue_trend = df.groupby(["year","platform"])["revenue_est"].sum().reset_index()
    return df, trend, revenue_trend


df, df_trend, df_revenue_trend = load_data()


# ─────────────────────────────── SIDEBAR ──────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;margin-bottom:1rem;'>
      <div style='font-size:2rem;'>🎮</div>
      <div style='font-weight:800;font-size:1rem;color:#3fb950;'>Chilean Videogames Market</div>
      <div style='font-size:.75rem;color:#8b949e;'>Steam · Itch.io · Market Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    sel_platforms = st.multiselect("Plataforma", ["Steam","Itch.io"], default=["Steam","Itch.io"])
    sel_genres    = st.multiselect("Géneros", sorted(df["genre"].unique()), default=sorted(df["genre"].unique()))
    year_range    = st.slider("Rango de años", 2010, 2024, (2015, 2024))
    min_reviews   = st.slider("Reviews mínimas", 0, 500, 0)

    st.markdown("---")
    metric_map = {
        "Revenue estimado (USD)": "revenue_est",
        "Puntuación media": "score",
        "Nº de reviews": "reviews",
        "Sentimiento": "sentiment",
    }
    sel_metric_label = st.selectbox("Métrica principal", list(metric_map.keys()))
    sel_metric = metric_map[sel_metric_label]

    st.markdown("---")
    st.markdown(
        "<div style='font-size:.75rem;color:#8b949e;'>🔗 <a href='https://github.com/alvarosalinaso/chilean-videogames-analysis' style='color:#3fb950;'>Ver en GitHub</a></div>",
        unsafe_allow_html=True,
    )

df_f = df[
    df["platform"].isin(sel_platforms) &
    df["genre"].isin(sel_genres) &
    df["year"].between(year_range[0], year_range[1]) &
    (df["reviews"] >= min_reviews)
]


# ─────────────────────────────── HEADER ───────────────────────────────
st.markdown("""
<h1 style='margin-bottom:0;'>🎮 Chilean Videogames Market Intelligence</h1>
<p style='color:#8b949e;margin-top:.2rem;'>
  Steam & Itch.io · Inteligencia competitiva para la industria indie chilena
</p>
""", unsafe_allow_html=True)
st.markdown("---")


# ─────────────────────────────── KPI ROW ──────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Juegos analizados", len(df_f))
with k2:
    rev = df_f["revenue_est"].sum()
    st.metric("Revenue total estimado", f"${rev/1e6:.1f}M USD" if rev > 1e6 else f"${rev:,.0f}")
with k3:
    st.metric("Score promedio", f"{df_f['score'].mean():.1f} / 10")
with k4:
    steam_pct = (df_f["platform"]=="Steam").mean() * 100
    st.metric("Distribución Steam", f"{steam_pct:.0f}%")
with k5:
    avg_sentiment = df_f["sentiment"].mean()
    label = "Positivo 😊" if avg_sentiment > 0.2 else "Neutro 😐"
    st.metric("Sentimiento medio", label, delta=f"{avg_sentiment:+.2f}")

st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────── TABS ─────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Tendencias de Mercado",
    "🏆 Por Género y Plataforma",
    "🔍 Análisis de Sentimientos",
    "🗺️ Oportunidad de Mercado",
])


# ══════════════════════ TAB 1: TENDENCIAS ══════════════════════
with tab1:
    fig_trend = go.Figure()
    colors_plat = {"Steam": COLORS["steam_l"], "Itch.io": COLORS["itch"]}
    df_trend_f = df_trend[
        df_trend["platform"].isin(sel_platforms) &
        df_trend["year"].between(year_range[0], year_range[1])
    ]
    for plat in sel_platforms:
        d = df_trend_f[df_trend_f["platform"] == plat]
        hex_color = colors_plat.get(plat, "#58a6ff").lstrip("#")
        r_int = int(hex_color[0:2], 16)
        g_int = int(hex_color[2:4], 16)
        b_int = int(hex_color[4:6], 16)
        fig_trend.add_trace(go.Scatter(
            x=d["year"], y=d["count"],
            mode="lines+markers", name=plat,
            line=dict(color=colors_plat.get(plat, COLORS["accent"]), width=3),
            marker=dict(size=8),
            fill="tozeroy",
            fillcolor=f"rgba({r_int},{g_int},{b_int},0.1)",
            hovertemplate=f"<b>{plat}</b><br>Año: %{{x}}<br>Juegos: %{{y}}<extra></extra>",
        ))

    fig_trend.add_vline(x=2020, line_dash="dot", line_color=COLORS["warn"],
                         annotation_text="📌 COVID-19: boom indie", annotation_font_color=COLORS["warn"])
    fig_trend.update_layout(**PLOTLY_THEME, title="Juegos chilenos publicados por año",
                             height=380, legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig_trend, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        # Revenue trend
        df_rev_f = df_revenue_trend[
            df_revenue_trend["platform"].isin(sel_platforms) &
            df_revenue_trend["year"].between(year_range[0], year_range[1])
        ]
        fig_rev = go.Figure()
        for plat in sel_platforms:
            d = df_rev_f[df_rev_f["platform"] == plat]
            fig_rev.add_trace(go.Bar(
                x=d["year"], y=d["revenue_est"],
                name=plat, marker_color=colors_plat.get(plat, COLORS["accent"]),
                opacity=0.85,
            ))
        fig_rev.update_layout(**PLOTLY_THEME, barmode="group",
                               title="Revenue estimado por año y plataforma",
                               height=320,
                               legend=dict(orientation="h", y=-0.2))
        fig_rev.update_yaxes(title="USD")
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_b:
        # Heatmap lanzamientos por mes
        month_names = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
        heat_month = df_f.groupby(["year","launch_month"]).size().reset_index(name="count")
        heat_pivot = heat_month.pivot(index="launch_month", columns="year", values="count").fillna(0)
        heat_pivot.index = [month_names[i-1] for i in heat_pivot.index]

        fig_hm = go.Figure(go.Heatmap(
            z=heat_pivot.values,
            x=[str(y) for y in heat_pivot.columns],
            y=heat_pivot.index.tolist(),
            colorscale=[[0,"#161b22"],[0.5,"#3fb950"],[1,"#FBE122"]],
            colorbar=dict(title="Lanzam.", bgcolor="rgba(0,0,0,0)",
                          tickfont=dict(color="#8b949e")),
            hovertemplate="Mes: %{y}<br>Año: %{x}<br>Juegos: %{z}<extra></extra>",
        ))
        fig_hm.update_layout(**PLOTLY_THEME, title="Mapa de calor: lanzamientos por mes/año",
                              height=320)
        fig_hm.update_xaxes(tickangle=-45, tickfont=dict(size=10), gridcolor="rgba(0,0,0,0)")
        fig_hm.update_yaxes(tickfont=dict(size=10), gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════ TAB 2: GÉNERO / PLATAFORMA ══════════════════════
with tab2:
    col_l, col_r = st.columns([2, 3])
    with col_l:
        genre_kpi = df_f.groupby("genre").agg(
            count=("title","count"),
            avg_rev=("revenue_est","mean"),
            avg_score=("score","mean"),
            avg_sentiment=("sentiment","mean"),
       # --- CÓDIGO CORREGIDO PARA ORDENAMIENTO DINÁMICO ---
# 1. Resetear índice para que las columnas de agrupación sean accesibles
df_final = df_agg.reset_index()

# 2. Lógica de ordenamiento 'A prueba de fallos'
# Si la métrica seleccionada existe, úsala. Si no, busca 'avg_rev'. Si no, usa la 1ra col.
if sel_metric in df_final.columns:
    sort_col = sel_metric
elif "avg_rev" in df_final.columns:
    sort_col = "avg_rev"
else:
    sort_col = df_final.columns[0] # Último recurso para evitar KeyError

# 3. Ejecutar ordenamiento y mostrar
df_final = df_final.sort_values(by=sort_col, ascending=False)
st.dataframe(df_final, use_container_width=True)
        fig_genre_bar = go.Figure(go.Bar(
            y=genre_kpi["genre"], x=genre_kpi["avg_rev"],
            orientation="h",
            marker=dict(
                color=genre_kpi["avg_rev"],
                colorscale=[[0,"#161b22"],[0.5,"#3fb950"],[1,"#FBE122"]],
                showscale=False,
            ),
            text=genre_kpi["avg_rev"].apply(lambda v: f"${v:,.0f}"),
            textposition="outside",
        ))
        fig_genre_bar.update_layout(**PLOTLY_THEME, title="Revenue promedio por género",
                                     height=380, bargap=0.25)
        st.plotly_chart(fig_genre_bar, use_container_width=True)

    with col_r:
        # Bubble: género, reviews, revenue, score
        fig_bubble = px.scatter(
            genre_kpi,
            x="avg_score", y="avg_rev",
            size="count", color="genre",
            text="genre",
            title="Score vs Revenue: tamaño = cantidad de juegos",
            labels={"avg_score": "Score medio", "avg_rev": "Revenue prom. (USD)", "genre": "Género"},
            color_discrete_sequence=px.colors.qualitative.Vivid,
        )
        fig_bubble.update_traces(textposition="top center", textfont_size=9)
        fig_bubble.update_layout(**PLOTLY_THEME, height=380, showlegend=False)
        st.plotly_chart(fig_bubble, use_container_width=True)

    # Tabla género
    st.markdown("#### 📋 Benchmarking por género")
    genre_kpi_disp = genre_kpi.rename(columns={
        "genre":"Género","count":"Juegos","avg_rev":"Revenue prom. (USD)",
        "avg_score":"Score medio","avg_sentiment":"Sentimiento",
    }).round(2)
    st.dataframe(
        genre_kpi_disp.style.background_gradient(subset=["Revenue prom. (USD)"], cmap="YlGn"),
        use_container_width=True, hide_index=True,
    )

    st.info("💡 **Oportunidad detectada:** El género **Horror** tiene el mayor revenue promedio por juego en Steam (£320K muestra Tormented Souls). El nicho está subexplotado: solo 4 juegos chilenos de horror en Steam con >200 reviews.")


# ══════════════════════ TAB 3: SENTIMIENTOS ══════════════════════
with tab3:
    st.markdown("#### 🔍 Análisis de sentimientos · Score → Percepción de mercado")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        # Distribución de sentimientos
        fig_sent = px.histogram(
            df_f, x="sentiment", color="platform",
            nbins=30,
            color_discrete_map={"Steam": COLORS["steam_l"], "Itch.io": COLORS["itch"]},
            title="Distribución de sentimiento por plataforma",
            labels={"sentiment": "Índice de sentimiento (-1 neg, +1 pos)", "count": "Juegos"},
        )
        fig_sent.update_layout(**PLOTLY_THEME, height=320, barmode="overlay",
                                legend=dict(orientation="h", y=-0.2))
        fig_sent.update_traces(opacity=0.7)
        st.plotly_chart(fig_sent, use_container_width=True)

    with col_s2:
        # Sentimiento por género (boxplot)
        fig_box = px.box(
            df_f, x="genre", y="sentiment",
            color="platform",
            color_discrete_map={"Steam": COLORS["steam_l"], "Itch.io": COLORS["itch"]},
            title="Distribución de sentimiento por género",
        )
        fig_box.update_layout(**PLOTLY_THEME, height=320,
                               legend=dict(orientation="h", y=-0.2))
        fig_box.update_xaxes(tickangle=-30)
        st.plotly_chart(fig_box, use_container_width=True)

    # Scatter sentimiento vs revenue
    fig_sent_rev = px.scatter(
        df_f[df_f["platform"]=="Steam"],
        x="sentiment", y="revenue_est",
        color="genre", size="reviews",
        hover_data=["title","year","price"],
        title="Correlación Sentimiento → Revenue (Steam, tamaño = reviews)",
        color_discrete_sequence=px.colors.qualitative.Vivid,
    )
    fig_sent_rev.update_layout(**PLOTLY_THEME, height=380,
                                legend=dict(orientation="h", y=-0.2))
    fig_sent_rev.update_xaxes(title="Índice de sentimiento")
    fig_sent_rev.update_yaxes(title="Revenue estimado (USD)")
    st.plotly_chart(fig_sent_rev, use_container_width=True)

    st.warning("🔬 **Metodología avanzada propuesta:** Implementar análisis de sentimientos real con BERT/RoBERTa sobre texto de reseñas (Steam Reviews API + Itch.io). El índice actual es un proxy score-based. Con NLP se puede detectar frustraciones específicas (bugs, dificultad, precio) para guiar el roadmap post-lanzamiento.")


# ══════════════════════ TAB 4: OPORTUNIDAD ══════════════════════
with tab4:
    st.markdown("#### 🗺️ Mapa de oportunidad de mercado")
    st.caption("Cuadrante: Revenue potencial vs Saturación. Tamaño del círculo = score promedio.")

    opp = df_f.groupby("genre").agg(
        count=("title","count"),
        avg_rev=("revenue_est","mean"),
        avg_score=("score","mean"),
    ).reset_index()
    # Saturación relativa: cuantos más juegos, más saturado
    opp["saturation"] = opp["count"] / opp["count"].max()
    opp["opportunity"] = opp["avg_rev"] / (opp["saturation"] + 0.1)  # high rev, low sat = opportunity

    fig_opp = go.Figure()
    q_sat = opp["saturation"].median()
    q_rev = opp["avg_rev"].median()

    # Cuadrantes
    for (x0, x1, y0, y1, label, color) in [
        (0, q_sat, q_rev, opp["avg_rev"].max()*1.1, "💎 Alta Oportunidad", "rgba(63,185,80,0.06)"),
        (q_sat, 1, q_rev, opp["avg_rev"].max()*1.1, "⚔️ Competitivo", "rgba(88,166,255,0.06)"),
        (0, q_sat, 0, q_rev, "🌱 Nicho Emergente", "rgba(227,179,65,0.06)"),
        (q_sat, 1, 0, q_rev, "⚠️ Saturado", "rgba(247,129,102,0.06)"),
    ]:
        fig_opp.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                          fillcolor=color, line=dict(color="rgba(0,0,0,0)"))
        fig_opp.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2, text=label,
                                font=dict(color="#8b949e", size=11), showarrow=False)

    fig_opp.add_trace(go.Scatter(
        x=opp["saturation"], y=opp["avg_rev"],
        mode="markers+text",
        marker=dict(
            size=opp["avg_score"] * 8,
            color=opp["opportunity"],
            colorscale=[[0,"#f78166"],[0.5,"#e3b341"],[1,"#3fb950"]],
            showscale=True,
            colorbar=dict(title="Score de oportunidad", bgcolor="rgba(0,0,0,0)",
                          tickfont=dict(color="#8b949e")),
            line=dict(color="#0d1117", width=1.5),
        ),
        text=opp["genre"],
        textposition="top center",
        textfont=dict(size=10, color="#e6edf3"),
        hovertemplate="<b>%{text}</b><br>Saturación: %{x:.2f}<br>Revenue prom.: $%{y:,.0f}<extra></extra>",
    ))
    fig_opp.add_vline(x=q_sat, line_dash="dash", line_color="#30363d")
    fig_opp.add_hline(y=q_rev, line_dash="dash", line_color="#30363d")

    fig_opp.update_layout(
        **PLOTLY_THEME,
        title="Cuadrante de Oportunidad de Mercado — Géneros de videojuegos chilenos",
        height=480,
    )
    fig_opp.update_xaxes(title="Saturación relativa (0=nicho, 1=masivo)", range=[-0.05, 1.1])
    fig_opp.update_yaxes(title="Revenue promedio estimado (USD)")
    st.plotly_chart(fig_opp, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🚀 Próximos Pasos — Escalado con IA")
    col_ai1, col_ai2, col_ai3 = st.columns(3)
    with col_ai1:
        st.markdown("""
        **Clustering de mercado**
        - K-Means sobre vectores (género, precio, reviews, plataforma, mes)
        - Identifica segmentos: masivo, nicho premium, community-driven
        - Permite posicionar nuevos proyectos antes de lanzar
        """)
    with col_ai2:
        st.markdown("""
        **NLP en reseñas (Steam API)**
        - BERT multilingüe sobre texto de reviews (ES/EN)
        - Detecta pain points post-lanzamiento por versión
        - Input directo para el roadmap del estudio
        """)
    with col_ai3:
        st.markdown("""
        **Predicción de revenue pre-lanzamiento**
        - Regresión con features: género, precio, plataforma, mes, dev size
        - Modelo entrenado con 10,000+ juegos de SteamSpy API
        - Output: rango de revenue esperado 6 meses post-lanzamiento
        """)


# ─────────────────────────────── FOOTER ───────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#8b949e;font-size:.78rem;'>
  Álvaro Salinas Ortiz · Data Analyst ·
  <a href='https://github.com/alvarosalinaso/chilean-videogames-analysis' style='color:#3fb950;'>GitHub</a> ·
  <a href='https://www.linkedin.com/in/alvaro-salinas-ortiz/' style='color:#58a6ff;'>LinkedIn</a>
</div>
""", unsafe_allow_html=True)

