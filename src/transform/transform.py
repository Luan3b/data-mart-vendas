
import pandas as pd
from src.extract.extract import extrair_csvs

# 1. CLIENTES
def transformar_clientes(df_raw):
  df = df_raw.copy()
  df = df[[
      "Id Cliente",
      "Nome Completo",
      "Genero",
      "Data de Nacimento",
  ]].copy()
  df.columns = ["id_cliente", "nome_cliente", "genero", "data_nascimento"]

  df["id_cliente"] = pd.to_numeric(
      df["id_cliente"], errors="coerce"
  ).astype("Int64")
  
  df["data_nascimento"] = pd.to_datetime(
      df["data_nascimento"], errors="coerce"
  )

  return df.dropna(subset=["id_cliente"]).drop_duplicates(subset=["id_cliente"])

def transformar_dados(df_clientes):

    print("\n========== TRANSFORM ==========")

    print("\n--- CLIENTES TRATADOS ---")

    print(df_clientes.head())

    print("\n--- INFORMAÇÕES ---")

    df_clientes.info()

    print("\n--- QUANTIDADE DE CLIENTES ---")

    print(len(df_clientes))

    return df_clientes

if __name__ == "__main__":

    (
        df_clientes,
        df_produtos,
        df_lojas,
        df_vendas
    ) = extrair_csvs()

    clientes = transformar_clientes(df_clientes)

    transformar_dados(clientes)