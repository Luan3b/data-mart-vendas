
CREATE TABLE IF NOT EXISTS dim_cliente (
    sk_cliente SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL,
    nome_cliente VARCHAR(150) NOT NULL,
    genero VARCHAR(20),
    data_nascimento DATE,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    versao INT NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX IF NOT EXISTS uk_dim_cliente_atual
ON dim_cliente (id_cliente)
WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_dim_cliente_lookup ON dim_cliente(id_cliente, is_current);

CREATE TABLE IF NOT EXISTS dim_produto (
    sk_produto SERIAL PRIMARY KEY,
    id_produto INT NOT NULL UNIQUE,
    nome_produto VARCHAR(150) NOT NULL,
    categoria VARCHAR(100),
    marca VARCHAR(100),
    preco_unitario NUMERIC(15,2),
    custo_unitario NUMERIC(15,2)
);

CREATE TABLE IF NOT EXISTS dim_tempo (
    sk_tempo INT PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    ano INT NOT NULL,
    mes INT NOT NULL,
    dia INT NOT NULL,
    trimestre INT NOT NULL,
    nome_dia_semana VARCHAR(20) NOT NULL,
    nome_mes VARCHAR(20) NOT NULL,
    semestre VARCHAR(20) NOT NULL,
    nome_trimestre VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_loja (
    sk_loja SERIAL PRIMARY KEY,
    id_loja INT NOT NULL UNIQUE,
    nome_loja VARCHAR(150),
    cidade VARCHAR(100),
    estado VARCHAR(100),
    pais VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS fato_vendas (
    sk_venda BIGSERIAL PRIMARY KEY,

    sk_cliente INT NOT NULL,
    sk_produto INT NOT NULL,
    sk_loja INT NOT NULL,
    sk_tempo INT NOT NULL,

    qtd_vendida INT NOT NULL,
    qtd_devolvida INT NOT NULL DEFAULT 0,
    qtd_liquida INT NOT NULL,

    preco_unitario NUMERIC(15,2) NOT NULL,
    custo_unitario NUMERIC(15,2) NOT NULL,

    receita_bruta NUMERIC(15,2) NOT NULL,
    valor_devolvido NUMERIC(15,2) NOT NULL,
    receita_liquida NUMERIC(15,2) NOT NULL,
    custo_total NUMERIC(15,2) NOT NULL,
    lucro_bruto NUMERIC(15,2) NOT NULL,

    FOREIGN KEY (sk_cliente)
        REFERENCES dim_cliente(sk_cliente),

    FOREIGN KEY (sk_produto)
        REFERENCES dim_produto(sk_produto),

    FOREIGN KEY (sk_loja)
        REFERENCES dim_loja(sk_loja),

    FOREIGN KEY (sk_tempo)
        REFERENCES dim_tempo(sk_tempo)
);
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
