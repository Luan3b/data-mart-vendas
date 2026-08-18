import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def conectar_banco():
    print("\n[VALIDATION] Conectando ao PostgreSQL...")

    conexao = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )

    print("[VALIDATION] Conexão realizada com sucesso!")

    return conexao


def validar_tabelas(cursor):

    print("\n========================================")
    print("       VALIDAÇÃO DO DATA MART")
    print("========================================")

    tabelas = [
        "dim_cliente",
        "dim_produto",
        "dim_loja",
        "dim_tempo",
        "fato_vendas",
    ]

    for tabela in tabelas:

        cursor.execute(
            f"SELECT COUNT(*) FROM {tabela}"
        )

        quantidade = cursor.fetchone()[0]

        print(
            f"[VALIDATION] {tabela}: "
            f"{quantidade:,} registros"
        )


def validar_fato(cursor):

    print("\n[VALIDATION] Verificando fato_vendas...")

    cursor.execute("""
        SELECT COUNT(*)
        FROM fato_vendas
    """)

    total = cursor.fetchone()[0]

    print(
        f"[VALIDATION] Total de vendas: "
        f"{total:,}"
    )


def validar_valores(cursor):

    print("\n[VALIDATION] Verificando valores...")

    cursor.execute("""
        SELECT COUNT(*)
        FROM fato_vendas
        WHERE receita_bruta < 0
           OR receita_liquida < 0
           OR lucro_bruto IS NULL
    """)

    problemas = cursor.fetchone()[0]

    if problemas == 0:

        print(
            "[VALIDATION] Nenhum problema encontrado."
        )

    else:

        print(
            f"[VALIDATION] {problemas:,} registros "
            "com possíveis problemas."
        )


def validar_chaves_estrangeiras(cursor):

    print(
        "\n[VALIDATION] Verificando chaves estrangeiras..."
    )

    consultas = {

        "Clientes inexistentes": """
            SELECT COUNT(*)
            FROM fato_vendas f
            LEFT JOIN dim_cliente c
                ON f.sk_cliente = c.sk_cliente
            WHERE c.sk_cliente IS NULL
        """,

        "Produtos inexistentes": """
            SELECT COUNT(*)
            FROM fato_vendas f
            LEFT JOIN dim_produto p
                ON f.sk_produto = p.sk_produto
            WHERE p.sk_produto IS NULL
        """,

        "Lojas inexistentes": """
            SELECT COUNT(*)
            FROM fato_vendas f
            LEFT JOIN dim_loja l
                ON f.sk_loja = l.sk_loja
            WHERE l.sk_loja IS NULL
        """,

        "Datas inexistentes": """
            SELECT COUNT(*)
            FROM fato_vendas f
            LEFT JOIN dim_tempo t
                ON f.sk_tempo = t.sk_tempo
            WHERE t.sk_tempo IS NULL
        """,
    }

    for descricao, consulta in consultas.items():

        cursor.execute(consulta)

        problemas = cursor.fetchone()[0]

        if problemas == 0:

            print(
                f"[OK] {descricao}: nenhum problema"
            )

        else:

            print(
                f"[ERRO] {descricao}: "
                f"{problemas:,} registros"
            )


def main():

    conexao = None
    cursor = None

    try:

        conexao = conectar_banco()

        cursor = conexao.cursor()

        validar_tabelas(cursor)

        validar_fato(cursor)

        validar_valores(cursor)

        validar_chaves_estrangeiras(cursor)

        print("\n========================================")
        print("   VALIDAÇÃO FINALIZADA COM SUCESSO")
        print("========================================")

    except Exception as erro:

        print("\n[ERRO] Falha durante a validação.")
        print(f"[ERRO] {erro}")

        raise

    finally:

        if cursor is not None:
            cursor.close()

        if conexao is not None:
            conexao.close()

        print("[VALIDATION] Conexão encerrada.")


if __name__ == "__main__":
    main()