
import os
import pandas as pd

def test_arquivos_csv_existem():
    assert os.path.exists("midia_paga_com_alertas.csv"), "Arquivo midia_paga_com_alertas.csv ausente!"
    assert os.path.exists("comentarios_classificados_ia.csv"), "Arquivo comentarios_classificados_ia.csv ausente!"

def test_integridade_midia_paga():
    df = pd.read_csv("midia_paga_com_alertas.csv")
    assert not df.empty, "O dataset de midia paga esta vazio!"
    for col in ["data", "nome_campanha", "valor_gasto", "roas", "cpa", "status_campanha"]:
        assert col in df.columns, f"Coluna ausente: {col}"
    assert (df["valor_gasto"] >= 0).all(), "Existem gastos negativos!"

def test_integridade_reviews_ia():
    df = pd.read_csv("comentarios_classificados_ia.csv")
    assert not df.empty, "O dataset de reviews esta vazio!"
    assert "sentimento_ia" in df.columns
    assert "aspecto_ia" in df.columns
