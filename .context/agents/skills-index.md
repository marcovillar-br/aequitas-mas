# Aequitas-MAS: Agents and Skills Index

This document serves as a router to select the correct tool or specialized agent for the current task.

## 🧭 Quick Decision Map

| If you need... | Use this Skill | Context File |
| :--- | :--- | :--- |
| **Cloud Infrastructure** (AWS Fargate, S3, Costs, Terraform) | `aws-advisor` | `.context/skills/aws-advisor.md` |
| **Domain Modeling** (Bounded Contexts, Entities, Graham/Fisher) | `domain-analysis` | `.context/skills/domain-analysis.md` |
| **Technical Documentation** (TDDs, Specs, Architecture) | `tdd-creator` | `.context/skills/tdd-creator.md` |
| **Security** (Python, OWASP, Dependencies, PII) | `security` | `.context/skills/security.md` |
| **Data Collection** (Scraping, Web, Non-API Data) | `playwright` | `.context/skills/playwright.md` |
| **Create New Agents** (New investors, Personas) | `subagent-creator` | `.context/skills/subagent-creator.md` |

---

## 🚦 Triggers and Usage Instructions

### 1. AWS Advisor (`aws-advisor`)
**Trigger:** "How to configure Fargate?", "Create a secure S3 bucket", "AWS cost estimate".
- **Focus:** Infrastructure as Code (IaC), Cloud Security, Cost Optimization.
- **Golden Rule:** Always prioritize managed services and security *by default*.

### 2. Domain Analysis (`domain-analysis`)
**Trigger:** "Define the Stock entity", "Separate Graham's logic from Fisher's", "Analyze this module".
- **Focus:** Domain-Driven Design (DDD), Bounded Contexts.
- **Golden Rule:** Do not mix different investment logics in the same entity.

### 3. Technical Design Doc (`tdd-creator`)
**Trigger:** "Plan the balance sheet analysis feature", "Create a design doc for the risk module".
- **Focus:** Architecture, Risks, Implementation Plan.
- **Golden Rule:** Do not start coding complex features without an approved TDD.

### 4. Security Best Practices (`security`)
**Trigger:** "Review this Python code", "How to handle sensitive data?", "Input validation".
- **Focus:** Secure financial Python, data sanitization, secrets management.
- **Golden Rule:** Never expose API keys or PII data in logs.

### 5. Playwright Automation (`playwright`)
**Trigger:** "Scrape data from this site", "yfinance doesn't have this data".
- **Focus:** Resilient web data collection.
- **Golden Rule:** Use robust selectors and handle network failures.

### 6. Subagent Creator (`subagent-creator`)
**Trigger:** "Create an agent specialized in Howard Marks", "New analysis node".
- **Focus:** Generation of personas and system prompts.
- **Golden Rule:** Each agent must have a unique and clear objective.

---

## 📜 Global Rules (Always Active)

Regardless of the chosen skill, always follow:
1. **Coding Guidelines:** `.context/rules/coding-guidelines.md` (Python 3.12, Poetry, Type Hints).
2. **RPI Methodology:** Research -> Plan -> Implement.
