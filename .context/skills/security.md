# SKILL: SECURITY, COMPLIANCE & FINOPS

## 1. Trigger / Intent
Activate this skill during infrastructure setup, code reviews, environment configuration, or when designing LangGraph state transitions to ensure zero-trust architecture and financial integrity.

## 2. Infrastructure & FinOps Constraints

### 2.1. Secret Management (Zero Trust)
* **Local Environment:** Enforce the use of IDE-native Secret Managers (e.g., Google IDX Secret Manager). NEVER instruct the user to commit `.env` files.
* **Production Environment:** AWS Secrets Manager is mandatory. API keys (Gemini, Anthropic, AWS) must be injected at runtime.
* **IAM Least Privilege:** Fargate tasks and Lambda functions must operate with the absolute minimum required AWS IAM permissions.

### 2.2. FinOps & Circuit Breakers
* **Graph Recursion Limit:** LangGraph execution MUST include a strict `recursion_limit` (e.g., `recursion_limit=15`) upon compilation to prevent infinite LLM debate loops and unexpected billing spikes.

## 3. LLM & State Security (Agentic Context)

### 3.1. State Edge Validation
* **Graph Isolation:** State variables must not bleed across different financial assets. Use unique `thread_id` configurations in LangGraph.
* **Pydantic Firewalls:** The transition between graph nodes (edges) must act as a validation firewall. If an LLM outputs malformed data, the Pydantic parser (>= v2.0) should catch the `ValidationError` and trigger a deterministic fallback, not a hallucination.

### 3.2. GenAI Vulnerability Mitigation
* **Prompt Injection:** Sanitize all external inputs (e.g., news articles scraped by Playwright) before injecting them into the Gemini/Claude context windows.
* **Numerical Integrity:** Language Models are prohibited from performing financial arithmetic. All state values representing money or percentages must be handled as `decimal.Decimal` in Python, never as `float`.

## 4. Audit & Observability
* **Structured Logging:** Use JSON-formatted logging for all agent decisions.
* **PII Protection:** Ensure logs are sanitized. Never log personal identifiable information or raw proprietary trading alpha signals.
