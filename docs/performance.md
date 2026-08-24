# ⚡ Otimização e Performance

Este documento descreve as estratégias adotadas para garantir alta performance no processamento em memória e na ingestão/consulta no PostgreSQL.

---

## 1. Otimizações no Processamento (Python / Pandas)

* **Transformações Vetorizadas:** Eliminação de loops iterativos (`for index, row`) no processamento dos mais de 1,1 milhão de registros, utilizando operações vetorizadas nativas do Pandas.
* **Mapeamento via Hash Maps (Dicionários):** A resolução de *Surrogate Keys* (`id_* -> sk_*`) é feita em memória usando dicionários Python indexados, tornando o lookup quase instantâneo ($O(1)$).
* **Tipagem Adequada:** Conversão antecipada de tipos de dados (`int32`, `float64`, `datetime64`) para reduzir o consumo de memória RAM.

---

## 2. Otimizações no Banco de Dados (PostgreSQL)

* **Carga em Lote (*Batch Loading*):** Utilização de `psycopg2.extras.execute_values`, com páginas de 5.000 registros nas dimensões, 1.000 na dimensão tempo e 10.000 na tabela fato.
* **Controle Transacional:** O orquestrador confirma a carga após concluir todas as dimensões e a tabela fato; em caso de erro durante a carga, executa `rollback`.

---

## 3. Índices de Consulta (Performance de Leitura)

Para acelerar os filtros e agrupamentos das ferramentas analíticas, foram definidos índices nas chaves estrangeiras da tabela fato:

```sql
CREATE INDEX idx_fato_cliente ON fato_vendas (sk_cliente);
CREATE INDEX idx_fato_produto ON fato_vendas (sk_produto);
CREATE INDEX idx_fato_loja    ON fato_vendas (sk_loja);
CREATE INDEX idx_fato_tempo   ON fato_vendas (sk_tempo);
```