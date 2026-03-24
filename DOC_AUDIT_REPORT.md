# Documentation Integrity Audit Report

## 1. Broken Links Found
* **[File Scanned]**: `.ai/aidd-003-tech-lead-mentor-prompt.md`
  * **Broken Reference**: `.ai/SPEC.md`
  * **Line Context**: "1. **Verify Context:** Ensure `.ai/aidd-001-unified-system-prompt.md` is loaded. Update `.ai/SPEC.md` with the new quantitative/business requirements." (Also found in step 2: "... based on .ai/SPEC.md...")

* **[File Scanned]**: `setup.md`
  * **Broken Reference**: `PLAN.md`, `SPEC.md`
  * **Line Context**: "- **GEM (Architect):** owner of `PLAN.md`, `SPEC.md`, and architectural direction."

## 2. Architectural Inconsistencies
* **[File Scanned]**: `.ai/aidd-003-tech-lead-mentor-prompt.md`
  * **Issue**: Incorrectly references `.ai/SPEC.md`, violating the actual project topology where specifications reside in `.context/`. This will cause context retrieval failure during orchestration.
  * **Recommendation**: Rewrite the instructions to point explicitly to `.context/SPEC.md`.

## 3. Semantic & Cognitive Bloat Findings
* **[File Scanned]**: `setup.md`
  * **Bloat Issue**: Severe architectural leakage. Mixes operational instructions with deep architectural theory (Engineering Team Topology, Secret Management & Zero Trust, Risk Confinement, Time-Aware Backtesting, and Cloud Agnosticism).
  * **Recommendation**: Consolidate the architectural dogmas and system contracts into `.context/SPEC.md` or `.ai/aidd-001-unified-system-prompt.md`. Reduce `setup.md` strictly to actionable operational guidance (`git clone`, `poetry install`, `export` commands, API startup).

* **[File Scanned]**: `.context/rules/coding-guidelines.md`
  * **Bloat Issue**: Repeats redundant domain theory in "Section 4. State Management & Controlled Degradation" and "Section 6. Security & Cloud Agnosticism".
  * **Recommendation**: Reduce the text to strictly actionable coding rules (e.g., "Use `Optional[float] = None`", "Do not import `boto3`") and remove the philosophical explanations already present in the unified system prompt.

* **[File Scanned]**: `.context/domain/personas.md`
  * **Bloat Issue**: Contains a redundant "Non-Negotiable Dogmas" section at the bottom, duplicating rules explicitly defined in the core `.ai/aidd-001-unified-system-prompt.md`.
  * **Recommendation**: Remove the duplicated dogmas section to rely purely on the unified system prompt as the Single Source of Truth (SSOT).

## 4. Recommended Actions
Execute the following exact terminal commands to resolve the referential integrity issues:

```bash
sed -i 's/\.ai\/SPEC\.md/.context\/SPEC.md/g' .ai/aidd-003-tech-lead-mentor-prompt.md
sed -i 's/of `PLAN\.md`, `SPEC\.md`/of `.context\/PLAN.md`, `.context\/SPEC.md`/g' setup.md
```

**To resolve Semantic and Cognitive Bloat:**
Trigger the `sdd-writing-plans` skill to process this audit and generate a `plan-doc-semantic-refactor-002` targeting `setup.md`, `.context/rules/coding-guidelines.md`, and `.context/domain/personas.md` for pruning and consolidation.