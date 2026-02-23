# Aequitas-MAS: Catálogo de Agentes e Orquestração (LangGraph)

Este documento define os nós (Nodes) operacionais do Grafo Acíclico Direcionado (DAG) do Aequitas-MAS. Cada agente é estritamente confinado ao seu Bounded Context para mitigar alucinações cognitivas e financeiras.

## 🧠 1. Supervisor (Aequitas Core)
**Função Arquitetural:** Roteamento e Orquestração (Máquina de Estados).
- **Objetivo:** Analisar o estado atual (`AequitasState`) e decidir qual especialista acionar em seguida, ou se o ciclo deve ser encerrado por falta de dados (degradação controlada).
- **Mecanismo:** Utiliza *Conditional Edges* no LangGraph.
- **Restrição (Risk Confinement):** O Supervisor não analisa o ativo. Ele apenas delega tarefas e verifica se o Pydantic validou os dados corretamente.

---

## 📊 2. Agente Graham (O Quantitativo)
**Função Arquitetural:** Análise fundamentalista rigorosa baseada em demonstrativos contábeis.
- **Objetivo:** Calcular o *Preço Justo* e a *Margem de Segurança* do ativo.
- **Mecanismo:** *Tool-Use Obligatory*. O agente é proibido de realizar aritmética mentalmente.
- **Regras de Atuação:**
  1. Acionar invariavelmente as ferramentas determinísticas em Python (`src/tools/`) para ler dados de fontes oficiais (ex: yfinance via `get_graham_data`).
  2. Se as ferramentas retornarem erro (ex: ativo inexistente ou dados insuficientes), o agente deve falhar rapidamente e devolver o erro ao Supervisor.
  3. Não considerar, sob nenhuma hipótese, projeções de crescimento futuro não tangíveis.

---

## 📰 3. Agente Fisher (O Qualitativo)
**Função Arquitetural:** Análise de "Fosso Econômico" (Moat), qualidade de gestão e sentimento de mercado corporativo.
- **Objetivo:** Entender o contexto além dos números (Relatórios de RI, fatos relevantes, governança).
- **Mecanismo:** *Retrieval-Augmented Generation (RAG)*.
- **Regras de Atuação:**
  1. Basear todas as afirmações estritamente nos documentos injetados no contexto.
  2. Cumprir a Rastreabilidade Ética: Retornar obrigatoriamente um array com as URLs/Fontes (`source_urls`) para toda análise gerada.
  3. Se a informação não estiver no contexto recuperado, declarar explicitamente: "Dados qualitativos insuficientes".

---

## ⚖️ 4. Agente Marks (O Auditor / Gestor de Risco)
**Função Arquitetural:** Atuar como *Advogado do Diabo* e mitigar viés de sobrevivência/excesso de otimismo.
- **Objetivo:** Auditar os *outputs* combinados de Graham e Fisher.
- **Mecanismo:** *Second-Level Thinking* (Pensamento de Segundo Nível).
- **Regras de Atuação:**
  1. Avaliar a fase atual do Pêndulo de Mercado (Market Cycle).
  2. Confrontar a tese de Graham: "A margem de segurança compensa o risco de governança apontado por Fisher?".
  3. Gerar o log final de auditoria que aprova ou veta a recomendação, adicionando restrições focadas em proteção de capital (Drawdown).