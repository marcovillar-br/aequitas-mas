---
plan_id: plan-pre-sprint16-doc-sync-001
target_files:
  - ".context/SPEC.md"
  - "docs/official/Aequitas-MAS_01_Documento_Mestre_Arquitetura_Especificacao_v2_pt-BR.md"
  - ".context/PLAN.md"
  - ".context/current-sprint.md"
enforced_dogmas: [artifact-driven-communication, scope-discipline, ssot]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Pre-Sprint 16 architectural documentation sync. Updates all specification
and architecture artifacts to reflect the Cyclic Graph topology delivered
in Sprint 15 (milestone v2.5).

**This is a DOCUMENTATION-ONLY task. Zero `.py`, `.tf`, `.sh`, or `.yml`
files may be modified.**

Three target documents:

1. **`.context/SPEC.md`** — Replace the linear DAG sequence with the cyclic
   topology. Document `iteration_count`, `reflection_feedback`,
   `_MAX_ITERATIONS=2`, and the `[REFLECTION]` prompt injection.

2. **`docs/official/Aequitas-MAS_01_...v2_pt-BR.md`** — Update the logical
   architecture sections (§2, §4) to reflect the hybrid reflection
   capability. Replace "DAG" with "Cyclic Graph" where appropriate.

3. **`.context/PLAN.md`** — Verify v2.5 is DELIVERED and v3.0 is NEXT.
   Already done in prior commit — verify only, no changes expected.

---

## 2. File Implementation

### Step 2.1 — Update SPEC.md topology and state contracts (artifact-only)

* **Target:** `.context/SPEC.md`
* **Actions:**

  **A — Section 1 (Topologia):**
  Replace the linear sequence:
  ```
  graham -> fisher -> macro -> marks -> core_consensus -> __end__
  ```
  with the cyclic topology:
  ```
  graham -> fisher -> macro -> marks -> core_consensus
                                              |
                            route_after_consensus
                              /              \
                     fisher (loop)        __end__
                  (if cv.p_value > 0.05   (if iter >= 2
                   && iter < 2)            || cv absent
                                           || cv significant)
  ```
  Add invariant: `_MAX_ITERATIONS=2` as domain-level circuit breaker.

  **B — Section 2.1 (AgentState):**
  Add the new fields to the documented contract:
  ```
  iteration_count: int = 0
  reflection_feedback: Optional[str] = None
  signal_significance: Optional[EconometricResult] = None
  cross_validation: Optional[EconometricResult] = None
  ```

  **C — Section 7 (Próxima Extensão):**
  Replace the stale Sprint 14 reference with Sprint 15 delivered scope
  and Sprint 16 (v3.0) as the next target.

---

### Step 2.2 — Update official architecture document (artifact-only)

* **Target:** `docs/official/Aequitas-MAS_01_Documento_Mestre_Arquitetura_Especificacao_v2_pt-BR.md`
* **Actions:**

  **A — Section 2 (Gestão de Estado):**
  Replace "Grafos Acíclicos Direcionados (DAGs)" with "Grafo Cíclico com
  semântica de Comitê Iterativo". Add note about `route_after_consensus`
  and the reflection loop.

  **B — Section 4 (Agentes):**
  Add bullet about the `[REFLECTION — Iteration N]` prompt injection
  capability in Fisher, Macro, and Marks. Note that Graham is excluded
  (quantitative data doesn't change on reflection).

  **C — Section 5 (Critérios de Aceite):**
  Add `_MAX_ITERATIONS=2` as an explicit acceptance criterion (circuit
  breaker for reflection loop).

---

### Step 2.3 — Verify PLAN.md (artifact-only)

* **Target:** `.context/PLAN.md`
* **Action:** Verify v2.5 is marked ✅ DELIVERED and v3.0 is NEXT.
  If already correct, no changes needed.

---

## 3. Definition of Done (DoD)

- [ ] `SPEC.md` Section 1: Cyclic topology documented with ASCII diagram.
- [ ] `SPEC.md` Section 2.1: `iteration_count`, `reflection_feedback`,
  `signal_significance`, and `cross_validation` fields documented.
- [ ] `SPEC.md` Section 7: Updated to Sprint 15 + v3.0 target.
- [ ] `docs/official/...v2_pt-BR.md`: DAG → Cyclic Graph, reflection
  capability documented, circuit breaker in acceptance criteria.
- [ ] `PLAN.md`: v2.5 ✅ DELIVERED, v3.0 NEXT — verified.
- [ ] **HARD CONSTRAINT:** Zero `.py`, `.tf`, `.sh`, or `.yml` files modified.
