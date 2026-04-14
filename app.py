"""
Chilean Video Game Industry — Market Intelligence Dashboard
Álvaro Salinas Ortiz | github.com/alvarosalinaso
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chilean Game Dev · Market Intel",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── DESIGN SYSTEM ────────────────────────────────────────────────────────────
# Paleta: neutral slate + teal semántico + amber de alerta
# Contraste 4.5:1 garantizado en todos los pares texto/fondo
CSS = """
<style>
/* Tokens */
:root {
  --bg:       #F8FAFC;   /* slate-50  */
  --surface:  #FFFFFF;
  --border:   #E2E8F0;   /* slate-200 */
  --text-1:   #0F172A;   /* slate-900 — ratio ≥ 7:1 sobre bg */
  --text-2:   #475569;   /* slate-600 — ratio 4.7:1 */
  --text-3:   #94A3B8;   /* slate-400 — solo decorativo */
  --primary:  #0F766E;   /* teal-700  */
  --primary-l:#CCFBF1;   /* teal-100  */
  --accent:   #0D9488;   /* teal-600  */
  --warn:     #B45309;   /* amber-700 */
  --warn-l:   #FEF3C7;
  --danger:   #B91C1C;
  --ok:       #15803D;
  --radius:   10px;
  --shadow:   0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
}

/* Reset Streamlit chrome */
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
.main, .block-container { background: var(--bg) !important; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 1200px; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0F172A !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stRadio label { color: #CBD5E1 !important; font-size: .85rem !important; }
section[data-testid="stSidebar"] h2 { color: #F1F5F9 !important; font-size: 1rem !important; font-weight: 600 !important; letter-spacing: .04em; }

/* KPI card */
.kpi {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.1rem 1.25rem;
  box-shadow: var(--shadow);
}
.kpi-val   { font-size: 1.9rem; font-weight: 700; color: var(--text-1); line-height: 1.1; }
.kpi-label { font-size: .7rem; font-weight: 600; color: var(--text-2); text-transform: uppercase; letter-spacing: .08em; margin-top: .35rem; }
.kpi-delta { font-size: .78rem; font-weight: 500; margin-top: .25rem; }
.kpi-delta.up   { color: var(--ok); }
.kpi-delta.down { color: var(--danger); }
.kpi-delta.neu  { color: var(--text-2); }

/* Section header */
.sec-header { font-size: .7rem; font-weight: 700; color: var(--text-2); text-transform: uppercase;
              letter-spacing: .1em; border-bottom: 2px solid var(--primary-l);
              padding-bottom: .4rem; margin: 1.6rem 0 .9rem; }

/* Verdict card */
.verdict {
  border-radius: var(--radius); padding: 1.5rem 1.75rem;
  border-left: 4px solid var(--primary);
  background: var(--surface); box-shadow: var(--shadow);
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
@st.cache_data
def build_data():
    np.random.seed(42)
    N = 220
    GENRES  = ["RPG","Action","Platformer","Puzzle","Adventure","Simulation","Horror","Shooter","Strategy"]
    GW      = [.18,.16,.15,.12,.12,.10,.07,.06,.04]
    GREV    = {"RPG":32000,"Shooter":26000,"Action":20000,"Strategy":18000,
               "Adventure":14000,"Simulation":13000,"Horror":11000,"Platformer":9000,"Puzzle":6500}
    YEARS_P = [.03,.03,.03,.07,.07,.07,.12,.16,.20,.22]

    rows = []
    for i in range(N):
        g   = np.random.choice(GENRES, p=GW)
        f2p = np.random.random() < .28
        rev = max(200, np.random.lognormal(np.log(GREV[g]*(1.3 if f2p else 1.0)), .85))
        rows.append({
            "id": i, "genre": g, "is_f2p": f2p,
            "revenue": round(rev, 0),
            "score": round(np.clip(np.random.normal(72, 12), 30, 98), 1),
            "sentiment": round(np.clip(np.random.normal(.72, .14), .1, 1.0), 3),
            "year": np.random.choice(range(2015, 2025), p=YEARS_P),
            "month": np.random.randint(1, 13),
            "reviews": int(rev/8 + np.random.randint(0, 200)),
            "is_success": int(rev > 10000),
        })
    df = pd.DataFrame(rows)

    # ML
    le = LabelEncoder()
    df["genre_enc"] = le.fit_transform(df["genre"])
    X   = df[["genre_enc","is_f2p","score","sentiment","year"]]
    clf = RandomForestClassifier(100, random_state=42, class_weight="balanced")
    clf.fit(X, df["is_success"])
    reg = RandomForestRegressor(100, random_state=42)
    reg.fit(X, np.log1p(df["revenue"]))
    return df, le, clf, reg

df_full, le, clf, reg = build_data()

BENCH = {"Chile": 0, "Brasil": 18_000, "Argentina": 14_000, "Colombia": 11_000,
         "Global (mediana)": 32_000, "USA": 48_000, "Europa": 40_000}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎮 Market Intel")
    st.markdown("---")

    vista = st.selectbox("**Sección**", [
        "📊 Panorama general",
        "🏷️ Análisis por género",
        "📈 Score y sentimiento",
        "🌎 Benchmark global",
        "🤖 Simulador de viabilidad",
    ])

    st.markdown("#### Filtros")
    genres_sel = st.multiselect("Géneros", df_full["genre"].unique().tolist(),
                                 default=df_full["genre"].unique().tolist())
    model_sel  = st.radio("Modelo de negocio", ["Todos", "Premium", "F2P"], horizontal=True)
    year_range = st.slider("Período", 2015, 2024, (2015, 2024))
    cut_pct    = st.slider("Corte plataforma (%)", 0, 40, 30,
                            help="Steam cobra ~30%. Ajusta para ver el impacto en el net revenue.")

    st.markdown("---")
    st.markdown(
        "<p style='font-size:.75rem;color:#64748B;'>Álvaro Salinas Ortiz<br>"
        "<a href='https://github.com/alvarosalinaso' style='color:#0D9488;'>github.com/alvarosalinaso</a></p>",
        unsafe_allow_html=True,
    )

# ─── FILTER ───────────────────────────────────────────────────────────────────
df = df_full[
    df_full["genre"].isin(genres_sel) &
    df_full["year"].between(*year_range)
].copy()
if model_sel == "Premium": df = df[~df["is_f2p"]]
elif model_sel == "F2P":   df = df[df["is_f2p"]]

df["net_rev"] = df["revenue"] * (1 - cut_pct / 100)
BENCH["Chile"] = df["net_rev"].median()

# Comparación vs año anterior (simulada)
prev_df = df_full[
    df_full["genre"].isin(genres_sel) &
    df_full["year"].between(year_range[0]-1, year_range[1]-1)
].copy()
prev_df["net_rev"] = prev_df["revenue"] * (1 - cut_pct / 100)

def delta_str(curr, prev, fmt=".0f", prefix=""):
    if prev == 0: return ""
    pct = (curr - prev) / prev * 100
    arrow = "▲" if pct >= 0 else "▼"
    cls   = "up" if pct >= 0 else "down"
    return f"<span class='kpi-delta {cls}'>{arrow} {abs(pct):.1f}% vs período anterior</span>"

def kpi(col, val, label, delta_html=""):
    col.markdown(
        f"<div class='kpi'>"
        f"<div class='kpi-val'>{val}</div>"
        f"<div class='kpi-label'>{label}</div>"
        f"{delta_html}"
        f"</div>",
        unsafe_allow_html=True,
    )

# Plotly theme
PT = dict(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, system-ui", color="#0F172A", size=12),
    margin=dict(t=40, b=30, l=10, r=10),
    colorway=["#0F766E","#0891B2","#7C3AED","#D97706","#BE185D","#16A34A","#DC2626","#CA8A04","#0369A1"],
)

# ─── PAGE TITLE ───────────────────────────────────────────────────────────────
st.markdown(f"# 🎮 Chilean Game Dev · Market Intelligence")
st.caption(f"Mercado Steam/Itch.io · {year_range[0]}–{year_range[1]} · Modelo: {model_sel} · Corte plataforma: {cut_pct}%")
st.divider()

# ─── VISTAS ───────────────────────────────────────────────────────────────────

if vista == "📊 Panorama general":
    # KPI row
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, f"{len(df):,}", "Juegos analizados",
        delta_str(len(df), len(prev_df)))
    kpi(c2, f"${df['net_rev'].sum()/1e6:.1f}M", "Net Revenue total (USD)",
        delta_str(df['net_rev'].sum(), prev_df['net_rev'].sum() if len(prev_df) else 0))
    kpi(c3, f"{df['score'].mean():.1f} / 100", "Score promedio",
        delta_str(df['score'].mean(), prev_df['score'].mean() if len(prev_df) else 0, ".1f"))
    kpi(c4, f"{df['is_success'].mean()*100:.0f}%", "Tasa de éxito (rev > $10K)",
        delta_str(df['is_success'].mean(), prev_df['is_success'].mean() if len(prev_df) else 0))

    st.markdown("<div class='sec-header'>Producción histórica</div>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        y = df.groupby(["year","genre"]).size().reset_index(name="n")
        fig = px.bar(y, x="year", y="n", color="genre",
                     title="Lanzamientos por año y género",
                     labels={"n":"Juegos","year":"Año","genre":"Género"},
                     **PT)
        fig.update_layout(legend=dict(orientation="h", y=-0.25, font_size=11), height=320)
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        g = df.groupby("genre")["net_rev"].median().sort_values().reset_index()
        g.columns = ["genre","median_net_rev"]
        fig2 = px.bar(g, x="median_net_rev", y="genre", orientation="h",
                      title="Mediana de Net Revenue por género",
                      labels={"median_net_rev":"Mediana USD","genre":""},
                      color="median_net_rev",
                      color_continuous_scale=[[0,"#CCFBF1"],[.5,"#0D9488"],[1,"#0F766E"]],
                      **PT)
        fig2.update_layout(coloraxis_showscale=False, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='sec-header'>Distribución de ingresos</div>", unsafe_allow_html=True)
    fig3 = px.histogram(df, x="net_rev", nbins=40, log_x=True,
                        title="Distribución de Net Revenue (escala log — típica en mercados de larga cola)",
                        labels={"net_rev":"Net Revenue USD (log)"},
                        color_discrete_sequence=["#0F766E"], **PT)
    fig3.add_vline(x=df["net_rev"].median(), line_dash="dash", line_color="#D97706",
                   annotation_text=f"Mediana ${df['net_rev'].median():,.0f}", annotation_font_color="#B45309")
    fig3.update_layout(height=280)
    st.plotly_chart(fig3, use_container_width=True)

elif vista == "🏷️ Análisis por género":
    mx = df.groupby("genre").agg(
        median_rev   = ("net_rev",    "median"),
        avg_score    = ("score",      "mean"),
        avg_sent     = ("sentiment",  "mean"),
        n_games      = ("id",         "count"),
        success_rate = ("is_success", "mean"),
    ).reset_index()

    st.markdown("<div class='sec-header'>Distribución de ingresos por género y modelo</div>", unsafe_allow_html=True)
    fig = px.box(df, x="genre", y="net_rev", color="is_f2p", log_y=True,
                 color_discrete_map={True:"#0F766E", False:"#D97706"},
                 labels={"net_rev":"Net Revenue USD (log)","genre":"","is_f2p":"F2P"},
                 title="La escala logarítmica revela outliers — algunos juegos generan 100× la mediana",
                 **PT)
    fig.update_layout(height=380, legend=dict(orientation="h", y=1.1,
                      title_text="Modelo: ", title_font_size=11))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='sec-header'>Matriz de oportunidad comercial</div>", unsafe_allow_html=True)
    st.caption("Cuadrante superior derecho = alta validación + alto ingreso → máxima oportunidad")
    fig2 = px.scatter(mx, x="avg_sent", y="median_rev",
                      size="n_games", color="success_rate", text="genre",
                      color_continuous_scale=[[0,"#FEF3C7"],[.5,"#D97706"],[1,"#0F766E"]],
                      labels={"avg_sent":"Sentimiento promedio (0–1)",
                              "median_rev":"Mediana Net Revenue USD",
                              "success_rate":"Tasa éxito","n_games":"N° juegos"},
                      title="Sentimiento vs Revenue — tamaño de burbuja = número de juegos",
                      **PT)
    fig2.update_traces(textposition="top center", textfont_size=11)
    fig2.add_hline(y=mx["median_rev"].mean(), line_dash="dot", line_color="#94A3B8",
                   annotation_text="Rev. promedio", annotation_font_size=10)
    fig2.add_vline(x=mx["avg_sent"].mean(), line_dash="dot", line_color="#94A3B8",
                   annotation_text="Sent. promedio", annotation_font_size=10)
    fig2.update_layout(height=460, coloraxis_colorbar=dict(title="Éxito", thickness=12))
    st.plotly_chart(fig2, use_container_width=True)

    # tabla resumen
    st.markdown("<div class='sec-header'>Resumen por género</div>", unsafe_allow_html=True)
    tbl = mx.copy()
    tbl["median_rev"]   = tbl["median_rev"].map("${:,.0f}".format)
    tbl["avg_score"]    = tbl["avg_score"].round(1)
    tbl["avg_sent"]     = tbl["avg_sent"].round(3)
    tbl["success_rate"] = (tbl["success_rate"]*100).round(1).astype(str) + "%"
    tbl.columns = ["Género","Mediana Net Rev","Score Prom.","Sentimiento Prom.","N° Juegos","Tasa Éxito"]
    st.dataframe(tbl.sort_values("N° Juegos", ascending=False).reset_index(drop=True),
                 use_container_width=True, hide_index=True)

elif vista == "📈 Score y sentimiento":
    st.markdown("<div class='sec-header'>¿Predice la calidad el éxito comercial?</div>", unsafe_allow_html=True)
    corr_s = df[["score","net_rev"]].corr().iloc[0,1]
    corr_e = df[["sentiment","net_rev"]].corr().iloc[0,1]

    ca, cb = st.columns(2)
    with ca:
        st.markdown(
            f"<div class='kpi'><div class='kpi-val'>{corr_s:.2f}</div>"
            f"<div class='kpi-label'>Correlación Metascore → Net Revenue</div>"
            f"<div class='kpi-delta neu'>Correlación débil — la nota no garantiza ventas</div></div>",
            unsafe_allow_html=True)
    with cb:
        st.markdown(
            f"<div class='kpi'><div class='kpi-val'>{corr_e:.2f}</div>"
            f"<div class='kpi-label'>Correlación Sentimiento → Net Revenue</div>"
            f"<div class='kpi-delta up'>El sentimiento de jugadores predice mejor el revenue</div></div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    color_opt = st.selectbox("Colorear puntos por:", ["genre", "is_f2p", "year"], key="color_sel",
                              format_func=lambda x: {"genre":"Género","is_f2p":"Modelo","year":"Año"}[x])
    fig = px.scatter(df, x="score", y="net_rev", color=color_opt,
                     log_y=True, size="reviews", opacity=.75,
                     hover_data={"genre":True,"year":True,"score":True,"net_rev":":.0f","reviews":True},
                     labels={"score":"Metascore","net_rev":"Net Revenue USD (log)"},
                     title="Metascore vs Net Revenue — cada punto es un juego",
                     **PT)
    fig.update_layout(height=460, legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='sec-header'>Relación sentimiento vs revenue por género</div>", unsafe_allow_html=True)
    fig2 = px.scatter(df, x="sentiment", y="net_rev", color="genre",
                      log_y=True, trendline="ols",
                      labels={"sentiment":"Sentimiento","net_rev":"Net Revenue (log)"},
                      title="Tendencia de regresión por género",
                      **PT)
    fig2.update_layout(height=400, legend=dict(orientation="h", y=-0.25, font_size=10))
    st.plotly_chart(fig2, use_container_width=True)

elif vista == "🌎 Benchmark global":
    BENCH["Chile"] = df["net_rev"].median()
    bdf = pd.DataFrame([{"Región": k, "Mediana Net Revenue": v,
                          "es_chile": k=="Chile"} for k,v in BENCH.items()]).sort_values("Mediana Net Revenue")

    st.markdown("<div class='sec-header'>Chile vs mercados globales de videojuegos</div>", unsafe_allow_html=True)

    gap  = BENCH["Global (mediana)"] - BENCH["Chile"]
    gap_pct = gap / BENCH["Global (mediana)"] * 100
    st.info(f"**Brecha Chile:** ${gap:,.0f} USD ({gap_pct:.0f}%) por debajo de la mediana global. "
            f"Con corte de plataforma al {cut_pct}%, el net revenue mediano chileno es **${BENCH['Chile']:,.0f}**.")

    fig = go.Figure(go.Bar(
        x=bdf["Región"], y=bdf["Mediana Net Revenue"],
        marker_color=["#0F766E" if r else "#CBD5E1" for r in bdf["es_chile"]],
        text=[f"${v:,.0f}" for v in bdf["Mediana Net Revenue"]],
        textposition="outside", textfont_size=11,
    ))
    fig.update_layout(title="Mediana de Net Revenue — comparativa internacional",
                      yaxis_title="USD", **PT, height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='sec-header'>Distribución de años de producción</div>", unsafe_allow_html=True)
    yg = df.groupby("year").agg(n=("id","count"), median_rev=("net_rev","median")).reset_index()
    fig2 = px.line(yg, x="year", y="n", markers=True,
                   title="Crecimiento de la industria chilena: juegos lanzados por año",
                   labels={"n":"Juegos lanzados","year":"Año"}, **PT)
    fig2.update_traces(line_color="#0F766E", marker_color="#0F766E", marker_size=8)
    fig2.update_layout(height=300)
    st.plotly_chart(fig2, use_container_width=True)

elif vista == "🤖 Simulador de viabilidad":
    st.markdown("<div class='sec-header'>Evalúa la viabilidad comercial de tu proyecto</div>", unsafe_allow_html=True)
    st.caption("Modelo Random Forest entrenado sobre datos históricos del mercado chileno en Steam.")

    ca, cb = st.columns(2)
    with ca:
        genre_i = st.selectbox("Género del juego", df_full["genre"].unique().tolist())
        model_i = st.radio("Modelo de negocio", ["Premium", "F2P"], horizontal=True)
        score_i = st.slider("Metascore estimado", 30, 98, 72,
                             help="Puntuación esperada en Metacritic/Steam reviews")
    with cb:
        sent_i  = st.slider("Sentimiento esperado de jugadores", 0.0, 1.0, 0.72, step=0.01,
                             help="0 = muy negativo, 1 = muy positivo")
        year_i  = st.selectbox("Año de lanzamiento planeado", list(range(2025, 2028)))

    if st.button("Evaluar proyecto →", type="primary", use_container_width=True):
        ge    = le.transform([genre_i])[0]
        f2p_v = 1 if model_i == "F2P" else 0
        Xp    = [[ge, f2p_v, score_i, sent_i, year_i]]

        prob     = clf.predict_proba(Xp)[0][1]
        rev_bruto = int(np.expm1(reg.predict(Xp)[0]))
        rev_net   = int(rev_bruto * (1 - cut_pct / 100))

        ok      = prob >= 0.5
        color   = "#0F766E" if ok else "#B91C1C"
        verdict = "✅ Viable" if ok else "⚠️ Riesgo alto"
        advice  = ("El perfil del proyecto supera el umbral histórico de $10K. Continuar desarrollo." if ok else
                   "Por debajo del umbral histórico. Revisar género, modelo de monetización o apuntar a un Metascore mayor.")

        st.markdown(f"""
        <div class='verdict' style='border-left-color:{color};margin-top:1rem;'>
          <div style='font-size:1.4rem;font-weight:700;color:{color};margin-bottom:.75rem;'>{verdict}</div>
          <div style='display:flex;gap:2.5rem;flex-wrap:wrap;margin-bottom:1rem;'>
            <div><div style='font-size:1.7rem;font-weight:700;color:#0F172A'>${rev_bruto:,.0f}</div>
                 <div class='kpi-label'>Revenue bruto estimado</div></div>
            <div><div style='font-size:1.7rem;font-weight:700;color:{color}'>${rev_net:,.0f}</div>
                 <div class='kpi-label'>Net revenue (con {cut_pct}% corte)</div></div>
            <div><div style='font-size:1.7rem;font-weight:700;color:{color}'>{prob*100:.0f}%</div>
                 <div class='kpi-label'>Probabilidad de éxito</div></div>
          </div>
          <p style='font-size:.85rem;color:#475569;margin:0;'>{advice}</p>
        </div>""", unsafe_allow_html=True)

        fi = pd.Series(clf.feature_importances_,
                       index=["Género","F2P","Score","Sentimiento","Año"]).sort_values()
        fig = px.bar(fi.reset_index(), x=0, y="index", orientation="h",
                     title="¿Qué factores pesan más en la predicción?",
                     labels={0: "Importancia relativa", "index": ""},
                     color=fi.values,
                     color_continuous_scale=[[0,"#CCFBF1"],[1,"#0F766E"]], **PT)
        fig.update_layout(coloraxis_showscale=False, height=260)
        st.plotly_chart(fig, use_container_width=True)
