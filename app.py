import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="Chilean Game Dev", page_icon="🎮", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;800&family=Inter:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;background:#f0fafa;}
.block-container{padding-top:1.5rem;background:#f0fafa;}
h1,h2,h3{font-family:'Syne',sans-serif;font-weight:800;color:#134e4a;}
.kpi{background:#fff;border-radius:14px;padding:1.1rem 1.3rem;border:1.5px solid #99f6e4;box-shadow:0 2px 8px rgba(13,148,136,.08);}
.kpi-v{font-size:2.1rem;font-weight:800;color:#0d9488;letter-spacing:-1px;}
.kpi-l{font-size:0.68rem;color:#6b7280;text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;}
section[data-testid="stSidebar"]{background:#134e4a!important;}
section[data-testid="stSidebar"] *{color:#ccfbf1!important;}
</style>""", unsafe_allow_html=True)

np.random.seed(42)
N=200
GENRES=["RPG","Action","Platformer","Puzzle","Adventure","Simulation","Horror","Shooter","Strategy"]
GW=[0.18,0.16,0.15,0.12,0.12,0.10,0.07,0.06,0.04]
GREV={"RPG":32000,"Shooter":26000,"Action":20000,"Strategy":18000,"Adventure":14000,"Simulation":13000,"Horror":11000,"Platformer":9000,"Puzzle":6500}
BENCH={"Chile":0,"Brasil":18000,"Argentina":14000,"Colombia":11000,"Global (mediana)":32000,"USA":48000,"Europa":40000}
TEAL="#0d9488"; TEAL2="#14b8a6"; AMBER="#d97706"; ROSE="#e11d48"
PALETTE=[TEAL,TEAL2,"#0f766e","#0891b2",AMBER,ROSE,"#7c3aed","#65a30d","#dc2626"]

data=[]
for i in range(N):
    g=np.random.choice(GENRES,p=GW); f2p=np.random.random()<0.28
    rev=max(200,np.random.lognormal(np.log(GREV[g]*(1.3 if f2p else 1.0)),0.85))
    score=np.clip(np.random.normal(72,12),30,98)
    sentiment=np.clip(np.random.normal(0.72,0.14),0.1,1.0)
    year=np.random.choice(range(2015,2025),p=[0.03]*3+[0.07]*3+[0.12,0.16,0.20,0.22])
    data.append({"title":f"Juego_{i:03d}","genre":g,"is_f2p":f2p,"revenue_est":round(rev,0),
        "score":round(score,1),"sentiment":round(sentiment,3),"year":year,
        "is_success":int(rev>10000),"reviews":int(rev/8+np.random.randint(0,200))})
df=pd.DataFrame(data)
le=LabelEncoder(); df["genre_enc"]=le.fit_transform(df["genre"])
X=df[["genre_enc","is_f2p","score","sentiment","year"]]
clf=RandomForestClassifier(n_estimators=100,random_state=42,class_weight="balanced"); clf.fit(X,df["is_success"])
reg=RandomForestRegressor(n_estimators=100,random_state=42); reg.fit(X,np.log1p(df["revenue_est"]))

with st.sidebar:
    st.markdown("## 🎮 Filtros")
    vista=st.selectbox("Vista",["Panorama de mercado","Por género","Score vs Revenue","Benchmark global","Simulador ML"])
    genres_s=st.multiselect("Géneros",GENRES,default=GENRES)
    model_s=st.radio("Modelo",["Todos","Solo Premium","Solo F2P"])
    yr=st.slider("Años",2015,2024,(2015,2024))
    cut=st.slider("Corte plataforma %",0,40,30)

dff=df[df["genre"].isin(genres_s)&df["year"].between(*yr)].copy()
if model_s=="Solo Premium": dff=dff[~dff["is_f2p"]]
elif model_s=="Solo F2P": dff=dff[dff["is_f2p"]]
dff["rev_net"]=dff["revenue_est"]*(1-cut/100)
BENCH["Chile"]=dff["rev_net"].median()

st.markdown("# 🎮 Chilean Game Dev · Market Intel")
st.markdown(f"### {vista}"); st.divider()

if vista=="Panorama de mercado":
    c1,c2,c3,c4=st.columns(4)
    for col,val,lab in zip([c1,c2,c3,c4],[len(dff),f"${dff['rev_net'].sum():,.0f}",f"{dff['score'].mean():.1f}",f"{dff['is_success'].mean()*100:.0f}%"],["Juegos","Net Revenue total","Score promedio","Tasa éxito"]):
        col.markdown(f"<div class='kpi'><div class='kpi-v'>{val}</div><div class='kpi-l'>{lab}</div></div>",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        fig=px.bar(dff.groupby(["year","genre"]).size().reset_index(name="count"),x="year",y="count",color="genre",title="Lanzamientos por año",color_discrete_sequence=PALETTE)
        fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0fafa",height=310,font=dict(family="Inter"))
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        gr=dff.groupby("genre")["rev_net"].median().sort_values(ascending=True).reset_index()
        fig2=px.bar(gr,x="rev_net",y="genre",orientation="h",title="Mediana Net Revenue",color="rev_net",color_continuous_scale=[[0,"#ccfbf1"],[1,TEAL]])
        fig2.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0fafa",height=310,coloraxis_showscale=False,font=dict(family="Inter"))
        st.plotly_chart(fig2,use_container_width=True)

elif vista=="Por género":
    fig=px.box(dff,x="genre",y="rev_net",color="is_f2p",log_y=True,color_discrete_map={True:TEAL,False:AMBER},title="Net Revenue por género y modelo")
    fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0fafa",height=420,font=dict(family="Inter"))
    st.plotly_chart(fig,use_container_width=True)
    mx=dff.groupby("genre").agg(median_rev=("rev_net","median"),avg_sent=("sentiment","mean"),count=("title","count"),success=("is_success","mean")).reset_index()
    fig2=px.scatter(mx,x="avg_sent",y="median_rev",size="count",color="success",text="genre",color_continuous_scale=[[0,"#ccfbf1"],[1,TEAL]],title="Matriz oportunidad: Sentimiento vs Revenue")
    fig2.update_traces(textposition="top center")
    fig2.add_hline(y=mx["median_rev"].mean(),line_dash="dash",line_color="#99f6e4")
    fig2.add_vline(x=mx["avg_sent"].mean(),line_dash="dash",line_color="#99f6e4")
    fig2.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0fafa",height=420,font=dict(family="Inter"))
    st.plotly_chart(fig2,use_container_width=True)

elif vista=="Score vs Revenue":
    ca,cb=st.columns([3,1])
    with cb:
        log_y=st.checkbox("Escala log Y",True); color_by=st.selectbox("Color por",["genre","is_f2p","year"])
    fig=px.scatter(dff,x="score",y="rev_net",color=color_by,log_y=log_y,size="reviews",hover_data=["title","genre","year"],title="Metascore vs Net Revenue",color_discrete_sequence=PALETTE)
    corr=dff[["score","sentiment","rev_net"]].corr()["rev_net"]
    fig.add_annotation(x=88,y=np.log10(dff["rev_net"].max()) if log_y else dff["rev_net"].max(),text=f"Corr Score: {corr['score']:.2f} | Sentiment: {corr['sentiment']:.2f}",bgcolor="rgba(13,148,136,.12)",font=dict(color=TEAL,size=12),showarrow=False)
    fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0fafa",height=490,font=dict(family="Inter"))
    st.plotly_chart(fig,use_container_width=True)

elif vista=="Benchmark global":
    bdf=pd.DataFrame([{"region":k,"median_rev":v,"is_chile":k=="Chile"} for k,v in BENCH.items()]).sort_values("median_rev")
    fig=go.Figure(go.Bar(x=bdf["region"],y=bdf["median_rev"],marker_color=[TEAL if r else "#ccfbf1" for r in bdf["is_chile"]],text=[f"${v:,.0f}" for v in bdf["median_rev"]],textposition="outside"))
    fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0fafa",height=420,title="Chile vs mercados globales",font=dict(family="Inter"))
    st.plotly_chart(fig,use_container_width=True)
    gap=32000-BENCH["Chile"]
    st.info(f"Brecha Chile vs global: **${gap:,.0f}** ({gap/32000*100:.0f}%). Net revenue con {cut}% corte: **${BENCH['Chile']:,.0f}**")

elif vista=="Simulador ML":
    st.markdown("### Evalúa tu proyecto")
    c1,c2=st.columns(2)
    with c1:
        gin=st.selectbox("Género",GENRES); min_=st.radio("Modelo",["Premium","F2P"]); sin_=st.slider("Metascore",30,98,72)
    with c2:
        sent=st.slider("Sentimiento esperado",0.0,1.0,0.72); yin=st.selectbox("Año",range(2025,2028))
    if st.button("🚀 Evaluar",type="primary"):
        Xp=[[le.transform([gin])[0],1 if min_=="F2P" else 0,sin_,sent,yin]]
        prob=clf.predict_proba(Xp)[0][1]; rev=int(np.expm1(reg.predict(Xp)[0])); rn=int(rev*(1-cut/100))
        ok=prob>=0.5; c=TEAL if ok else ROSE; v="✅ VIABLE" if ok else "⚠️ RIESGO ALTO"
        st.markdown(f"<div style='background:#fff;border:2px solid {c};border-radius:14px;padding:1.5rem;margin-top:1rem'><h3 style='color:{c};font-family:Syne,sans-serif;'>{v}</h3><div style='display:flex;gap:2rem;margin-top:1rem;flex-wrap:wrap'><div><div style='font-size:1.8rem;font-weight:800;color:#134e4a'>${rev:,.0f}</div><div style='color:#6b7280;font-size:.7rem;text-transform:uppercase'>Revenue bruto</div></div><div><div style='font-size:1.8rem;font-weight:800;color:{TEAL}'>${rn:,.0f}</div><div style='color:#6b7280;font-size:.7rem;text-transform:uppercase'>Net Revenue</div></div><div><div style='font-size:1.8rem;font-weight:800;color:{c}'>{prob*100:.1f}%</div><div style='color:#6b7280;font-size:.7rem;text-transform:uppercase'>Prob. éxito</div></div></div></div>",unsafe_allow_html=True)
        fi=pd.Series(clf.feature_importances_,index=["Género","F2P","Score","Sentimiento","Año"])
        fig=px.bar(fi.sort_values(),orientation="h",title="Importancia de variables",color=fi.sort_values(),color_continuous_scale=[[0,"#ccfbf1"],[1,TEAL]])
        fig.update_layout(plot_bgcolor="#fff",paper_bgcolor="#f0fafa",height=250,coloraxis_showscale=False,font=dict(family="Inter"))
        st.plotly_chart(fig,use_container_width=True)
