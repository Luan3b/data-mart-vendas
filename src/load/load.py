import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()

from src.extract.extract import extrair_csvs
from src.transform.transform import (
    transformar_clientes,
    transformar_fato_vendas,
    transformar_localizacao,
    transformar_lojas,
    transformar_produtos,
    transformar_tempo,
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def carregar_clientes(cursor, df):
  print("\n[LOAD] Carregando clientes...")
  dados = [
      (
          int(r.id_cliente),
          str(r.nome_cliente),
          str(r.genero),
          (
              r.data_nascimento.to_pydatetime()
              if pd.notna(r.data_nascimento)
              else None
          ),
      )
      for r in df.itertuples(index=False)
  ]
  execute_values(
      cursor,
      "INSERT INTO dim_cliente (id_cliente," 
      " nome_cliente, " 
      "genero,"
      " data_nascimento)" 
      " VALUES %s ON CONFLICT (id_cliente) DO NOTHING",
      dados,
      page_size=5000,
  )
  print(f"[LOAD] Clientes carregados: {len(dados):,}")


def carregar_produtos(cursor, df):
  print("\n[LOAD] Carregando produtos...")
  dados = [
      (
          int(r.id_produto),
          str(r.nome_produto),
          str(r.categoria),
          str(r.marca),
          float(r.preco_unitario) if pd.notna(r.preco_unitario) else None,
          float(r.custo_unitario) if pd.notna(r.custo_unitario) else None,
      )
      for r in df.itertuples(index=False)
  ]
  execute_values(
      cursor,
      "INSERT INTO dim_produto (id_produto," 
      " nome_produto," 
      " categoria, marca,"
      " preco_unitario," 
      " custo_unitario)" 
      " VALUES %s ON CONFLICT (id_produto) DO NOTHING",
      dados,
      page_size=5000,
  )
  print(f"[LOAD] Produtos carregados: {len(dados):,}")


def carregar_lojas(cursor, df):
  print("\n[LOAD] Carregando lojas...")
  dados = [
      (int(r.id_loja), str(r.nome_loja), str(r.cidade), str(r.estado))
      for r in df.itertuples(index=False)
  ]
  execute_values(
      cursor,
      "INSERT INTO dim_loja (id_loja, " 
      "nome_loja," 
      " cidade, estado)" 
      "VALUES %s ON CONFLICT (id_loja) DO NOTHING",
      dados,
      page_size=5000,
  )
  print(f"[LOAD] Lojas carregadas: {len(dados):,}")


def carregar_localizacao(cursor, df):
  print("\n[LOAD] Carregando localizações...")
  dados = [
      (str(r.cidade), str(r.estado), None, "Brasil")
      for r in df.itertuples(index=False)
  ]
  execute_values(
      cursor,
      "INSERT INTO dim_localizacao (cidade," 
      " estado," 
      " sigla_estado," 
      " pais)" 
      " VALUES %s ON CONFLICT (cidade, estado) DO NOTHING",
      dados,
      page_size=1000,
  )
  print(f"[LOAD] Localizações carregadas: {len(dados):,}")


def carregar_tempo(cursor, df):
  print("\n[LOAD] Carregando dimensão tempo...")
  dados = [
      (
          int(r.sk_tempo),
          r.data,
          int(r.ano),
          int(r.mes),
          int(r.dia),
          int(r.trimestre),
      )
      for r in df.itertuples(index=False)
  ]
  execute_values(
      cursor,
      "INSERT INTO dim_tempo (sk_tempo," 
      " data, " 
      "ano," 
      " mes, " 
      "dia," 
      " trimestre)" 
      " VALUES %s ON CONFLICT (sk_tempo) DO NOTHING",
      dados,
      page_size=1000,
  )
  print(f"[LOAD] Datas carregadas: {len(dados):,}")


def carregar_fato_vendas(cursor, df_fato):
  print("\n[LOAD] Carregando tabela fato_vendas...")
  dados = [
      (
          int(r.sk_cliente),
          int(r.sk_produto),
          int(r.sk_loja),
          int(r.sk_tempo),
          int(r.qtd_vendida),
          int(r.qtd_devolvida),
          int(r.qtd_liquida),
          float(r.preco_unitario),
          float(r.custo_unitario),
          float(r.receita_bruta),
          float(r.valor_devolvido),
          float(r.receita_liquida),
          float(r.custo_total),
          float(r.lucro_bruto),
      )
      for r in df_fato.itertuples(index=False)
  ]
  if not dados:
    print("[LOAD] Nenhum registro de venda para carregar.")
    return

  execute_values(
      cursor,
      """
        INSERT INTO fato_vendas (
            sk_cliente,
            sk_produto,
            sk_loja, 
            sk_tempo,
            qtd_vendida, 
            qtd_devolvida, 
            qtd_liquida,
            preco_unitario,
            custo_unitario,
            receita_bruta,
            valor_devolvido,
            receita_liquida, 
            custo_total, 
            lucro_bruto
        ) VALUES %s
        """,
      dados,
      page_size=10000,
  )
  print(f"[LOAD] Fato Vendas carregada: {len(dados):,} registros inseridos!")


def conectar_banco():
  print("\n[LOAD] Conectando ao PostgreSQL...")
  conexao = psycopg2.connect(
      host=DB_CONFIG["host"],
      port=DB_CONFIG["port"],
      database=DB_CONFIG["database"],
      user=DB_CONFIG["user"],
      password=DB_CONFIG["password"],
  )
  print("[LOAD] Conexão realizada com sucesso!")
  return conexao


def main():
  print("\n========================================")
  print("           ETL - PIPELINE")
  print("========================================")

  # 1. EXTRAÇÃO
  df_cli_raw, df_prod_raw, df_loja_raw, df_vendas_raw = extrair_csvs()

  # 2. TRANSFORMAÇÃO DE DIMENSÕES
  print("\n[TRANSFORM] Processando dimensões...")
  df_cli = transformar_clientes(df_cli_raw)
  df_prod = transformar_produtos(df_prod_raw)
  df_lojas = transformar_lojas(df_loja_raw)
  df_loc = transformar_localizacao(df_lojas)
  df_tempo = transformar_tempo(df_vendas_raw)

  print("\n[TRANSFORM] Dados transformados com sucesso!")
  print(f"Clientes: {len(df_cli):,}")
  print(f"Produtos: {len(df_prod):,}")
  print(f"Lojas: {len(df_lojas):,}")
  print(f"Vendas Raw: {len(df_vendas_raw):,}")

  # Mapeamento dos custos dos produtos para cálculo da fato
  map_custos = dict(
      zip(df_prod["id_produto"].dropna(), df_prod["custo_unitario"])
  )

  # 3. CONEXÃO E CARGA DE DIMENSÕES
  conexao = conectar_banco()
  try:
    cursor = conexao.cursor()

    carregar_clientes(cursor, df_cli)
    carregar_produtos(cursor, df_prod)
    carregar_lojas(cursor, df_lojas)
    carregar_localizacao(cursor, df_loc)
    carregar_tempo(cursor, df_tempo)

    # 4. BUSCA MAPAS DAS SURROGATE KEYS NO BANCO (id_* -> sk_*)
    cursor.execute("SELECT id_cliente, sk_cliente FROM dim_cliente")
    map_cli = dict(cursor.fetchall())

    cursor.execute("SELECT id_produto, sk_produto FROM dim_produto")
    map_prod = dict(cursor.fetchall())

    cursor.execute("SELECT id_loja, sk_loja FROM dim_loja")
    map_loja = dict(cursor.fetchall())

    # 5. TRANSFORMAÇÃO DA FATO E CARGA
    print("\n[TRANSFORM] Processando fato_vendas...")
    df_fato = transformar_fato_vendas(
        df_vendas_raw, map_cli, map_prod, map_loja, map_custos
    )

    carregar_fato_vendas(cursor, df_fato)

    conexao.commit()
    print("\n========================================")
    print("       ETL FINALIZADO COM SUCESSO")
    print("========================================")

  except Exception as e:
    conexao.rollback()
    print("\n[ERRO] Falha durante o LOAD.")
    print(f"[ERRO] {e}")
    raise
  finally:
    cursor.close()
    conexao.close()
    print("[LOAD] Conexão encerrada.")


if __name__ == "__main__":
  main()


  """
import pandas as pd
import psycopg2

def import_xls(xls_file, table_name, db_params):
  df = pd.read_excel(xls_file)

  conn = psycopg2.connect(**db_params)
  cursor = conn.cursor()

  print('Iniciando importação')

  for _, row in df.iterrows():
    insert_row = (row['nome'], row['endereco'], row['numero'], row['email'], row['telefone'])
    insert_query = f"INSERT INTO {table_name} (nome, endereco, numero, email, telefone) VALUES (%s, %s, %s, %s, %s);"
    cursor.execute(insert_query, insert_row)
    print(insert_row)

  conn.commit()
  cursor.close()
  conn.close()

  print('Script finalizado')

def export_xls(table_name, db_params):
  conn = psycopg2.connect(**db_params)
  cursor = conn.cursor()

  print('Iniciando exportação')

  select_query = f"SELECT * FROM {table_name}"
  cursor.execute(select_query)

  print('Executando a query')

  data = cursor.fetchall()

  df = pd.DataFrame(data, columns=[col[0] for col in cursor.description])

  cursor.close()
  conn.close()

  print('Exportar')
  df.to_excel('nova-planilha.xlsx', index=False)

  print('Fim do script')

xls_file = 'clientes-002.xlsx'
table_name = 'cliente'
db_params = {
  'host': 'localhost',
  'database': 'importacao',
  'user': 'postgres',
  'password': 'postgres'
}

# import_xls(xls_file, table_name, db_params)
export_xls(table_name, db_params)"""