
import pandas as pd
import numpy as np

# 1. Carrega a base gerada no passo anterior
df = pd.read_csv("midia_paga_performance.csv")
df["data"] = pd.to_datetime(df["data"])
df = df.sort_values(by=["campaign_id", "data"]).reset_index(drop=True)

# 2. Cálculo de Média Móvel e Desvio Padrão (Janela dos últimos 14 dias por campanha)
# Usamos shift(1) para comparar o dia de hoje com o histórico dos 14 dias anteriores
grupo_campanha = df.groupby("campaign_id")

df["roas_media_hist"] = grupo_campanha["roas"].transform(lambda x: x.shift(1).rolling(14, min_periods=7).mean())
df["roas_std_hist"] = grupo_campanha["roas"].transform(lambda x: x.shift(1).rolling(14, min_periods=7).std())

df["ctr_media_hist"] = grupo_campanha["ctr"].transform(lambda x: x.shift(1).rolling(14, min_periods=7).mean())
df["ctr_std_hist"] = grupo_campanha["ctr"].transform(lambda x: x.shift(1).rolling(14, min_periods=7).std())

# 3. Cálculo do Z-Score (Quantos desvios-padrão o dia atual caiu em relação ao normal)
df["z_score_roas"] = (df["roas"] - df["roas_media_hist"]) / df["roas_std_hist"]
df["z_score_ctr"] = (df["ctr"] - df["ctr_media_hist"]) / df["ctr_std_hist"]

# 4. Regra de Negócio: Classificação automática de anomalias (Z-Score menor que -2.0 indica queda severa)
condicoes = [
    (df["z_score_roas"] < -2.0) & (df["z_score_ctr"] >= -2.0),
    (df["z_score_ctr"] < -2.0)
]
diagnosticos = [
    "ALERTA CRÍTICO: Queda de Conversão/ROAS (Verificar Comentários/Página)",
    "ALERTA CRIATIVO: Fadiga de Anúncio/Queda de CTR"
]

df["status_campanha"] = np.select(condicoes, diagnosticos, default="Normal")

# 5. Filtra e exibe no terminal um resumo das campanhas que apresentaram problemas
anomalias = df[df["status_campanha"] != "Normal"]
resumo_alertas = (
    anomalias.groupby(["campaign_id", "nome_campanha", "canal", "status_campanha"])
    .agg(
        dias_com_alerta=("data", "count"),
        primeiro_dia_alerta=("data", "min"),
        roas_medio_no_alerta=("roas", "mean"),
        cpa_medio_no_alerta=("cpa", "mean")
    )
    .reset_index()
)

print("\n=== RELATÓRIO DE ANOMALIAS DETECTADAS NAS CAMPANHAS ===")
print(resumo_alertas.to_string(index=False))

# Salva a base processada pronta para ser consumida pelos próximos módulos
df.to_csv("midia_paga_com_alertas.csv", index=False)
print("\nArquivo 'midia_paga_com_alertas.csv' salvo com sucesso!")