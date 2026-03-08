### 🧪 PROMPT DE VALIDAÇÃO: Auditoria de Integridade Aequitas-MAS (V3.0 - Full Scope)

**Contexto:** Atue como o Mentor PhD do projeto Aequitas-MAS. Preciso validar se as premissas de design, os contratos de código e a topologia SOTA (State of the Art) estão devidamente mapeados na sua base de conhecimento.

**Tarefa:** Explique como o ecossistema multiagente deve processar a análise da empresa fictícia `TECH3`, que apresenta um cenário de **Pânico Extremo**, seguindo rigorosamente os documentos normativos e os contratos em `/src`.

**Sua resposta deve obrigatoriamente abordar as 6 frentes abaixo:**

1. **Confinamento de Risco (Motor Quantitativo):** Como o `state.py` garante que o Agente Graham não alucine matematicamente ao calcular o Valor Justo? Cite a biblioteca, a classe específica e justifique a escolha de tipos numéricos.
2. **Integração SOTA Qualitativa (Fisher):** Explique como o Agente Fisher emula as camadas do *FinRobot* para avaliar o *Micro-Quality* e qual é a exigência do Pydantic para garantir a rastreabilidade ética.
3. **Integração SOTA Holística (Macro):** Como o Agente Macro utiliza o conceito de **HyDE RAG** (referenciado no *MarketSenseAI* de 2025) para enriquecer a análise de juros sem sobrecarregar a janela de contexto?
4. **Fórmula e Decisão de Auditoria (Marks):** Apresente a fórmula SOTA de **Valor Intrínseco Dinâmico** em LaTeX e explique, com base na **Doutrina de Howard Marks**, qual deve ser a intervenção do Agente Auditor se o Preço de Mercado for amplamente inferior ao Valor Justo neste cenário de pânico.
5. **Arquitetura de Fluxo (Aequitas Core/LangGraph):** Explique o papel da função `router` em `graph.py` e como ela utiliza o histórico do estado para evitar falhas em cascata ("Death Loops").
6. **Restrição de Infraestrutura (DIP):** Qual é a regra de ouro inegociável sobre o uso de SDKs de provedores de nuvem (ex: `boto3`) dentro da pasta `/src/agents`?

---

### O que esperar de uma resposta correta (Gabarito Oficial do Mentor V3.0):

Para que a IA seja considerada validada e alinhada ao escopo completo do projeto, a resposta deve conter:

* **Precisão de Tipagem e Confinamento:** Menção obrigatória ao uso de **`math.isfinite()`** sobre tipos `float` com validação **Pydantic V2** (`@field_validator`) no `state.py`. O sistema **deliberadamente NÃO usa `decimal.Decimal`**, adotando a "Degradação Controlada" onde `Optional[float] = None` representa ausência de dados, negando ao LLM a chance de alucinar cálculos.
* **Rastreabilidade Ética e SOTA:** Confirmação de que o Agente Fisher avalia governança (*Scuttlebutt* / FinRobot Concept-CoT) e que **ambos** (Fisher e Macro) são obrigados pelo *schema* Pydantic a popular a lista `source_urls` para validação de fonte humana.
* **HyDE RAG:** Explicação de que o Agente Macro gera um documento vetorizado "hipotético ideal" simulando atas do COPOM/FED para buscar os fragmentos reais correspondentes, contornando os limites de *tokens*.
* **Fórmulas Dinâmicas Exatas:**
  $$M_{dinâmico} = \frac{1}{(Selic + ERP)} \times P/B_{conservador}$$
  $$V_{Justo} = \sqrt{M_{dinâmico} \times LPA \times VPA}$$
  *(Onde $Selic$ incorpora o custo de oportunidade).*
* **Decisão Contracíclica:** A decisão obrigatória para o pânico é **COMPRAR (Agressividade Máxima)**, pois a distorção psicológica criou uma Margem de Segurança massiva, anulando o risco de perda permanente de capital.
* **Prevenção de Death Loops:** Menção de que o `router` analisa a variável `executed_nodes` em `state.messages` para não reinvocar agentes degradados.
* **Inversão de Dependência (DIP):** Afirmação de que `import boto3` é **estritamente proibido** em `/src/agents/`. Código *Cloud-Native* deve confinar provedores externos na camada `/src/infra/adapters/`.
* **Protocolo Ético Final:** Inclusão do *Disclaimer* de que o sistema é um framework acadêmico de Suporte à Decisão (DSS) e **não constitui recomendação de investimento**.