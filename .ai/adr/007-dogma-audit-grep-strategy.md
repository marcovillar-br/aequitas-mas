# ADR 007: Dogma Audit Strategy (MVP) — Static Grep in CI/CD

## Status
Accepted (Sprint 3.3 preparation, 2026-03-10).

## 1. Context

Aequitas-MAS enforces two non-negotiable architectural dogmas at code level:

1. **Controlled Degradation dogma:** `decimal.Decimal` is forbidden in `src/agents/` and
   `src/core/` state-facing layers.
2. **Dependency Inversion dogma:** `boto3` imports are forbidden in `src/agents/` and
   `src/core/`; cloud SDKs must stay in `src/infra/adapters/`.

These constraints must be enforced automatically in every PR, with minimal CI overhead.
For MVP, the team evaluated:

| Approach | Pros | Cons |
|---|---|---|
| **Static `grep -E` in GitHub Actions** | Zero dependencies, fast, transparent | Limited semantic awareness (no AST) |
| AST/linter custom rule | Stronger semantic coverage | Higher implementation/maintenance cost for current sprint |

## 2. Decision

For MVP, we keep dogma audits in CI as **static `grep -E` checks** inside the
`quality` job of `.github/workflows/pipeline.yml`.

Additionally, this sprint records and addresses a known blind spot: explicit alias import forms.
The decision is to **expand the regex set in the current sprint** to include alias-oriented
patterns, specifically:

- Decimal alias pattern: `from decimal import.*Decimal.*as`
- boto3 alias pattern: `import boto3.*as`

This keeps enforcement lightweight while reducing false negatives without introducing new tools.

## 3. Technical Debt Registration

Static grep remains an intentional compromise. Even with expanded regex, the following
limitations are documented as technical debt:

- Dynamic imports (`__import__`, `importlib`) are not reliably detectable via regex.
- Indirect re-export patterns can bypass simple text matching.
- Regex checks do not understand Python scope or execution semantics.

## 4. Consequences

**Positive**
- Fast and deterministic dogma gate in CI for every PR.
- No extra dependency/plugin burden in the pipeline.
- Immediate mitigation of alias-import blind spots in the current sprint.

**Negative**
- Coverage is still lexical, not semantic.
- Long-term robustness may require migration to AST-based enforcement.

## 5. Migration Trigger

Migrate from grep to AST-level enforcement (Ruff custom rule or equivalent) when either:
- a real violation escapes CI due to regex limitations, or
- repository scale/complexity makes lexical checks insufficient.

## 6. Implementation Reference

- `.github/workflows/pipeline.yml` — `quality` job, "Dogma Audit" steps.
- Scope audited: `src/agents/` and `src/core/` only.
- Allowed exception zone: `src/infra/adapters/` for infrastructure SDK imports.
