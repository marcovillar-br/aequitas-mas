# ADR 007: Dogma Audit Strategy — Static Grep in CI/CD

## 1. Context

The Aequitas-MAS architecture enforces two non-negotiable Risk Confinement dogmas:

1. **Dogma 3.2 (Controlled Degradation):** `decimal.Decimal` is forbidden in LangGraph state
   schemas (`src/agents/`, `src/core/`). Violations break JSON serialization with DynamoDB.
2. **Dogma 3.3 (DIP):** Cloud SDK imports (`boto3`) are forbidden in `src/agents/` and
   `src/core/`. Infrastructure interactions must be abstracted behind `src/infra/adapters/`.

These rules must be enforced automatically at every pull request. Two approaches were evaluated:

| Approach | Pros | Cons |
|---|---|---|
| **Static `grep` in GitHub Actions** | Zero dependencies, portable, fast, human-readable | Cannot detect dynamic imports or aliased imports |
| Custom Ruff plugin / AST analysis | Full import graph analysis, catches all alias forms | Requires plugin development; significant complexity for MVP |

## 2. Decision

We adopt **static `grep -E` patterns in the `quality` job of `.github/workflows/pipeline.yml`**
as the dogma enforcement mechanism for the MVP phase.

The patterns are expanded beyond the initial implementation to explicitly catch alias imports,
reducing the known false-negative surface:

**Dogma Audit 1 (Decimal):**
```
(decimal\.Decimal|from decimal import.*Decimal)
```

**Dogma Audit 2 (boto3):**
```
(import boto3|from boto3\b)
```

This approach is **pragmatic for MVP**: it covers the primary import forms used in this
codebase, adds zero dependencies, and executes in under 1 second in CI.

**Known limitations (registered as technical debt):**
- Dynamic imports: `__import__('boto3')` — not caught.
- Module alias: `import boto3 as b3` — the `import boto3` pattern catches `import boto3 as b3`
  since the pattern matches the prefix. `from boto3 as` is not a valid Python syntax, so this
  is a non-issue.
- Wildcard re-export: `from src.infra.adapters import boto3_client` — not caught, but this
  form would violate the naming convention and be caught in code review.

## 3. Consequences

**Positive:**
- Dogma violations are blocked at PR merge time — no manual review dependency.
- Zero additional packages or plugins required in the CI environment (`poetry install --without infra`).
- Patterns are human-readable and auditable by any team member.
- CI execution overhead: < 1 second per audit step.

**Negative:**
- Limited coverage of advanced import patterns (see Known Limitations above).
- As the agent count grows, `src/agents/` expands — each new agent module is automatically
  covered by the existing `grep` scope (no maintenance required per agent).

## 4. Migration Path (Technical Debt)

When the codebase grows beyond **6 agent modules**, or if a dogma violation is discovered
in production that was missed by grep, migrate to one of:

- **Ruff custom rule** (`src/` plugin): AST-based, catches all import forms.
- **`import-linter`** (pre-commit + CI): contract-based import graph enforcement.

This migration requires no architectural changes — only the `quality` job step changes.

## 5. Implementation Reference

- `.github/workflows/pipeline.yml` — Steps "Dogma Audit 1" and "Dogma Audit 2".
- Patterns audited in: `src/agents/` and `src/core/` (not `src/infra/`, where boto3 is allowed).
