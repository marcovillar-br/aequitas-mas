# 🗺️ AEQUITAS-MAS: SKILL ROUTING INDEX

## Purpose
This document serves as the central registry for all specialized skills available to the AI Assistant. When interacting with the user, cross-reference the user's request with this index to dynamically load the appropriate skill context from the `.context/skills/` or `.ai/skills/` directory.

For `.context/skills/*.md` and `.ai/skills/*/SKILL.md`, the YAML frontmatter is the canonical metadata source. The visible `Name`, `Description`, and `Triggers` sections in skill bodies must remain aligned with that metadata. This index is a human-readable routing map derived from that metadata.

## Registered Skills

| Name | Title | Primary Triggers | Applies To | Priority | File Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `aws-advisor` | AWS Cloud Infrastructure Advisor | cloud infrastructure, aws, terraform, cdk, fargate | architecture, implementation, review | high | `.context/skills/aws-advisor.md` |
| `context-manager` | Context Management Skill (Aequitas-MAS) | resume context, sync state, compliance audit, ssot | documentation, review, session-management | high | `.context/skills/context-manager.md` |
| `domain-analysis` | Domain-Driven Design (DDD) & Architecture | financial analysis, ddd, graham, fisher, marks | architecture, modeling, review | high | `.context/skills/domain-analysis.md` |
| `github-manager` | GitHub & Version Control Manager | git, github, branch, commit, pull request | implementation, collaboration, release-management | medium | `.context/skills/github-manager.md` |
| `playwright` | Playwright Automation & Data Extraction | scraping, playwright, browser automation, data extraction | implementation, data-collection, review | medium | `.context/skills/playwright.md` |
| `sdd-auditor` | SDD Auditor (Evaluator Persona) | audit the code, run qa, sdd audit | review, qa, compliance | high | `.ai/skills/sdd-auditor/SKILL.md` |
| `sdd-implementer` | SDD Implementer (Muscle Persona) | implement the plan, sdd implement | implementation, tdd | high | `.ai/skills/sdd-implementer/SKILL.md` |
| `sdd-writing-plans` | SDD Writing Plans (Orchestrator Persona) | plan this feature, write a plan, sdd plan | planning, architecture | high | `.ai/skills/sdd-writing-plans/SKILL.md` |
| `security` | Security, Compliance & FinOps | security, compliance, finops, secret management | architecture, implementation, review | high | `.context/skills/security.md` |
| `subagent-creator` | Subagent Creator (LangGraph Nodes) | create agent, create node, subagent, langgraph node | architecture, implementation, review | high | `.context/skills/subagent-creator.md` |
| `tech-design-doc` | Technical Design Document (TDD) Creator | tdd, technical design, pre-implementation, mermaid | planning, architecture, documentation | high | `.context/skills/tech-design-doc.md` |

## Routing Protocol
1. Identify the core domain of the user's prompt.
2. Match the request against the skill frontmatter, prioritizing `triggers`, `applies_to`, and `priority`.
3. If the domain matches a registered trigger, silently ingest the corresponding `.md` file into working memory before generating the response.
4. If multiple skills apply, prioritize the strictest or most foundational constraint first.
5. Recommended precedence for overlapping cases:
   - `sdd-writing-plans` must always precede `sdd-implementer`.
   - `tech-design-doc.md` before implementation when the task is still in planning or specification.
   - `subagent-creator.md` when creating or changing LangGraph nodes or agent personas.
   - `security.md` whenever a task touches secrets, runtime isolation, compliance, or cost risk.

## Topology Validation
- Registry scope is exhaustive for every `.md` file currently present under `.context/skills/` and `.ai/skills/`.
- All listed paths resolve to valid local files.
- Registry entries must remain aligned with each skill file's YAML frontmatter and mirrored body metadata.
- This registry is the canonical routing source referenced by the environment.
