### 🇧🇷 Versão Oficial em Português do Brasil (pt-BR)

**Aequitas-MAS: Documento Mestre de Arquitetura e Especificação**
**Versão:** 3.0 (Consolidada - SOTA 2026, Triple Barrier, Horizonte 5 Anos)
**Status:** Documento Normativo Único para Orquestração de LLMs

**1. FILOSOFIA DE OPERAÇÃO E IDENTIDADE**

* **Propósito do Sistema:** O Aequitas-MAS é um Sistema de Suporte à Decisão (DSS) focado no mercado financeiro brasileiro (B3). Distanciando-se de *chatbots* de uso geral, a arquitetura foi concebida para emular o "Sistema 2" de raciocínio humano descrito por Kahneman — um processamento analítico, lento e deliberativo focado em *Value Investing*.
* **Dogma do Confinamento de Risco (Risk Confinement):** A arquitetura abandona a premissa ingênua de "alucinação zero" para adotar o Confinamento de Risco. Parte-se do pressuposto arquitetural de que Modelos de Linguagem de Grande Escala (LLMs) possuem altíssima capacidade de inferência semântica, mas são inerentemente falhos (papagaios estocásticos) e estatisticamente propensos à alucinação quando submetidos a cálculos matemáticos rigorosos.
* **Estratégia de Mitigação de Alucinação (Hibridização Cognitiva):** O sistema implementa uma separação estrita de papéis:
* **Cérebro (LLM como Orquestrador Probabilístico):** O LLM é expressamente proibido de realizar aritmética interna. Sua função restringe-se a formular a hipótese analítica, invocar o ferramental e ler os resultados.
* **Músculo (Tools Determinísticas em Python):** Toda a execução de cálculos e extração de dados opera sob o padrão *Code Interpreter/Tools*. Ferramentas estritamente tipadas em Python puro executam o cálculo (ex: $Valor Justo = \sqrt{22.5 \times VPA \times LPA}$) ou a extração da B3.



**2. GESTÃO DE ESTADO E MÁQUINA DE ESTADOS FINITA (LANGGRAPH)**

* A arquitetura opera como um **Grafo Cíclico** com semântica de **Comitê Iterativo** e capacidade de **Self-Reflection**. O roteador `route_after_consensus` permite que o consenso devolva o controle ao comitê qualitativo (Fisher → Macro → Marks) para re-avaliação quando a cross-validação econométrica indica sinais sem significância estatística (`p_value > 0.05`). Um circuit breaker (`_MAX_ITERATIONS=2`) garante terminação determinística.
* **Reflexão Estruturada:** Quando o loop de reflexão é disparado, os agentes qualitativos recebem um bloco `[REFLECTION — Iteration N]` no prompt contendo o feedback do supervisor, permitindo ajuste de análise. O Agente Graham (quantitativo) NÃO participa do loop — dados de mercado não mudam entre iterações.
* **A Validação:** A "verdade" do sistema reside em *schemas* rígidos validados pelo pacote Pydantic (v2). Nenhuma saída de texto livre do LLM é aceita como dado estruturado. Se um agente tentar inserir um dado com tipagem incorreta, a exceção é devolvida ao LLM para correção antes de avançar o grafo. O estado lida com dados ausentes de forma defensiva através da tipagem `Optional[float] = None`. Campos de reflexão: `iteration_count: int = 0` e `reflection_feedback: Optional[str] = None`.

**3. ECOSSISTEMA DE DESENVOLVIMENTO: AI-ASSISTED WORKSPACE**

Para evitar o viés de "funciona na minha máquina" e alinhar o projeto a ambientes *Cloud-Native*, adotamos um desenvolvimento assistido por IA multiplataforma.

* **Infraestrutura Declarativa (VS Code + LLMs):** O ambiente local ($E_{local}$) utiliza o VS Code como IDE oficial, enriquecido com assistentes de IA (GCA, Claude, Copilot).
* **Gestor de Pacotes:** Utiliza-se exclusivamente o Poetry (substituindo o `requirements.txt`), garantindo a exata mesma versão de bibliotecas, mitigando quebras de estado.
* **Princípio de Inversão de Dependência (Multi-Cloud):** O *Core* de raciocínio do Aequitas-MAS é cego em relação ao provedor de nuvem. É expressamente proibido o uso de importações diretas de SDKs de nuvem (como `import boto3`) dentro dos arquivos de Agentes (`/src/agents`).

**4. ESTRUTURA DOS AGENTES (PERSONAS) E INFRAESTRUTURA**

O sistema utiliza a técnica de *Tree-of-Thought* (ToT) delegada a especialistas com capacidade de **Self-Reflection** via loop cíclico, respeitando o Princípio da Responsabilidade Única (SRP):

* **Aequitas Core (Supervisor):** Roteamento e orquestração via *LangGraph Conditional Edges*. Possui a responsabilidade exclusiva de invocar a *Tool* determinística de otimização de portfólio (Álgebra Linear / Fronteira Eficiente de Markowitz) após o consenso das avaliações dos subagentes. Após o consenso, `route_after_consensus` avalia se o loop de reflexão deve ser disparado com base na significância da cross-validação econométrica.
* **Agente Graham (Quantitativo):** Análise determinística com horizonte de **5 anos** (adaptação B3 per Testa & Lima 2012); consome *Tools* tipadas para extração de múltiplos teóricos, ROIC (qualidade) e Dividend Yield (renda). Interpreta sinais via `GrahamInterpretation` com `roic_assessment` e `dividend_yield_assessment`.
* **Agente Fisher (Micro-Qualitativo):** Avaliação exclusiva de governança corporativa e microeconomia através da leitura de *filings* corporativos e *Scuttlebutt* via RAG.
* **Agente Macro (Holístico):** Processamento RAG de relatórios macroeconômicos (FED, Banco Central) utilizando Geração Aumentada por Recuperação baseada em *HyDE* para definição do contexto temporal.
* **Agente Marks (Auditor):** Crítico focado em atuar de forma contracíclica e mitigar viés de sobrevivência. Em iterações de reflexão (`iteration_count > 0`), recebe o feedback do supervisor via bloco `[REFLECTION — Iteration N]` no prompt.
* **Capacidade de Reflexão:** Fisher, Macro e Marks recebem o bloco `[REFLECTION]` condicionalmente quando `iteration_count > 0` e `reflection_feedback` está presente. Na primeira passagem (`iteration_count == 0`), o bloco é vazio — zero impacto no comportamento original.
* **Infraestrutura de Estado:** A persistência em ambiente de desenvolvimento opera com `MemorySaver` em memória para anular custos. Em homologação/produção, utiliza-se Amazon DynamoDB (via interfaces e *Adapters* como `BaseCheckpointSaver`) e Amazon OpenSearch Serverless para o motor vetorial RAG.

**5. ARQUITETURAS PREDITIVAS SOTA 2026 (Camada de Tools)**

O dogma de Confinamento de Risco estipula que LLMs operam exclusivamente como
orquestradores semânticos — sendo sumariamente proibidos de atuar como
calculadoras financeiras ou geradores de previsões estocásticas. As arquiteturas
preditivas avançadas residem exclusivamente em `src/tools/`, encapsuladas por
contratos Pydantic. As projeções são expostas aos agentes como variáveis de
contexto observáveis e estruturadas.

* **Temporal Fusion Transformer (TFT):** Rede de Seleção de Variáveis com
  Atenção Multi-Cabeça Interpretável e previsão quantílica. Gera intervalos de
  confiança e projeções de probabilidade de risco de cauda para consumo do
  Agente Marks. Horizonte: janela de 5 anos.
* **Amazon Chronos-2:** *Foundation Model* baseado em T5 com tokenização por
  quantização. Projeção direcional rápida de tendências de preço (*zero-shot*)
  sem necessidade de retreinamento por ativo.
* **PatchTST / iTransformer:** Agrupamento em *patches* para expansão da janela
  histórica e atenção inter-variáveis. Captura sazonalidades de longo prazo e
  correlação entre indicadores macroeconômicos e preço da ação.
* **CatBoost / LightGBM:** Motor de extração de características (*Feature
  Selection*) e classificação probabilística para detecção de *Value Traps* via
  dados tabulares fundamentalistas. Codificação nativa de variáveis categóricas
  (setor B3, governança, rating) sem *One-Hot Encoding*.

**⛔ BACKLOG — SUSPENSO: Redes Neurais em Grafos (GNN/GAT/STGAT)**

A integração de Graph Attention Networks para modelagem topológica de correlações
de portfólio (`NetworkRiskMetrics`) está **explicitamente suspensa**. Requer
infraestrutura de GPU dedicada (Amazon SageMaker endpoints) não provisionada na
conta AWS atual. Zero código GNN será produzido até que a infra de inferência
esteja disponível. O schema `NetworkRiskMetrics` (node_centrality,
sector_contagion_risk) permanece como especificação arquitetural para
implementação futura.

**6. GOVERNANÇA DE RISCO: TRIPLE BARRIER (AlphaX 2025)**

O framework de Triple Barrier, inspirado no sistema AlphaX (2025), governa o
ciclo de vida das teses de investimento no comitê iterativo:

* **Barreira Superior (Take Profit Analítico):** Ativada quando a projeção de
  preços (TFT/Chronos-2) converge consistentemente acima do Valor Justo de
  Graham. O comitê, liderado pelo Agente Marks, formaliza exigência de
  desinvestimento, capturando o prêmio de assimetria.
* **Barreira Inferior (Stop Loss de Fundamentos):** Ativada pela deterioração
  dinâmica do Altman Z-Score e/ou queda do Piotroski F-Score — não apenas por
  declínio percentual de preço. Força preservação de capital antes da
  materialização de insolvência.
* **Barreira Vertical (Janela Temporal):** Horizonte absoluto de retenção da
  tese — forçando reavaliação ao término do trimestre contábil ou na divulgação
  de novo Formulário de Referência pela CVM. Garante que o sistema opere com
  fundamentos atualizados na janela de 5 anos.

Implementação: ferramenta determinística em `src/tools/` consumida pelo
`core_consensus_node`. Os sinais de barreira são campos `Optional` no
`AgentState`, degradando para `None` quando a infraestrutura preditiva não está
disponível.

**7. CRITÉRIOS DE ACEITE E DEGRADAÇÃO (DEFINITION OF DONE)**

Para que qualquer etapa seja considerada válida e auditável nos rigores do TCC:

* **Separação de Preocupações / Inversão de Dependência (DIP):** O comando `import boto3` não pode constar dentro de `/src/agents/`.
* **Validação Matemática (Shift-Left Testing):** 100% das funções determinísticas em `/src/tools/` devem ser acompanhadas por rigorosos testes unitários escritos em `pytest`, comprovando a precisão do cálculo financeiro sem o auxílio do modelo generativo.
* **Degradação Controlada:** Na ausência da resolução de um Ticker (ex: FAKE3) ou métrica financeira, o fluxo deve interceptar a anomalia e retornar `None` sob o esquema Pydantic (`Optional[float] = None`), negando sumariamente ao LLM o acesso probabilístico para "adivinhar" o valor.
* **Circuit Breaker de Reflexão:** O loop de reflexão do comitê é limitado a `_MAX_ITERATIONS=2`. Após 2 passagens, o grafo termina independentemente do estado da cross-validação. Este é um critério de aceite obrigatório para prevenir loops infinitos e controlar custos LLM (FinOps).
* **Rastreabilidade Ética e Transparência:** O Agente Fisher (e Macro) é arquiteturalmente obrigado pelo *schema* Pydantic a devolver listas de URLs ou IDs de documentos de origem. O relatório final tem de ostentar a fórmula Python invocada pelo código em *logs*.
