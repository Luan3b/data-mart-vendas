import os
import pandas as pd

DATA_RAW_DIR = "data/raw"


def extrair_csvs():
  """Lê os arquivos CSV originais e retorna os DataFrames brutos."""
  print("📂 [EXTRACT] Lendo arquivos da pasta data/raw/...")

  df_clientes = pd.read_csv(os.path.join(DATA_RAW_DIR, "Cadastro Clientes.xlsx - Planilha1.csv"))
  df_produtos = pd.read_csv(os.path.join(DATA_RAW_DIR, "Cadastro Produto.xlsx - Produto.csv"))
  df_lojas = pd.read_csv(os.path.join(DATA_RAW_DIR, "Cadastro Lojas.xlsx - Planilha1.csv"))
  df_vendas_2022 = pd.read_csv(os.path.join(DATA_RAW_DIR, "Base Vendas - 2022.xlsx - 2022.csv"))
  df_vendas_2024 = pd.read_csv(os.path.join(DATA_RAW_DIR, "Base Vendas - 2024.xlsx - 2024.csv"))
  df_vendas_2023 = pd.read_csv(os.path.join(DATA_RAW_DIR, "Base Vendas - 2023.xlsx - 2023.csv"))

# Junta as bases de vendas em uma única tabela  
  df_vendas = pd.concat( [ df_vendas_2022, df_vendas_2023, df_vendas_2024 ], ignore_index=True )

  print("✅ [EXTRACT] Leitura dos arquivos finalizada com sucesso!")
  return df_clientes, df_produtos, df_lojas, df_vendas

# Executa o Extract quando o arquivo for chamado diretamente
if __name__ == "__main__":

    df_clientes, df_produtos, df_lojas, df_vendas = extrair_csvs()

    print("\n========== CLIENTES ==========")
    print(df_clientes.head())

    print("\n========== PRODUTOS ==========")
    print(df_produtos.head())

    print("\n========== LOJAS ==========")
    print(df_lojas.head())

    print("\n========== VENDAS ==========")
    print(df_vendas.head())