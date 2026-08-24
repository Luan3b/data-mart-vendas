# Análises de Negócio

Este documento descreve as análises que podem ser realizadas sobre a `fato_vendas` e suas dimensões. As consultas SQL prontas estão em [`sql/04_queries.sql`](../sql/04_queries.sql).

## Indicadores Principais

- **Receita líquida:** soma de `fato_vendas.receita_liquida`.
- **Lucro bruto:** soma de `fato_vendas.lucro_bruto`.
- **Margem de lucro:** lucro bruto dividido pela receita líquida, em percentual.
- **Volume vendido:** soma de `qtd_vendida` ou `qtd_liquida`, conforme o objetivo da análise.
- **Taxa de devolução:** valor devolvido dividido pela receita bruta.
- **Clientes únicos:** contagem distinta de `sk_cliente`.

## Perguntas Analíticas

### Evolução temporal

Qual foi a receita, o lucro, o volume vendido e a margem por ano e mês? A `dim_tempo` permite comparar os períodos carregados e calcular crescimento mensal e receita acumulada no ano.

### Produtos e categorias

Quais produtos geram mais receita líquida e lucro? Quais categorias concentram o faturamento? A análise deve agrupar a fato por `dim_produto` e ordenar os resultados pelos valores agregados.

### Desempenho regional

Quais estados e lojas apresentam maior receita, ticket médio e taxa de devolução? Cidade e estado são atributos de `dim_loja` e devem ser usados diretamente nos agrupamentos.

### Devoluções

Quais lojas possuem maior impacto financeiro de devoluções? Compare `valor_devolvido` com `receita_bruta` e observe a taxa de devolução apenas onde houve devolução.

## Cuidados de Interpretação

- A base atualmente carregada inclui vendas de 2022, 2023 e 2024.
- `qtd_vendida` e `receita_bruta` representam o valor bruto; `qtd_liquida` e `receita_liquida` descontam devoluções.
- O ticket médio calculado nas consultas é a receita líquida média por linha da fato, não necessariamente por pedido comercial.
- Reexecuções podem duplicar a tabela fato, pois ela não possui uma chave natural da origem. Verifique a carga antes de interpretar totais.
