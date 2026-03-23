### 🇧🇷 Versão Oficial em Português do Brasil (pt-BR)

**MANUAL DE ENGENHARIA E FLUXO DE TRABALHO: RPI & SDD**
**Projeto:** Aequitas-MAS (Multi-Agent System)
**Domínio:** Arquitetura de Software Híbrida e Desenvolvimento Orientado a Especificações
**Versão:** 2.0 (Integração RAG HyDE e Tipagem Defensiva)

**1. Introdução**
Para o desenvolvimento de sistemas complexos baseados em agentes inteligentes como o Aequitas-MAS, a integração das metodologias RPI (*Research, Plan, Implement*) e SDD (*Spec-Driven Development*) é mandatória. O sistema opera como um Sistema de Suporte à Decisão (DSS) focado no mercado financeiro brasileiro (B3). Diferente de *chatbots* de uso geral, ele emula o "Sistema 2" de raciocínio de Kahneman — lento, deliberativo e analítico. Para garantir esta precisão na fase de desenvolvimento, as responsabilidades de ideação, arquitetura e codificação devem ser estritamente divididas entre diferentes plataformas de IA.

**2. A Estrutura da Equipe (Papéis e Ferramentas)**
A configuração ideal do ecossistema de desenvolvimento divide-se nos seguintes papéis funcionais:

| Membro da Equipe | Ferramenta | Papel Principal | Artefatos Gerados / Responsabilidade |
| --- | --- | --- | --- |
| **O Humano** | Orquestrador (Tech Lead) | Toma as decisões finais de arquitetura, move o contexto entre as ferramentas e aprova os artefatos. | Garante o cumprimento do *Dogma do Confinamento de Risco*. |
| **O Pesquisador** | NotebookLM | Especialista no Domínio | Vasculha bibliografias (ex: livros de Graham, papers sobre HyDE RAG) e extrai regras imunes a alucinação. |
| **O Arquiteto** | Gemini (GEM) / Claude | Mentor e Designer de Software | Traduz a teoria em contratos de software. Define schemas rígidos e fluxos (StateGraph). Gera o `SPEC.md` e o `PLAN.md`. |
| **O Cientista** | Google AI Studio | Laboratório de Experimentação | Testa o comportamento de *prompts*, temperatura e rotas dos agentes (ex: Agente Macro) antes de virarem código. |
| **O Desenvolvedor** | VS Code + GCA/Copilot | Implementador Cirúrgico | Escreve o código-fonte estritamente alinhado ao plano, operando em ambiente *Cloud-Native* e garantindo a tipagem estrita. |

**3. O Fluxo de Trabalho Integrado (Ciclo RPI & SDD)**
Abaixo detalha-se o ciclo de vida para a implementação de uma nova funcionalidade (ex: adição do Agente Macro e Motor de Markowitz).

**Fase 1: Research (Pesquisa de Fundamentos) $\rightarrow$ NotebookLM**
Antes da arquitetura, estabelece-se o rigor teórico. LLMs possuem alta capacidade de inferência semântica, mas são estatisticamente propensos à alucinação em cálculos matemáticos.

* **Ação do Tech Lead:** Faz o *upload* de artigos acadêmicos sobre *MarketSenseAI* e documentos macroeconômicos para o NotebookLM.
* **Execução:** Elabora interrogações direcionadas: *"Sintetize a metodologia de extração de sinais macroeconômicos utilizando HyDE para a construção de um Agente Macro independente"*.
* **Resultado:** Um resumo conceitual robusto, com *fact-checking* garantido pelas fontes.

**Fase 2: Plan & Spec (Especificação Orientada a Design) $\rightarrow$ Arquiteto (Gemini/Claude)**
A arquitetura abandona *pipelines* lineares (*Chains*) em favor de Grafos Acíclicos Direcionados (LangGraph). A teoria converte-se em contratos.

* **Ação do Tech Lead:** Entrega o resumo gerado pelo NotebookLM ao Arquiteto com diretrizes estruturais claras.
* **Execução:** *"Atue como Arquiteto de Software. Baseado nesta teoria, elabore a especificação técnica (SPEC.md) isolando o Agente Fisher do Agente Macro. Defina o estado do sistema ($S_t$) mutável a cada nó, utilizando a tipagem Pydantic (v2). Certifique-se de prever a degradação controlada com `Optional[float] = None` para evitar a quebra do grafo na ausência de dados. Crie o PLAN.md"*.
* **Resultado:** O contrato de dados e um *checklist* atômico de tarefas.

**Fase 3: Experimentation (Validação Lógica) $\rightarrow$ Google AI Studio**
O "sandbox" de engenharia de *prompts*.

* **Ação do Tech Lead:** Utiliza o AI Studio para afinar o *System Prompt* de roteamento do Supervisor (Aequitas Core).
* **Execução:** Simula a recepção de ranqueamentos dos subagentes e testa a injeção da instrução: *"Invoque a Tool de Álgebra Linear para calcular a Fronteira Eficiente de Markowitz"*.
* **Resultado:** O *prompt* otimizado e os hiperparâmetros congelados para produção.

**Fase 4: Implement (Codificação Cirúrgica) $\rightarrow$ VS Code + Assistentes**
O escopo está fechado. A implementação entra no ambiente de desenvolvimento.

* **Ação do Tech Lead:** Abre a IDE (VS Code), garantindo que as credenciais operam sob o padrão *Zero Trust*.
* **Execução:** Aciona o assistente de código: *"Leia o PLAN.md e a SPEC.md. Execute o Passo 1. Implemente as ferramentas tipadas em Python puro para a otimização de portfólio. Lembre-se que o LLM nunca calcula indicadores financeiro mentalmente. Retorne `None` via esquema Pydantic em caso de erro. Proibido o uso de import boto3 nos Agentes"*.
* **Resultado:** Código gerado em conformidade com o `poetry.lock`, cobertura de testes matemáticos isolados (`pytest`), e mecanismos de degradação controlada.

**Síntese Operacional:**
O retrabalho e a dívida técnica manifestam-se quando a restrição de escopo é violada. Mantendo o NotebookLM no domínio do **problema**, o Arquiteto no domínio da **arquitetura**, o AI Studio no domínio do **comportamento** e a IDE no domínio da **sintaxe**, alcança-se a resiliência arquitetural exigida pelo padrão Aequitas-MAS.
