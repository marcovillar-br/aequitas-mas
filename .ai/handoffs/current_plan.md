# 🗺️ Current Plan: Agent Prompt Hardening & Governance

## 1. Objective
Analyze and harden the active prompts in `src/agents/` so the agent layer becomes more consistent, reviewable, and dogma-safe. The next implementation cycle should standardize prompt construction, tighten qualitative boundaries, and eliminate user-facing leakage of internal failures while preserving the current graph topology and deterministic tooling contracts.

## 2. Scope & Constraints
- **Target Files:** `src/agents/core.py`, `src/agents/fisher.py`, `src/agents/graham.py`, `src/agents/macro.py`, `src/agents/marks.py`.
- **Primary Goal:** Prompt governance, not feature expansion.
- **Hard Constraints:**
  - no financial math may move into prompts or LLM-facing logic
  - no regression in `as_of_date` / temporal invariance rules
  - deterministic tools remain the only place for calculations
  - LLM-visible degradation messages must stay stable and user-facing in pt-BR
- **Out of Scope:**
  - graph topology changes
  - new endpoints
  - infrastructure adapters
  - speculative prompt experimentation outside the existing agent roles

## 3. Findings From Prompt Analysis

### 3.1 Prompt Construction Is Inconsistent
- `core.py` and `macro.py` already use `ChatPromptTemplate.from_messages(...)`.
- `marks.py` uses an inline `ChatPromptTemplate.from_template(...)`.
- `graham.py` and `fisher.py` still build prompts as raw strings.
- The resulting agent layer mixes prompt styles and makes review/audit harder than necessary.

### 3.2 Guardrails Are Uneven Across Agents
- `core.py` and `graham.py` are explicit about “no math in prompts”.
- `macro.py` documents Risk Confinement well, but the guardrails are embedded differently across HyDE and synthesis stages.
- `fisher.py` and `marks.py` rely more on descriptive prose than on compact, repeatable guardrail structure.

### 3.3 Failure Output Hygiene Still Needs Cross-Agent Standardization
- `core.py` was recently hardened to keep raw optimizer exceptions out of user-facing rationale.
- `fisher.py` still injects raw exception strings into `key_risks` placeholder outputs.
- `marks.py` still embeds raw exception text into `audit_log` / `marks_verdict`.
- Prompt and failure-governance should be treated as one review surface.

## 4. Implementation Steps (For SDD Implementer)

### Phase 1: Normalize Prompt Topology
- [ ] Extract or refactor each agent prompt into an explicit, reviewable prompt-construction surface.
- [ ] Prefer named helpers or module-level prompt templates over ad-hoc inline string assembly when practical.
- [ ] Ensure every prompt makes these items explicit:
  - agent role
  - allowed evidence
  - forbidden behavior
  - required language (`pt-BR`)
  - expected output contract

### Phase 2: Standardize Dogma Guardrails
- [ ] Review prompts across all five agents and align the language used for:
  - Risk Confinement
  - Controlled Degradation
  - source traceability
  - “do not invent facts / do not invent numbers”
- [ ] Ensure prompt wording does not leave ambiguity about when the model must degrade instead of speculate.

### Phase 3: Harden Failure Messaging Adjacent to Prompts
- [ ] Remove raw internal exception text from user-facing `AIMessage`, `rational`, `marks_verdict`, or placeholder qualitative outputs.
- [ ] Keep technical detail only in structured logs and, when necessary, in audit-facing traces.
- [ ] Preserve stable pt-BR wording for degraded states across agents.

### Phase 4: Regression Coverage
- [ ] Add or update `pytest` coverage for any agent whose failure semantics change.
- [ ] Include explicit tests for:
  - sanitized failure messaging
  - blocked/degraded state shape
  - unchanged deterministic boundaries

## 5. Definition of Done
- Prompt construction across `src/agents/` is materially more consistent and easier to audit.
- No active prompt path allows financial arithmetic or hidden tool substitution by the LLM.
- User-facing degraded outputs no longer leak raw internal exception strings.
- Updated tests cover the new prompt/failure-governance behavior.
- The agent layer remains aligned with the Artifact-Driven Blackboard architecture and the five dogmas.
