### 🧪 PROMPT DE VALIDAÇÃO: Auditoria de Integridade Aequitas-MAS (V2.1)

**Contexto:** Atue como o Mentor PhD do projeto Aequitas-MAS. Preciso validar se as premissas de design e os contratos de código estão devidamente mapeados na sua base de conhecimento.

**Tarefa:** Explique como o sistema deve processar a análise de uma empresa fictícia (ex: `TECH3`) que apresenta um cenário de **Pânico Extremo**, seguindo rigorosamente os documentos normativos e o código em `/src`.

**Sua resposta deve obrigatoriamente abordar:**

1. **Confinamento de Risco e Tipagem:** Como o `state.py` garante que não ocorram alucinações matemáticas ao calcular o Valor Justo? Cite a biblioteca e a classe específica utilizada.
2. **Fórmula e Decisão de Auditoria:** Apresente a fórmula de **Valor Intrínseco de Graham** em LaTeX e explique, com base na **Doutrina de Howard Marks**, qual deve ser a decisão do sistema se o Preço de Mercado for amplamente inferior ao Valor Justo em um cenário de pânico.
3. **Arquitetura de Fluxo (LangGraph):** Explique o papel do `router` em `graph.py` e como ele utiliza o histórico de mensagens para evitar loops infinitos ("Death Loops") entre os agentes.
4. **Integração SOTA:** Como o **Agente Macro** utiliza o conceito de **HyDE RAG** (referenciado nos papers de 2025) para enriquecer a análise sem sobrecarregar a janela de contexto?.
5. **Restrição de Nuvem (DIP):** Qual é a regra de ouro sobre o uso de SDKs de provedores de nuvem (como `boto3`) dentro da pasta `/src/agents`?.

---

### O que esperar de uma resposta correta (Gabarito do Mentor):

Para que eu (ou qualquer instância deste modelo) seja considerado validado, a resposta deve conter:

* **Precisão Técnica:** Menção obrigatória ao uso de **`math.isfinite()`** sobre tipos `float` com validação **Pydantic V2** (`@field_validator`) para rejeitar valores não-finitos (NaN/Inf). O sistema **deliberadamente NÃO usa `decimal.Decimal`**, seguindo a doutrina de "Controlled Degradation" onde `Optional[float] = None` representa ausência de dados ao invés de alucinação matemática.

* **Fórmulas Exatas (SOTA - Versão Dinâmica com Selic):**

$$M_{dinâmico} = \frac{1}{(Selic + ERP)} \times P/B_{conservador}$$

$$V_{Justo} = \sqrt{M_{dinâmico} \times LPA \times VPA}$$

Onde: $Selic$ = Taxa básica (BCB API), $ERP$ = 4.5% (Equity Risk Premium Brasil), $P/B_{conservador}$ = 1.5 (Multiplicador Graham).

**Nota:** A fórmula clássica estática ($\sqrt{22.5 \times LPA \times VPA}$) foi substituída por esta versão adaptativa que incorpora o custo de oportunidade do mercado brasileiro.

* **Conformidade de Arquitetura:** Citação de que o estado é validado via **Pydantic V2** (`BaseModel` com `frozen=True`) e que o `router` verifica `executed_nodes` no histórico de mensagens para prevenir Death Loops.
* **Protocolo Ético:** Inclusão do *Disclaimer* obrigatório de que o sistema é um framework acadêmico de Suporte à Decisão (DSS) e **não constitui recomendação de investimento**.
* **Inversão de Dependência (DIP):** Afirmação de que `import boto3` é **estritamente proibido** dentro de `/src/agents/` para manter a independência de nuvem. SDKs de provedores devem estar confinados a `/src/infra/adapters/`.

Este protocolo garante que o sistema não se comporte como um chatbot genérico, mas como um **Sistema de Suporte à Decisão (DSS)** de alta precisão com fundamentos auditáveis.