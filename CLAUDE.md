# AEQUITAS-MAS — Claude Code Instructions

## Mandatory Context Loading (Execute Before Any Task)

Before writing any code, plan, or analysis, you MUST read the following files in order:

1. **`.ai/aidd-001-unified-system-prompt.md`** — Canonical SSOT: project identity, architecture, full dogma definitions, and key entry points. This is the single authoritative source for all architectural rules.
2. **`.context/rules/coding-guidelines.md`** — Authoritative rules for stack, typing, naming, testing, and security. These rules override all default Claude behaviors.
3. **`.context/agents/skills-index.md`** — Central routing map for specialized skills. Use it to decide when a task requires additional context from `.context/skills/` or `.ai/skills/`.

Treat the YAML frontmatter in `.context/skills/*.md` and `.ai/skills/*/SKILL.md` as the canonical metadata source for skill routing. Keep the visible body sections aligned with that metadata.

Do not proceed with any task until these files have been read and their constraints are active in your working context.

---

## CRITICAL DOGMAS (Quick Reference — canonical source: `.ai/aidd-001-unified-system-prompt.md`)

Violation of any rule below is a hard architectural error. Stop and correct before continuing.

- **FORBIDDEN:** `decimal.Decimal` in LangGraph state schemas. Use `Optional[float] = None`.
- **FORBIDDEN:** `boto3` or cloud SDKs inside `/src/agents/` or `/src/core/`. Use `/src/infra/adapters/`.
- **FORBIDDEN:** Financial calculations inside LLM prompts or agent nodes. Delegate to `/src/tools/`.

---

## Language Protocol

- **Code, variables, docstrings, comments, commit messages:** English.
- **All user-facing output and chat responses:** Brazilian Portuguese (pt-BR).

## Architecture at a Glance

- Hexagonal (Ports & Adapters) + DDD, orchestrated via LangGraph stateful DAGs.
- State: Pydantic V2 `BaseModel` with `ConfigDict(frozen=True)`. Financial fields: `Optional[float] = None`.
- Agent DI: factory closures (`create_<agent>(dependency)`) injected at `src/core/graph.py`.
- Test suite: `poetry run pytest` — maintain 0 regressions at all times.

## Artifact-Driven Blackboard Workflow (Superpowers)

We no longer use legacy slash commands. All non-trivial tasks MUST follow the Artifact-Driven Blackboard topology using Superpowers skills:
1. **Plan:** Trigger the `sdd-writing-plans` skill to generate `.ai/handoffs/current_plan.md`.
2. **Implement:** Trigger the `sdd-implementer` skill to execute the plan via RED-GREEN-REFACTOR TDD.
3. **Audit:** Trigger the `sdd-auditor` skill to verify dogma compliance before committing.
