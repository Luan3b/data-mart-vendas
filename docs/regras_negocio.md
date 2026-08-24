# 💼 Regras de Negócio - Data Mart Vendas

Este documento formaliza as regras lógicas, financeiras e de qualidade aplicadas durante o processo de transformação e carga dos dados.

---

## 1. Regras Financeiras e Métricas Analíticas

Todas as métricas financeiras são pré-calculadas linha a linha no módulo de transformação para garantir consistência e performance no banco analítico.

| Métrica | Regra de Negócio / Fórmula | Descrição |
|---|---|---|
| **Quantidade Líquida** | `qtd_vendida - qtd_devolvida` | Volume real de produtos que permaneceram com o cliente. |
| **Receita Bruta** | `qtd_vendida * preco_unitario` | Faturamento total gerado antes do abatimento de devoluções. |
| **Valor Devolvido** | `qtd_devolvida * preco_unitario` | Impacto financeiro das devoluções na venda. |
| **Receita Líquida** | `receita_bruta - valor_devolvido` | Faturamento líquido real obtido na transação. |
| **Custo Total** | `qtd_liquida * custo_unitario` | Custo dos produtos efetivamente comercializados. |
| **Lucro Bruto** | `receita_liquida - custo_total` | Margem de contribuição bruta da transação. |

---

## 2. Regras de Higienização e Tratamento

* **Sanitização de Valores Monetários:** Valores com formatações atípicas (ex.: `"2278.,8"`) são padronizados para formato decimal (`2278.8`) durante a transformação e gravados no PostgreSQL como `NUMERIC(15,2)`.
* **Tratamento de Nulos:** Registros sem identificadores ou data de venda válidos não são enviados para a tabela fato. Valores numéricos ausentes são preenchidos com zero durante o cálculo das métricas.
* **Padronização de Gênero:** Valores `M` e `F` são convertidos para `Masculino` e `Feminino`; valores não mapeados tornam-se nulos.
* **Estruturação de Cabeçalhos:** Linhas de metadados e linhas em branco no topo de planilhas brutas (como a de lojas) são descartadas na extração.

---

## 3. Regras de Integridade Dimensional

* **Unicidade nas Dimensões:** Chaves naturais (`id_cliente`, `id_produto`, `id_loja`) são deduplicadas antes da carga.
* **Substituição por Surrogate Keys (SKs):** Toda chave de negócio na tabela fato é substituída por um identificador numérico interno gerado no Data Mart.
* **Dimensão Tempo Obrigatória:** Toda transação carregada deve possuir data válida convertida no formato de chave inteira `YYYYMMDD`.

## 4. Histórico de Clientes

Alterações em nome, gênero ou data de nascimento geram uma nova versão em `dim_cliente` (SCD Tipo 2). A versão anterior é marcada como não vigente e preservada para histórico.