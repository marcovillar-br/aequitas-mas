# 🗺️ AEQUITAS-MAS: SKILL ROUTING INDEX

## Purpose
This document serves as the central registry for all specialized skills available to the AI Assistant. When interacting with the user, cross-reference the user's request with this index to dynamically load the appropriate skill context from the `.ai/skills/` directory.

For `.ai/skills/*/SKILL.md`, the YAML frontmatter is the canonical metadata source. Use `name` and `description` as the required top-level fields, and place any extra routing hints under `metadata`. The visible `Name`, `Description`, and `Triggers` sections in skill bodies must remain aligned with that metadata. This index is a human-readable routing map derived from that metadata.

## Registered Skills

| Name | Title | Primary Triggers | Applies To | Priority | File Path |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `aws-advisor` | AWS Cloud Infrastructure Advisor | cloud infrastructure, aws, terraform, cdk, fargate | architecture, implementation, review | high | `.ai/skills/aws-advisor/SKILL.md` |
| `context-manager` | Context Management Skill (Aequitas-MAS) | resume context, sync state, compliance audit, ssot | documentation, review, session-management | high | `.ai/skills/context-manager/SKILL.md` |
| `domain-analysis` | Domain-Driven Design (DDD) & Architecture | financial analysis, ddd, graham, fisher, marks | architecture, modeling, review | high | `.ai/skills/domain-analysis/SKILL.md` |
| `github-manager` | GitHub & Version Control Manager | git, github, branch, commit, pull request | implementation, collaboration, release-management | medium | `.ai/skills/github-manager/SKILL.md` |
| `playwright` | Playwright Automation & Data Extraction | scraping, playwright, browser automation, data extraction | implementation, data-collection, review | medium | `.ai/skills/playwright/SKILL.md` |
| `sdd-auditor` | SDD Auditor (Evaluator Persona) | audit the code, run qa, sdd audit | review, qa, compliance | high | `.ai/skills/sdd-auditor/SKILL.md` |
| `sdd-implementer` | SDD Implementer (Muscle Persona) | implement the plan, sdd implement | implementation, tdd | high | `.ai/skills/sdd-implementer/SKILL.md` |
| `sdd-reviewer` | SDD Code Reviewer (The Shield) | review the code, run the shield, gate the push, sdd review | review, qa, compliance, release-management | high | `.ai/skills/sdd-reviewer/SKILL.md` |
| `sdd-writing-plans` | SDD Writing Plans (Orchestrator Persona) | plan this feature, write a plan, sdd plan | planning, architecture | high | `.ai/skills/sdd-writing-plans/SKILL.md` |
| `security` | Security, Compliance & FinOps | security, compliance, finops, secret management | architecture, implementation, review | high | `.ai/skills/security/SKILL.md` |
| `subagent-creator` | Subagent Creator (LangGraph Nodes) | create agent, create node, subagent, langgraph node | architecture, implementation, review | high | `.ai/skills/subagent-creator/SKILL.md` |
| `tech-design-doc` | Technical Design Document (TDD) Creator | tdd, technical design, pre-implementation, mermaid | planning, architecture, documentation | high | `.ai/skills/tech-design-doc/SKILL.md` |

## Routing Protocol
1. Identify the core domain of the user's prompt.
2. Match the request against the skill frontmatter, prioritizing `description` and any optional `metadata.triggers`, `metadata.applies_to`, and `metadata.priority`.
3. If the domain matches a registered trigger, silently ingest the corresponding skill file into working memory before generating the response. All active skills resolve under `.ai/skills/*/SKILL.md`.
4. If multiple skills apply, prioritize the strictest or most foundational constraint first.
5. Recommended precedence for overlapping cases:
   - `sdd-writing-plans` must always precede `sdd-implementer`.
   - `tech-design-doc` before implementation when the task is still in planning or specification.
   - `subagent-creator` when creating or changing LangGraph nodes or agent personas.
   - `security` whenever a task touches secrets, runtime isolation, compliance, or cost risk.
6. `sdd-reviewer` is the final gate in the SDD pipeline and must always be invoked after `sdd-auditor` passes. It authorizes or blocks the remote push — it never precedes implementation.

## Topology Validation
- Registry scope is exhaustive for every active skill under `.ai/skills/`.
- All listed paths resolve to valid local files.
- Registry entries must remain aligned with each skill file's YAML frontmatter and mirrored body metadata.
- `.context/skills/` is deprecated and must not be referenced as an active routing source.
- This registry is the canonical routing source referenced by the environment.
