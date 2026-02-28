# SKILL: GITHUB & VERSION CONTROL MANAGER

## 1. Trigger
Activate this skill when the user requests assistance with Git commands, creating branches, writing commit messages, structuring Pull Requests, or managing repository state.

## 2. Core Directives

### 2.1. Branch Naming Convention
* Enforce a structured, standard naming convention for all branches: `<type>/<scope>-<brief-description>`.
* **Valid types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
* **Example:** `feat/graham-valuation-tool`, `test/b3-fetcher-mocks`, `docs/academic-methodology`.
* NEVER suggest committing directly to the `main` or `master` branch. Always suggest working on a specific branch.

### 2.2. Conventional Commits (Semantic Commits)
* All commit messages MUST follow the Conventional Commits specification.
* **Format:** `<type>(<scope>): <description>`
* **Language Rule for Commits:** Use English for the `<type>` and `<scope>` to maintain compatibility with standard CI/CD release tools. However, the `<description>` and any extended body MUST be in **Brazilian Portuguese (pt-BR)** to align with the UFG academic documentation.
* **Examples:** - `feat(b3_fetcher): implementa extração determinística de tickers`
  - `test(graham_agent): adiciona cobertura de mocks para cálculo de P/L`
  - `docs(readme): atualiza estrutura da arquitetura hexagonal`

### 2.3. Zero Trust & Security (Pre-Commit Audit)
* **CRITICAL SECURITY RULE:** Before providing `git add` or `git commit` commands, explicitly remind the user to verify that NO secrets, API keys (AWS, Anthropic, OpenAI), or `.env` files are included in the staging area.
* Remind the user of the "Secret Management" dogma (Section 4.2 of ETD v5.0) which dictates the exclusive use of Google IDX Secret Manager or local environment variables injected at runtime.

### 2.4. Definition of Done (DoD) Verification
* Before suggesting a merge or creating a Pull Request template, verify if the DoD from `.context/current-sprint.md` is met.
* If the commit involves the `/src/tools/` or `/src/agents/` directories, ask the user if the `pytest` mathematical validations have passed successfully.

## 3. Pull Request Template Generation
If the user asks to generate a PR description, format it clearly with:
1. **Contexto:** Qual problema esta PR resolve?
2. **Alterações Técnicas:** Lista de mudanças baseadas na arquitetura hexagonal.
3. **Evidência de Testes:** Confirmação de que `poetry run pytest` foi executado.