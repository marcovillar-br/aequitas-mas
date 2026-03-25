# Documentation Integrity Audit Report

> **Audit Date:** 2026-03-24
> **Protocol:** `.ai/aidd-004-documentation-integrity-audit.md`
> **Exclusion:** `.ai/archive/` — not scanned.
> **Scope:** `.ai/` (excl. archive), `.context/`, repository root `.md` files.

---

## 1. Broken Links Found

### Issue 1.1 — `CLAUDE.md` references deleted `.context/skills/` directory
* **[File Scanned]**: `CLAUDE.md`
  * **Broken Reference**: `.context/skills/`
  * **Line 9 Context**: "Use it to decide when a task requires additional context from `.context/skills/` or `.ai/skills/`."
  * **Line 11 Context**: "Treat the YAML frontmatter in `.context/skills/*.md` and `.ai/skills/*/SKILL.md` as the canonical metadata source..."
  * **Status**: `.context/skills/` was deleted during `plan-migrate-legacy-skills-001`. The `skills-index.md` explicitly states (line 39): "`.context/skills/` is deprecated and must not be referenced as an active routing source."
  * **Severity**: 🔴 HIGH — `CLAUDE.md` is read at the start of every task. It currently instructs routing to a non-existent directory.

### Issue 1.2 — `ADR 001` references archived `.ai/context.md` as current SSOT
* **[File Scanned]**: `.ai/adr/001-ssot-and-lazy-persistence-loading.md`
  * **Broken Reference**: `.ai/context.md`
  * **Line 18 Context**: "We established `.ai/context.md` as the absolute Single Source of Truth for all architectural dogmas."
  * **Status**: `.ai/context.md` was archived to `.ai/archive/context.md`. The current SSOT is `.ai/aidd-001-unified-system-prompt.md`.
  * **Severity**: 🟡 MEDIUM — Historical ADR documenting a past decision; functionally accurate at time of writing but now misleads readers about the active SSOT location.

---

## 2. Architectural Inconsistencies

### Issue 2.1 — `CLAUDE.md` contradicts `skills-index.md` on active routing source
* **[File Scanned]**: `CLAUDE.md`
  * **Issue**: Lines 9 and 11 instruct agents to look for skill context in `.context/skills/`, which the `skills-index.md` (the canonical routing registry) explicitly deprecates. This creates a direct contradiction between two authoritative files.
  * **Recommendation**: Remove all references to `.context/skills/` from `CLAUDE.md`. Retain only `.ai/skills/` as the active routing path.

### Issue 2.2 — `ADR 001` states stale SSOT location
* **[File Scanned]**: `.ai/adr/001-ssot-and-lazy-persistence-loading.md`
  * **Issue**: The ADR body asserts `.ai/context.md` is the current SSOT. Any reader consulting this ADR for architectural guidance receives incorrect information about where canonical dogmas live.
  * **Recommendation**: Add a deprecation notice after the YAML frontmatter and annotate line 18 to note that `.ai/context.md` was superseded by `.ai/aidd-001-unified-system-prompt.md`.

---

## 3. Index Drift Validation

* **[File Scanned]**: `.context/agents/skills-index.md`
* **Result**: ✅ PASS — All 12 registered skills resolve to valid files.

| Skill | Path | Exists |
| :--- | :--- | :---: |
| `aws-advisor` | `.ai/skills/aws-advisor/SKILL.md` | ✅ |
| `context-manager` | `.ai/skills/context-manager/SKILL.md` | ✅ |
| `domain-analysis` | `.ai/skills/domain-analysis/SKILL.md` | ✅ |
| `github-manager` | `.ai/skills/github-manager/SKILL.md` | ✅ |
| `playwright` | `.ai/skills/playwright/SKILL.md` | ✅ |
| `sdd-auditor` | `.ai/skills/sdd-auditor/SKILL.md` | ✅ |
| `sdd-implementer` | `.ai/skills/sdd-implementer/SKILL.md` | ✅ |
| `sdd-reviewer` | `.ai/skills/sdd-reviewer/SKILL.md` | ✅ |
| `sdd-writing-plans` | `.ai/skills/sdd-writing-plans/SKILL.md` | ✅ |
| `security` | `.ai/skills/security/SKILL.md` | ✅ |
| `subagent-creator` | `.ai/skills/subagent-creator/SKILL.md` | ✅ |
| `tech-design-doc` | `.ai/skills/tech-design-doc/SKILL.md` | ✅ |

---

## 4. Semantic & Cognitive Bloat Findings

### Finding 4.1 — `coding-guidelines.md` repeats dogma definitions canonical in `aidd-001`
* **[File Scanned]**: `.context/rules/coding-guidelines.md`
  * **Bloat Issue**: Sections 4, 5, and 6 (lines 41–61) restate Risk Confinement, Controlled Degradation, and Inversion of Control — definitions already canonical in `.ai/aidd-001-unified-system-prompt.md`. Maintenance burden: any update to the dogma in `aidd-001` must be manually synchronized here.
  * **Assessment**: Acceptable redundancy for a rule-oriented normative document. The issue is not duplication per se, but the absence of an explicit cross-reference that would clarify the relationship between the two files.
  * **Recommendation**: Add a note at the top of `coding-guidelines.md` pointing to `aidd-001` as the canonical dogma source, framing `coding-guidelines.md` as the practical implementation rules derived from those dogmas.

### Finding 4.2 — `README.md`: no bloat detected
* **[File Scanned]**: `README.md`
  * **Assessment**: High-level architectural overview is appropriate for a README. No duplication of `SPEC.md` contracts or `aidd-001` dogmas.
  * **Status**: ✅ PASS

### Finding 4.3 — `setup.md`: purely operational, no architectural leakage
* **[File Scanned]**: `setup.md`
  * **Assessment**: Contains only prerequisites, installation, configuration, and quality-gate commands. No dogma definitions or architectural prose.
  * **Status**: ✅ PASS

### Finding 4.4 — `.context/SPEC.md`: correct SSOT for runtime contracts
* **[File Scanned]**: `.context/SPEC.md`
  * **Assessment**: Properly scoped to formal runtime contracts (AgentState, port interfaces, presentation boundaries). No duplication of operational setup or dogma definitions.
  * **Status**: ✅ PASS

---

## 5. Compliance Summary

| Check | Result | Issues |
| :--- | :---: | :--- |
| Broken Links | 🔴 2 found | `CLAUDE.md` (high), `ADR 001` (medium) |
| Architectural Inconsistencies | 🔴 2 found | Same files as above |
| Index Drift (12 skills) | ✅ PASS | None |
| Cognitive Bloat — `setup.md` | ✅ PASS | None |
| Cognitive Bloat — `coding-guidelines.md` | 🟡 Advisory | Cross-reference missing |
| Cognitive Bloat — `README.md`, `SPEC.md` | ✅ PASS | None |
| Stale model references | ✅ PASS | None found in active files |
| Legacy slash command references | ✅ PASS | None found in active files |

---

## 6. Recommended Actions

### Action 1 — Fix `CLAUDE.md` (HIGH — breaking)

In `CLAUDE.md`, apply the following two edits:

**Line 9** — replace:
```
"Use it to decide when a task requires additional context from `.context/skills/` or `.ai/skills/`."
```
with:
```
"Use it to decide when a task requires additional context from `.ai/skills/`."
```

**Line 11** — replace:
```
"Treat the YAML frontmatter in `.context/skills/*.md` and `.ai/skills/*/SKILL.md` as the canonical metadata source for skill routing."
```
with:
```
"Treat the YAML frontmatter in `.ai/skills/*/SKILL.md` as the canonical metadata source for skill routing."
```

---

### Action 2 — Annotate `ADR 001` (MEDIUM — historical accuracy)

In `.ai/adr/001-ssot-and-lazy-persistence-loading.md`, add a deprecation notice after the YAML frontmatter block:

```markdown
> **⚠ SUPERSEDED REFERENCE:** This ADR was written when `.ai/context.md` served as the
> SSOT. That file has since been archived to `.ai/archive/context.md`. The current
> canonical SSOT for all architectural dogmas is `.ai/aidd-001-unified-system-prompt.md`.
```

---

### Action 3 — Add cross-reference note to `coding-guidelines.md` (ADVISORY)

At the top of `.context/rules/coding-guidelines.md`, after the opening blockquote, add:

```markdown
> **Dogma Source:** The canonical definitions of all non-negotiable dogmas (Risk
> Confinement, Controlled Degradation, Temporal Invariance, Inversion of Control) live
> in `.ai/aidd-001-unified-system-prompt.md`. This file focuses on the practical
> implementation rules and coding patterns derived from those dogmas.
```
