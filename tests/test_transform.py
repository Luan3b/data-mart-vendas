import pandas as pd
from src.transform.transform import tratar_preco, transformar_clientes, transformar_produtos

def test_tratar_preco():
    assert tratar_preco("2278.,8") == 2278.8
    assert tratar_preco("150.50") == 150.50
    assert tratar_preco(None) is None
    assert tratar_preco("invalido") is None

def test_transformar_clientes():
    df_mock = pd.DataFrame({
        "Id Cliente": [1, 1, None],
        "Nome Completo": ["Ana", "Ana", "Carlos"],
        "Genero": ["F", "F", "M"],
        "Data de Nacimento": ["1990-01-01", "1990-01-01", "1985-05-05"]
    })
    df_res = transformar_clientes(df_mock)
    assert len(df_res) == 1
    assert "id_cliente" in df_res.columns
    assert df_res["id_cliente"].iloc[0] == 1

def test_transformar_produtos():
    df_mock = pd.DataFrame({
        "Id Produto": [10],
        "Nome Produto": ["Teclado"],
        "Categoria": ["Periféricos"],
        "Marca": ["Logi"],
        "Preço Unit.": ["100.,5"],
        "Custo Unit.": ["50.0"]
    })
    df_res = transformar_produtos(df_mock)
    assert df_res["preco_unitario"].iloc[0] == 100.5
    assert df_res["custo_unitario"].iloc[0] == 50.0

if __name__ == "__main__":
    test_tratar_preco()
    test_transformar_clientes()
    test_transformar_produtos()
    print("✅ Todos os testes de transformação passaram!")