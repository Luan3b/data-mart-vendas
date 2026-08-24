# 📖 Dicionário de Dados - Data Mart Vendas

Este documento descreve a estrutura física das tabelas, colunas, tipos de dados, nulidade e regras de negócio do Data Mart no PostgreSQL.

---

# Dicionário de Dados - Data Mart Vendas

Este documento descreve a estrutura física das tabelas do Data Mart no PostgreSQL, incluindo colunas, tipos de dados, nulidade, chaves e regras de negócio.

## 1. Tabela Fato

### `fato_vendas`

Armazena uma linha para cada registro de venda carregado dos arquivos de origem e suas métricas calculadas.

| Coluna | Tipo de dado | Nulo? | Chave / descrição |
| :--- | :--- | :--- | :--- |
| `sk_venda` | `BIGSERIAL` (`BIGINT`) | NÃO | Chave primária substituta, gerada automaticamente pelo PostgreSQL. |
| `sk_cliente` | `INTEGER` | NÃO | Chave estrangeira para `dim_cliente(sk_cliente)`. |
| `sk_produto` | `INTEGER` | NÃO | Chave estrangeira para `dim_produto(sk_produto)`. |
| `sk_loja` | `INTEGER` | NÃO | Chave estrangeira para `dim_loja(sk_loja)`. |
| `sk_tempo` | `INTEGER` | NÃO | Chave estrangeira para `dim_tempo(sk_tempo)`, no formato `YYYYMMDD`. |
| `qtd_vendida` | `INTEGER` | NÃO | Quantidade bruta de itens vendidos. |
| `qtd_devolvida` | `INTEGER` | NÃO | Quantidade de itens devolvidos; padrão `0` no banco. |
| `qtd_liquida` | `INTEGER` | NÃO | Quantidade líquida: `qtd_vendida - qtd_devolvida`. |
| `preco_unitario` | `NUMERIC(15,2)` | NÃO | Preço unitário praticado na venda. |
| `custo_unitario` | `NUMERIC(15,2)` | NÃO | Custo unitário associado ao produto. |
| `receita_bruta` | `NUMERIC(15,2)` | NÃO | `qtd_vendida * preco_unitario`. |
| `valor_devolvido` | `NUMERIC(15,2)` | NÃO | `qtd_devolvida * preco_unitario`. |
| `receita_liquida` | `NUMERIC(15,2)` | NÃO | `receita_bruta - valor_devolvido`. |
| `custo_total` | `NUMERIC(15,2)` | NÃO | `qtd_liquida * custo_unitario`. |
| `lucro_bruto` | `NUMERIC(15,2)` | NÃO | `receita_liquida - custo_total`. |

## 2. Tabelas de Dimensão

### `dim_cliente`

Dimensão cadastral de clientes com histórico de alterações no padrão SCD Tipo 2.

| Coluna | Tipo de dado | Nulo? | Chave / descrição |
| :--- | :--- | :--- | :--- |
| `sk_cliente` | `SERIAL` (`INTEGER`) | NÃO | Chave primária substituta, gerada automaticamente. |
| `id_cliente` | `INTEGER` | NÃO | Chave natural do cadastro de origem. |
| `nome_cliente` | `VARCHAR(150)` | NÃO | Nome cadastral completo. |
| `genero` | `VARCHAR(20)` | SIM | Gênero padronizado, como `Masculino` ou `Feminino`. |
| `data_nascimento` | `DATE` | SIM | Data de nascimento convertida para data. |
| `data_inicio` | `DATE` | NÃO | Início da vigência da versão cadastral. |
| `data_fim` | `DATE` | SIM | Fim da vigência; fica nulo na versão atual. |
| `is_current` | `BOOLEAN` | NÃO | Indica se a versão é a atual; padrão `TRUE`. |
| `versao` | `INTEGER` | NÃO | Número da versão cadastral; padrão `1`. |

Existe um índice único parcial para garantir apenas uma versão atual por `id_cliente`.

### `dim_produto`

Catálogo de produtos, categorias, marcas e valores de referência.

| Coluna | Tipo de dado | Nulo? | Chave / descrição |
| :--- | :--- | :--- | :--- |
| `sk_produto` | `SERIAL` (`INTEGER`) | NÃO | Chave primária substituta. |
| `id_produto` | `INTEGER` | NÃO | Chave natural do cadastro de origem; possui restrição `UNIQUE`. |
| `nome_produto` | `VARCHAR(150)` | NÃO | Descrição comercial do produto. |
| `categoria` | `VARCHAR(100)` | SIM | Categoria mercadológica. |
| `marca` | `VARCHAR(100)` | SIM | Marca ou fabricante. |
| `preco_unitario` | `NUMERIC(15,2)` | SIM | Preço de tabela padrão. |
| `custo_unitario` | `NUMERIC(15,2)` | SIM | Custo unitário padrão. |

### `dim_loja`

Dimensão das unidades físicas e sua localização.

| Coluna | Tipo de dado | Nulo? | Chave / descrição |
| :--- | :--- | :--- | :--- |
| `sk_loja` | `SERIAL` (`INTEGER`) | NÃO | Chave primária substituta. |
| `id_loja` | `INTEGER` | NÃO | Chave natural do cadastro de origem; possui restrição `UNIQUE`. |
| `nome_loja` | `VARCHAR(150)` | SIM | Nome ou identificação da loja. |
| `cidade` | `VARCHAR(100)` | SIM | Cidade da loja. |
| `estado` | `VARCHAR(100)` | SIM | Estado ou UF da loja. |
| `pais` | `VARCHAR(100)` | SIM | País da loja; preenchido na transformação quando ausente. |

### `dim_tempo`

Dimensão de calendário derivada das datas de venda para análises temporais e sazonais.

| Coluna | Tipo de dado | Nulo? | Chave / descrição |
| :--- | :--- | :--- | :--- |
| `sk_tempo` | `INTEGER` | NÃO | Chave primária no formato numérico `YYYYMMDD`. |
| `data` | `DATE` | NÃO | Data completa da venda; possui restrição `UNIQUE`. |
| `ano` | `INTEGER` | NÃO | Ano do calendário. |
| `mes` | `INTEGER` | NÃO | Mês numérico de `1` a `12`. |
| `dia` | `INTEGER` | NÃO | Dia do mês de `1` a `31`. |
| `trimestre` | `INTEGER` | NÃO | Trimestre do ano de `1` a `4`. |
| `nome_dia_semana` | `VARCHAR(20)` | NÃO | Nome do dia da semana. |
| `nome_mes` | `VARCHAR(20)` | NÃO | Nome do mês. |
| `semestre` | `VARCHAR(20)` | NÃO | Primeiro ou segundo semestre. |
| `nome_trimestre` | `VARCHAR(20)` | NÃO | Nome do trimestre. |

## 3. Relacionamentos

- `fato_vendas.sk_cliente` referencia `dim_cliente.sk_cliente`.
- `fato_vendas.sk_produto` referencia `dim_produto.sk_produto`.
- `fato_vendas.sk_loja` referencia `dim_loja.sk_loja`.
- `fato_vendas.sk_tempo` referencia `dim_tempo.sk_tempo`.

O modelo atual não possui uma tabela `dim_localizacao`; cidade, estado e país permanecem como atributos de `dim_loja`.