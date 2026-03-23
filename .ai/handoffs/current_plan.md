# 🗺️ Current Plan: Modernize Official SDD Workflow Documentation

## 1. Objective
Update the official engineering manual and legacy operational ADR to fully reflect the Aequitas-MAS Artifact-Driven Blackboard architecture, formally deprecating the fragmented RPI (Research, Plan, Implement) toolchain.

## 2. Scope & Constraints
- **Target 1:** `docs/official/Aequitas-MAS_50_Manual_Engenharia_Fluxo_Trabalho_RPI_SDD_v2_pt-BR.md`
  - Upgrade version from v2.0 to v3.0.
  - Replace legacy RPI terminology with the new Superpowers SDD Workflow (Orchestrator, Implementer, Auditor).
  - Update artifact references to `.ai/handoffs/current_plan.md` and `.ai/handoffs/eod_summary.md`.
- **Target 2:** `.ai/adr/006-agnostic-operational-flow.md`
  - Ensure the deprecation notice comprehensively explains the shift to the Artifact-Driven Blackboard and cross-references the new manual.

## 3. Implementation Steps (For SDD Implementer)

### Step 1: Update the Official Manual (pt-BR)
- [ ] Rename the file to remove "RPI" and add "Blackboard" (e.g., `Aequitas-MAS_50_Manual_Engenharia_Fluxo_Trabalho_Blackboard_SDD_v3_pt-BR.md`).
- [ ] Rewrite Section 2 to define the new unified roles: Orchestrator (The Brain), Implementer (The Muscle), and Auditor (Unified QA).
- [ ] Rewrite Section 3 to map the Blackboard workflow phases (Planning -> Implementation -> Audit) instead of Research -> Plan -> Implement.

### Step 2: Reinforce ADR 006 Deprecation
- [ ] Review `.ai/adr/006-agnostic-operational-flow.md` and append a concluding section formally linking to the v3.0 manual in `docs/official/` for historical traceability.

## 4. Definition of Done
- The official pt-BR manual correctly instructs users on the Artifact-Driven Blackboard topology.
- All references to the legacy RPI flow are removed from active instructional text.
- The legacy ADR 006 is firmly closed and cross-referenced with the new topology.