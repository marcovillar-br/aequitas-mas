# 🗺️ Current Plan: Documentation Integrity Audit & Sprint 8 Closure

## 1. Objective
Realizar uma auditoria abrangente da documentação e limpeza para eliminar 'Context Poisoning' e otimizar o Signal-to-Noise Ratio para os agentes. Encerrar oficialmente a Sprint 8, atualizando os documentos arquiteturais chave para refletir as entregas.

## 2. Scope & Constraints
- **Diretórios Alvo:** `.ai/handoffs/`, `.ai/adr/`, `.context/`, `docs/official/`, `README.md`.
- **Exclusão:** O diretório `.ai/archive/` e seus subdiretórios devem ser ignorados.
- **Alinhamento com Blackboard:** Todas as atualizações devem reforçar a Arquitetura de Blackboard Orientada a Artefatos.
- **Sem Alucinação de LLM:** O Implementador deve seguir estritamente o plano, sem inferir mudanças adicionais.

## 3. Implementation Steps (For SDD Implementer)

### Step 1: Correção Crítica de Bug (Pré-Fechamento da Sprint 8)
- [x] **Aplicar Patch em `src/agents/core.py`:** Implementar a correção identificada na auditoria anterior para garantir que `optimization_blocked=True` seja definido em **todas** as ramificações de falha do otimizador.

```diff
--- a/home/marco/projects/aequitas-mas/src/agents/core.py
+++ b/home/marco/projects/aequitas-mas/src/agents/core.py
@@ -134,6 +134,7 @@
             "audit_log": [f"[Core/Consensus] {rationale}"],
             "messages": [AIMessage(content=rationale, name="core_consensus")],
             "executed_nodes": ["core_consensus"],
+            "optimization_blocked": True,
        }

    try:
@@ -155,6 +156,7 @@
             "audit_log": [f"[Core/Consensus] {rationale}"],
             "messages": [AIMessage(content=rationale, name="core_consensus")],
             "executed_nodes": ["core_consensus"],
+            "optimization_blocked": True,
        }

    if decision.approval_status == "block":
```

### Step 2: Poda de Arquivos Obsoletos
- [x] **Deletar Manual Legado:** Executar `git rm docs/official/Aequitas-MAS_50_Manual_Engenharia_Fluxo_Trabalho_RPI_SDD_v2_pt-BR.md`. (Este arquivo foi substituído pela versão v3 do manual Blackboard).

### Step 3: Atualizar Status da Sprint e Documentação Principal
- [x] **Atualizar `.context/current-sprint.md`:**
  - Marcar o Step 3 como concluído: `[x] Step 3: Graph Integration (resilient optimizer integration in core_consensus_node, ensuring optimization_blocked=True and logging rationale upon degradation).`
  - Mudar o status da Sprint 8 para `DONE`.
  - Atualizar os Macro-Objetivos da Sprint 8 para refletir a entrega bem-sucedida do endpoint `/portfolio` determinístico e da integração resiliente no `core_consensus_node`.
- [x] **Atualizar `README.md`:**
  - Na seção "Next", atualizar "Sprint 8: TBD" para "Sprint 8: Portfolio API & Resilient Graph Integration (DONE)".
  - Adicionar um breve resumo das entregas chave da Sprint 8 (ex: endpoint `/portfolio` determinístico, `core_consensus_node` resiliente).
- [x] **Atualizar `.context/PLAN.md`:**
  - Remover as seções "Immediate Priority" e "Próximos passos", pois estão obsoletas.
  - Atualizar o status da "Sprint 7 Closed — Real Data Ingestion & Dynamic Constraints" para `DONE`.
  - Adicionar uma nova seção para "Sprint 8 — Portfolio API & Resilient Graph Integration" com seu status como `DONE` e um resumo de suas entregas.
  - Garantir que não haja resquícios do fluxo "RPI" nas seções de planejamento ativas.
- [x] **Atualizar `.context/SPEC.md`:**
  - Revisar a Seção 2.4 "Contrato do Supervisor" para garantir que esteja totalmente alinhada com a integração resiliente do otimizador e a flag `optimization_blocked=True`.
  - Garantir que não haja referências diretas ao fluxo "RPI" ou à toolchain fragmentada na especificação ativa.
- [x] **Atualizar `setup.md`:**
  - Na Seção 1 "Engineering Team Topology", garantir que a descrição do GCA esteja alinhada com a Arquitetura de Blackboard e o uso de `.ai/handoffs/current_plan.md`.
  - Na Seção 9 "API Runtime", atualizar a lista de endpoints ativos para incluir `POST /portfolio`.
  - Revisar "System Version" e "Architecture Version" para ver se precisam ser atualizados para `6.0.0` e `3.0` respectivamente, refletindo as entregas da Sprint 8 e a arquitetura Blackboard.

### Step 4: Auditoria Final e Resumo de Fim de Dia (EOD)
- [x] **Executar SDD Auditor:** Após todas as modificações, acionar a skill `sdd-auditor` para realizar uma auditoria final de integridade da documentação.
- [x] **Gerar Resumo EOD:** Criar um novo `.ai/handoffs/eod_summary.md` resumindo a conclusão da limpeza da documentação e o encerramento da Sprint 8.

## 4. Definition of Done
- O bug crítico em `src/agents/core.py` foi corrigido.
- Todos os artefatos de documentação obsoletos foram deletados ou arquivados corretamente.
- `README.md` e `.context/current-sprint.md` refletem com precisão o encerramento da Sprint 8.
- `.context/PLAN.md` e `.context/SPEC.md` estão totalmente modernizados e livres de resquícios do RPI.
- Uma auditoria final da documentação confirma a ausência de links quebrados ou inconsistências.
- Um `eod_summary.md` abrangente para esta limpeza e encerramento da Sprint 8 foi gerado.
