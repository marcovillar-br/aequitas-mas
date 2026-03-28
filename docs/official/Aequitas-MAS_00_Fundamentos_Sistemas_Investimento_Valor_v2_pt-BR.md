### 🇧🇷 Versão Oficial em Português do Brasil (pt-BR)

**Aequitas-MAS: Fundamentos e Sistemas de Investimento em Valor**
**Versão:** 2.0
**Status:** Documento Oficial de Regras de Domínio

# TEMA 1: O MOTOR QUANTITATIVO (Doutrina de Benjamin Graham e Joel Greenblatt)

A fundação do motor quantitativo baseia-se na premissa de que a inteligência artificial não deve realizar inferências matemáticas estocásticas (Regra do Confinamento de Risco). Os cálculos devem ser estritamente determinísticos, executados via código, extraindo o Valor Justo e a Qualidade Sistêmica dos ativos.

### Fórmulas Matemáticas Exatas

**1. Valor Intrínseco (Fórmula de Graham Adaptada)**
Utilizada para calcular o valor real do negócio desconsiderando a cotação volátil do Senhor Mercado.

$$V_{Justo} = \sqrt{22.5 \times VPA \times LPA}$$

*Onde: A constante $22.5$ é o produto do limite máximo tolerado por Graham para o Índice Preço/Lucro (15) e o Índice Preço/Valor Patrimonial (1.5). $VPA$ é o Valor Patrimonial por Ação e $LPA$ é o Lucro por Ação.*

**2. Margem de Segurança (Graham)**
Diferença percentual mandatória entre o Valor Intrínseco calculado e o Preço de Mercado.

$$Margem\_de\_Seguranca = \left( \frac{V_{Justo} - Preco_{Mercado}}{V_{Justo}} \right) \times 100$$

**3. Retorno sobre o Capital Empregado - ROIC (Greenblatt)**
Métrica primária de Qualidade (Ganho), atuando como um *proxy* matemático para o Fosso Econômico (*Moat*).

$$ROIC = \frac{EBIT}{\text{Ativo Total} - \text{Passivo Circulante}}$$

**4. Retorno de Ganhos - Earnings Yield / EY (Greenblatt)**
Métrica primária de Preço (Valor), avaliando o custo da empresa livre de distorções de estrutura de capital.

$$EY = \frac{EBIT}{EV}$$

$$EV (\text{Enterprise Value}) = \text{Capitalização de Mercado} + \text{Dívida Líquida}$$

### Critérios Fundamentalistas Adaptados para B3 (Horizonte de 5 Anos)

A aplicação direta dos filtros originais de Graham (10 anos de lucros, 20 anos
de dividendos) demonstrou-se excessivamente restritiva para o mercado acionário
brasileiro. Conforme validado empiricamente por Testa & Lima (2012), a redução
do horizonte para 5 anos adapta os critérios à realidade de mercados emergentes
(ciclos mais curtos, inflação estrutural, volatilidade da Selic) sem comprometer
a integridade do *Value Investing*.

| Indicador Fundamentalista | Regra Original (Graham) | Critério Adaptado (B3 / 5 Anos) | Justificativa |
| --- | --- | --- | --- |
| **Histórico de Lucratividade** | 10 anos sem prejuízos | **5 anos** contínuos sem prejuízos | Adequação aos ciclos econômicos mais curtos de mercados emergentes. |
| **Pagamento de Dividendos** | 20 anos ininterruptos | Pagamento contínuo nos últimos **5 anos** | Previne exclusão de empresas que retiveram lucros para expansão recente. |
| **Crescimento de Lucros** | Mínimo de 33% em 10 anos | Aumento de **15% a 30% em 5 anos** | Ajuste proporcional ao horizonte reduzido, capturando tração de crescimento atual. |
| **Liquidez Corrente** | ≥ 2.0 | ≥ 2.0 (ou mediana setorial ≥ 1.5) | Preserva solvência sem penalizar eficiência do capital de giro brasileiro. |
| **Tamanho da Empresa** | Receita ≥ US$ 100M | Receita ≥ R$ 300M | Filtro de liquidez que exclui *micro-caps* com baixa governança. |
| **Múltiplos de Preço** | P/L × P/VP ≤ 22.5 | P/L × P/VP ≤ 22.5 (mantido) | Núcleo da Margem de Segurança — invariante. |

### Filtros de Segurança Intransponíveis

| Filtro de Segurança | Regra de Negócio (Contrato Lógico) | Fonte Base |
| --- | --- | --- |
| **Múltiplos de Graham** | O produto de $P/L \times P/VP$ não deve ultrapassar **22.5**. | *Fundamentação Teórica - Graham* |
| **Gatilho de Rejeição (Lucro)** | Se $LPA \le 0$ ou $VPA \le 0$, o Valor Intrínseco retorna $0.0$. Compra bloqueada. | *QA Log - Código Graham* |
| **Ranking Mágico** | Classificar os ativos separadamente por $ROIC$ (decrescente) e $EY$ (decrescente). Somar as posições. Selecionar o Top *X* do ranking final. | *Fórmula Mágica - Greenblatt* |
| **Confiabilidade Numérica (Degradação Controlada)** | Exigência de tipagem explícita `Optional[float] = None` no *schema* Pydantic se o dado oficial não existir. É matematicamente proibido gerar aproximações estocásticas, evitando a quebra da Máquina de Estados. | *Arquitetura LangGraph - Aequitas Core* |
| **Diversificação Mínima** | A estratégia Greenblatt exige a compra de uma cesta de 20 a 30 ações de alta pontuação estatística para mitigação de risco de *mispricing*. | *Fundamentação Teórica - Greenblatt* |

---

# TEMA 2: A AVALIAÇÃO MICRO-QUALITATIVA (Doutrina de Philip Fisher)

A avaliação de Philip Fisher busca um *alpha* lento e estrutural, focando estritamente na Qualidade Corporativa (*Micro-Quality*) e no Crescimento Sustentável.

### Sistematização do Método *Scuttlebutt*

O *Scuttlebutt* é a metodologia de investigação qualitativa que busca ir além dos balanços oficiais. No MAS, isso é traduzido pelo uso de processamento de linguagem natural (NLP/RAG) sobre PDFs de Relações com Investidores (RI), Formulários de Referência da CVM, Transcrições de *Earnings Calls* e Notícias.

### Checklist Atômico de Qualidade e Crescimento Sustentável

| Passo | Critério de Avaliação (Fisher) | Indicador Qualitativo Buscado no Texto |
| --- | --- | --- |
| **1** | **Eficácia de P&D** | Evidências de inovação tecnológica, lançamentos de novos produtos ou liderança técnica. O crescimento de receitas não pode depender apenas de aumentos de preço. |
| **2** | **Profundidade da Gestão** | A diretoria possui plano de sucessão? A gestão é ética, racional e foca no aumento do valor intrínseco de longo prazo para os acionistas minoritários?. |
| **3** | **Crescimento Sustentável** | Identificação de vantagens competitivas duradouras (*Moats*). A empresa possui mercado endereçável para aumentar vendas por múltiplos anos?. |
| **4** | **Relações de Pessoal** | A empresa é tida como um bom lugar para se trabalhar? (Atua como proxy para moral corporativa e rentabilidade futura). |
| **5** | **Integração de Sentimento** | Avaliação do tom e da confiança dos executivos durante a sessão de perguntas e respostas (Q&A) das *Earnings Calls*. |

---

# TEMA 3: A AVALIAÇÃO MACROECONÔMICA (Sinais Holísticos e Contexto de Mercado)

Para evitar a miopia corporativa, o sistema exige uma avaliação holística do ambiente económico que cerca os ativos. Este módulo atua de forma independente para preservar a coesão do Agente Fisher.

### Metodologia de Ingestão de Dados Macro

* **Fontes de Inteligência:** Ingestão periódica de relatórios do FED (Federal Reserve), atas do COPOM (Banco Central do Brasil) e indicadores inflacionários (IPCA, CPI).
* **Mecanismo de Processamento:** Utilização de Geração Aumentada por Recuperação baseada em *Hypothetical Dense Embeddings* (HyDE) e *Semantic Chunking* para avaliar os ciclos de taxas de juros e a saúde do crédito, elementos que impactam diretamente a taxa de desconto aplicada ao *Valuation* dos ativos.

---

# TEMA 4: AUDITORIA DE RISCO E PSICOLOGIA (Doutrina de Howard Marks)

O Risco, sob a ótica desta doutrina, não é a volatilidade estatística ($Beta$), mas sim a **probabilidade de perda permanente de capital**. A principal fonte desse risco é comportamental: pagar um preço excessivo devido à ganância.

### Matriz de Cenários de Rejeição e Ação (*Timing* Contracíclico)

| Cenário de Mercado (Estado do Pêndulo) | Análise de Múltiplos (Graham/Greenblatt) | Decisão Obrigatória (Regra de Negócio) | Justificativa do Auditor |
| --- | --- | --- | --- |
| **Euforia Extrema (Ganância)** | Empresa apresenta ótimo ROIC, mas $V_{Justo}$ está muito abaixo do Preço de Mercado. | **REJEITAR / VENDER** | O risco de *mispricing* é máximo. Pagar caro por um ativo de qualidade aniquila a assimetria positiva. |
| **Pânico Extremo (Medo)** | Preços em queda livre, $V_{Justo}$ amplamente superior ao Preço de Mercado. | **COMPRAR (Agressividade Máxima)** | A distorção psicológica criou uma *Margem de Segurança* massiva. Assimetria positiva ótima (alto upside, baixo downside). |
| **Consenso Otimista (Primeiro Nível)** | Ação popular nas notícias; ROIC médio; Múltiplos esticados. | **REJEITAR** | Armadilha de valor de curto prazo. Falta de *Moat* sustentável e ausência de margem de erro. |

---

# TEMA 5: ASSIMETRIA INFORMACIONAL E COMPORTAMENTO DE MANADA

### Regras Teóricas para Mitigação em Sistemas de IA

**1. Desconto do Viés de Notícias (Moderação de Sentimento)**
O agente não deve basear recomendações exclusivamente em feeds de notícias diárias, que possuem baixo SNR (*Signal-to-Noise Ratio*). O sentimento proveniente de notícias deve ser obrigatoriamente cruzado com a análise das seções de risco de arquivamentos oficiais.

**2. Controle de Obsolescência e Validação de Fonte**
Aplicação de indexação RAG com *timestamp* obrigatório. A IA deve retornar a URL ou ID do documento fonte associado à afirmação. Se a informação não estiver na base de conhecimento oficial, a saída mandatória é `"Não sei" / Null`.

**3. Proteção Contra Oscilações Irracionais — Triple Barrier (AlphaX 2025)**
Implementação do método de "Tripla Barreira" (*Triple Barrier*) inspirado no
framework AlphaX, adaptado para o comitê iterativo do Aequitas-MAS:

* **Barreira Superior (Take Profit Analítico):** Ativada quando a projeção de
  preços converge consistentemente acima do Valor Justo de Graham. O comitê
  formaliza exigência de desinvestimento, capturando o prêmio de assimetria.
* **Barreira Inferior (Stop Loss de Fundamentos):** Ativada não apenas por
  declínio percentual de preço, mas pela deterioração dinâmica do Altman
  Z-Score e/ou queda do Piotroski F-Score, forçando preservação de capital
  antes da materialização de insolvência.
* **Barreira Vertical (Janela Temporal):** Horizonte absoluto de retenção da
  tese — forçando reavaliação ao término do trimestre contábil ou na
  divulgação de novo Formulário de Referência pela CVM. Garante que o
  sistema opere com fundamentos atualizados na janela de 5 anos.
