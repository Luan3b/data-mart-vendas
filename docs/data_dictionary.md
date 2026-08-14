# 📖 Dicionário de Dados - Data Mart Vendas

Este documento descreve a estrutura física das tabelas, colunas, tipos de dados, nulidade e regras de negócio do Data Mart no PostgreSQL.

---

### 1. Tabela Fato

### `fato_vendas`
Armazena o histórico transacional das vendas e as métricas calculadas da operação.

|      Coluna      | Tipo de Dado| Nulo? | Descrição / Regra |
| :--- | :--- | :--- | :--- |
| `sk_venda`       | `BIGINT`  | NÃO | Surrogate Key primária (Auto-incremento) |
| `sk_cliente`     | `INTEGER` | NÃO | Foreign Key referenciando `dim_cliente(sk_cliente)`      |
| `sk_produto`     | `INTEGER` | NÃO | Foreign Key referenciando `dim_produto(sk_produto)`      |
| `sk_loja`        | `INTEGER` | NÃO | Foreign Key referenciando `dim_loja(sk_loja)|
| `sk_tempo`       | `INTEGER` | NÃO | Foreign Key referenciando `dim_tempo(sk_tempo)` |
| `qtd_vendida`    | `INTEGER` | NÃO | Quantidade bruta de itens vendidos |
| `qtd_devolvida`  | `INTEGER` | NÃO | Quantidade de itens devolvidos |
| `qtd_liquida`    | `INTEGER` | NÃO | Quantidade líquida (`qtd_vendida - qtd_devolvida`)    |
| `preco_unitario` | `NUMERIC` | NÃO | Preço unitário praticado na transação |
| `custo_unitario` | `NUMERIC` | NÃO | Custo unitário de aquisição/fabricação |
| `receita_bruta`  | `NUMERIC` | NÃO | Valor total bruto (`qtd_vendida * preco_unitario`)   |
| `valor_devolvido`| `NUMERIC` | NÃO | Valor total devolvido (`qtd_devolvida * preco_unitario`)   |
| `receita_liquida`| `NUMERIC` | NÃO | Faturamento líquido (`receita_bruta - valor_devolvido`)  |
| `custo_total`    | `NUMERIC` | NÃO | Custo total líquido (`qtd_liquida * custo_unitario`)   |
| `lucro_bruto`    | `NUMERIC` | NÃO | Resultado operacional bruto (`receita_liquida - custo_total`) |

---

### 2. Tabelas de Dimensão

### `dim_cliente`
Contexto demográfico e cadastral dos clientes.

| Coluna | Tipo de Dado | Nulo? | Descrição |
| :--- | :--- | :--- | :--- |
| `sk_cliente`     |`INTEGER`| NÃO | Surrogate Key primária da dimensão |
| `id_cliente`     |`INTEGER`| NÃO | Natural Key (identificador original do cliente) |
| `nome_cliente`   |`VARCHAR`| NÃO | Nome cadastral completo do cliente |
| `genero`         |`CHAR`   | SIM | Gênero do cliente (`M`, `F`, etc.) |
| `data_nascimento`|`DATE`   | SIM | Data de nascimento do cliente |

---

### `dim_produto`
Catálogo de produtos, categorização de mercado e custos de referência.

|      Coluna     |Tipo de Dado| Nulo? | Descrição |

| `sk_produto`    | `INTEGER` | NÃO | Surrogate Key primária da dimensão |
| `id_produto`    | `INTEGER` | NÃO | Natural Key (identificador original do produto) |
| `nome_produto`  | `VARCHAR` | NÃO | Descrição comercial do produto |
| `categoria`     | `VARCHAR` | SIM | Categoria mercadológica |
| `marca`         | `VARCHAR` | SIM | Marca / Fabricante |
| `preco_unitario`| `NUMERIC` | SIM | Preço de tabela padrão |
| `custo_unitario`| `NUMERIC` | SIM | Custo unitário padrão |

---

### `dim_loja`
Identificação das unidades físicas e associação com localizações.

|    Coluna  | Tipo de Dado | Nulo? | Descrição |

| `sk_loja`  | `INTEGER` | NÃO | Surrogate Key primária da dimensão |
| `id_loja`  | `INTEGER` | NÃO | Natural Key (identificador original da loja) |
| `nome_loja`| `VARCHAR` | SIM | Nome fantasia / identificação da loja |
| `cidade`   | `VARCHAR` | SIM | Cidade onde a loja está situada |
| `estado`   | `VARCHAR` | SIM | Estado / UF de localização da loja |

---

### `dim_localizacao`
Dimensão geográfica normalizada para agregação regional.

|      Coluna     | Tipo de Dado | Nulo? | Descrição |

| `sk_localizacao`| `INTEGER` | NÃO | Surrogate Key primária da dimensão |
| `cidade`        | `VARCHAR` | NÃO | Nome do município |
| `estado`        | `VARCHAR` | NÃO | Nome do estado por extenso |
| `sigla_estado`  | `CHAR`    | SIM | Sigla federativa do estado (UF) |
| `pais`          | `VARCHAR` | SIM | País de referência (`Brasil`) |

---

### `dim_tempo`
Dimensão de calendário para análises temporais e sazonais.

|    Coluna  | Tipo de Dado | Nulo? | Descrição |

| `sk_tempo` | `INTEGER` | NÃO | Surrogate Key no padrão numérico `YYYYMMDD` |
| `data`     | `DATE`    | NÃO | Data completa do evento |
| `ano`      | `INTEGER` | NÃO | Ano do calendário (`2022`, `2023`, `2024`) |
| `mes`      | `INTEGER` | NÃO | Mês numérico (`1` a `12`) |
| `dia`      | `INTEGER` | NÃO | Dia do mês (`1` a `31`) |
| `trimestre`| `INTEGER` | NÃO | Trimestre do ano (`1` a `4`) |