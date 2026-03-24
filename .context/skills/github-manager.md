---
name: github-manager
description: Skill for branch strategy, conventional commits, pull requests, and repository state management.
metadata:
  title: GitHub & Version Control Manager
  triggers:
    - git
    - github
    - branch
    - commit
    - pull request
    - pr
    - repository state
  tags:
    - git
    - github
    - version-control
    - workflow
    - ci-cd
  applies_to:
    - implementation
    - collaboration
    - release-management
  language: en
  output_language: pt-BR
  priority: medium
  status: active
  version: 1
---

# SKILL: GITHUB & VERSION CONTROL MANAGER

## 1. Trigger
Activate this skill when the user requests assistance with Git commands, creating branches, writing commit messages, structuring Pull Requests, or managing repository state.

## 2. Core Directives

### 2.0. Integration Strategy (Current Project Stage)
* Default integration flow is feature/fix branches into `development`.
* Open PRs to `main` only for controlled release promotion approved by the Tech Lead.
* For CI-only fixes (workflow/OIDC), prefer short-lived branches such as `fix/ci-<brief-description>` and PR into `development`.

### 2.1. Branch Management Protocol
* **Mandatory Isolation:** Never write implementation code directly on the `main` or `development` branches.
* **Naming Convention:** Always create a new branch using semantic prefixes: `feat/`, `fix/`, `chore/`, or `docs/`.
* **Branch Format:** `<prefix>/sprint<X>-<feature-name>`.
* **Timing:** A new branch must be checked out immediately after `PLAN.md` is approved and BEFORE any code is written in the Implement phase.

### 2.2. Branch Naming Convention
* Enforce a structured, standard naming convention for all branches: `<type>/<scope>-<brief-description>`.
* **Valid types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
* **Example:** `feat/graham-valuation-tool`, `test/b3-fetcher-mocks`, `docs/academic-methodology`.
* NEVER suggest committing directly to the `main` or `master` branch. Always suggest working on a specific branch.
* If a user opens a PR with wrong base branch, instruct to edit PR base to `development` (when in implementation stage) before merge.

### 2.3. Conventional Commits (Semantic Commits)
* All commit messages MUST follow the Conventional Commits specification.
* **Format:** `<type>(<scope>): <description>`
* **Language Rule for Commits:** Use English for the `<type>` and `<scope>` to maintain compatibility with standard CI/CD release tools. However, the `<description>` and any extended body MUST be in **Brazilian Portuguese (pt-BR)** to align with the UFG academic documentation.
* **Examples:** - `feat(b3_fetcher): implementa extração determinística de tickers`
  - `test(graham_agent): adiciona cobertura de mocks para cálculo de P/L`
  - `docs(readme): atualiza estrutura da arquitetura hexagonal`

### 2.4. Zero Trust & Security (Pre-Commit Audit)
* **CRITICAL SECURITY RULE:** Before providing `git add` or `git commit` commands, explicitly remind the user to verify that NO secrets, API keys (AWS, Anthropic, OpenAI), or `.env` files are included in the staging area.
* Remind the user that runtime secrets must remain behind the project's secret-store boundary (`SecretStorePort`), with local execution currently backed by `EnvSecretAdapter`.
* For GitHub OIDC troubleshooting, prefer temporary debug logs and remove them after 1-2 successful runs.
* During early development stage, avoid automatic `terraform apply` in CI to prevent accidental deployment and unnecessary cloud costs.

### 2.5. Definition of Done (DoD) Verification
* Before suggesting a merge or creating a Pull Request template, verify if the DoD from `.context/current-sprint.md` is met.
* If the commit involves the `/src/tools/` or `/src/agents/` directories, ask the user if the `pytest` mathematical validations have passed successfully.
* For infrastructure/workflow changes, confirm CI status and target environment (`dev`/`hom`/`prod`) before merge recommendation.

### 2.6. Push and Merge Safety
* Do not push or merge automatically unless the user explicitly requests it.
* Before any push, summarize staged files and intended target branch in one short confirmation line.
* If there are unrelated local changes, avoid bundling them in the same commit unless user explicitly asks.
* **Mandatory Pre-Delivery Gate:** Before any remote delivery (`git push`), run `./scripts/validate_delivery.sh --mode auto` and confirm it passed successfully.
* **Risk-Based Validation:** Allow the gate to scale by changed-file risk:
  - `full` for `src/core/`, `src/agents/`, `src/tools/`, `src/api/`, or `main.py`
  - `standard` for `tests/`, `scripts/`, `infra/terraform/`, and `.github/workflows/`
  - `light` for documentation-only changes
* **Extended Runtime Validation:** If the delivery touches entrypoints, graph wrappers, adapters, runtime configuration, or environment loading, prefer `./scripts/validate_delivery.sh --mode full --live-smoke` before push.
* If the validation script fails, STOP immediately. Do not recommend commit or push until the failure is resolved.

## 3. Pull Request Template Generation
If the user asks to generate a PR description, format it clearly with:
1. **Contexto:** Qual problema esta PR resolve?
2. **Alterações Técnicas:** Lista de mudanças baseadas na arquitetura hexagonal.
3. **Evidência de Testes:** Confirmação de que `poetry run pytest` foi executado.
4. **Base Branch:** Confirmação explícita de `base=development` (ou justificativa formal para `main`).

## 4. Observation: When HOM/PROD Rollout Starts
When the project begins active delivery to `hom`/`prod`, switch from dev-only flow to controlled promotion flow:
1. Promote in sequence: `development` -> `release/*` (HOM) -> `main` (PROD).
2. Enable protected environments in GitHub (`hom` and `prod`) with required human approval.
3. Re-enable deployment in CI only with explicit gate (`workflow_dispatch` or release-tag strategy).
4. Keep OIDC trust policy restricted by branch/event and environment-specific role.
5. Require green CI and review approval before each promotion step.
