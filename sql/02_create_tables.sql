CREATE TABLE dim_localizacao (
    sk_localizacao SERIAL PRIMARY KEY,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(100) NOT NULL,
    sigla_estado CHAR(2),
    pais VARCHAR(100) DEFAULT 'Brasil'
);

"""Id Cliente,Nome Completo,Genero,Data de Nacimento"""

CREATE TABLE dim_cliente (
    sk_cliente SERIAL PRIMARY KEY,
    nome_cliente VARCHAR(100) NOT NULL,
    data_nascimento DATE,
    genero CHAR(1)
);

"""Id Produto,Nome Produto,Categoria,Marca,Preço Unit.,Custo Unit."""

create table dim_produto (
    sk_produto SERIAL PRIMARY KEY,
    nome_produto VARCHAR(100) NOT NULL,
    categoria VARCHAR(100),
    preco DECIMAL(10, 2)
);

Create table dim_tempo (
    sk_tempo SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    ano INT NOT NULL,
    mes INT NOT NULL,
    dia INT NOT NULL
);

"""Id Loja,Nome Loja,Cidade,Estado"""  

CREATE Table dim_loja (
    sk_loja SERIAL PRIMARY KEY,
    id_loja INT UNIQUE NOT NULL,
    localidade VARCHAR(100),
    cidade VARCHAR(50),
    tipo_loja VARCHAR(50),
    gerente VARCHAR(150)
);

CREATE TABLE fato_vendas (
    sk_venda BIGSERIAL PRIMARY KEY,
    sk_cliente INT REFERENCES dim_cliente(sk_cliente),
    sk_produto INT REFERENCES dim_produto(sk_produto),
    sk_loja INT REFERENCES dim_loja(sk_loja),
    sk_tempo INT REFERENCES dim_tempo(sk_tempo),
    qtd_vendida INT NOT NULL,
    qtd_devolvida INT DEFAULT 0,
    qtd_liquida INT NOT NULL,
    preco_unitario NUMERIC(10, 2) NOT NULL,
    custo_unitario NUMERIC(10, 2) NOT NULL,
    receita_bruta NUMERIC(10, 2) NOT NULL,
    valor_devolvido NUMERIC(10, 2) NOT NULL,
    receita_liquida NUMERIC(10, 2) NOT NULL,
    custo_total NUMERIC(10, 2) NOT NULL,
    lucro_bruto NUMERIC(10, 2) NOT NULL
);

SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;
