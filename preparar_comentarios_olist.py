import pandas as pd

print("Carregando tabelas da Olist...")
reviews = pd.read_csv("olist_order_reviews_dataset.csv")
items = pd.read_csv("olist_order_items_dataset.csv")
products = pd.read_csv("olist_products_dataset.csv")

# 1. Junta as 3 tabelas para saber de qual categoria é cada comentário
df_merged = (
    reviews.merge(items, on="order_id", how="inner")
    .merge(products, on="product_id", how="inner")
)

# 2. Remove avaliações em branco (mantém apenas quem escreveu um comentário real)
df_merged = df_merged.dropna(subset=["review_comment_message"]).copy()
df_merged["review_comment_message"] = df_merged["review_comment_message"].str.strip()
df_merged = df_merged[df_merged["review_comment_message"].str.len() > 10]

# 3. Mapeia exatamente as 5 categorias da Olist para os campaign_id do seu Módulo 1
mapa_campanhas = {
    "beleza_saude": "CAMP_01",
    "informatica_acessorios": "CAMP_02",
    "relogios_presentes": "CAMP_03",
    "esporte_lazer": "CAMP_04",
    "cama_mesa_banho": "CAMP_05"
}

# Filtra apenas as 5 categorias e cria a coluna campaign_id
df_filtrado = df_merged[df_merged["product_category_name"].isin(mapa_campanhas.keys())].copy()
df_filtrado["campaign_id"] = df_filtrado["product_category_name"].map(mapa_campanhas)

# Remove duplicatas de pedido/avaliação
df_filtrado = df_filtrado.drop_duplicates(subset=["review_id"])

# 4. Seleciona uma amostra equilibrada (50 comentários por campanha = 250 no total)
# Na CAMP_02 (Informática), priorizamos notas baixas (1 e 2) para refletir a anomalia de queda de ROAS!
amostras = []
for camp_id in mapa_campanhas.values():
    df_camp = df_filtrado[df_filtrado["campaign_id"] == camp_id]
    if camp_id == "CAMP_02":
        # Pega maioria de comentários negativos para a IA diagnosticar a queda da CAMP_02
        negativos = df_camp[df_camp["review_score"] <= 2].sample(35, random_state=42)
        positivos = df_camp[df_camp["review_score"] >= 4].sample(15, random_state=42)
        amostras.append(pd.concat([negativos, positivos]))
    else:
        amostras.append(df_camp.sample(50, random_state=42))

df_final = pd.concat(amostras, ignore_index=True)

# Seleciona apenas as colunas limpas para o Módulo 2
colunas_finais = ["review_id", "campaign_id", "product_category_name", "review_score", "review_comment_message"]
df_final = df_final[colunas_finais]

df_final.to_csv("comentarios_campanhas_olist.csv", index=False)
print("\nArquivo 'comentarios_campanhas_olist.csv' criado com sucesso!")
print("\nQuantidade de comentários por campanha:")
print(df_final["campaign_id"].value_counts())