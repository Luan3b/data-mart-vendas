# Documentação do Processo ETL (Extract, Transform, Load)

Este documento detalha o funcionamento, as regras de negócio, os fluxos de tratamento e a estratégia de carregamento do pipeline de dados do **Data Mart de Vendas**.

---

## 1. Visão Geral do Fluxo

O pipeline foi projetado para consolidar arquivos brutos dispersos em formato CSV, aplicar transformações vetorizadas em memória utilizando **Python (Pandas)** e realizar a ingestão de alto desempenho no **PostgreSQL** via **psycopg2**.

```
┌──────────────────────┐
│  Arquivos CSV Raw    │ ── Clientes, Produtos, Lojas, Vendas 2022-2024
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 1. EXTRACT           │ ── Consolidação e leitura dos dados transacionais
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. TRANSFORM         │ ── Sanitização, deduplicação, dimensões e métricas
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 3. LOAD              │ ── Lookups de Surrogate Keys e Batch Insert
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 4. VALIDATION        │ ── Testes automatizados via Pytest
└──────────────────────┘
```

---

## 2. Etapa 1: Extração

**Arquivo:** `src/extract/extract.py`

A etapa de extração é responsável por ler os arquivos `.csv` armazenados no diretório `data/raw/` e estruturá-los em DataFrames para o pipeline.

### Fontes de Dados

**Cadastros:**

- `Cadastro Clientes.xlsx - Planilha1.csv`
- `Cadastro Produto.xlsx - Produto.csv`
- `Cadastro Lojas.xlsx - Planilha1.csv`

**Transações de vendas:**

- `Base Vendas - 2022.xlsx - 2022.csv`
- `Base Vendas - 2023.xlsx - 2023.csv`
- `Base Vendas - 2024.xlsx - 2024.csv`

### Lógica de Extração

- Unificação dos arquivos de 2022, 2023 e 2024 em um único DataFrame consolidado: `vendas_raw`.
- Tratamento de encodings e delimitadores padrão durante a leitura.

---

## 3. Etapa 2: Transformação

**Arquivo:** `src/transform/transform.py`

A etapa de transformação isola as regras de negócio, preparando as tabelas dimensão e fato antes de qualquer comunicação com o banco de dados.

### 3.1 Tratamento de Tipos e Dados

#### Limpeza de Valores Monetários

Correção de divergências de formatação em strings de preços e custos.

Exemplo:

```
"2278.,8" → 2278.8
```

O tratamento é realizado utilizando operações de `regex`/`replace`.

#### Tratamento de Datas

- Conversão de valores de texto para o tipo nativo `datetime`.
- Coerção de valores inválidos.

#### Resolução de Cabeçalhos e Linhas Nulas

- Limpeza de linhas vazias.
- Correção de cabeçalhos deslocados.
- Remoção de colunas sem nome (`Unnamed`).

### 3.2 Construção das Dimensões em Memória

| Dimensão | Tratamento |
|---|---|
| `dim_cliente` | Deduplicação por `id_cliente` e padronização de `nome_cliente`, `genero` e `data_nascimento`. |
| `dim_produto` | Deduplicação por `id_produto` e tipagem de custos e preços. |
| `dim_loja` | Mapeamento unificado das unidades físicas. |
| `dim_tempo` | Geração da dimensão calendário a partir das datas das vendas. |

A `dim_tempo` extrai:

- ano;
- mês;
- dia;
- trimestre;
- `sk_tempo` no padrão `YYYYMMDD`.

### 3.3 Engenharia de Métricas da Tabela Fato

Para otimizar o consumo em ferramentas de BI e reduzir a necessidade de cálculos no banco, as métricas analíticas são calculadas diretamente na `fato_vendas`.

| Métrica | Regra / Fórmula |
|---|---|
| `qtd_liquida` | `qtd_vendida - qtd_devolvida` |
| `receita_bruta` | `qtd_vendida * preco_unitario` |
| `valor_devolvido` | `qtd_devolvida * preco_unitario` |
| `receita_liquida` | `receita_bruta - valor_devolvido` |
| `custo_total` | `qtd_liquida * custo_unitario` |
| `lucro_bruto` | `receita_liquida - custo_total` |

---

## 4. Etapa 3: Carga

**Arquivo:** `src/load/load.py`

A etapa de carga transfere os dados transformados para o PostgreSQL, mantendo a integridade referencial do modelo dimensional.

### 4.1 Mapeamento de Surrogate Keys

Antes da inserção da tabela fato, o script consulta o banco para obter os identificadores gerados nas dimensões.

| ID de negócio | Surrogate Key |
|---|---|
| `id_cliente` | `sk_cliente` |
| `id_produto` | `sk_produto` |
| `id_loja` | `sk_loja` |
| `data` | `sk_tempo` (`YYYYMMDD`) |

Os IDs de negócio são substituídos pelas respectivas chaves substitutas inteiras. A data da venda é convertida para `sk_tempo` no padrão `YYYYMMDD`.

### 4.2 Otimização de Ingestão em Lotes

Em vez de realizar inserções unitárias (`INSERT INTO ... VALUES (...)`), a carga utiliza:

```
psycopg2.extras.execute_values
```

Os dados são enviados em blocos paginados com:

```
page_size = 10000
```

Essa estratégia reduz a sobrecarga de rede e I/O, permitindo carregar aproximadamente **1.145.961 registros** em poucos segundos.

### 4.3 Controle Transacional (ACID)

O pipeline implementa controle estrito de transação:

```python
try:
    carregar_dim_cliente()
    carregar_dim_produto()
    carregar_dim_loja()
    carregar_dim_localizacao()
    carregar_dim_tempo()
    carregar_fato_vendas()

    conexao.commit()  # Efetiva a gravação total

except Exception:
    conexao.rollback()  # Reverte tudo caso ocorra qualquer falha

finally:
    conexao.close()
```

---

## 5. Etapa 4: Validação de Qualidade

**Diretório:** `tests/`

Ao término do carregamento, a suíte de testes automatizados valida os principais critérios de qualidade dos dados.

### Testes Realizados

- **Teste de Volume:** confirmação do volume mínimo definido no teste de banco.
- **Teste de Nulidade:** garantia de que nenhuma chave substituta (`sk_*`) contenha valores nulos.
- **Teste de Consistência Numérica:** ausência de preços ou quantidades negativas indevidas.
- **Teste de Integridade Referencial:** validação da ausência de registros órfãos, garantindo que todas as vendas estejam conectadas às dimensões.

---

## 6. Resumo do Pipeline

```
EXTRACT
   │
   ├── Lê arquivos CSV
   └── Consolida vendas 2022-2024
   │
   ▼
TRANSFORM
   │
   ├── Limpa e padroniza dados
   ├── Cria dimensões
   └── Calcula métricas da fato
   │
   ▼
LOAD
   │
   ├── Resolve Surrogate Keys
   ├── Executa Batch Insert
   └── Controla transação ACID
   │
   ▼
VALIDATION
   │
   ├── Consistência numérica
   └── Integridade referencial
```

---

## Estrutura Relacionada do Projeto

```
data/
└── raw/
    ├── Cadastro Clientes.xlsx - Planilha1.csv
    ├── Cadastro Produto.xlsx - Produto.csv
    ├── Cadastro Lojas.xlsx - Planilha1.csv
    ├── Base Vendas - 2022.xlsx - 2022.csv
    ├── Base Vendas - 2023.xlsx - 2023.csv
    └── Base Vendas - 2024.xlsx - 2024.csv

src/
├── extract/
│   └── extract.py
├── transform/
│   └── transform.py
└── load/
    └── load.py

tests/
├── test_transform.py
└── test_database.py

docs/
└── processo_etl.md
```