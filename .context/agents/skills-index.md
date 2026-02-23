# Aequitas-MAS: Development Skills Index

This document serves as a router to select the correct tool or specialized skill for development and engineering tasks.

## 🧭 Quick Decision Map

| If you need to... | Use this Skill | Context File |
| :--- | :--- | :--- |
| **Manage Project Memory** (Sync state, EoD Reports) | `context-manager` | `.context/skills/context-manager.md` |
| **Cloud Infrastructure** (AWS Fargate, S3, Terraform) | `aws-advisor` | `.context/skills/aws-advisor.md` |
| **Domain Modeling** (DDD, Bounded Contexts, Value Investing) | `domain-analysis` | `.context/skills/domain-analysis.md` |
| **Technical Documentation** (TDDs, Specs, Architecture) | `tdd-creator` | `.context/skills/tdd-creator.md` |
| **Security & Compliance** (Python, OWASP, PII, Precision) | `security` | `.context/skills/security.md` |
| **Data Collection** (Scraping, Playwright, Web Data) | `playwright` | `.context/skills/playwright.md` |
| **Create New Agents** (Personas, System Prompts) | `subagent-creator` | `.context/skills/subagent-creator.md` |

---

## 🚦 Triggers and Usage Instructions

### 1. Context Manager (`context-manager`)
**Trigger:** "Resume context", "Update project status", "Sync state", "Gere o checkpoint".
- **Focus:** Alignment between LLM memory, documentation, and codebase.
- **Golden Rule:** Never assume previous knowledge; always verify the latest Checkpoint.

### 2. AWS Advisor (`aws-advisor`)
**Trigger:** "Configure Fargate", "S3 encryption", "Terraform setup", "AWS costs".
- **Focus:** Serverless Infrastructure, Security, and FinOps.
- **Golden Rule:** Prioritize managed services and Zero Trust IAM roles.

### 3. Domain Analysis (`domain-analysis`)
**Trigger:** "Graham logic", "Fisher qualitative criteria", "Define Ticker entity".
- **Focus:** Domain-Driven Design (DDD) for Value Investing.
- **Golden Rule:** Maintain strict isolation between Quantitative and Qualitative domains.

### 4. Technical Design Doc (`tdd-creator`)
**Trigger:** "Plan the risk module", "Design doc for LangGraph flow".
- **Focus:** Architecture, Risk Assessment, and Implementation Plans.
- **Golden Rule:** No complex coding without a pre-approved TDD.

### 5. Security Best Practices (`security`)
**Trigger:** "Audit this code", "Numerical precision check", "Secret management".
- **Focus:** Financial integrity, `Decimal` precision, and GenAI safety.
- **Golden Rule:** `float` is forbidden for financial values; `Decimal` is mandatory.

### 6. Playwright Automation (`playwright`)
**Trigger:** "Scrape B3 news", "Web data collection", "Async scraper".
- **Focus:** Resilient data extraction from non-API sources.
- **Golden Rule:** Use exponential backoff and validate scraped data against Pydantic schemas.

### 7. Subagent Creator (`subagent-creator`)
**Trigger:** "Create a Macro Agent", "New node for ESG analysis".
- **Focus:** Persona generation and System Prompt engineering.
- **Golden Rule:** Every agent must have a unique Bounded Context and mandatory English-Cognitive/PT-BR-Output policy.

---

## 📜 Global Rules (Always Active)

1. **Language Policy:** Cognitive/Code (English) | User Output (Portuguese PT-BR).
2. **Methodology:** RPI (Research -> Plan -> Implement).
3. **Risk Confinement:** No internal math by LLM; delegate all calculations to Python Tools.