# Glossário dos Índices

Descrição detalhada de cada índice coletado pela API. Para uso e endpoints, veja o [README](README.md).

---

## Inflação e preços

### INCC-M — Índice Nacional de Custo da Construção (Mensal)
Mede a variação dos custos de construção civil no Brasil. Composto por mão de obra e materiais de construção. Calculado pela FGV.

**Aplicação:** Reajuste de contratos de obras e incorporações imobiliárias. Em compras de imóvel na planta, o saldo devedor é corrigido mensalmente pelo INCC-M até a entrega das chaves.

### IGP-M — Índice Geral de Preços do Mercado
Média ponderada de três sub-índices: IPA-M (60%, preços no atacado), IPC-M (30%, preços ao consumidor) e INCC-M (10%, custo da construção). Calculado pela FGV.

**Aplicação:** Reajuste de aluguéis residenciais e comerciais, tarifas de energia elétrica e contratos de longo prazo.

### IGP-DI — Índice Geral de Preços — Disponibilidade Interna
Mesma metodologia do IGP-M, mas com coleta em período diferente (dia 1 ao dia 30 do mês). Reflete o preço dentro do mercado doméstico. Calculado pela FGV.

**Aplicação:** Correção de contratos de obras públicas de infraestrutura, debêntures e financiamentos do BNDES.

### IPCA — Índice Nacional de Preços ao Consumidor Amplo
Inflação oficial do Brasil. Mede a variação de preços de uma cesta de bens e serviços consumidos por famílias com renda de 1 a 40 salários mínimos. Calculado pelo IBGE.

**Aplicação:** Meta de inflação do Banco Central, correção do Tesouro IPCA+ (NTN-B), reajuste de planos de saúde.

### IPCA-15
Prévia do IPCA com coleta entre a segunda metade do mês anterior e a primeira metade do mês de referência. Calculado pelo IBGE.

**Aplicação:** Indicador antecedente da inflação oficial. Usado para ajustar expectativas de mercado antes da divulgação do IPCA cheio.

### IPCA Acumulado 12M
IPCA acumulado nos últimos 12 meses. Publicado pelo BACEN (SGS 13522).

**Aplicação:** Referência para metas de inflação, análise macroeconômica e deflação de taxas nominais para calcular juros reais.

### INPC — Índice Nacional de Preços ao Consumidor
Similar ao IPCA, mas focado em famílias de menor renda (1 a 5 salários mínimos). Calculado pelo IBGE.

**Aplicação:** Reajuste do salário mínimo, benefícios previdenciários e dissídios coletivos.

### SINAPI — Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil
Pesquisa mensal do IBGE/CEF com preços de insumos e mão de obra na construção civil, por estado.

**Aplicação:** Referência obrigatória para orçamentos de obras financiadas com recursos públicos federais.

### ANP Diesel — Preço médio do Diesel
Levantamento semanal da ANP com o preço médio de revenda do diesel ao consumidor.

**Aplicação:** Reajuste de contratos de transporte, BDI em orçamentos de engenharia e composição de custos rodoviários.

---

## Taxas de juros

### Selic — Taxa do Sistema Especial de Liquidação e Custódia
Taxa básica de juros da economia brasileira. Valor acumulado no mês, publicado diariamente pelo BACEN (SGS 11).

**Aplicação:** Referência para toda a cadeia de crédito, correção de dívidas tributárias e rendimento do Tesouro Selic.

### Selic Meta
Taxa-alvo definida pelo COPOM a cada 45 dias. Publicada pelo BACEN (SGS 432).

**Aplicação:** Sinaliza a direção da política monetária. Impacta custo de financiamento, viabilidade de empreendimentos e valuation de empresas.

### CDI — Certificado de Depósito Interbancário
Taxa de juros das operações de crédito entre bancos. Praticamente igual à Selic. Publicada pelo BACEN (SGS 4391).

**Aplicação:** Benchmark do mercado financeiro. Rentabilidade de CDBs, fundos de renda fixa, LCIs e debêntures.

### Juros Real
CDI acumulado em 12 meses deflacionado pelo IPCA do período. Indicador calculado pela API.

**Aplicação:** Custo de oportunidade real do capital. Referência para taxas mínimas de atratividade (TMA) em empreendimentos imobiliários. Quanto maior o juro real, maior a exigência de retorno para investir em imóveis.

### TR — Taxa Referencial
Taxa calculada a partir da remuneração dos CDBs. Publicada pelo BACEN (SGS 226).

**Aplicação:** Base de correção de financiamentos imobiliários (modalidade TR+), FGTS e caderneta de poupança.

### TJLP — Taxa de Juros de Longo Prazo
Taxa de juros de referência para empréstimos de longo prazo. Publicada pelo BACEN (SGS 7811).

**Aplicação:** Financiamentos do BNDES e operações de crédito de longo prazo.

### Poupança (rendimento)
Rendimento mensal da caderneta de poupança. Publicado pelo BACEN (SGS 433).

**Aplicação:** Referência de rendimento conservador e base para cálculo de custo de captação SBPE.

### Taxa de Financiamento Imobiliário PF
Taxa média de juros dos financiamentos imobiliários concedidos a pessoas físicas. Publicada pelo BACEN (SGS 25497).

**Aplicação:** Referência para análise de viabilidade de empreendimentos e custo de aquisição de imóveis pelo comprador final.

---

## Câmbio

### PTAX USD — Taxa de Câmbio Dólar
Média das cotações do dólar apuradas pelo Banco Central no mercado interbancário. Publicada pelo BACEN (SGS 3696).

**Aplicação:** Contratos de câmbio, precificação de importações, correção de dívidas em moeda estrangeira.

---

## Financiamento imobiliário (SBPE)

### SBPE contratações valor
Volume em R$ das operações contratadas com recursos da poupança SBPE. Publicado pelo BACEN (SGS 20631).

**Aplicação:** Indicador de atividade do mercado de crédito imobiliário. Acompanha o ciclo de aquecimento/desaquecimento do setor.

### SBPE contratações unidades
Número de unidades financiadas com recursos da poupança SBPE. Publicado pelo BACEN (SGS 20632).

**Aplicação:** Volume de operações imobiliárias financiadas. Complementa o indicador de valor para avaliar ticket médio.

### SBPE saldo poupança
Saldo total da caderneta de poupança SBPE em R$ bilhões. Publicado pelo BACEN (SGS 7481). Possui defasagem de ~6-9 meses.

**Aplicação:** Indica a disponibilidade de funding para financiamento imobiliário. Quedas no saldo sinalizam restrição de crédito no setor.

---

## Renda fixa e curva de juros

### NTN-B 2035 — taxa indicativa
Taxa real de juros do título público NTN-B com vencimento em 15/05/2035. Extraída da curva ETTJ IPCA da ANBIMA (endpoint CZ-down.asp, público).

**Aplicação:** Referência de custo de oportunidade para investimentos imobiliários de longo prazo. Correlação inversa com o IFIX.

### ETTJ IPCA 5 anos
Taxa real da Estrutura a Termo de Taxas de Juros no vértice de 5 anos. Fonte: ANBIMA.

**Aplicação:** Referência para TMA de incorporações para venda (ciclo ~5 anos).

### ETTJ IPCA 10 anos
Taxa real da ETTJ no vértice de 10 anos. Fonte: ANBIMA.

**Aplicação:** Referência para TMA de empreendimentos de base imobiliária (renda, ciclo 10+ anos).

---

## Mercado de capitais

### IFIX — Índice de Fundos de Investimento Imobiliário
Carteira teórica de FIIs da B3. Mede o desempenho médio dos fundos imobiliários negociados em bolsa.

**Aplicação:** Benchmark para investidores em FIIs, análise de retorno do mercado imobiliário listado.

### IBOVESPA — Índice Bovespa
Principal índice do mercado de ações brasileiro. Composto pelas ações mais negociadas na B3.

**Aplicação:** Benchmark para renda variável, análise de custo de oportunidade para empreendimentos imobiliários.

### IMOB — Índice Imobiliário B3
Performance das empresas do setor imobiliário listadas em bolsa (incorporadoras, construtoras, shoppings).

**Aplicação:** Monitoramento do desempenho do setor imobiliário no mercado de capitais.

### SMLL — Índice Small Cap B3
Performance das empresas de menor capitalização na B3.

**Aplicação:** Acompanhamento de empresas menores do setor, incluindo incorporadoras regionais.

### IDIV — Índice Dividendos B3
Ações com maior dividend yield na B3.

**Aplicação:** Referência para investidores focados em renda, comparação com yield de FIIs e aluguéis.

### IFNC — Índice Financeiro B3
Performance do setor financeiro listado (bancos, seguradoras, B3).

**Aplicação:** Indicador de saúde do sistema financeiro, que impacta diretamente a oferta de crédito imobiliário.

---

## Atividade econômica

### PIB Trimestral
Taxa de variação do PIB a preços de mercado em relação ao mesmo período do ano anterior. Fonte: IBGE SIDRA (agregado 5932). RowKey usa o último mês do trimestre (Q1=03, Q2=06, Q3=09, Q4=12). Publicado com ~2 meses de defasagem.

**Aplicação:** Indicador macroeconômico de crescimento. Referência para análise de viabilidade e projeção de demanda imobiliária.

### Insumos Construção Civil
Índice de produção física dos insumos típicos da construção civil (IBGE PIM-PF, tabela 8886, base 2022=100). Proxy para dados do SNIC (cimento), que não possui API pública.

**Aplicação:** Acompanhamento da atividade da construção civil via consumo de insumos.

### Metalurgia
Índice de produção física da metalurgia (IBGE PIM-PF, tabela 8888, classificação 544[129333], base 2022=100). Proxy para dados do Instituto Aço Brasil (aço longo), que não possui API pública.

**Aplicação:** Acompanhamento do consumo de aço no setor de construção civil.

---

## Internacional

### SOFR — Secured Overnight Financing Rate
Taxa de juros overnight garantida, publicada pelo Federal Reserve Bank of New York.

**Aplicação:** Referência internacional para operações em dólar, substituto da LIBOR. Usado em análises de custo de captação internacional e comparação de juros reais entre países.
