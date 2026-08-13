SELECT 
    t.ano,
    COUNT(*) AS total_vendas,
    SUM(f.qtd_vendida) AS itens_vendidos,
    SUM(f.qtd_devolvida) AS itens_devolvidos,
    ROUND(SUM(f.receita_bruta)::numeric, 2) AS receita_bruta,
    ROUND(SUM(f.receita_liquida)::numeric, 2) AS receita_liquida,
    ROUND(SUM(f.lucro_bruto)::numeric, 2) AS lucro_bruto
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano
ORDER BY t.ano;