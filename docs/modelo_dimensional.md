# 📐 Modelo Dimensional - Data Mart Vendas

Este documento detalha o desenho lógico e dimensional do Data Mart, justificando as escolhas arquiteturais de modelagem.

---

## 1. Tipo de Modelagem

O projeto implementa um **Star Schema**, priorizando leitura simples para ferramentas de BI e consultas analíticas (OLAP). A localização permanece como atributos de `dim_loja`; não existe uma tabela `dim_localizacao` no modelo atual.

```text
                    ┌─────────────────┐
                    │  dim_cliente    │
                    └────────┬────────┘
                             │ (sk_cliente)
                             ▼
┌─────────────────┐    ┌───────────────┐    ┌─────────────────┐
│  dim_produto    │───►│  fato_vendas  │◄───│    dim_loja     │
└─────────────────┘    └───────┬───────┘    └────────┬────────┘
    (sk_produto)                 │ (sk_tempo)
               ▼
             ┌─────────────────┐
             │   dim_tempo     │
             └─────────────────┘
```

## 2. Granularidade da Tabela Fato

- **Nível de Granularidade:** Uma linha de venda do arquivo de origem.
- **Período:** Os arquivos atualmente carregados correspondem a 2022, 2023 e 2024.

---

## 3. Justificativa das Surrogate Keys (SKs)

1. **Desacoplamento Operacional:** Isola o ambiente analítico de alterações nos identificadores dos sistemas de origem.
2. **Performance de Indexação:** Chaves inteiras compactas (`INTEGER` e `BIGINT`) aceleram operações de `JOIN` e diminuem o consumo de memória no PostgreSQL.
3. **Padronização Temporal:** A chave `sk_tempo` no formato `YYYYMMDD` facilita joins e agregações por períodos sem conversão de data em tempo de execução.

## 4. Histórico de Clientes

A `dim_cliente` utiliza SCD Tipo 2. Alterações cadastrais encerram a versão atual (`is_current = FALSE`, com `data_fim`) e inserem uma nova versão com outra surrogate key. As demais dimensões são carregadas com deduplicação por chave natural.