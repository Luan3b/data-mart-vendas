import os
import psycopg2
import pytest
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture(scope="module")
def db_cursor():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", 5432),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()
    yield cur
    cur.close()
    conn.close()

def test_quantidade_registros(db_cursor):
    db_cursor.execute("SELECT COUNT(*) FROM fato_vendas;")
    total = db_cursor.fetchone()[0]
    assert total >= 1_145_000, f"FALHA: Quantidade inesperada ({total})"

def test_valores_nulos_e_negativos(db_cursor):
    # Nulos em SKs
    db_cursor.execute("""
        SELECT COUNT(*) FROM fato_vendas 
        WHERE sk_cliente IS NULL OR sk_produto IS NULL OR sk_loja IS NULL OR sk_tempo IS NULL;
    """)
    assert db_cursor.fetchone()[0] == 0, "FALHA: Existem SKs nulas na tabela fato."

    # Negativos indevidos
    db_cursor.execute("SELECT COUNT(*) FROM fato_vendas WHERE preco_unitario < 0 OR qtd_vendida < 0;")
    assert db_cursor.fetchone()[0] == 0, "FALHA: Existem valores negativos em preço ou quantidade."

def test_integridade_fks(db_cursor):
    db_cursor.execute("""
        SELECT COUNT(*) 
        FROM fato_vendas f
        LEFT JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente
        LEFT JOIN dim_produto p ON f.sk_produto = p.sk_produto
        LEFT JOIN dim_loja l ON f.sk_loja = l.sk_loja
        LEFT JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        WHERE c.sk_cliente IS NULL 
           OR p.sk_produto IS NULL 
           OR l.sk_loja IS NULL 
           OR t.sk_tempo IS NULL;
    """)
    assert db_cursor.fetchone()[0] == 0, "FALHA: Existem registros órfãos na fato_vendas."
if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()
    try:
        print("\n🔍 Testando integridade do PostgreSQL...")
        test_quantidade_registros(cur)
        test_valores_nulos_e_negativos(cur)
        test_integridade_fks(cur)
        print("🎉 Todos os testes de banco passaram com sucesso!\n")
    finally:
        cur.close()
        conn.close()