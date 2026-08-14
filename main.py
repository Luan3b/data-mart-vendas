#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
                     DATA MART DE VENDAS - PIPELINE ETL
================================================================================

Orquestrador principal do processo Extract → Transform → Load → Validate

Uso:
    python main.py                  # Executa pipeline completo
    python main.py --validate-only  # Apenas valida dados existentes
    python main.py --help           # Mostra opcções de ajuda

Variáveis de ambiente (.env):
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    DEBUG (opcional): true para modo verbose
    ETL_MODE (opcional): 'full' ou 'incremental'

================================================================================
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Configurar path para importar módulos locais
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psycopg2
from dotenv import load_dotenv
import pandas as pd

from src.extract.extract import extrair_csvs
from src.transform.transform import (
    transformar_clientes,
    transformar_produtos,
    transformar_lojas,
    transformar_localizacao,
    transformar_tempo,
    transformar_fato_vendas,
)
from src.load.load import (
    carregar_clientes,
    carregar_produtos,
    carregar_lojas,
    carregar_localizacao,
    carregar_tempo,
    carregar_fato_vendas,
)
from src.validation.validation import (
    validar_tabelas,
    validar_fato,
    validar_valores,
)

# ================================================================================
# CONFIGURAÇÃO DE LOGGING
# ================================================================================

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"etl_{timestamp}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

# ================================================================================
# CONFIGURAÇÃO DE AMBIENTE
# ================================================================================

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "datamart_vendas"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ETL_MODE = os.getenv("ETL_MODE", "full")

# ================================================================================
# FUNÇÕES PRINCIPAIS
# ================================================================================


def criar_conexao():
    """Estabelece conexão com PostgreSQL."""
    try:
        logger.info(f"🔗 Conectando ao PostgreSQL ({DB_CONFIG['host']}:{DB_CONFIG['port']})...")
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("✅ Conexão estabelecida com sucesso!")
        return conn
    except psycopg2.Error as e:
        logger.error(f"❌ ERRO ao conectar ao banco: {e}")
        sys.exit(1)


def criar_tabelas(conn):
    """Cria as tabelas do Data Mart (se não existirem)."""
    logger.info("\n📋 [1/5] Verificando estrutura do banco...")

    cursor = conn.cursor()

    try:
        # Verifica se a tabela fato_vendas já existe
        cursor.execute("""
            SELECT EXISTS(
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'fato_vendas'
            );
        """)

        tabela_existe = cursor.fetchone()[0]

        if tabela_existe:
            logger.info("   ✓ Tabelas já existem no banco")
            cursor.close()
            return

        logger.info("   ⚠️  Tabelas não encontradas. Criando...")

        # Ler e executar script de criação
        script_path = "sql/02_create_tables.sql"
        with open(script_path, "r", encoding="utf-8") as f:
            script = f.read()

        # Dividir por semicolons e executar cada statement
        for statement in script.split(";"):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)

        conn.commit()
        logger.info("   ✓ Tabelas criadas com sucesso!")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ ERRO ao criar tabelas: {e}")
        sys.exit(1)
    finally:
        cursor.close()


def extrair_dados():
    """Extrai dados dos arquivos CSV."""
    logger.info("\n📂 [2/5] Extraindo dados dos CSV...")

    try:
        df_clientes_raw, df_produtos_raw, df_lojas_raw, df_vendas_raw = extrair_csvs()
        
        logger.info(f"   ✓ Clientes: {len(df_clientes_raw):,} registros")
        logger.info(f"   ✓ Produtos: {len(df_produtos_raw):,} registros")
        logger.info(f"   ✓ Lojas: {len(df_lojas_raw):,} registros")
        logger.info(f"   ✓ Vendas: {len(df_vendas_raw):,} registros")

        return df_clientes_raw, df_produtos_raw, df_lojas_raw, df_vendas_raw

    except FileNotFoundError as e:
        logger.error(f"❌ ERRO: Arquivo não encontrado: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ ERRO ao extrair dados: {e}")
        sys.exit(1)


def transformar_dados(df_clientes_raw, df_produtos_raw, df_lojas_raw, df_vendas_raw):
    """Transforma e sanitiza dados."""
    logger.info("\n🔄 [3/5] Transformando dados...")

    try:
        # Dimensões
        df_clientes = transformar_clientes(df_clientes_raw)
        logger.info(f"   ✓ Clientes transformados: {len(df_clientes):,}")

        df_produtos = transformar_produtos(df_produtos_raw)
        logger.info(f"   ✓ Produtos transformados: {len(df_produtos):,}")

        df_lojas = transformar_lojas(df_lojas_raw)
        logger.info(f"   ✓ Lojas transformadas: {len(df_lojas):,}")

        df_localizacao = transformar_localizacao(df_lojas)
        logger.info(f"   ✓ Localizações extraídas: {len(df_localizacao):,}")

        df_tempo = transformar_tempo(df_vendas_raw)
        logger.info(f"   ✓ Dimensão tempo criada: {len(df_tempo):,} datas únicas")

        # Tabela Fato (requer mapas de lookup)
        map_clientes = dict(zip(df_clientes["id_cliente"], df_clientes.index + 1))
        map_produtos = dict(zip(df_produtos["id_produto"], df_produtos.index + 1))
        map_lojas = dict(zip(df_lojas["id_loja"], df_lojas.index + 1))
        map_custos = dict(zip(df_produtos["id_produto"], df_produtos["custo_unitario"]))

        df_fato = transformar_fato_vendas(
            df_vendas_raw,
            map_clientes,
            map_produtos,
            map_lojas,
            map_custos,
        )
        logger.info(f"   ✓ Fato de vendas calculada: {len(df_fato):,} transações")

        return df_clientes, df_produtos, df_lojas, df_localizacao, df_tempo, df_fato

    except Exception as e:
        logger.error(f"❌ ERRO ao transformar dados: {e}")
        if DEBUG:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


def carregar_dados(
    conn,
    df_clientes,
    df_produtos,
    df_lojas,
    df_localizacao,
    df_tempo,
    df_fato,
):
    """Carrega dados transformados no PostgreSQL."""
    logger.info("\n💾 [4/5] Carregando dados no PostgreSQL...")

    cursor = conn.cursor()

    try:
        carregar_clientes(cursor, df_clientes)
        carregar_produtos(cursor, df_produtos)
        carregar_lojas(cursor, df_lojas)
        carregar_localizacao(cursor, df_localizacao)
        carregar_tempo(cursor, df_tempo)
        carregar_fato_vendas(cursor, df_fato)

        conn.commit()
        logger.info("   ✓ Todos os dados carregados com sucesso!")

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ ERRO ao carregar dados: {e}")
        if DEBUG:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        cursor.close()


def validar_dados(conn):
    """Executa validações de integridade."""
    logger.info("\n✅ [5/5] Validando dados...")

    cursor = conn.cursor()

    try:
        validar_tabelas(cursor)
        validar_fato(cursor)
        validar_valores(cursor)
        logger.info("   ✓ Validação concluída com sucesso!")

    except Exception as e:
        logger.error(f"❌ ERRO na validação: {e}")
        if DEBUG:
            import traceback
            logger.error(traceback.format_exc())
    finally:
        cursor.close()


def executar_pipeline():
    """Executa o pipeline ETL completo."""
    logger.info("=" * 80)
    logger.info("          🚀 INICIANDO DATA MART DE VENDAS - PIPELINE ETL")
    logger.info("=" * 80)
    logger.info(f"Modo: {ETL_MODE} | Debug: {DEBUG}")
    logger.info(f"Log: {LOG_FILE}")

    # 1. Conectar ao banco
    conn = criar_conexao()

    # 2. Criar tabelas (se necessário)
    criar_tabelas(conn)

    # 3. Extrair
    df_clientes_raw, df_produtos_raw, df_lojas_raw, df_vendas_raw = extrair_dados()

    # 4. Transformar
    df_clientes, df_produtos, df_lojas, df_localizacao, df_tempo, df_fato = (
        transformar_dados(df_clientes_raw, df_produtos_raw, df_lojas_raw, df_vendas_raw)
    )

    # 5. Carregar
    carregar_dados(
        conn,
        df_clientes,
        df_produtos,
        df_lojas,
        df_localizacao,
        df_tempo,
        df_fato,
    )

    # 6. Validar
    validar_dados(conn)

    conn.close()

    logger.info("\n" + "=" * 80)
    logger.info("          ✨ PIPELINE CONCLUÍDO COM SUCESSO!")
    logger.info("=" * 80)
    logger.info(f"📝 Detalhes em: {LOG_FILE}\n")


def validar_apenas(conn):
    """Apenas valida dados sem rodar o ETL."""
    logger.info("\n" + "=" * 80)
    logger.info("          🔍 MODO: VALIDAÇÃO APENAS")
    logger.info("=" * 80)

    validar_dados(conn)

    conn.close()

    logger.info("\n" + "=" * 80)
    logger.info("          ✅ VALIDAÇÃO CONCLUÍDA")
    logger.info("=" * 80 + "\n")


# ================================================================================
# MAIN
# ================================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Data Mart de Vendas - Pipeline ETL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                      # Executa pipeline completo
  python main.py --validate-only      # Apenas valida dados
  python main.py --help               # Mostra esta ajuda
        """,
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Executa apenas validação (sem ETL)",
    )

    args = parser.parse_args()

    try:
        if args.validate_only:
            conn = criar_conexao()
            validar_apenas(conn)
        else:
            executar_pipeline()

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Pipeline interrompido pelo usuário")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ ERRO FATAL: {e}")
        if DEBUG:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
