# 🗺️ Current Plan: Mar/26 (ePrompt) - FinRobot CoT Refactoring

## 1. Objective
Refatorar os *System Prompts* da "Tríade de Agentes" (Graham, Fisher, Marks) em `src/agents/` para implementar o padrão avançado de engenharia *Chain-of-Thought* (CoT) estruturado, emulando a arquitetura do artigo FinRobot (Zhang et al., 2024). A refatoração deve manter rigorosamente a tipagem estrita (Pydantic V2) e os dogmas arquiteturais de Zero Math e Risk Confinement.

## 2. Scope & Constraints
- **Arquivos Alvo:** `src/agents/graham.py`, `src/agents/fisher.py`, `src/agents/marks.py`.
- **Dogma Zero Math:** Os LLMs permanecem estritamente proibidos de realizar cálculos matemáticos ou projetar preços. A matemática continua isolada em `src/tools/`.
- **Compatibilidade de Esquema:** A refatoração não deve alterar as assinaturas das funções ou os esquemas de resposta Pydantic atuais (`FisherAnalysis`, `MarksVerdict`, `GrahamMetrics`).
- **Padrão de Saída:** O raciocínio CoT ("pensamento em voz alta" do modelo) deve ser instruído no *prompt*, mas a saída final exigida pelo `with_structured_output` deve permanecer limpa e de acordo com o contrato.
- **Idioma:** Toda a saída cognitiva gerada pelo LLM deve permanecer em Português do Brasil (pt-BR).

## 3. Implementation Steps (For SDD Implementer)

### Step 1: Refatoração do Agente Graham (Concept-CoT)
- **Arquivo:** `src/agents/graham.py`
- **Ação:** Atualizar a função `_build_interpreter_prompt`.
- **Requisitos de Prompt:**
  - Injetar instruções explícitas de *Chain-of-Thought* orientadas a conceitos (*Concept-CoT*).
  - Obrigar o LLM a estruturar sua resposta em 3 fases mentais invisíveis antes de gerar o texto final:
    1. Análise de Lucratividade (avaliar LPA e VPA frente ao Preço Observado).
    2. Avaliação da Margem de Segurança (interpretar se a diferença calculada oferece proteção real).
    3. Síntese do Senhor Mercado (verificar se o preço atual reflete pessimismo irracional ou otimismo excessivo).
  - Manter o *disclaimer* de "Do not perform arithmetic".

### Step 2: Refatoração do Agente Fisher (Data-CoT & Concept-CoT)
- **Arquivo:** `src/agents/fisher.py`
- **Ação:** Atualizar a variável `prompt` dentro da função `fisher_agent`.
- **Requisitos de Prompt:**
  - Implementar o "Método Scuttlebutt" via CoT.
  - O *prompt* deve instruir o LLM a processar as notícias em passos sequenciais lógicos:
    1. *Data Extraction*: Identificar fatos vs. ruído/opinião.
    2. *Moat Evaluation*: Buscar evidências de vantagens competitivas (ou perda delas) nas notícias.
    3. *Risk Synthesis*: Consolidar as evidências nos `key_risks` e calcular o `sentiment_score` com base na gravidade do impacto no negócio a longo prazo.

### Step 3: Refatoração do Agente Marks (Thesis-CoT)
- **Arquivo:** `src/agents/marks.py`
- **Ação:** Atualizar o `ChatPromptTemplate` na função `marks_agent`.
- **Requisitos de Prompt:**
  - Transformar o *prompt* em uma camada *Thesis-CoT* final (Ação/Veredito).
  - O LLM deve ser forçado a ponderar os relatórios em etapas antes de emitir o "APPROVE/VETO":
    1. Contraste: A Margem de Segurança quantitativa (Graham) é grande o suficiente para absorver os riscos qualitativos (Fisher)?
    2. Reflexão Contracíclica: O sentimento de notícias (Fisher) indica "efeito manada" que está distorcendo a valuation?
    3. Conclusão Direta: Emitir a string de veredito final exigida pelo esquema Pydantic.

### Step 4: Testes de Regressão e Auditoria
- **Ação:** Executar a suíte de testes existente (`pytest`) para garantir que os testes unitários (`test_graham_agent.py`, `test_fisher_agent.py`, `test_marks_agent.py`) continuam passando após a alteração dos *prompts*. As assinaturas das funções e as saídas Pydantic não devem ter quebrado.

## 4. Definition of Done
- Os *System Prompts* de Graham, Fisher e Marks foram enriquecidos com diretrizes explícitas de *Chain-of-Thought* (CoT).
- O comportamento determinístico da matemática permanece intacto.
- A aplicação passa em todos os testes unitários sem erros de conversão do `with_structured_output`.
- O código continua perfeitamente alinhado com a tipagem estrita e o Dogma de Confinamento de Risco.
