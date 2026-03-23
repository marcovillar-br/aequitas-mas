### 🇧🇷 Versão Oficial em Português do Brasil (pt-BR)

**Aequitas-MAS: Documento Mestre de Arquitetura e Especificação**
**Versão:** 2.0 (Consolidada - AI-Assisted Workspace, Risk Confinement & RAG HyDE)
**Status:** Documento Normativo Único para Orquestração de LLMs

**1. FILOSOFIA DE OPERAÇÃO E IDENTIDADE**

* **Propósito do Sistema:** O Aequitas-MAS é um Sistema de Suporte à Decisão (DSS) focado no mercado financeiro brasileiro (B3). Distanciando-se de *chatbots* de uso geral, a arquitetura foi concebida para emular o "Sistema 2" de raciocínio humano descrito por Kahneman — um processamento analítico, lento e deliberativo focado em *Value Investing*.
* **Dogma do Confinamento de Risco (Risk Confinement):** A arquitetura abandona a premissa ingênua de "alucinação zero" para adotar o Confinamento de Risco. Parte-se do pressuposto arquitetural de que Modelos de Linguagem de Grande Escala (LLMs) possuem altíssima capacidade de inferência semântica, mas são inerentemente falhos (papagaios estocásticos) e estatisticamente propensos à alucinação quando submetidos a cálculos matemáticos rigorosos.
* **Estratégia de Mitigação de Alucinação (Hibridização Cognitiva):** O sistema implementa uma separação estrita de papéis:
* **Cérebro (LLM como Orquestrador Probabilístico):** O LLM é expressamente proibido de realizar aritmética interna. Sua função restringe-se a formular a hipótese analítica, invocar o ferramental e ler os resultados.
* **Músculo (Tools Determinísticas em Python):** Toda a execução de cálculos e extração de dados opera sob o padrão *Code Interpreter/Tools*. Ferramentas estritamente tipadas em Python puro executam o cálculo (ex: $Valor Justo = \sqrt{22.5 \times VPA \times LPA}$) ou a extração da B3.



**2. GESTÃO DE ESTADO E MÁQUINA DE ESTADOS FINITA (LANGGRAPH)**

* A arquitetura abandona pipelines lineares (*Chains*) em favor de Grafos Acíclicos Direcionados (DAGs). O estado do sistema ($S_t$) muta a cada nó, permitindo "Reflexão" e "Correção de Erros" (*Self-Correction*).
* **A Validação:** A "verdade" do sistema reside em *schemas* rígidos validados pelo pacote Pydantic (v2). Nenhuma saída de texto livre do LLM é aceita como dado estruturado. Se um agente tentar inserir um dado com tipagem incorreta, a exceção é devolvida ao LLM para correção antes de avançar o grafo. O estado lida com dados ausentes de forma defensiva através da tipagem `Optional[float] = None`.

**3. ECOSSISTEMA DE DESENVOLVIMENTO: AI-ASSISTED WORKSPACE**

Para evitar o viés de "funciona na minha máquina" e alinhar o projeto a ambientes *Cloud-Native*, adotamos um desenvolvimento assistido por IA multiplataforma.

* **Infraestrutura Declarativa (VS Code + LLMs):** O ambiente local ($E_{local}$) utiliza o VS Code como IDE oficial, enriquecido com assistentes de IA (GCA, Claude, Copilot).
* **Gestor de Pacotes:** Utiliza-se exclusivamente o Poetry (substituindo o `requirements.txt`), garantindo a exata mesma versão de bibliotecas, mitigando quebras de estado.
* **Princípio de Inversão de Dependência (Multi-Cloud):** O *Core* de raciocínio do Aequitas-MAS é cego em relação ao provedor de nuvem. É expressamente proibido o uso de importações diretas de SDKs de nuvem (como `import boto3`) dentro dos arquivos de Agentes (`/src/agents`).

**4. ESTRUTURA DOS AGENTES (PERSONAS) E INFRAESTRUTURA**

O sistema utiliza a técnica de *Tree-of-Thought* (ToT) delegada a especialistas, respeitando o Princípio da Responsabilidade Única (SRP):

* **Aequitas Core (Supervisor):** Roteamento e orquestração via *LangGraph Conditional Edges*. Possui a responsabilidade exclusiva de invocar a *Tool* determinística de otimização de portfólio (Álgebra Linear / Fronteira Eficiente de Markowitz) após o consenso das avaliações dos subagentes.
* **Agente Graham (Quantitativo):** Análise determinística; consome apenas as *Tools* tipadas (`yfinance` ou APIs da B3) para extração de múltiplos teóricos.
* **Agente Fisher (Micro-Qualitativo):** Avaliação exclusiva de governança corporativa e microeconomia através da leitura de *filings* corporativos e *Scuttlebutt* via RAG.
* **Agente Macro (Holístico):** Processamento RAG de relatórios macroeconômicos (FED, Banco Central) utilizando Geração Aumentada por Recuperação baseada em *HyDE* para definição do contexto temporal.
* **Agente Marks (Auditor):** Crítico focado em atuar de forma contracíclica e mitigar viés de sobrevivência.
* **Infraestrutura de Estado:** A persistência em ambiente de desenvolvimento opera com `SqliteSaver` em memória para anular custos. Em homologação/produção, utiliza-se Amazon DynamoDB (via interfaces e *Adapters* como `BaseCheckpointSaver`) e Amazon OpenSearch Serverless para o motor vetorial RAG.

**5. CRITÉRIOS DE ACEITE E DEGRADAÇÃO (DEFINITION OF DONE)**

Para que qualquer etapa seja considerada válida e auditável nos rigores do TCC:

* **Separação de Preocupações / Inversão de Dependência (DIP):** O comando `import boto3` não pode constar dentro de `/src/agents/`.
* **Validação Matemática (Shift-Left Testing):** 100% das funções determinísticas em `/src/tools/` devem ser acompanhadas por rigorosos testes unitários escritos em `pytest`, comprovando a precisão do cálculo financeiro sem o auxílio do modelo generativo.
* **Degradação Controlada:** Na ausência da resolução de um Ticker (ex: FAKE3) ou métrica financeira, o fluxo deve interceptar a anomalia e retornar `None` sob o esquema Pydantic (`Optional[float] = None`), negando sumariamente ao LLM o acesso probabilístico para "adivinhar" o valor.
* **Rastreabilidade Ética e Transparência:** O Agente Fisher (e Macro) é arquiteturalmente obrigado pelo *schema* Pydantic a devolver listas de URLs ou IDs de documentos de origem. O relatório final tem de ostentar a fórmula Python invocada pelo código em *logs*.
