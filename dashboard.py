import streamlit as st
import pandas as pd
import plotly.express as px

# Configura a página para modo wide ocupando toda a tela
st.set_page_config(layout="wide", page_title="Dashboard de Marketing")

st.title("📊 Painel Executivo: Performance de Mídia e Voz do Cliente")

# Carrega as bases de dados processadas
df_midia = pd.read_csv("midia_paga_com_alertas.csv")
df_reviews = pd.read_csv("comentarios_classificados_ia.csv")

# Converte a coluna de data para o formato datetime
df_midia["data"] = pd.to_datetime(df_midia["data"])

# Métricas de topo (KPIs gerais)
roas_medio = df_midia["roas"].mean()
cpa_medio = df_midia["cpa"].mean()
total_gasto = df_midia["valor_gasto"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("ROAS Médio Geral", f"{roas_medio:.2f}x")
col2.metric("CPA Médio (R$)", f"R$ {cpa_medio:.2f}")
col3.metric("Investimento Total", f"R$ {total_gasto:,.2f}")

st.divider()

# Criação de duas colunas para os gráficos lado a lado
tab1, tab2 = st.tabs(["Evolução de Mídia", "Análise de Sentimento"])

with tab1:
    st.subheader("Evolução Diária do ROAS com Indicadores de Anomalia")
    # Filtro lateral de campanha
    campanha_selecionada = st.selectbox("Selecione a Campanha para Filtrar:", df_midia["nome_campanha"].unique())
    df_filtrado = df_midia[df_midia["nome_campanha"] == campanha_selecionada]
    
    fig_roas = px.line(
        df_filtrado, x="data", y="roas", color="canal",
        labels={"data": "Data", "roas": "Retorno sobre Gasto (ROAS)"},
        markers=True
    )
    # Adiciona linha de meta aceitável (ex假设 ROAS 1.5)
    fig_roas.add_hline(y=1.5, line_dash="dash", line_color="green", annotation_text="Meta Mínima")
    
    # Destaca pontos de anomalia crítica
    anomalias = df_filtrado[df_filtrado["status_campanha"].str.contains("ALERTA CRÍTICO")]
    fig_roas.add_scatter(
        x=anomalias["data"], y=anomalias["roas"],
        mode="markers", marker=dict(color="red", size=12, symbol="x"),
        name="Queda Crítica de Conversão"
    )
    st.plotly_chart(fig_roas, use_container_width=True)

with tab2:
    st.subheader("Distribuição de Reclamações por Categoria (Top Problemas)")
    # Filtra apenas sentimentos negativos
    df_negativos = df_reviews[df_reviews["sentimento_ia"] == "Negativo"]
    
    fig_barras = px.bar(
        df_negativos, x="aspecto_ia", color="campaign_id",
        title="Principais Gargalos Relatados pelos Consumidores",
        labels={"aspecto_ia": "Categoria do Problema", "campaign_id": "Campanha"},
        barmode="group"
    )
    st.plotly_chart(fig_barras, use_container_width=True)

# Exibe tabela detalhada dos alertas
st.subheader("⚠️ Log de Ocorrências Críticas")
st.table(df_filtrado[df_filtrado["status_campanha"] != "Normal"][["data", "nome_campanha", "cpa", "roas", "status_campanha"]])