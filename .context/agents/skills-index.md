# 🗺️ AEQUITAS-MAS: SKILL ROUTING INDEX

## Purpose
This document serves as the central registry for all specialized skills available to the AI Assistant. When interacting with the user, cross-reference the user's request with this index to dynamically load the appropriate skill context from the `.context/skills/` directory.

## Registered Skills

| Skill Identifier | Trigger / Intent | File Path |
| :--- | :--- | :--- |
| **AWS Advisor** | Cloud infrastructure, Terraform, AWS DynamoDB, OpenSearch. | `.context/skills/aws-advisor.md` |
| **Domain Analysis** | Financial theory, Value Investing (Graham, Fisher, Marks), Economic indicators. | `.context/skills/domain-analysis.md` |
| **Playwright** | Web scraping, data extraction from B3, dynamic DOM interaction. | `.context/skills/playwright.md` |
| **Security & Compliance** | Secret management, zero-trust enforcement, code vulnerabilities. | `.context/skills/security.md` |
| **Subagent Creator** | Structuring new LangGraph nodes, creating new agents, writing system prompts. | `.context/skills/subagent-creator.md` |
| **TDD Creator** | Writing `pytest` mocks, unit tests, testing mathematical validations. | `.context/skills/tdd-creator.md` |
| **GitHub Manager** | Git commands, Semantic Commits (Conventional Commits), Branching, PRs. | `.context/skills/github-manager.md` |

## Routing Protocol
1. Identify the core domain of the user's prompt.
2. If the domain matches a "Trigger", silently ingest the corresponding `.md` file into your working memory before generating the response.
3. If multiple skills apply (e.g., writing tests for a web scraper), prioritize the strictest constraint (e.g., `tdd-creator.md`).