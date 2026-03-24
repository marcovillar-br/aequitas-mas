# 🗺️ PLAN: Execução de Engenharia — Aequitas-MAS

## 1. Arquitetura Baseline (Status: Sprints 1 a 8 Concluídas)

O baseline arquitetural vigente do repositório entrega as seguintes capacidades:

- **Orquestração (LangGraph):** Cyclic Graph com semântica de Iterative Committee (`graham -> fisher -> macro -> marks -> core_consensus -> __end__`).
- **Estado (Pydantic):** `AgentState` imutável, tipado defensivamente e ancorado temporalmente via `as_of_date`.
- **RAG & Contexto (HyDE):** Retrieval qualitativo time-aware operando via `VectorStorePort`.
- **Ingestão Histórica (B3):** Ingestão real via `B3HistoricalFetcher` conectada ao engine de backtesting determinístico com degradação controlada.
- **Otimização de Portfólio:** Ferramenta matemática determinística isolada, acessível de forma resiliente pelo `core_consensus_node` (que falha fechado com `optimization_blocked=True`).
- **API Gateway (FastAPI):** Fronteiras HTTP tipadas para `/analyze`, `/backtest/run` e `/portfolio`, operando com sanitização de erros.
- **Infraestrutura e Segurança:** Gerenciamento de credenciais via `SecretStorePort` (Zero Trust) e documentação unificada sob a arquitetura de Blackboard.

## 2. Academic & SOTA Roadmap 2026-2027 (Integrated V2)

O Aequitas-MAS atingiu maturidade técnica à frente do calendário acadêmico. O planejamento de longo prazo agora se alinha à grade de Pós-Graduação (UFG) e ao estado da arte (SOTA):

- **Mar/26 (ePrompt): Engenharia do Blackboard.** Refinamento dos System Prompts para a "Tríade de Agentes" (Graham, Fisher, Marks) usando Chain-of-Thought (CoT) para emular o paper FinRobot, mantendo a tipagem estrita.
- **Abr-Mai/26 (Framework & API): Telemetry & Streaming.** Expandir o FastAPI atual com telemetria avançada, auditoria de logs no OpenSearch e streaming assíncrono das respostas do LangGraph.
  - **Deterministic Thesis-CoT Reporting:** Criação de um gerador de PDF em Python (utilizando Matplotlib e WeasyPrint) que consome o JSON final do LLM (Pydantic) para renderizar um relatório profissional, abolindo alucinações visuais do modelo.
- **Jun-Jul/26 (DAIA): Shift-Left Testing Avançado.** Expandir a base de testes atual (144 testes) para cobrir Edge Cases estatísticos e comprovar o Risk Confinement.
- **Ago-Set/26 (EGI & AM): Validação Econométrica.** Aplicar a metodologia de Damodar Gujarati para provar que os sinais do Agente Macro (HyDE RAG) e Agente Fisher possuem significância estatística.
- **Out-Nov/26 (LLM & Agent): Refinamento do Grafo Cíclico.** Aplicar padrões de Reasoning and Acting (ReAct) e Tree-of-Thought (ToT) no `core_consensus_node`, focando no Agente Marks (Risco).
- **Dez/26-Jan/27 (EAD): Expansão de Fatores SOTA.** Integrar fatores quantitativos institucionais via Selenium/Pandas para municiar o motor determinístico do Agente Graham. Expansão da boundary `HistoricalMarketData` para suportar o cálculo de Piotroski F-Score (Quality/Value Trap filter) e Altman Z-Score (Bankruptcy Risk) via ferramentas em Python puro.
- **Jan-Fev/27 (AMLDO): Aprimoramento do RAG (MarketSenseAI).** Focar em Semantic Chunking para transcrições de Earnings Calls, refinando o Agente Fisher.
- **Fev-Mar/27 (PA): Defesa e TCC Final.** Simulação de Backtesting em larga escala, formatação ABNT/USP-ESALQ e redação do paper final demonstrando a geração de Alpha frente à Fórmula Mágica e ao Ibovespa.

## 3. Cross-Cutting Engineering Track (AWS Serverless & FinOps)

Em paralelo ao roadmap acadêmico, o Aequitas-MAS executa uma trilha de infraestrutura focada em implantação em nuvem e otimização de custos:

- **API Deployment (Abr-Mai/26):** Empacotamento do gateway FastAPI para AWS Lambda (Serverless) para alcançar a capacidade *Scale-to-Zero*, conectando os adaptadores de persistência do DynamoDB e OpenSearch Serverless.
- **CI/CD & IAC Pipeline (Jun-Jul/26):** Ativação da esteira de CI/CD via GitHub Actions para aplicar o estado do Terraform e executar os testes automatizados *shift-left* (DAIA) na nuvem.
- **Cloud Backtesting Engine (Fev-Mar/27):** Execução do backtesting quantitativo final do TCC na infraestrutura AWS para provar a viabilidade arquitetural e de FinOps (custos *Scale-to-Zero* versus Performance).

## 4. 🚀 Optional SOTA Backlog (If Time Permits)

- **Explainable AI (XAI) Dashboard:** Um frontend em Streamlit ou Gradio consumindo nosso FastAPI para visualizar a execução do LangGraph, a evolução do `AgentState` e o raciocínio CoT (Chain-of-Thought) em tempo real durante a defesa da tese.
- **Historical Stress Testing:** Expansão do `BacktestEngine` determinístico para executar cenários isolados de "Cisne Negro" (ex: crash da COVID-19, Joesley Day), provando a resiliência do nosso *Risk Confinement* e o valor do Agente Marks.
- **Regime-Aware Consensus (Dynamic Weights):** Aprimoramento do `core_consensus_node` para que o Supervisor altere dinamicamente os pesos de votação com base na taxa Selic (ex: priorizando Graham/Marks sobre Fisher em ambientes de juros altos).
- **Graph-of-Thought (GoT) / GraphRAG:** Experimentação com prompting estruturado em grafos e Knowledge Graphs para o Agente Macro mapear causalidades econômicas complexas, referenciando metodologias avançadas (Shao, 2024).
