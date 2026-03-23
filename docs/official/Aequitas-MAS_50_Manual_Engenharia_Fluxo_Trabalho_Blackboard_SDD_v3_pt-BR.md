### 🇧🇷 Versão Oficial em Português do Brasil (pt-BR)

**MANUAL DE ENGENHARIA E FLUXO DE TRABALHO: BLACKBOARD & SDD**
**Projeto:** Aequitas-MAS (Multi-Agent System)
**Domínio:** Arquitetura de Software Híbrida e Desenvolvimento Orientado a Especificações
**Versão:** 3.0 (Arquitetura de Blackboard Orientada a Artefatos)

**1. Introdução**
Para o desenvolvimento de sistemas complexos baseados em agentes inteligentes como o Aequitas-MAS, a integração da metodologia de *Artifact-Driven Blackboard* com o SDD (*Spec-Driven Development*) é mandatória. O sistema opera como um Sistema de Suporte à Decisão (DSS) focado no mercado financeiro brasileiro (B3). Diferente de *chatbots* de uso geral, ele emula o "Sistema 2" de raciocínio de Kahneman — lento, deliberativo e analítico. Para garantir esta precisão na fase de desenvolvimento, as responsabilidades são divididas em "Personas" da IA atuando sobre um quadro negro (Blackboard) compartilhado. O antigo fluxo fragmentado RPI (*Research, Plan, Implement*) foi oficialmente descontinuado.

**2. A Estrutura da Equipe (Papéis e Ferramentas)**
A configuração atual do ecossistema de desenvolvimento divide-se nos seguintes papéis unificados:

| Membro da Equipe | Ferramenta | Papel Principal | Artefatos Gerados / Responsabilidade |
| --- | --- | --- | --- |
| **O Humano** | Tech Lead | Toma as decisões finais de arquitetura, gerencia o Event Loop e aprova os artefatos. | Garante o cumprimento do *Dogma do Confinamento de Risco*. |
| **O Orquestrador** | sdd-writing-plans (The Brain) | Arquiteto e Planejador | Escreve o blueprint arquitetural estrito no `.ai/handoffs/current_plan.md`. |
| **O Implementador** | sdd-implementer (The Muscle) | Desenvolvedor Cirúrgico | Lê o plano e executa o código/testes sem desvio de escopo (TDD estrito). |
| **O Auditor** | sdd-auditor (Unified QA) | Garantia de Qualidade | Verifica os dogmas, valida a ausência de regressões e gera o `.ai/handoffs/eod_summary.md`. |
| **O Pesquisador** | NotebookLM | Especialista no Domínio | Mantém a verdade absoluta sobre bibliografias e teoria de MAS imunes a alucinação. |
| **O Cientista** | Google AI Studio | Laboratório de Experimentação | Valida hiperparâmetros e prompts do LLM de forma isolada antes da integração na base. |

**3. O Fluxo de Trabalho Integrado (Ciclo Blackboard)**
Abaixo detalha-se o ciclo de vida para a implementação de uma nova funcionalidade utilizando o Blackboard e as habilidades (skills) `sdd-*`.

**Fase 1: Planning (Planejamento Arquitetural) $\rightarrow$ Orquestrador**
A arquitetura e os contratos são definidos *antes* de qualquer código ser escrito.
* **Ação do Tech Lead:** Invoca a habilidade `sdd-writing-plans` informando o macro-objetivo.
* **Execução:** O Orquestrador analisa a topologia de código, valida contratos (ex: schemas imutáveis do Pydantic V2) e formaliza os passos estruturais.
* **Resultado:** O artefato canônico `.ai/handoffs/current_plan.md` é gerado ou atualizado.

**Fase 2: Implementation (Codificação Cirúrgica) $\rightarrow$ Implementador**
O escopo está fechado. A implementação entra no ambiente de desenvolvimento de forma restrita e mecânica.
* **Ação do Tech Lead:** Invoca a habilidade `sdd-implementer`.
* **Execução:** O Implementador consome o plano e inicia o ciclo RED-GREEN-REFACTOR. A IA escreve o teste que falha, implementa o código determinístico puro (evitando alucinação matemática e a tipagem `Decimal` restrita) e faz o teste passar.
* **Resultado:** Código gerado em conformidade total com o `poetry.lock` e cobertura de testes isolados (`pytest`).

**Fase 3: Audit & Delivery (Auditoria e Fechamento) $\rightarrow$ Auditor**
A validação final contra os dogmas e a consolidação do estado do ciclo.
* **Ação do Tech Lead:** Invoca a habilidade `sdd-auditor`.
* **Execução:** O Auditor escaneia a implementação verificando o *Risk Confinement*, *Controlled Degradation* (regras de `Optional[float] = None`) e Inversão de Controle.
* **Resultado:** Após aprovação plena, o Auditor gera o `.ai/handoffs/eod_summary.md`. O Tech Lead, então, pode executar o push e o merge do artefato final.

**Síntese Operacional:**
O retrabalho e a dívida técnica manifestam-se agressivamente quando restrições de escopo ou limites matemáticos são violados pelo LLM. Mantendo o estado e o plano puramente confinados em `.ai/handoffs/`, a equipe de agentes independentes opera sobre contratos de dados imutáveis, eliminando o drift histórico do modelo RPI legado e garantindo a resiliência assíncrona exigida pelo Aequitas-MAS.