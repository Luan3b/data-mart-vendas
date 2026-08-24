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


def carregar_clientes(cursor, df_novos):
    print("\n[LOAD] Processando SCD Tipo 2 para dim_cliente...")

    # A chave surrogate pertence ao banco; o DataFrame pode conter uma chave
    # provisoria criada durante a transformacao e ela nao participa do merge.
    df_novos = df_novos.drop(columns=["sk_cliente"], errors="ignore")

    # 1. Busca versões ativas atuais no banco
    cursor.execute("""
        SELECT sk_cliente, id_cliente, nome_cliente, genero, data_nascimento, versao
        FROM dim_cliente
        WHERE is_current = TRUE;
    """)
    rows = cursor.fetchall()
    
    colunas_banco = ["sk_cliente", "id_cliente", "nome_cliente", "genero", "data_nascimento", "versao"]
    df_atuais = pd.DataFrame(rows, columns=colunas_banco)

    # Carga Inicial (tabela vazia)
    if df_atuais.empty:
        print("   -> Carga inicial: inserindo todos os registros.")
        dados_iniciais = [
            (
                int(r.id_cliente),
                str(r.nome_cliente),
                str(r.genero),
                r.data_nascimento,
                r.data_inicio,
                None,
                True,
                1
            )
            for r in df_novos.itertuples(index=False)
        ]
        
        query_insert = """
            INSERT INTO dim_cliente (
                id_cliente, nome_cliente, genero, data_nascimento, 
                data_inicio, data_fim, is_current, versao
            ) VALUES %s;
        """
        psycopg2.extras.execute_values(cursor, query_insert, dados_iniciais, page_size=5000)
        print(f"[LOAD] Clientes inseridos: {len(dados_iniciais):,}")
        return

    # 2. Identificação de Novos vs Alterados
    df_merge = pd.merge(
        df_novos, 
        df_atuais, 
        on="id_cliente", 
        how="left", 
        suffixes=("_novo", "_atual")
    )

    novos_clientes = df_merge[df_merge["sk_cliente"].isna()].copy()
    
    alterados = df_merge[
        df_merge["sk_cliente"].notna() & (
            (df_merge["nome_cliente_novo"].astype(str) != df_merge["nome_cliente_atual"].astype(str)) |
            (df_merge["genero_novo"].astype(str) != df_merge["genero_atual"].astype(str)) |
            (df_merge["data_nascimento_novo"] != df_merge["data_nascimento_atual"])
        )
    ].copy()

    # 3. Expirar versão anterior dos registros alterados
    if not alterados.empty:
        sks_para_expirar = alterados["sk_cliente"].astype(int).tolist()
        data_corte = df_novos["data_inicio"].iloc[0]

        cursor.execute("""
            UPDATE dim_cliente
            SET is_current = FALSE,
                data_fim = %s
            WHERE sk_cliente = ANY(%s);
        """, (data_corte, sks_para_expirar))
        print(f"   -> Registros antigos arquivados (is_current=False): {len(sks_para_expirar):,}")

    # 4. Inserir novos clientes + novas versões dos alterados
    linhas_para_inserir = []

    for r in novos_clientes.itertuples(index=False):
        linhas_para_inserir.append((
            int(r.id_cliente),
            str(r.nome_cliente),
            str(r.genero),
            r.data_nascimento,
            r.data_inicio,
            None,
            True,
            1
        ))

    for r in alterados.itertuples(index=False):
        linhas_para_inserir.append((
            int(r.id_cliente),
            str(r.nome_cliente_novo),
            str(r.genero_novo),
            r.data_nascimento_novo,
            r.data_inicio,
            None,
            True,
            int(r.versao) + 1
        ))

    if linhas_para_inserir:
        query_insert = """
            INSERT INTO dim_cliente (
                id_cliente, nome_cliente, genero, data_nascimento, 
                data_inicio, data_fim, is_current, versao
            ) VALUES %s;
        """
        psycopg2.extras.execute_values(cursor, query_insert, linhas_para_inserir, page_size=5000)

    print(f"[LOAD] Novos clientes inseridos: {len(novos_clientes):,}")
    print(f"[LOAD] Novas versões criadas (SCD2): {len(alterados):,}")

def carregar_produtos(cursor, df):
  print("\n[LOAD] Carregando produtos...")
  dados = [
      (
          int(r.sk_produto),
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
      "INSERT INTO dim_produto (sk_produto, id_produto," 
      " nome_produto," 
      " categoria, marca,"
      " preco_unitario," 
      " custo_unitario)" 
      " VALUES %s ON CONFLICT (id_produto) DO NOTHING",
      dados,
      page_size=5000,
  )
  print(f"[LOAD] Produtos carregados: {len(dados):,}")


from psycopg2.extras import execute_values

def carregar_lojas(cursor, df):
    print("\n[LOAD] Carregando lojas...")

    df = df.drop_duplicates(subset=['id_loja']).copy()
    dados = [
        (int(r.sk_loja), int(r.id_loja), str(r.nome_loja), str(r.cidade), str(r.estado), str(r.pais))
        for r in df.itertuples(index=False)
    ]

    query = """
        INSERT INTO dim_loja (
            sk_loja,
            id_loja,
            nome_loja,
            cidade,
            estado,
            pais
        )
        VALUES %s
        ON CONFLICT (id_loja) DO NOTHING;
    """

    execute_values(
        cursor,
        query,
        dados,
        page_size=5000,
    )
    print(f"[LOAD] Lojas processadas: {len(dados):,}")


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
          str(r.nome_dia_semana),
          str(r.nome_mes),
          str(r.semestre),
          str(r.nome_trimestre),
      )
      for r in df.itertuples(index=False)
  ]
  execute_values(
      cursor,
      "INSERT INTO dim_tempo ("
      "sk_tempo, data, ano, mes, dia, trimestre, nome_dia_semana, nome_mes, semestre, nome_trimestre) "
      "VALUES %s ON CONFLICT (sk_tempo) DO NOTHING",
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
