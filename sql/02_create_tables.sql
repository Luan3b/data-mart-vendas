CREATE TABLE dim_localizacao (
    sk_localizacao SERIAL PRIMARY KEY,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(100) NOT NULL,
    sigla_estado CHAR(2),
    pais VARCHAR(100) DEFAULT 'Brasil',
    UNIQUE (cidade, estado)
);
"""Id Cliente,Nome Completo,Genero,Data de Nacimento"""

CREATE TABLE dim_cliente (
    sk_cliente SERIAL PRIMARY KEY,
    id_cliente INT NOT NULL UNIQUE,
    nome_cliente VARCHAR(150) NOT NULL,
    genero CHAR(1),
    data_nascimento DATE
);

"""Id Produto,Nome Produto,Categoria,Marca,Preço Unit.,Custo Unit."""

CREATE TABLE dim_produto (
    sk_produto SERIAL PRIMARY KEY,
    id_produto INT NOT NULL UNIQUE,
    nome_produto VARCHAR(150) NOT NULL,
    categoria VARCHAR(100),
    marca VARCHAR(100),
    preco_unitario NUMERIC(15,2),
    custo_unitario NUMERIC(15,2)
);

CREATE TABLE dim_tempo (
    sk_tempo INT PRIMARY KEY,
    data DATE NOT NULL UNIQUE,
    ano INT NOT NULL,
    mes INT NOT NULL,
    dia INT NOT NULL,
    trimestre INT NOT NULL
);

"""Id Loja,Nome Loja,Cidade,Estado"""  

CREATE TABLE dim_loja (
    sk_loja SERIAL PRIMARY KEY,
    id_loja INT NOT NULL UNIQUE,
    nome_loja VARCHAR(150),
    cidade VARCHAR(100),
    estado VARCHAR(100)
);

CREATE TABLE fato_vendas (
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
