import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from src.extract.extract import extrair_csvs

from src.transform.transform import (
    transformar_clientes,
    transformar_produtos,
    transformar_lojas,
)


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "123456",
}

def carregar_clientes(cursor, df):

    print("\n[LOAD] Carregando clientes...")

    dados = [
        (
            int(row.id_cliente),
            str(row.nome_cliente),
            str(row.genero),
            row.data_nascimento.to_pydatetime()
            if pd.notna(row.data_nascimento)
            else None,
        )
        for row in df.itertuples(index=False)
    ]

    if not dados:
        print("[LOAD] Nenhum cliente para carregar.")
        return

    execute_values(
        cursor,
        """
        INSERT INTO dim_cliente (
            id_cliente,
            nome_cliente,
            genero,
            data_nascimento
        )
        VALUES %s
        ON CONFLICT (id_cliente) DO NOTHING
        """,
        dados,
        page_size=5000,
    )

    print(f"[LOAD] Clientes carregados: {len(dados):,}")


def carregar_produtos(cursor, df):

    print("\n[LOAD] Carregando produtos...")

    dados = [
        (
            int(row.id_produto),
            str(row.nome_produto),
            str(row.categoria),
            str(row.marca),
            float(row.preco_unitario)
            if pd.notna(row.preco_unitario)
            else None,
            float(row.custo_unitario)
            if pd.notna(row.custo_unitario)
            else None,
        )
        
        for row in df.itertuples(index=False)
    ]

    if not dados:
        print("[LOAD] Nenhum produto para carregar.")
        return

    execute_values(
        cursor,
        """
        INSERT INTO dim_produto (
            id_produto,
            nome_produto,
            categoria,
            marca,
            preco_unitario,
            custo_unitario
        )
        VALUES %s
        ON CONFLICT (id_produto) DO NOTHING
        """,
        dados,
        page_size=5000,
    )

    print(f"[LOAD] Produtos carregados: {len(dados):,}")

def carregar_lojas(cursor, df):

    print("\n[LOAD] Carregando lojas...")

    dados = [
        (
            int(row.id_loja),
            str(row.nome_loja),
            str(row.cidade),
            str(row.estado),
        )
        for row in df.itertuples(index=False)
    ]

    if not dados:
        print("[LOAD] Nenhuma loja para carregar.")
        return

    execute_values(
        cursor,
        """
        INSERT INTO dim_loja (
            id_loja,
            nome_loja,
            cidade,
            estado
        )
        VALUES %s
        ON CONFLICT (id_loja) DO NOTHING
        """,
        dados,
        page_size=5000,
    )

    print(f"[LOAD] Lojas carregadas: {len(dados):,}")

def carregar_localizacao(cursor, df_lojas):

    print("\n[LOAD] Carregando localizações...")

    df = df_lojas[
        [
            "cidade",
            "estado",
        ]
    ].copy()

    df["cidade"] = (
        df["cidade"]
        .fillna("Não Informado")
        .astype(str)
        .str.strip()
    )

    df["estado"] = (
        df["estado"]
        .fillna("Não Informado")
        .astype(str)
        .str.strip()
    )

    df = df.drop_duplicates(
        subset=["cidade", "estado"]
    )

    dados = [
        (
            str(row.cidade),
            str(row.estado),
            None,
            "Brasil",
        )
        for row in df.itertuples(index=False)
    ]

    if not dados:
        print("[LOAD] Nenhuma localização para carregar.")
        return

    execute_values(
        cursor,
        """
        INSERT INTO dim_localizacao (
            cidade,
            estado,
            sigla_estado,
            pais
        )
        VALUES %s
        ON CONFLICT (cidade, estado) DO NOTHING
        """,
        dados,
        page_size=1000,
    )

    print(f"[LOAD] Localizações carregadas: {len(dados):,}")

def carregar_tempo(cursor, df_vendas):

    print("\n[LOAD] Carregando dimensão tempo...")

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

    df = df[
        [
            "sk_tempo",
            "data",
            "ano",
            "mes",
            "dia",
            "trimestre",
        ]
    ].drop_duplicates(
        subset=["sk_tempo"]
    )

    dados = [
        (
            int(row.sk_tempo),
            row.data,
            int(row.ano),
            int(row.mes),
            int(row.dia),
            int(row.trimestre),
        )
        for row in df.itertuples(index=False)
    ]

    if not dados:
        print("[LOAD] Nenhuma data para carregar.")
        return

    execute_values(
        cursor,
        """
        INSERT INTO dim_tempo (
            sk_tempo,
            data,
            ano,
            mes,
            dia,
            trimestre
        )
        VALUES %s
        ON CONFLICT (sk_tempo) DO NOTHING
        """,
        dados,
        page_size=1000,
    )

    print(f"[LOAD] Datas carregadas: {len(dados):,}")


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
    print("           ETL - LOAD")
    print("========================================")


    (
        df_clientes_raw,
        df_produtos_raw,
        df_lojas_raw,
        df_vendas_raw,
    ) = extrair_csvs()

    print("\n[TRANSFORM] Transformando dados...")

    clientes = transformar_clientes(
        df_clientes_raw
    )

    produtos = transformar_produtos(
        df_produtos_raw
    )

    lojas = transformar_lojas(
        df_lojas_raw
    )

    print("\n[TRANSFORM] Dados transformados com sucesso!")

    print(f"Clientes: {len(clientes):,}")
    print(f"Produtos: {len(produtos):,}")
    print(f"Lojas: {len(lojas):,}")
    print(f"Vendas: {len(df_vendas_raw):,}")

    conexao = conectar_banco()

    try:

        cursor = conexao.cursor()

        carregar_clientes(
            cursor,
            clientes
        )

        carregar_produtos(
            cursor,
            produtos
        )

        carregar_lojas(
            cursor,
            lojas
        )

        carregar_localizacao(
            cursor,
            lojas
        )

        carregar_tempo(
            cursor,
            df_vendas_raw
        )

        conexao.commit()

        print("\n========================================")
        print("       LOAD FINALIZADO COM SUCESSO")
        print("========================================")

    except Exception as erro:

        conexao.rollback()

        print("\n[ERRO] Falha durante o LOAD.")
        print(f"[ERRO] {erro}")

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