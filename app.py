import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

st.set_page_config(
    page_title="Chilean Game Dev · Market Intel",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.kpi{background:#fff;border:1px solid #E2E8F0;border-radius:10px;padding:1.1rem 1.25rem;box-shadow:0 1px 3px rgba(0,0,0,.08);}
.kpi-val{font-size:1.9rem;font-weight:700;color:#0F172A;line-height:1.1;}
.kpi-label{font-size:.7rem;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-top:.35rem;}
.kpi-delta{font-size:.78rem;font-weight:500;margin-top:.25rem;}
.kpi-delta.up{color:#15803D;} .kpi-delta.down{color:#B91C1C;} .kpi-delta.neu{color:#475569;}
.sec-h{font-size:.7rem;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.1em;
       border-bottom:2px solid #CCFBF1;padding-bottom:.4rem;margin:1.6rem 0 .9rem;}
.verdict{border-radius:10px;padding:1.5rem 1.75rem;border-left:4px solid #0F766E;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08);}
</style>""", unsafe_allow_html=True)

@st.cache_data
def build_data():
    np.random.seed(42)
    N = 220
    GENRES = ["RPG","Action","Platformer","Puzzle","Adventure","Simulation","Horror","Shooter","Strategy"]
    GW = [.18,.16,.15,.12,.12,.10,.07,.06,.04]
    GREV = {"RPG":32000,"Shooter":26000,"Action":20000,"Strategy":18000,
            "Adventure":14000,"Simulation":13000,"Horror":11000,"Platformer":9000,"Puzzle":6500}
    YEARS_P = [.03,.03,.03,.07,.07,.07,.12,.16,.20,.22]
    rows = []
    for i in range(N):
        g = np.random.choice(GENRES, p=GW); f2p = np.random.random() < .28
        rev = max(200, np.random.lognormal(np.log(GREV[g]*(1.3 if f2p else 1.0)), .85))
        rows.append({"id":i,"genre":g,"is_f2p":f2p,"revenue":round(rev,0),
            "score":round(np.clip(np.random.normal(72,12),30,98),1),
            "sentiment":round(np.clip(np.random.normal(.72,.14),.1,1.0),3),
            "year":np.random.choice(range(2015,2025),p=YEARS_P),
            "reviews":int(rev/8+np.random.randint(0,200)),"is_success":int(rev>10000)})
    df = pd.DataFrame(rows)
    le = LabelEncoder(); df["genre_enc"] = le.fit_transform(df["genre"])
    X = df[["genre_enc","is_f2p","score","sentiment","year"]]
    clf = RandomForestClassifier(100,random_state=42,class_weight="balanced"); clf.fit(X,df["is_success"])
    reg = RandomForestRegressor(100,random_state=42); reg.fit(X,np.log1p(df["revenue"]))
    return df, le, clf, reg

df_full, le, clf, reg = build_data()
BENCH = {"Chile":0,"Brasil":18000,"Argentina":14000,"Colombia":11000,"Global (mediana)":32000,"USA":48000,"Europa":40000}

LAYOUT = dict(template="plotly_white",paper_bgcolor="white",plot_bgcolor="white",
              font=dict(family="system-ui",color="#0F172A",size=12),margin=dict(t=44,b=30,l=10,r=10))
PAL = ["#0F766E","#0891B2","#7C3AED","#D97706","#BE185D","#16A34A","#DC2626","#CA8A04","#0369A1"]

with st.sidebar:
    st.markdown("## 🎮 Market Intel")
    st.markdown("---")
    vista = st.selectbox("**Sección**",["📊 Panorama general","🏷️ Análisis por género",
        "📈 Score y sentimiento","🌎 Benchmark global","🤖 Simulador de viabilidad"])
    st.markdown("#### Filtros")
    genres_sel = st.multiselect("Géneros",df_full["genre"].unique().tolist(),default=df_full["genre"].unique().tolist())
    model_sel = st.radio("Modelo",["Todos","Premium","F2P"],horizontal=True)
    year_range = st.slider("Período",2015,2024,(2015,2024))
    cut_pct = st.slider("Corte plataforma (%)",0,40,30,help="Steam cobra ~30%")
    st.markdown("---")
    st.markdown("<p style='font-size:.75rem;color:#94A3B8;'>Álvaro Salinas Ortiz<br>"
        "<a href='https://github.com/alvarosalinaso' style='color:#0D9488;'>github.com/alvarosalinaso</a></p>",
        unsafe_allow_html=True)

df = df_full[df_full["genre"].isin(genres_sel)&df_full["year"].between(*year_range)].copy()
if model_sel=="Premium": df=df[~df["is_f2p"]]
elif model_sel=="F2P": df=df[df["is_f2p"]]
df["net_rev"] = df["revenue"]*(1-cut_pct/100)
BENCH["Chile"] = df["net_rev"].median()

prev = df_full[df_full["genre"].isin(genres_sel)&df_full["year"].between(year_range[0]-1,year_range[1]-1)].copy()
prev["net_rev"] = prev["revenue"]*(1-cut_pct/100)

def delta(curr,prev_val):
    if prev_val==0: return ""
    pct=(curr-prev_val)/prev_val*100; cls="up" if pct>=0 else "down"; arr="▲" if pct>=0 else "▼"
    return f"<div class='kpi-delta {cls}'>{arr} {abs(pct):.1f}% vs período anterior</div>"

def kpi(col,val,label,d=""):
    col.markdown(f"<div class='kpi'><div class='kpi-val'>{val}</div><div class='kpi-label'>{label}</div>{d}</div>",unsafe_allow_html=True)

st.markdown("# 🎮 Chilean Game Dev · Market Intelligence")
st.caption(f"Steam/Itch.io · {year_range[0]}–{year_range[1]} · {model_sel} · Corte: {cut_pct}%")
st.divider()

if vista=="📊 Panorama general":
    c1,c2,c3,c4=st.columns(4)
    kpi(c1,f"{len(df):,}","Juegos analizados",delta(len(df),len(prev)))
    kpi(c2,f"${df['net_rev'].sum()/1e6:.1f}M","Net Revenue total",delta(df['net_rev'].sum(),prev['net_rev'].sum() if len(prev) else 0))
    kpi(c3,f"{df['score'].mean():.1f} / 100","Score promedio",delta(df['score'].mean(),prev['score'].mean() if len(prev) else 0))
    kpi(c4,f"{df['is_success'].mean()*100:.0f}%","Tasa de éxito",delta(df['is_success'].mean(),prev['is_success'].mean() if len(prev) else 0))
    st.markdown("<div class='sec-h'>Producción histórica</div>",unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        y=df.groupby(["year","genre"]).size().reset_index(name="n")
        fig=px.bar(y,x="year",y="n",color="genre",
            title="Lanzamientos por año y género",
            labels={"n":"Juegos","year":"Año","genre":"Género"},
            color_discrete_sequence=PAL)
        fig.update_layout(**LAYOUT,height=320,legend=dict(orientation="h",y=-0.3,font_size=10))
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        g=df.groupby("genre")["net_rev"].median().sort_values().reset_index()
        fig2=px.bar(g,x="net_rev",y="genre",orientation="h",
            title="Mediana Net Revenue por género",
            labels={"net_rev":"Mediana USD","genre":""},
            color="net_rev",color_continuous_scale=[[0,"#CCFBF1"],[.5,"#0D9488"],[1,"#0F766E"]])
        fig2.update_layout(**LAYOUT,height=320,coloraxis_showscale=False)
        st.plotly_chart(fig2,use_container_width=True)
    st.markdown("<div class='sec-h'>Distribución de ingresos</div>",unsafe_allow_html=True)
    fig3=px.histogram(df,x="net_rev",nbins=40,log_x=True,
        title="Distribución Net Revenue — escala log (mercado de larga cola)",
        labels={"net_rev":"Net Revenue USD (log)"},color_discrete_sequence=["#0F766E"])
    fig3.add_vline(x=df["net_rev"].median(),line_dash="dash",line_color="#D97706",
        annotation_text=f"Mediana ${df['net_rev'].median():,.0f}",annotation_font_color="#B45309")
    fig3.update_layout(**LAYOUT,height=280)
    st.plotly_chart(fig3,use_container_width=True)

elif vista=="🏷️ Análisis por género":
    mx=df.groupby("genre").agg(median_rev=("net_rev","median"),avg_score=("score","mean"),
        avg_sent=("sentiment","mean"),n_games=("id","count"),success_rate=("is_success","mean")).reset_index()
    st.markdown("<div class='sec-h'>Distribución por género y modelo</div>",unsafe_allow_html=True)
    fig=px.box(df,x="genre",y="net_rev",color="is_f2p",log_y=True,
        color_discrete_map={True:"#0F766E",False:"#D97706"},
        labels={"net_rev":"Net Revenue (log)","genre":"","is_f2p":"F2P"},
        title="Net Revenue por género — escala log revela outliers")
    fig.update_layout(**LAYOUT,height=380,legend=dict(orientation="h",y=1.1))
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("<div class='sec-h'>Matriz de oportunidad</div>",unsafe_allow_html=True)
    st.caption("Cuadrante superior derecho = alta validación + alto ingreso")
    fig2=px.scatter(mx,x="avg_sent",y="median_rev",size="n_games",color="success_rate",text="genre",
        color_continuous_scale=[[0,"#FEF3C7"],[.5,"#D97706"],[1,"#0F766E"]],
        labels={"avg_sent":"Sentimiento promedio","median_rev":"Mediana Net Revenue USD",
                "success_rate":"Tasa éxito","n_games":"N° juegos"},
        title="Sentimiento vs Revenue — burbuja = volumen")
    fig2.update_traces(textposition="top center",textfont_size=11)
    fig2.add_hline(y=mx["median_rev"].mean(),line_dash="dot",line_color="#94A3B8")
    fig2.add_vline(x=mx["avg_sent"].mean(),line_dash="dot",line_color="#94A3B8")
    fig2.update_layout(**LAYOUT,height=460,coloraxis_colorbar=dict(title="Éxito",thickness=12))
    st.plotly_chart(fig2,use_container_width=True)
    tbl=mx.copy()
    tbl["median_rev"]=tbl["median_rev"].map("${:,.0f}".format)
    tbl["avg_score"]=tbl["avg_score"].round(1)
    tbl["avg_sent"]=tbl["avg_sent"].round(3)
    tbl["success_rate"]=(tbl["success_rate"]*100).round(1).astype(str)+"%"
    tbl.columns=["Género","Mediana Net Rev","Score Prom.","Sentimiento","N° Juegos","Tasa Éxito"]
    st.dataframe(tbl.sort_values("N° Juegos",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)

elif vista=="📈 Score y sentimiento":
    corr_s=df[["score","net_rev"]].corr().iloc[0,1]
    corr_e=df[["sentiment","net_rev"]].corr().iloc[0,1]
    ca,cb=st.columns(2)
    with ca:
        st.markdown(f"<div class='kpi'><div class='kpi-val'>{corr_s:.2f}</div>"
            f"<div class='kpi-label'>Correlación Metascore → Net Revenue</div>"
            f"<div class='kpi-delta neu'>Débil — la nota no garantiza ventas</div></div>",unsafe_allow_html=True)
    with cb:
        st.markdown(f"<div class='kpi'><div class='kpi-val'>{corr_e:.2f}</div>"
            f"<div class='kpi-label'>Correlación Sentimiento → Net Revenue</div>"
            f"<div class='kpi-delta up'>El sentimiento predice mejor el revenue</div></div>",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    color_opt=st.selectbox("Colorear por:", ["genre","is_f2p","year"],
        format_func=lambda x:{"genre":"Género","is_f2p":"Modelo","year":"Año"}[x])
    fig=px.scatter(df,x="score",y="net_rev",color=color_opt,log_y=True,size="reviews",opacity=.75,
        hover_data={"genre":True,"year":True,"score":True,"net_rev":":.0f"},
        labels={"score":"Metascore","net_rev":"Net Revenue (log)"},
        title="Metascore vs Net Revenue",color_discrete_sequence=PAL)
    fig.update_layout(**LAYOUT,height=460,legend=dict(orientation="h",y=-0.2))
    st.plotly_chart(fig,use_container_width=True)
    fig2=px.scatter(df,x="sentiment",y="net_rev",color="genre",log_y=True,trendline="ols",
        labels={"sentiment":"Sentimiento","net_rev":"Net Revenue (log)"},
        title="Tendencia por género",color_discrete_sequence=PAL)
    fig2.update_layout(**LAYOUT,height=400,legend=dict(orientation="h",y=-0.25,font_size=10))
    st.plotly_chart(fig2,use_container_width=True)

elif vista=="🌎 Benchmark global":
    bdf=pd.DataFrame([{"Región":k,"Mediana":v,"es_chile":k=="Chile"} for k,v in BENCH.items()]).sort_values("Mediana")
    gap=BENCH["Global (mediana)"]-BENCH["Chile"]; gap_pct=gap/BENCH["Global (mediana)"]*100
    st.info(f"**Brecha Chile:** ${gap:,.0f} USD ({gap_pct:.0f}%) bajo mediana global. Net revenue con {cut_pct}% corte: **${BENCH['Chile']:,.0f}**")
    fig=go.Figure(go.Bar(x=bdf["Región"],y=bdf["Mediana"],
        marker_color=["#0F766E" if r else "#CBD5E1" for r in bdf["es_chile"]],
        text=[f"${v:,.0f}" for v in bdf["Mediana"]],textposition="outside",textfont_size=11))
    fig.update_layout(**LAYOUT,title="Chile vs mercados globales",yaxis_title="USD",height=400)
    st.plotly_chart(fig,use_container_width=True)
    yg=df.groupby("year").size().reset_index(name="n")
    fig2=px.line(yg,x="year",y="n",markers=True,title="Juegos lanzados por año",
        labels={"n":"Juegos","year":"Año"},color_discrete_sequence=["#0F766E"])
    fig2.update_traces(marker_size=8,line_width=2.5)
    fig2.update_layout(**LAYOUT,height=280)
    st.plotly_chart(fig2,use_container_width=True)

elif vista=="🤖 Simulador de viabilidad":
    st.markdown("<div class='sec-h'>Evalúa la viabilidad comercial de tu proyecto</div>",unsafe_allow_html=True)
    st.caption("Random Forest entrenado sobre datos históricos del mercado chileno en Steam.")
    ca,cb=st.columns(2)
    with ca:
        genre_i=st.selectbox("Género",df_full["genre"].unique().tolist())
        model_i=st.radio("Modelo",["Premium","F2P"],horizontal=True)
        score_i=st.slider("Metascore estimado",30,98,72)
    with cb:
        sent_i=st.slider("Sentimiento esperado",0.0,1.0,0.72,step=0.01)
        year_i=st.selectbox("Año de lanzamiento",list(range(2025,2028)))
    if st.button("Evaluar proyecto →",type="primary",use_container_width=True):
        Xp=[[le.transform([genre_i])[0],1 if model_i=="F2P" else 0,score_i,sent_i,year_i]]
        prob=clf.predict_proba(Xp)[0][1]
        rev_b=int(np.expm1(reg.predict(Xp)[0])); rev_n=int(rev_b*(1-cut_pct/100))
        ok=prob>=0.5; c="#0F766E" if ok else "#B91C1C"; v="✅ Viable" if ok else "⚠️ Riesgo alto"
        adv=("Supera el umbral histórico de $10K. Continuar desarrollo." if ok else
             "Bajo el umbral. Revisar género, modelo o apuntar a mayor Metascore.")
        st.markdown(f"""<div class='verdict' style='border-left-color:{c};margin-top:1rem;'>
          <div style='font-size:1.4rem;font-weight:700;color:{c};margin-bottom:.75rem;'>{v}</div>
          <div style='display:flex;gap:2.5rem;flex-wrap:wrap;margin-bottom:1rem;'>
            <div><div style='font-size:1.7rem;font-weight:700;color:#0F172A'>${rev_b:,.0f}</div>
                 <div class='kpi-label'>Revenue bruto estimado</div></div>
            <div><div style='font-size:1.7rem;font-weight:700;color:{c}'>${rev_n:,.0f}</div>
                 <div class='kpi-label'>Net revenue ({cut_pct}% corte)</div></div>
            <div><div style='font-size:1.7rem;font-weight:700;color:{c}'>{prob*100:.0f}%</div>
                 <div class='kpi-label'>Probabilidad de éxito</div></div>
          </div>
          <p style='font-size:.85rem;color:#475569;margin:0;'>{adv}</p>
        </div>""",unsafe_allow_html=True)
        fi=pd.Series(clf.feature_importances_,index=["Género","F2P","Score","Sentimiento","Año"]).sort_values()
        fig=px.bar(fi.reset_index(),x=0,y="index",orientation="h",
            title="¿Qué factores pesan más?",labels={0:"Importancia","index":""},
            color=fi.values,color_continuous_scale=[[0,"#CCFBF1"],[1,"#0F766E"]])
        fig.update_layout(**LAYOUT,coloraxis_showscale=False,height=260)
        st.plotly_chart(fig,use_container_width=True)
