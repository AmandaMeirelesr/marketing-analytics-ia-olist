import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(
    layout="wide",
    page_title="Marketing Analytics & IA - Olist",
    page_icon="📊"
)

# 2. Carregamento de Dados com Cache de Alta Performance
@st.cache_data
def carregar_dados():
    df_m = pd.read_csv("midia_paga_com_alertas.csv")
    df_r = pd.read_csv("comentarios_classificados_ia.csv")
    df_m["data"] = pd.to_datetime(df_m["data"])
    return df_m, df_r

df_midia, df_reviews = carregar_dados()

# 3. Barra Lateral: Filtros e Simulador What-If
st.sidebar.header("🎯 Filtros e Simulador")

campanhas_disponiveis = ["Todas as Campanhas"] + list(df_midia["nome_campanha"].unique())
campanha_selecionada = st.sidebar.selectbox("Filtrar por Campanha:", campanhas_disponiveis)

canais_disponiveis = list(df_midia["canal"].unique())
canais_selecionados = st.sidebar.multiselect(
    "Filtrar por Canal:",
    options=canais_disponiveis,
    default=canais_disponiveis
)

st.sidebar.divider()
st.sidebar.subheader("🔮 Simulador de Cenários (What-If)")
st.sidebar.caption("Simule o ganho financeiro ao resolver gargalos operacionais (frete/defeitos) que reduzem a conversão:")

melhoria_conversao = st.sidebar.slider(
    "Aumento projetado na Conversão (%):",
    min_value=0, max_value=50, value=15, step=5
)
reducao_cpa = st.sidebar.slider(
    "Redução estimada no CPA (%):",
    min_value=0, max_value=30, value=10, step=5
)

# Aplicar filtros na base de mídia
df_filtrado = df_midia[df_midia["canal"].isin(canais_selecionados)].copy()
if campanha_selecionada != "Todas as Campanhas":
    df_filtrado = df_filtrado[df_filtrado["nome_campanha"] == campanha_selecionada]

# 4. Cálculo Executivo de KPIs (Ponderados vs Médias)
total_gasto = df_filtrado["valor_gasto"].sum()
if "receita" in df_filtrado.columns:
    receita_total = df_filtrado["receita"].sum()
else:
    receita_total = (df_filtrado["valor_gasto"] * df_filtrado["roas"]).sum()

roas_real = receita_total / total_gasto if total_gasto > 0 else 0
cpa_medio = df_filtrado["cpa"].mean() if not df_filtrado.empty else 0
total_alertas = df_filtrado[df_filtrado["status_campanha"] != "Normal"].shape[0]

# Cálculos do Simulador What-If
receita_projetada = receita_total * (1 + melhoria_conversao / 100)
roas_projetado = receita_projetada / total_gasto if total_gasto > 0 else 0
cpa_projetado = cpa_medio * (1 - reducao_cpa / 100)
ganho_liquido_simulado = receita_projetada - receita_total

# 5. Cabeçalho e Cartões de KPIs
st.title("📊 Painel Executivo: Performance de Mídia Paga & Voz do Cliente (IA)")
st.markdown("Monitorização automatizada de anomalias em campanhas correlacionada com a análise de sentimento de avaliações reais da **Olist**.")

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Investimento Total",
    f"R$ {total_gasto:,.2f}",
    help="Soma total investida no período e filtros selecionados."
)
col2.metric(
    "ROAS Real (Ponderado)",
    f"{roas_real:.2f}x",
    delta=f"Simulado: {roas_projetado:.2f}x (+R$ {ganho_liquido_simulado:,.0f})",
    help="Receita Total dividida pelo Investimento Total."
)
col3.metric(
    "CPA Médio Atual",
    f"R$ {cpa_medio:.2f}",
    delta=f"Simulado: R$ {cpa_projetado:.2f} (-{reducao_cpa}%)",
    delta_color="inverse"
)
col4.metric(
    "Dias com Anomalia Crítica",
    f"{total_alertas} ocorrências",
    delta="Atenção necessária" if total_alertas > 0 else "Operação normal",
    delta_color="inverse" if total_alertas > 0 else "normal"
)

st.divider()

# 6. Separadores de Navegação Analítica
tab1, tab2, tab3 = st.tabs([
    "📈 Evolução de Mídia & Anomalias",
    "🧠 Diagnóstico de Sentimento (Olist)",
    "🔍 Explorador Inteligente de Reviews"
])

with tab1:
    st.subheader("Evolução Diária do ROAS e Deteção Estatística de Falhas")
    
    fig_roas = px.line(
        df_filtrado,
        x="data",
        y="roas",
        color="canal",
        labels={"data": "Data", "roas": "ROAS (Retorno sobre Gasto)", "canal": "Canal"},
        markers=True,
        template="plotly_white"
    )
    fig_roas.add_hline(
        y=1.5,
        line_dash="dash",
        line_color="green",
        annotation_text="Meta Mínima Aceitável (1.5x)"
    )
    
    anomalias = df_filtrado[df_filtrado["status_campanha"].str.contains("ALERTA", na=False)]
    if not anomalias.empty:
        fig_roas.add_scatter(
            x=anomalias["data"],
            y=anomalias["roas"],
            mode="markers",
            marker=dict(color="red", size=13, symbol="x"),
            name="Anomalia Detetada"
        )
    st.plotly_chart(fig_roas, use_container_width=True)

    st.subheader("⚠️ Registo de Ocorrências Críticas para Ação Rápida")
    df_log = df_filtrado[df_filtrado["status_campanha"] != "Normal"][
        ["data", "nome_campanha", "canal", "valor_gasto", "cpa", "roas", "status_campanha"]
    ].sort_values(by="data", ascending=False)
    
    st.dataframe(df_log, use_container_width=True, hide_index=True)

with tab2:
    col_g1, col_g2 = st.columns([2, 1])
    
    with col_g1:
        st.subheader("Principais Gargalos Relatados pelos Clientes (Reviews Negativos)")
        df_negativos = df_reviews[df_reviews["sentimento_ia"] == "Negativo"]
        
        fig_barras = px.histogram(
            df_negativos,
            x="aspecto_ia",
            color="campaign_id",
            barmode="group",
            labels={"aspecto_ia": "Categoria do Problema", "campaign_id": "Campanha Associada", "count": "Qtd. Reclamações"},
            template="plotly_white"
        )
        st.plotly_chart(fig_barras, use_container_width=True)
        
    with col_g2:
        st.subheader("Proporção Geral de Sentimentos")
        fig_pizza = px.pie(
            df_reviews,
            names="sentimento_ia",
            color="sentimento_ia",
            color_discrete_map={"Positivo": "#2ecc71", "Negativo": "#e74c3c", "Neutro": "#95a5a6"},
            hole=0.4
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

with tab3:
    st.subheader("🔍 Consulta Inteligente à Voz do Cliente")
    st.markdown("Pesquise por termos específicos (ex: *atraso, quebrado, correios, diferente, excelente*) para auditar os comentários reais classificados pela IA.")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        termo_busca = st.text_input("Procurar palavra-chave no comentário:", "")
    with col_f2:
        filtro_sentimento = st.selectbox("Filtrar Sentimento:", ["Todos"] + list(df_reviews["sentimento_ia"].unique()))
    with col_f3:
        filtro_aspecto = st.selectbox("Filtrar Categoria (Aspeto):", ["Todos"] + list(df_reviews["aspecto_ia"].unique()))
        
    df_busca = df_reviews.copy()
    if termo_busca:
        coluna_texto = "review_comment_message" if "review_comment_message" in df_busca.columns else df_busca.columns[0]
        df_busca = df_busca[df_busca[coluna_texto].astype(str).str.contains(termo_busca, case=False, na=False)]
    if filtro_sentimento != "Todos":
        df_busca = df_busca[df_busca["sentimento_ia"] == filtro_sentimento]
    if filtro_aspecto != "Todos":
        df_busca = df_busca[df_busca["aspecto_ia"] == filtro_aspecto]
        
    st.write(f"A exibir **{len(df_busca)}** avaliações correspondentes:")
    st.dataframe(df_busca, use_container_width=True, hide_index=True)
    
    csv_export = df_busca.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descarregar Relatório Filtrado (CSV)",
        data=csv_export,
        file_name="auditoria_reviews_olist.csv",
        mime="text/csv"
    )S