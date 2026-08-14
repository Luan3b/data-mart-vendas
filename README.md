# 📊 Data Mart de Vendas

Um **Data Mart analítico** moderno e escalável construído em **Python + PostgreSQL**, consolidando dados transacionais de vendas (2022-2024) em um modelo **Star Schema** otimizado para análises de BI.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Usar](#-como-usar)
- [Estrutura de Dados](#-estrutura-de-dados)
- [Documentação Técnica](#-documentação-técnica)
- [Testes](#-testes)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

Este projeto implementa um **pipeline ETL (Extract → Transform → Load)** completo que:

✅ **Consolida** dados de 3 arquivos de vendas (2022, 2023, 2024) + cadastros  
✅ **Limpa e padroniza** informações com regras de negócio  
✅ **Carrega** em banco PostgreSQL com performance otimizada  
✅ **Valida** integridade referencial automaticamente  
✅ **Documenta** todo o processo técnico

### 📊 Dados Processados

- **1.145.961+** registros de vendas
- **6 tabelas** (1 fato + 5 dimensões)
- **15 métricas** financeiras pré-calculadas
- **3 anos** de histórico transacional

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITETURA DO DATA MART                 │
└─────────────────────────────────────────────────────────────┘

  CSV Files              Python Pipeline             PostgreSQL
  ─────────────────     ──────────────────────      ──────────────
  ├─ Clientes      →    ┌──────────────────┐   →   Star Schema
  ├─ Produtos      →    │ 1. EXTRACT       │   →   ├─ dim_cliente
  ├─ Lojas         →    ├──────────────────┤   →   ├─ dim_produto
  └─ Vendas 22-24  →    │ 2. TRANSFORM     │   →   ├─ dim_loja
                        ├──────────────────┤   →   ├─ dim_tempo
                        │ 3. LOAD          │   →   ├─ dim_localizacao
                        ├──────────────────┤   →   └─ fato_vendas
                        │ 4. VALIDATE      │   →   
                        └──────────────────┘   →   1.145.961 linhas
```

### Modelo Dimensional (Star Schema)

```
                    ┌──────────────────┐
                    │   dim_cliente    │
                    └────────┬─────────┘
                             │ sk_cliente
                             ▼
┌──────────────┐        ┌─────────────┐       ┌──────────────┐
│ dim_produto  │───────►│ fato_vendas │◄──────│  dim_loja    │
└──────────────┘        └──────┬──────┘       └──────┬───────┘
  sk_produto                   │ sk_tempo            │
                               ▼                     ▼
                       ┌──────────────┐     ┌──────────────────┐
                       │  dim_tempo   │     │ dim_localizacao  │
                       └──────────────┘     └──────────────────┘
```

---

## 📁 Estrutura do Projeto

```
data-mart-vendas/
│
├── 📄 README.md                    ← Você está aqui
├── 📄 requirements.txt             ← Dependências Python
├── 📄 .env.example                 ← Template de variáveis de ambiente
├── 📄 main.py                      ← ⭐ Orquestrador do pipeline
│
├── 📂 data/
│   ├── raw/                        ← Arquivos CSV originais
│   │   ├── Base Vendas - 2022.xlsx - 2022.csv
│   │   ├── Base Vendas - 2023.xlsx - 2023.csv
│   │   ├── Base Vendas - 2024.xlsx - 2024.csv
│   │   ├── Cadastro Clientes.xlsx - Planilha1.csv
│   │   ├── Cadastro Lojas.xlsx - Planilha1.csv
│   │   └── Cadastro Produto.xlsx - Produto.csv
│   └── processed/                  ← Dados processados (gerados)
│
├── 📂 sql/
│   ├── 01_create_database.sql      ← Criação do banco
│   ├── 02_create_tables.sql        ← Criação das tabelas
│   ├── 03_indexes.sql              ← Índices de performance
│   ├── 04_queries.sql              ← Queries analíticas (WIP)
│   └── 05_dropa.sql                ← Script de limpeza (WIP)
│
├── 📂 src/
│   ├── extract/
│   │   └── extract.py              ← Leitura de CSVs
│   ├── transform/
│   │   └── transform.py            ← Sanitização e transformação
│   ├── load/
│   │   └── load.py                 ← Carga no PostgreSQL
│   └── validation/
│       ├── validation.py           ← Validações customizadas
│       └── validation_tabela.sql   ← Validações SQL (WIP)
│
├── 📂 tests/
│   ├── test_transform.py           ← Testes unitários
│   └── test_database.py            ← Testes de integridade
│
├── 📂 docs/
│   ├── analise.md                  ← Análises esperadas (WIP)
│   ├── data_dictionary.md          ← Dicionário de dados 📖
│   ├── modelo_dimensional.md       ← Diagrama e justificativas 📐
│   ├── performance.md              ← Otimizações ⚡
│   ├── processo_etl.md             ← Fluxo ETL detalhado 📋
│   └── regras_negocio.md           ← Regras e métricas 💼
│
└── 📂 logs/
    └── etl_*.log                   ← Logs de execução (gerados)
```

---

## 🔧 Pré-requisitos

### Sistema
- **Python 3.9+** (recomendado 3.11+)
- **PostgreSQL 12+** (local ou remoto)
- **pip** ou **poetry** (gerenciador de pacotes)

### Verificar instalação

```bash
python --version                    # Python 3.9+
psql --version                      # PostgreSQL 12+
```

---

## 💻 Instalação

### 1. Clonar o repositório

```bash
git clone <repo-url>
cd data-mart-vendas
```

### 2. Criar ambiente virtual

```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verificar instalação

```bash
python -c "import pandas, psycopg2; print('✅ Dependências OK')"
```

---

## ⚙️ Configuração

### 1. Copiar template de variáveis de ambiente

```bash
cp .env.example .env
```

### 2. Editar `.env` com suas credenciais

```bash
# .env (não commitar este arquivo!)

DB_HOST=localhost           # ou seu servidor remoto
DB_PORT=5432                # porta padrão PostgreSQL
DB_NAME=datamart_vendas     # nome do banco
DB_USER=postgres            # seu usuário
DB_PASSWORD=sua_senha       # sua senha

DEBUG=false                  # true para modo verbose
ETL_MODE=full               # ou 'incremental'
```

### 3. Criar banco de dados (opcional)

Se o banco não existir, crie manualmente:

```bash
psql -U postgres -c "CREATE DATABASE datamart_vendas ENCODING UTF8;"
```

### 4. Verificar conexão

```bash
python -c "
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    print('✅ Conexão com PostgreSQL OK')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

---

## 🚀 Como Usar

### Executar o Pipeline Completo

```bash
# Modo padrão (full): reconstrói dimensões e fatos
python main.py

# Ou com modo explícito
ETL_MODE=full python main.py
```

**O que acontece:**
1. ✅ Cria tabelas no PostgreSQL (se não existirem)
2. 📂 Extrai dados dos CSVs
3. 🔄 Transforma e sanitiza
4. 💾 Carrega no banco (batch loading otimizado)
5. ✔️ Valida integridade referencial

**Tempo esperado:** ~2-5 minutos (depende do hardware)

### Validar Apenas

Se já tem dados no banco e quer apenas validar:

```bash
python main.py --validate-only
```

### Ver Logs

```bash
# Último log
tail -f logs/etl_*.log

# Buscar erros
grep "❌\|ERROR" logs/etl_*.log

# Ver estatísticas
grep "✓" logs/etl_*.log
```

### Modo Debug

Para mais detalhes durante a execução:

```bash
DEBUG=true python main.py
```

---

## 📊 Estrutura de Dados

### Tabela Fato: `fato_vendas`

Armazena transações individuais com métricas financeiras pré-calculadas:

```sql
SELECT 
    sk_venda, sk_cliente, sk_produto, sk_loja, sk_tempo,
    qtd_vendida, qtd_devolvida, qtd_liquida,
    receita_liquida, custo_total, lucro_bruto
FROM fato_vendas
LIMIT 10;
```

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `sk_venda` | BIGINT | ID único da transação (PK) |
| `sk_cliente` | INT | FK → dim_cliente |
| `sk_produto` | INT | FK → dim_produto |
| `sk_loja` | INT | FK → dim_loja |
| `sk_tempo` | INT | FK → dim_tempo (formato: YYYYMMDD) |
| `qtd_vendida` | INT | Quantidade bruta |
| `qtd_devolvida` | INT | Quantidade devolvida |
| `qtd_liquida` | INT | qtd_vendida - qtd_devolvida |
| `receita_bruta` | NUMERIC | qtd_vendida × preco_unitario |
| `receita_liquida` | NUMERIC | receita_bruta - valor_devolvido |
| `lucro_bruto` | NUMERIC | receita_liquida - custo_total |

### Tabelas Dimensão

#### `dim_cliente`
```sql
SELECT sk_cliente, id_cliente, nome_cliente, genero, data_nascimento FROM dim_cliente;
```

#### `dim_produto`
```sql
SELECT sk_produto, id_produto, nome_produto, categoria, marca, preco_unitario FROM dim_produto;
```

#### `dim_loja`
```sql
SELECT sk_loja, id_loja, nome_loja, cidade, estado FROM dim_loja;
```

#### `dim_tempo`
```sql
SELECT sk_tempo, data, ano, mes, dia, trimestre FROM dim_tempo ORDER BY data;
```

### Queries Analíticas Comuns

**Total de vendas por mês:**
```sql
SELECT 
    t.ano, t.mes, COUNT(*) as num_transacoes,
    SUM(f.receita_liquida) as receita_total,
    SUM(f.lucro_bruto) as lucro_total
FROM fato_vendas f
JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
GROUP BY t.ano, t.mes
ORDER BY t.ano DESC, t.mes DESC;
```

**Top 10 produtos por faturamento:**
```sql
SELECT 
    p.nome_produto, p.categoria,
    SUM(f.qtd_liquida) as qtd_total,
    SUM(f.receita_liquida) as receita_total
FROM fato_vendas f
JOIN dim_produto p ON f.sk_produto = p.sk_produto
GROUP BY p.sk_produto, p.nome_produto, p.categoria
ORDER BY receita_total DESC
LIMIT 10;
```

---

## 📚 Documentação Técnica

Toda a documentação técnica está em `docs/`:

| Documento | Conteúdo |
|-----------|----------|
| [data_dictionary.md](docs/data_dictionary.md) | 📖 Dicionário completo de colunas, tipos, regras |
| [modelo_dimensional.md](docs/modelo_dimensional.md) | 📐 Star Schema, justificativas, diagramas |
| [processo_etl.md](docs/processo_etl.md) | 📋 Fluxo E-T-L detalhado, transformações |
| [regras_negocio.md](docs/regras_negocio.md) | 💼 Métricas, fórmulas, regras de higienização |
| [performance.md](docs/performance.md) | ⚡ Otimizações Pandas, batch loading, índices |

---

## ✅ Testes

### Rodar testes unitários

```bash
pytest tests/test_transform.py -v
```

**O que testa:**
- Conversão de preços com formato especial (ex: "2278.,8" → 2278.8)
- Deduplicação de clientes e produtos
- Conversão de tipos de dados

### Rodar testes de banco

```bash
pytest tests/test_database.py -v
```

**O que testa:**
- Quantidade mínima de registros (>1.145.000)
- Ausência de valores nulos nas chaves estrangeiras
- Integridade referencial (não há orfãos)
- Ausência de valores negativos indevidos

### Rodar todos os testes

```bash
pytest tests/ -v --tb=short
```

---

## 🔍 Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'psycopg2'`

```bash
pip install psycopg2-binary
```

### ❌ `psycopg2.Error: password authentication failed`

Verificar credenciais em `.env`:
```bash
psql -U postgres -d datamart_vendas  # Testar manualmente
```

### ❌ `FileNotFoundError: data/raw/*.csv`

Verificar se arquivos CSV estão no caminho correto:
```bash
ls data/raw/
# Deve listar os 6 arquivos CSV
```

### ❌ Timeout na carga de dados

Se a carga é muito lenta:
1. Aumentar `page_size` em `load.py` (para mais de 5000)
2. Rodar em máquina com mais RAM
3. Usar modo `incremental` em `.env` (se implementado)

### ❌ Dados duplicados após reexecutar

O código usa `ON CONFLICT ... DO NOTHING`, então:
- 1º run: insere tudo
- 2º run: ignora duplicatas

Para resetar:
```bash
# Opção 1: Executar script de limpeza (WIP)
psql -U postgres -d datamart_vendas -f sql/05_dropa.sql

# Opção 2: Deletar manualmente
psql -U postgres -d datamart_vendas -c "DELETE FROM fato_vendas; DELETE FROM dim_*;"
```

### ❌ Encoding de caracteres estranhos

Se ver "??" nos nomes, adicionar em `.env`:
```
DB_ENCODING=UTF8
PANDAS_ENCODING=utf-8
```

---


