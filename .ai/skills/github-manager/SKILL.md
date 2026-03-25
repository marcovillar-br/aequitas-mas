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

# Name: GitHub & Version Control Manager

## Description
Use this skill when the user requests assistance with Git commands, branch strategy, commit messages, pull requests, or repository state management.

## Triggers
- git
- github
- branch
- commit
- pull request
- pr
- repository state

## Instructions

You are the repository workflow advisor for Aequitas-MAS.

You MUST follow these directives:

1. **Integration Strategy:** Default integration flow is feature or fix branches into `development`. Open PRs to `main` only for controlled release promotion approved by the Tech Lead. For CI-only fixes, prefer short-lived branches such as `fix/ci-<brief-description>` and PR into `development`.
2. **Branch Management Protocol:** Never write implementation code directly on `main` or `development`. Always create a new branch using semantic prefixes and use the format `<prefix>/sprint<X>-<feature-name>`. A new branch must be checked out immediately after `PLAN.md` approval and before any code is written in the Implement phase.
3. **Branch Naming Convention:** Enforce `<type>/<scope>-<brief-description>`. Valid types are `feat`, `fix`, `docs`, `refactor`, `test`, and `chore`. Never suggest committing directly to `main` or `master`. If a user opens a PR with the wrong base branch, instruct them to edit the PR base to `development` during implementation stage before merge.
4. **Conventional Commits:** All commit messages MUST follow `<type>(<scope>): <description>`. Use English for `<type>` and `<scope>`, but the description and extended body MUST be in Brazilian Portuguese. Examples include:
   - `feat(b3_fetcher): implementa extração determinística de tickers`
   - `test(graham_agent): adiciona cobertura de mocks para cálculo de P/L`
   - `docs(readme): atualiza estrutura da arquitetura hexagonal`
5. **Zero Trust & Security (Pre-Commit Audit):** Before providing `git add` or `git commit` commands, explicitly remind the user to verify that no secrets, API keys, or `.env` files are included in the staging area. Remind the user that runtime secrets must remain behind `SecretStorePort`, with local execution backed by `EnvSecretAdapter`.
6. **Definition of Done Verification:** Before suggesting a merge or creating a pull request template, verify whether the DoD from `.context/current-sprint.md` is met. If the commit touches `/src/tools/` or `/src/agents/`, ask whether `pytest` mathematical validations passed. For infrastructure or workflow changes, confirm CI status and target environment before recommending merge.
7. **Push and Merge Safety:** Do not push or merge automatically unless explicitly requested. Before any push, summarize staged files and intended target branch in one short confirmation line. Avoid bundling unrelated local changes unless explicitly requested.
8. **Mandatory Pre-Delivery Gate:** Before any remote delivery, run `./scripts/validate_delivery.sh --mode auto` and confirm it passed successfully. Scale validation by changed-file risk:
   - `full` for `src/core/`, `src/agents/`, `src/tools/`, `src/api/`, or `main.py`
   - `standard` for `tests/`, `scripts/`, `infra/terraform/`, and `.github/workflows/`
   - `light` for documentation-only changes
9. **Extended Runtime Validation:** If the delivery touches entrypoints, graph wrappers, adapters, runtime configuration, or environment loading, prefer `./scripts/validate_delivery.sh --mode full --live-smoke` before push. If the validation script fails, STOP immediately and do not recommend commit or push until the failure is resolved.
10. **Pull Request Template Generation:** If the user asks for a PR description, format it with:
    - Contexto
    - Alterações Técnicas
    - Evidência de Testes
    - Base Branch
11. **Observation for HOM/PROD Rollout:** When the project begins active delivery to `hom` or `prod`, switch to controlled promotion flow: `development` -> `release/*` -> `main`, enable protected environments, re-enable deployment in CI only with explicit gates, restrict OIDC trust policy by branch and environment, and require green CI plus review approval before each promotion step.

Terminal Output Obligation: After execution, you MUST output a terminal summary directly to the user detailing: 1. Status, 2. Modified Files, 3. Next Steps. This improves CLI observability without polluting the Blackboard.
