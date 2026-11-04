import pandas as pd
import plotly.express as px

# Carrega os dados processados pelo detector de anomalias
df = pd.read_csv("midia_paga_com_alertas.csv")

# 1. Gráfico de Evolução do ROAS por Campanha
fig_roas = px.line(
    df, 
    x="data", 
    y="roas", 
    color="nome_campanha",
    title="Evolução Diária do ROAS por Campanha (Detecção de Queda na CAMP_02)",
    labels={"data": "Data", "roas": "ROAS (Retorno sobre Gasto)", "nome_campanha": "Campanha"}
)

# Destaca os pontos exatos onde o seu algoritmo detectou anomalia crítica
anomalias_roas = df[df["status_campanha"].str.contains("ALERTA CRÍTICO")]
fig_roas.add_scatter(
    x=anomalias_roas["data"], 
    y=anomalias_roas["roas"],
    mode="markers", 
    marker=dict(color="red", size=9, symbol="x"),
    name="Anomalia de Conversão/ROAS"
)

# Salva o gráfico como um arquivo HTML interativo (abre direto no navegador)
fig_roas.write_html("grafico_roas_alertas.html")
print("Gráfico 'grafico_roas_alertas.html' gerado com sucesso!")