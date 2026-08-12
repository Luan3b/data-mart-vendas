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

# 4. TRANSFORMAÇÃO DA TABELA FATO DE VENDAS
def transformar_fato_vendas(
   df_vendas_raw, dim_cli_db, dim_prod_db, dim_loja_db
):
 df = df_vendas_raw.copy()

 df["Id Cliente"] = pd.to_numeric(
     df["Id Cliente"], errors="coerce"
 ).astype("Int64")
 df["Id Produto"] = pd.to_numeric(
     df["Id Produto"], errors="coerce"
 ).astype("Int64")
 df["Id Loja"] = pd.to_numeric(df["Id Loja"], errors="coerce").astype("Int64")

 df["Preco Unitario"] = df["Preco Unitario"].apply(tratar_preco)

 # Lookups com as dimensões vindas do banco de dados
 df_fato = df.merge(
     dim_cli_db, left_on="Id Cliente", right_on="id_cliente", how="inner"
 )
 df_fato = df_fato.merge(
     dim_prod_db, left_on="Id Produto", right_on="id_produto", how="inner"
 )
 df_fato = df_fato.merge(
     dim_loja_db, left_on="Id Loja", right_on="id_loja", how="inner"
 )

 df_fato["sk_tempo"] = (
     pd.to_datetime(df_fato["Data Venda"]).dt.strftime("%Y%m%d").astype(int)
 )

 df_fato["qtd_vendida"] = (
     pd.to_numeric(df_fato["Qtd. Vendida"], errors="coerce")
     .fillna(0)
     .astype(int)
 )
 df_fato["qtd_devolvida"] = (
     pd.to_numeric(df_fato["Qtd. Devolvida"], errors="coerce")
     .fillna(0)
     .astype(int)
 )
 df_fato["qtd_liquida"] = df_fato["qtd_vendida"] - df_fato["qtd_devolvida"]

 df_fato["preco_unitario"] = df_fato["Preco Unitario"].fillna(0.0)
 df_fato["custo_unitario"] = df_fato["custo_unitario"].fillna(0.0)

 df_fato["receita_bruta"] = (
     df_fato["qtd_vendida"] * df_fato["preco_unitario"]
 )
 df_fato["valor_devolvido"] = (
     df_fato["qtd_devolvida"] * df_fato["preco_unitario"]
 )
 df_fato["receita_liquida"] = (
     df_fato["receita_bruta"] - df_fato["valor_devolvido"]
 )
 df_fato["custo_total"] = (
     df_fato["qtd_liquida"] * df_fato["custo_unitario"]
 )
 df_fato["lucro_bruto"] = df_fato["receita_liquida"] - df_fato["custo_total"]

 payload_fato = df_fato[[
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

 return payload_fato

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
