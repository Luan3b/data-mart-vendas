O pipeline foi projetado para consolidar arquivos brutos dispersos em formato CSV, aplicar transformações vetorizadas em memória utilizando Python (Pandas) e realizar a ingestão de alto desempenho no PostgreSQL via psycopg2.Plaintext┌──────────────────────┐
│  Arquivos CSV Raw    │ ── (Clientes, Produtos, Lojas, Vendas 2022-2024)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 1. EXTRACT           │ ── Consolidação e leitura dos dados transacionais
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. TRANSFORM         │ ── Sanitização, deduplicação, dimensões e cálculo de métricas
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 3. LOAD              │ ── Lookups de Surrogate Keys e Batch Insert no PostgreSQL
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 4. VALIDATION        │ ── Testes automatizados de integridade via Pytest
└──────────────────────┘
2. Etapa 1: Extração (src/extract/extract.py)A etapa de extração é responsável por ler os arquivos .csv armazenados no diretório data/raw/ e estruturá-los em DataFrames para o pipeline.Fontes de Dados:Cadastros: clientes.csv, produtos.csv, lojas.csv.Transações de Vendas: vendas_2022.csv, vendas_2023.csv, vendas_2024.csv.Lógica de Extração:Unificação dos arquivos anuais particionados de vendas em um único DataFrame consolidado (vendas_raw), somando mais de 1,14 milhão de transações.Tratamento de encodings e delimitadores padrão durante a leitura.3. Etapa 2: Transformação (src/transform/transform.py)A etapa de transformação isola 100% das regras de negócio e sanitização de dados, preparando as tabelas dimensão e fato antes de qualquer comunicação com o banco de dados.🧹 Higienização e Tratamento de TiposLimpeza de Valores Monetários: Correção de divergências de formatação em strings de preços/custos (exemplo: tratamento de inconsistências como "2278.,8" convertidas para o formato numérico 2278.8 via regex/replace).Tratamento de Datas: Conversão de formatos de texto para o tipo nativo datetime e coerção de valores inválidos.Resolução de Cabeçalhos e Linhas Nulas: Limpeza de linhas vazias/cabeçalhos deslocados e remoção de colunas sem nome (Unnamed).📦 Construção das Dimensões na Memóriadim_cliente: Deduplicação por id_cliente e padronização dos campos (nome_cliente, genero, data_nascimento).dim_produto: Deduplicação por id_produto e tipagem dos custos e preços.dim_loja: Mapeamento unificado das unidades físicas.dim_localizacao: Extração e normalização dos pares únicos de cidade e estado.dim_tempo: Geração da dimensão calendário a partir das datas das vendas, extraindo ano, mes, dia, trimestre e a chave formatada sk_tempo no padrão YYYYMMDD.💰 Engenharia de Métricas da Tabela FatoPara otimizar o consumo em ferramentas de BI e aliviar consultas no banco, as métricas analíticas são calculadas e gravadas diretamente na fato_vendas:Métrica CalculadaRegra / Fórmulaqtd_liquida$\text{qtd\_vendida} - \text{qtd\_devolvida}$receita_bruta$\text{qtd\_vendida} \times \text{preco\_unitario}$valor_devolvido$\text{qtd\_devolvida} \times \text{preco\_unitario}$receita_liquida$\text{receita\_bruta} - \text{valor\_devolvido}$custo_total$\text{qtd\_liquida} \times \text{custo\_unitario}$lucro_bruto$\text{receita\_liquida} - \text{custo\_total}$4. Etapa 3: Carga (src/load/load.py)A carga transfere os dados transformados para o PostgreSQL mantendo a integridade referencial do modelo dimensional.🔑 Mapeamento de Surrogate Keys (Lookups)Antes de inserir a tabela fato, o script consulta o banco para obter os identificadores gerados nas dimensões (id_* -> sk_*):id_cliente ➔ sk_clienteid_produto ➔ sk_produtoid_loja ➔ sk_lojadata ➔ sk_tempo (YYYYMMDD)Os IDs de negócio são substituídos pelas suas respectivas chaves substitutas inteiras (Surrogate Keys).🚀 Otimização de Ingestão em Lotes (Batch Loading)Em vez de inserções unitárias linha a linha (INSERT INTO ... VALUES (...)), a carga utiliza psycopg2.extras.execute_values.Os dados são enviados em blocos paginados (page_size=10000), reduzindo a sobrecarga de rede e I/O, permitindo carregar 1.145.961 registros em poucos segundos.🛡️ Controle Transacional (ACID)O pipeline implementa controle estrito de transação:Plaintexttry:
    Carregar dim_cliente
    Carregar dim_produto
    Carregar dim_loja
    Carregar dim_localizacao
    Carregar dim_tempo
    Carregar fato_vendas
    conexao.commit()      <-- Efetiva a gravação total
except Exception:
    conexao.rollback()    <-- Reverte tudo caso ocorra qualquer falha
finally:
    conexao.close()
5. Etapa 4: Validação de Qualidade (tests/)Ao término do carregamento, a suíte de testes automatizados valida os critérios de qualidade dos dados:Teste de Volume: Confirmação de mais de 1,1 milhão de registros na fato_vendas.Teste de Nulidade: Garantia de que nenhuma chave substituta (sk_*) contenha valores nulos.Teste de Consistência Numérica: Ausência de preços ou quantidades negativas indevidas.Teste de Integridade Referencial: Validação de ausência de registros órfãos (todas as vendas conectadas às dimensões).