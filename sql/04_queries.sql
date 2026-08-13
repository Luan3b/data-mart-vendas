CREATE OR REPLACE VIEW vw_vendas_bi AS
SELECT 
    f.sk_venda,
    c.nome_cliente,
    c.genero,
    p.nome_produto,
    p.categoria,
    p.marca,
    l.nome_loja,
    l.cidade,
    l.estado,
    t.data,
    t.ano,
    t.mes,
    t.trimestre,
    f.qtd_vendida,
    f.qtd_devolvida,
    f.qtd_liquida,
    f.preco_unitario,
    f.custo_unitario,
    f.receita_bruta,
    f.valor_devolvido,
    f.receita_liquida,
    f.custo_total,
    f.lucro_bruto
FROM fato_vendas f
JOIN dim_cliente c ON f.sk_cliente = c.sk_cliente
JOIN dim_produto p ON f.sk_produto = p.sk_produto
JOIN dim_loja l ON f.sk_loja = l.sk_loja
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo;