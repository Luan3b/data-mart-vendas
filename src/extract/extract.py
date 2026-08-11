import os
import pandas as pd

DATA_RAW_DIR = "data/raw"


def extrair_csvs():
  """Lê os arquivos CSV originais e retorna os DataFrames brutos."""
  print("📂 [EXTRACT] Lendo arquivos da pasta data/raw/...")

  df_clientes = pd.read_csv(os.path.join(DATA_RAW_DIR, "Cadastro Clientes.xlsx - Planilha1.csv"))
  df_produtos = pd.read_csv(os.path.join(DATA_RAW_DIR, "Cadastro Produtos.xlsx - Produto.csv"))
  df_lojas = pd.read_csv(os.path.join(DATA_RAW_DIR, "Cadastro Lojas.xlsx - Planilha1.csv"))
  df_vendas = pd.read_csv(os.path.join(DATA_RAW_DIR, "Base Vendas - 2024.xlsx - 2024.csv"))
  df_vendas = pd.read_csv(os.path.join(DATA_RAW_DIR, "Base Vendas - 2023.xlsx - 2023.csv"))
  df_vendas = pd.read_csv(os.path.join(DATA_RAW_DIR, "Base Vendas - 2022.xlsx - 2022.csv"))


  print("✅ [EXTRACT] Leitura dos arquivos finalizada com sucesso!")
  return df_clientes, df_produtos, df_lojas, df_vendas