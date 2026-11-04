import pandas as pd
import re
import chromadb

print("Carregando os 250 comentários reais da Olist...")
df_reviews = pd.read_csv("comentarios_campanhas_olist.csv")

# 1. Motor de NLP Local em Português (Classificação de Sentimento e Aspectos sem API paga)
def classificar_comentario_local(texto, nota):
    t = str(texto).lower()
    
    # Classificação de Sentimento combinando Léxico + Nota
    palavras_negativas = ["atraso", "não recebi", "nao recebi", "defeito", "péssimo", "pessimo", "ruim", "errado", "quebrado", "demora", "incompleto", "falsificado", "não funciona", "nao funciona", "horrível", "propaganda enganosa"]
    palavras_positivas = ["excelente", "ótimo", "otimo", "rápido", "rapido", "amei", "perfeito", "recomendo", "antes do prazo", "bom", "qualidade", "parabéns", "parabens", "lindo"]
    
    if nota <= 2 or any(p in t for p in palavras_negativas):
        sentimento = "Negativo"
    elif nota >= 4 or any(p in t for p in palavras_positivas):
        sentimento = "Positivo"
    else:
        sentimento = "Neutro"

    # Extração do Aspecto Principal (Tópico da reclamação ou elogio)
    if re.search(r"entrega|prazo|correio|chegou|atras|demor|frete|recebi|envio|transportadora", t):
        aspecto = "Entrega/Frete"
    elif re.search(r"defeito|quebr|estraga|funciona|qualidade|material|peça|peca|original|fals|bateria|carrega|trav", t):
        aspecto = "Qualidade/Defeito"
    elif re.search(r"diferente|foto|veio outro|errado|cor|tamanho|faltando|incompleto|modelo|anúncio|anuncio", t):
        aspecto = "Expectativa/Diferente da Foto"
    elif re.search(r"preço|preco|caro|barato|custo|benefício|beneficio|valor|vale a pena|dinheiro", t):
        aspecto = "Preço/Custo-Benefício"
    else:
        aspecto = "Atendimento/Outros"

    # Gera um resumo curto limpo
    resumo = texto[:55].strip() + "..." if len(texto) > 55 else texto.strip()
    return pd.Series([sentimento, aspecto, resumo])

print("Processando sentimento e tópicos localmente...")
df_reviews[["sentimento_ia", "aspecto_ia", "resumo_ia"]] = df_reviews.apply(
    lambda row: classificar_comentario_local(row["review_comment_message"], row["review_score"]), axis=1
)

# 2. Salva o CSV enriquecido com todos os 250 comentários classificados
df_reviews.to_csv("comentarios_classificados_ia.csv", index=False)
print("Arquivo 'comentarios_classificados_ia.csv' gerado com sucesso!")

# 3. Indexação Vetorial Gratuita no ChromaDB (Usa o modelo local padrão sem precisar de API)
print("\nCriando embeddings locais e salvando no ChromaDB (Na 1ª vez ele baixa o modelo gratuito automaticamente)...")
chroma_client = chromadb.PersistentClient(path="./chroma_db_marketing")
colecao = chroma_client.get_or_create_collection(name="reviews_campanhas")

colecao.upsert(
    ids=df_reviews["review_id"].astype(str).tolist(),
    documents=df_reviews["review_comment_message"].tolist(),
    metadatas=df_reviews[["campaign_id", "product_category_name", "sentimento_ia", "aspecto_ia", "resumo_ia"]].to_dict("records")
)
print("Banco vetorial './chroma_db_marketing' atualizado com 250 comentários!")

# 4. Exibe o Raio-X das reclamações por campanha no terminal
print("\n=== RAIO-X DE RECLAMAÇÕES POR CAMPANHA ===")
negativos = df_reviews[df_reviews["sentimento_ia"] == "Negativo"]
tabela_cruzada = pd.crosstab(negativos["campaign_id"], negativos["aspecto_ia"])
print(tabela_cruzada)