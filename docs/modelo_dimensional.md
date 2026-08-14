# 📐 Modelo Dimensional - Data Mart Vendas

Este documento detalha o desenho lógico e dimensional do Data Mart, justificando as escolhas arquiteturais de modelagem.

---

## 1. Tipo de Modelagem

O projeto implementa um **Star Schema Híbrido** (com extensão Snowflake na dimensão geográfica), priorizando alta velocidade de leitura para ferramentas de BI e consultas analíticas (OLAP).

```text
                    ┌─────────────────┐
                    │  dim_cliente    │
                    └────────┬────────┘
                             │ (sk_cliente)
                             ▼
┌─────────────────┐    ┌───────────────┐    ┌─────────────────┐
│  dim_produto    │───►│  fato_vendas  │◄───│    dim_loja     │
└─────────────────┘    └───────┬───────┘    └────────┬────────┘
  (sk_produto)                 │ (sk_tempo)          │ (cidade, estado)
                               ▼                     ▼
                       ┌─────────────────┐  ┌─────────────────┐
                       │   dim_tempo     │  │ dim_localizacao │
                       └─────────────────┘  └─────────────────┘
```

## 2. Granularidade da Tabela Fato

- **Nível de Granularidade:** Linha de item vendido por transação/pedido.
- **Volume:** **1.145.961 registros** cobrindo o período de 2022 a 2024.

---

## 3. Justificativa das Surrogate Keys (SKs)

1. **Desacoplamento Operacional:** Isola o ambiente analítico de alterações nos identificadores dos sistemas de origem.
2. **Performance de Indexação:** Chaves inteiras compactas (`INTEGER` e `BIGINT`) aceleram operações de `JOIN` e diminuem o consumo de memória no PostgreSQL.
3. **Padronização Temporal:** A chave `sk_tempo` no formato `YYYYMMDD` permite particionamento e agregações rápidas por períodos sem funções de conversão de data em tempo de execução.