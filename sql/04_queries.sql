-- ============================================================================
-- PROJETO DATA MART DE VENDAS - CONSULTAS ANALÍTICAS (OLAP)
-- ============================================================================

-- 1. Faturamento e Lucro Consolidado por Ano e Mês
-- Permite acompanhar o crescimento financeiro e sazonalidade das vendas.
SELECT
    t.ano,
    t.mes,
    COUNT(f.sk_venda) AS total_pedidos,
    SUM(f.qtd_vendida) AS volume_pecas,
    SUM(f.receita_bruta) AS receita_bruta,
    SUM(f.valor_devolvido) AS total_devolucoes,
    SUM(f.receita_liquida) AS receita_liquida,
    SUM(f.lucro_bruto) AS lucro_bruto,
    ROUND((SUM(f.lucro_bruto) / NULLIF(SUM(f.receita_liquida), 0)) * 100, 2) AS margem_lucro_pct
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.mes
ORDER BY t.ano, t.mes;


-- 2. Top 10 Produtos Mais Vendidos por Receita Líquida (Curva ABC)
-- Identifica os produtos campeões de faturamento.
SELECT
    p.id_produto AS codigo_produto,
    p.nome_produto,
    p.categoria,
    SUM(f.qtd_vendida) AS quantidade_total,
    SUM(f.receita_liquida) AS receita_total,
    SUM(f.lucro_bruto) AS lucro_total
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.id_produto, p.nome_produto, p.categoria
ORDER BY receita_total DESC
LIMIT 10;


-- 3. Desempenho de Vendas e Margem por Categoria de Produto
-- Avalia qual linha de produto entrega maior rentabilidade.
SELECT
    p.categoria,
    COUNT(f.sk_venda) AS total_vendas,
    SUM(f.receita_liquida) AS receita_liquida,
    SUM(f.custo_total) AS custo_total,
    SUM(f.lucro_bruto) AS lucro_bruto,
    ROUND((SUM(f.lucro_bruto) / NULLIF(SUM(f.receita_liquida), 0)) * 100, 2) AS margem_pct
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.categoria
ORDER BY receita_liquida DESC;


-- 4. Desempenho Regional de Vendas por Estado e Região da Loja
-- Analisa penetração geográfica e eficiência por praça.
SELECT
    l.estado,
    COUNT(DISTINCT l.sk_loja) AS total_lojas_ativas,
    COUNT(f.sk_venda) AS total_pedidos,
    SUM(f.receita_liquida) AS receita_liquida,
    ROUND(AVG(f.receita_liquida), 2) AS ticket_medio_pedido
FROM fato_vendas f
JOIN dim_loja l ON f.sk_loja = l.sk_loja
GROUP BY l.estado
ORDER BY receita_liquida DESC;


-- 5. Impacto de Devoluções por Loja (Top 10 Lojas com Mais Devoluções)
-- Identifica gargalos operacionais e qualidade de atendimento/produto.
SELECT
    l.nome_loja,
    l.cidade,
    l.estado,
    SUM(f.receita_bruta) AS receita_bruta,
    SUM(f.valor_devolvido) AS valor_devolvido,
    ROUND((SUM(f.valor_devolvido) / NULLIF(SUM(f.receita_bruta), 0)) * 100, 2) AS taxa_devolucao_pct
FROM fato_vendas f
JOIN dim_loja l ON f.sk_loja = l.sk_loja
GROUP BY l.nome_loja, l.cidade, l.estado
HAVING SUM(f.valor_devolvido) > 0
ORDER BY taxa_devolucao_pct DESC
LIMIT 10;