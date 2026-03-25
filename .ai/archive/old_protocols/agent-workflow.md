# 🏭 Aequitas-MAS: Agent Factory Quick Reference

**Architecture:** Artifact-Driven Blackboard Architecture
**Role:** Tech Lead (Human Event Loop)

---

## 🛑 PHASE 0: Pre-Flight Check (Tech Lead)
1. Certifique-se de que a branch está limpa (`git status`).
2. Verifique o objetivo atual em `.context/current-sprint.md`.
3. Garanta que a pasta `.ai/handoffs/` existe e está limpa de planos obsoletos.

---

## 🧠 PHASE 1: The Brain (Planning)
**Agente:** `aequitas-mas-orchestrator` (GCA)
**Objetivo:** Gerar a arquitetura matemática/lógica sem tocar em código.
**Ação:** Copie e cole o prompt abaixo no chat do Orquestrador:

> @aequitas-mas-orchestrator
> [SYSTEM TASK: ARTIFACT-DRIVEN PLANNING]
> 
> We are executing [INSERIR SPRINT E STEP AQUI]. You operate strictly on the Artifact-Driven Blackboard Architecture. You are FORBIDDEN from generating Python code. 
> 
> **Task:** Write the architectural plan into `.ai/handoffs/current_plan.md`.
> **Directives:**
> 1. Target files: [INSERIR ARQUIVOS ALVO]
> 2. Enforce Risk Confinement: No LLM mental math.
> 3. Enforce Defensive Typing: Pydantic V2 `frozen=True`, `Optional[float] = None`.
> 4. Enforce Temporal Invariance: Demand `as_of_date` (ADR 011).
> 5. Ban Decimal-based state values and demand `math.isfinite()`.
> 
> Write the file now and reply with "PLAN COMPLETE. ARTIFACT SAVED."

---

## 💪 PHASE 2: The Muscle (Implementation)
**Agente:** `aequitas-mas-implementer` (Codex)
**Objetivo:** Traduzir o plano em Python estrito e testes unitários.
**Ação:** Copie e cole o prompt abaixo no chat do Implementador:

> @aequitas-mas-implementer
> [SYSTEM TASK: ARTIFACT-DRIVEN IMPLEMENTATION]
> 
> **Execution Directives:**
> 1. **Read the Artifact:** Read the ENTIRE contents of `.ai/handoffs/current_plan.md`.
> 2. **Implement Source Code:** Generate the Python code exactly as planned. Enforce Defensive Typing and Risk Confinement (ban Decimal-based state values).
> 3. **Implement Tests:** Generate SOTA tests in `tests/` using `unittest.mock.patch`. Test both happy paths and controlled degradation (fallback) paths.
> 4. **Apply Changes:** Write directly to the workspace. Do not ask for permission.
> 
> Reply exactly with "IMPLEMENTATION COMPLETE." once files are saved.

---

## 🛡️ PHASE 3: The Gatekeeper (Validation)
**Agente:** Tech Lead (Terminal Humano)
**Objetivo:** Provar matematicamente que a entrega não quebrou o sistema.
**Ação:** Execute no terminal:

```bash
./scripts/validate_delivery.sh --mode auto
```
*Se falhar: Devolva o erro ao Implementador (Codex) e mande corrigir. Se passar (100% testes e Ruff), siga para a Fase 4.*

---

## 🔎 PHASE 4: The Inspector (Audit & Consolidation)
**Agente:** `aequitas-mas-auditor` (CGCA)
**Objetivo:** Auditar dogmas e documentar o fim do dia (EOD).
**Ação:** Copie e cole o prompt abaixo no chat do Auditor:

> @aequitas-mas-auditor
> [SYSTEM TASK: ARTIFACT-DRIVEN AUDIT & EOD SUMMARY]
> 
> The Codex Implementer finished the implementation for [INSERIR SPRINT/STEP]. The CI/CD validation script PASSED 100%.
> 
> **Audit Directives:**
> 1. **Analyze:** Review the newly written code in `src/` and `tests/`.
> 2. **Verify Dogmas:** Confirm the absence of Decimal-based state values and the presence of `math.isfinite()` and ADR 011 (`as_of_date`).
> 3. **Generate EOD Report:** Write a technical Markdown summary detailing the logic implemented, the schemas used, and the test results.
> 4. **Save Artifact:** Save this directly to `.ai/handoffs/eod_summary.md` (or specific sprint EOD file).
> 
> Reply with "AUDIT COMPLETE. EOD ARTIFACT SAVED."

---

## 💾 PHASE 5: The Commit (End of Cycle)
**Agente:** Tech Lead (Terminal Humano)
**Objetivo:** Versionar o estado limpo do repositório.
**Ação:**

```bash
git add .
git commit -m "feat(scope): implement [NOME DA FEATURE] via artifact-driven MAS"
git push
```
*(Atualize também o `.context/current-sprint.md` se a etapa/sprint for concluída).*
```
