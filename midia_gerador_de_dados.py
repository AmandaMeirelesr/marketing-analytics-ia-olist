
import pandas as pd
import numpy as np

# Semente fixa para garantir que os dados gerados sejam sempre os mesmos
np.random.seed(42)

# 1. Configuração das Campanhas mapeadas para as categorias reais da Olist
campanhas = [
    {
        "campaign_id": "CAMP_01",
        "nome_campanha": "Beleza_Verao_SempreAtiva",
        "olist_category": "beleza_saude",
        "canal": "Meta Ads",
        "gasto_diario_medio": 1200,
        "cpm_medio": 25.0,  # Custo por 1.000 impressões (R$)
        "ctr_base": 0.018,  # 1.8% de Taxa de Clique
        "cvr_base": 0.032,  # 3.2% de Taxa de Conversão
        "ticket_medio": 140.0
    },
    {
        "campaign_id": "CAMP_02",
        "nome_campanha": "Tech_Gamer_Performance",
        "olist_category": "informatica_acessorios",
        "canal": "Google Ads",
        "gasto_diario_medio": 2500,
        "cpm_medio": 45.0,
        "ctr_base": 0.035,
        "cvr_base": 0.025,
        "ticket_medio": 420.0
    },
    {
        "campaign_id": "CAMP_03",
        "nome_campanha": "Relogios_Presentes_Luxo",
        "olist_category": "relogios_presentes",
        "canal": "TikTok Ads",
        "gasto_diario_medio": 950,
        "cpm_medio": 18.0,
        "ctr_base": 0.014,
        "cvr_base": 0.018,
        "ticket_medio": 290.0
    },
    {
        "campaign_id": "CAMP_04",
        "nome_campanha": "Esporte_Fitness_Promo",
        "olist_category": "esporte_lazer",
        "canal": "Meta Ads",
        "gasto_diario_medio": 1500,
        "cpm_medio": 22.0,
        "ctr_base": 0.021,
        "cvr_base": 0.028,
        "ticket_medio": 195.0
    },
    {
        "campaign_id": "CAMP_05",
        "nome_campanha": "Casa_Conforto_Retargeting",
        "olist_category": "cama_mesa_banho",
        "canal": "Google Ads",
        "gasto_diario_medio": 1100,
        "cpm_medio": 30.0,
        "ctr_base": 0.026,
        "cvr_base": 0.038,
        "ticket_medio": 165.0
    }
]

# Período de 60 dias de campanha
datas = pd.date_range(start="2026-08-01", periods=60, freq="D")
registros = []

for camp in campanhas:
    for i, data in enumerate(datas):
        # Variação orgânica diária
        gasto = np.random.normal(camp["gasto_diario_medio"], camp["gasto_diario_medio"] * 0.12)
        cpm = np.random.normal(camp["cpm_medio"], camp["cpm_medio"] * 0.08)
        ctr = np.random.normal(camp["ctr_base"], camp["ctr_base"] * 0.08)
        cvr = np.random.normal(camp["cvr_base"], camp["cvr_base"] * 0.10)

        # --- INJEÇÃO DE ANOMALIAS PARA O SEU PROJETO DETECTAR ---
        
        # Anomalia 1: "CAMP_02" (Informática) sofre queda brusca de conversão após o dia 40
        # Cenário para o Módulo 2: Clientes reclamando nos comentários de frete caro/atraso ou produto com defeito
        if camp["campaign_id"] == "CAMP_02" and i >= 40:
            cvr = cvr * 0.45  # Conversão cai 55%, disparando o CPA e derrubando o ROAS

        # Anomalia 2: "CAMP_03" (Relógios) sofre fadiga de criativo após o dia 30
        # Cenário para o Módulo 2: Anúncio saturado, cliques caem pela metade
        if camp["campaign_id"] == "CAMP_03" and i >= 30:
            ctr = ctr * 0.55

        # Cálculos de funil
        impressoes = int((gasto / cpm) * 1000)
        cliques = max(1, int(impressoes * ctr))
        conversoes = max(0, int(cliques * cvr))
        
        # Receita com leve oscilação de carrinho
        receita = conversoes * np.random.normal(camp["ticket_medio"], camp["ticket_medio"] * 0.05)

        registros.append({
            "data": data.strftime("%Y-%m-%d"),
            "campaign_id": camp["campaign_id"],
            "nome_campanha": camp["nome_campanha"],
            "olist_category": camp["olist_category"],
            "canal": camp["canal"],
            "valor_gasto": round(max(50, gasto), 2),
            "impressoes": impressoes,
            "cliques": cliques,
            "conversoes": conversoes,
            "receita": round(max(0, receita), 2)
        })

df_midia = pd.DataFrame(registros)

# 2. Engenharia de Atributos: Cálculo dos KPIs de Marketing
df_midia["ctr"] = round((df_midia["cliques"] / df_midia["impressoes"]) * 100, 2)
df_midia["cpc"] = round(df_midia["valor_gasto"] / df_midia["cliques"], 2)
df_midia["taxa_conversao"] = round((df_midia["conversoes"] / df_midia["cliques"]) * 100, 2)
df_midia["cpa"] = np.where(df_midia["conversoes"] > 0, round(df_midia["valor_gasto"] / df_midia["conversoes"], 2), np.nan)
df_midia["roas"] = round(df_midia["receita"] / df_midia["valor_gasto"], 2)

# Salva o arquivo pronto para o Módulo 1
df_midia.to_csv("midia_paga_performance.csv", index=False)
print("Arquivo 'midia_paga_performance.csv' gerado com sucesso!")
print(df_midia.head())