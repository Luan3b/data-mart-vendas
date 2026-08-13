-- Otimização de busca pelas Surrogate Keys nas consultas analíticas
CREATE INDEX IF NOT EXISTS idx_fato_cliente ON fato_vendas(sk_cliente);
CREATE INDEX IF NOT EXISTS idx_fato_produto ON fato_vendas(sk_produto);
CREATE INDEX IF NOT EXISTS idx_fato_loja ON fato_vendas(sk_loja);
CREATE INDEX IF NOT EXISTS idx_fato_tempo ON fato_vendas(sk_tempo);