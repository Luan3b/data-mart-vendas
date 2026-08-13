import pandas as pd
from src.extract.extract import extrair_csvs


# Função auxiliar para conversão de texto/valores em formato numérico
def tratar_preco(valor):
   if pd.isna(valor):
       return None

   valor = str(valor).strip()

   # Corrige casos como: 2278.,8 -> 2278.8
   valor = valor.replace(".,", ".")

   try:
       return float(valor)
   except ValueError:
       return None

# 1. TRANSFORMAÇÃO DE CLIENTES
def transformar_clientes(df_raw):
 df = df_raw.copy()

 df = df[[
     "Id Cliente",
     "Nome Completo",
     "Genero",
     "Data de Nacimento",
 ]].copy()

 df.columns = [
     "id_cliente",
     "nome_cliente",
     "genero",
     "data_nascimento",
 ]

 df["id_cliente"] = pd.to_numeric(
     df["id_cliente"], errors="coerce"
 ).astype("Int64")

 df["data_nascimento"] = pd.to_datetime(
     df["data_nascimento"], errors="coerce"
 )

 df = df.dropna(subset=["id_cliente"])
 df = df.drop_duplicates(subset=["id_cliente"])

 return df

# 2. TRANSFORMAÇÃO DE PRODUTOS
def transformar_produtos(df_raw):
 df = df_raw.copy()

 df = df[[
     "Id Produto",
     "Nome Produto",
     "Categoria",
     "Marca",
     "Preço Unit.",
     "Custo Unit.",
 ]].copy()

 df.columns = [
     "id_produto",
     "nome_produto",
     "categoria",
     "marca",
     "preco_unitario",
     "custo_unitario",
 ]

 df["id_produto"] = pd.to_numeric(
     df["id_produto"], errors="coerce"
 ).astype("Int64")

 df["preco_unitario"] = (
       df["preco_unitario"]
       .apply(tratar_preco)
       .astype("Float64")
   )

 df["custo_unitario"] = (
       df["custo_unitario"]
       .apply(tratar_preco)
       .astype("Float64")
   )

 df = df.dropna(subset=["id_produto"])
 df = df.drop_duplicates(subset=["id_produto"])

 return df

# 3. TRANSFORMAÇÃO DE LOJAS
def transformar_lojas(df_raw):
 df = df_raw.copy()
 df.columns = df.columns.str.strip()

 df = df.dropna(subset=["Id Loja"]).copy()
 df = df[df["Id Loja"].astype(str).str.strip() != "Id Loja"]

 df["id_loja"] = pd.to_numeric(df["Id Loja"], errors="coerce").astype("Int64")

 cidade_col = "Cidade" if "Cidade" in df.columns else "Localidade"
 df["cidade"] = df[cidade_col].fillna("Não Informado")
 df["estado"] = (
     df["Estado"].fillna("Não Informado")
     if "Estado" in df.columns
     else "Não Informado"
 )

 df["nome_loja"] = (
     "Loja "
     + df["id_loja"].astype(str)
     + " - "
     + df[cidade_col].astype(str)
 )

 df_clean = df[["id_loja", "nome_loja", "cidade", "estado"]].copy()
 return df_clean.dropna(subset=["id_loja"]).drop_duplicates(
     subset=["id_loja"]
 )

def transformar_localizacao(df_lojas):
  df = df_lojas[["cidade", "estado"]].copy()
  df["cidade"] = df["cidade"].fillna("Não Informado").astype(str).str.strip()
  df["estado"] = df["estado"].fillna("Não Informado").astype(str).str.strip()
  return df.drop_duplicates(subset=["cidade", "estado"])

def transformar_tempo(df_vendas):

    df = df_vendas.copy()

    df["data_venda"] = pd.to_datetime(
        df["Data Venda"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["data_venda"]
    )

    df["data"] = df["data_venda"].dt.date
    df["sk_tempo"] = df["data_venda"].dt.strftime("%Y%m%d").astype(int)
    df["ano"] = df["data_venda"].dt.year
    df["mes"] = df["data_venda"].dt.month
    df["dia"] = df["data_venda"].dt.day
    df["trimestre"] = df["data_venda"].dt.quarter
    return df[
      ["sk_tempo", "data", "ano", "mes", "dia", "trimestre"]
  ].drop_duplicates(subset=["sk_tempo"])

# 4. TRANSFORMAÇÃO DA TABELA FATO DE VENDAS
def transformar_fato_vendas(
    df_vendas_raw, map_clientes, map_produtos, map_lojas, map_custos
):
  df = df_vendas_raw.copy()

  df["id_cliente"] = pd.to_numeric(
      df["Id Cliente"], errors="coerce"
  ).astype("Int64")
  df["id_produto"] = pd.to_numeric(
      df["Id Produto"], errors="coerce"
  ).astype("Int64")
  df["id_loja"] = pd.to_numeric(df["Id Loja"], errors="coerce").astype("Int64")

  # Lookup de Surrogate Keys
  df["sk_cliente"] = df["id_cliente"].map(map_clientes)
  df["sk_produto"] = df["id_produto"].map(map_produtos)
  df["sk_loja"] = df["id_loja"].map(map_lojas)

  df["data_venda"] = pd.to_datetime(df["Data Venda"], errors="coerce")
  df["sk_tempo"] = df["data_venda"].dt.strftime("%Y%m%d").astype("Int64")

  df = df.dropna(subset=["sk_cliente", "sk_produto", "sk_loja", "sk_tempo"])

  # Tratamento e Cálculo de Métricas
  df["qtd_vendida"] = (
      pd.to_numeric(df["Qtd. Vendida"], errors="coerce").fillna(0).astype(int)
  )
  df["qtd_devolvida"] = (
      pd.to_numeric(df["Qtd. Devolvida"], errors="coerce").fillna(0).astype(int)
  )
  df["qtd_liquida"] = df["qtd_vendida"] - df["qtd_devolvida"]

  df["preco_unitario"] = df["Preco Unitario"].apply(tratar_preco).fillna(0.0)
  df["custo_unitario"] = (
      df["id_produto"].map(map_custos).fillna(0.0).astype(float)
  )

  df["receita_bruta"] = df["qtd_vendida"] * df["preco_unitario"]
  df["valor_devolvido"] = df["qtd_devolvida"] * df["preco_unitario"]
  df["receita_liquida"] = df["receita_bruta"] - df["valor_devolvido"]
  df["custo_total"] = df["qtd_liquida"] * df["custo_unitario"]
  df["lucro_bruto"] = df["receita_liquida"] - df["custo_total"]

  return df[[
      "sk_cliente",
      "sk_produto",
      "sk_loja",
      "sk_tempo",
      "qtd_vendida",
      "qtd_devolvida",
      "qtd_liquida",
      "preco_unitario",
      "custo_unitario",
      "receita_bruta",
      "valor_devolvido",
      "receita_liquida",
      "custo_total",
      "lucro_bruto",
  ]]

# 5. DIAGNÓSTICO E INSPEÇÃO
def transformar_dados(df_clientes, df_produtos, df_lojas, df_vendas):
 print("\n========== TRANSFORM ==========")

 print("\n--- CLIENTES TRATADOS ---")
 print(df_clientes.head())
 print(f"Quantidade de clientes: {len(df_clientes):,}")

 print("\n--- PRODUTOS TRATADOS ---")
 print(df_produtos.head())
 print(f"Quantidade de produtos: {len(df_produtos):,}")

 print("\n--- LOJAS TRATADAS ---")
 print(df_lojas.head())
 print(f"Quantidade de lojas: {len(df_lojas):,}")

 print("\n--- VENDAS CONSOLIDADAS ---")
 print(f"Total de vendas no histórico: {len(df_vendas):,}")


if __name__ == "__main__":
 df_clientes_raw, df_produtos_raw, df_lojas_raw, df_vendas_raw = extrair_csvs()

 clientes = transformar_clientes(df_clientes_raw)
 produtos = transformar_produtos(df_produtos_raw)
 lojas = transformar_lojas(df_lojas_raw)

 transformar_dados(clientes, produtos, lojas, df_vendas_raw)
