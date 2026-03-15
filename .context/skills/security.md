# SKILL: SECURITY, COMPLIANCE & FINOPS

## 1. Trigger / Intent
Activate this skill during infrastructure setup, code reviews, environment configuration, or when designing LangGraph state transitions to ensure zero-trust architecture and financial integrity.

## 2. Infrastructure & FinOps Constraints

### 2.1. Secret Management (Zero Trust)
* **Local / CI Environment:** Secrets should be resolved through the local secret-store adapter (`EnvSecretAdapter`), which reads process environment variables without coupling domain code to a provider implementation. NEVER instruct the user to commit `.env` files.
* **Production Environment:** Prefer a dedicated adapter compatible with `SecretStorePort`, such as an AWS Secrets Manager integration. API keys (Gemini, Anthropic, AWS) must be injected at runtime.
* **IAM Least Privilege:** Fargate tasks and Lambda functions must operate with the absolute minimum required AWS IAM permissions.

### 2.2. FinOps & Circuit Breakers
* **Graph Recursion Limit:** LangGraph execution MUST include a strict `recursion_limit` (e.g., `recursion_limit=15`) upon compilation to prevent infinite LLM debate loops and unexpected billing spikes.

## 3. LLM & State Security (Agentic Context)

### 3.1. State Edge Validation
* **Graph Isolation:** State variables must not bleed across different financial assets. Use unique `thread_id` configurations in LangGraph.
* **Pydantic Firewalls:** The transition between graph nodes (edges) must act as a validation firewall. If an LLM outputs malformed data, the Pydantic parser (>= v2.0) should catch the `ValidationError` and trigger a deterministic fallback, not a hallucination.

### 3.2. GenAI Vulnerability Mitigation & Risk Confinement
* **Prompt Injection:** Sanitize all external inputs (e.g., news articles scraped by Playwright) before injecting them into the Gemini/Claude context windows.
* **Algorithmic Security (Anti-Hallucination):** The LLM acts solely as a probabilistic orchestrator. Allowing the LLM to execute raw math or "guess" missing multiples is considered a critical security vulnerability.
* **State Integrity over Precision:** To prevent catastrophic state failure in LangGraph, data contracts must explicitly handle missing values. 
  * **Rule:** Ban the use of `Decimal` in Pydantic models facing the LLM. Enforce `Optional[float] = None` to gracefully handle extraction anomalies and immediately cut off the LLM's stochastic guessing. This supersedes standard financial coding guidelines to maintain graph integrity.

### 3.3. Execution Sandboxing
* Tools executing the `Code Interpreter` pattern or external financial libraries must run in isolated boundaries. The LLM cannot write and execute arbitrary Python code on the fly; it can only invoke pre-approved, strictly typed functions from `/src/tools/`.

## 4. Audit & Observability
* **Structured Logging:** Use JSON-formatted logging for all agent decisions.
* **PII Protection:** Ensure logs are sanitized. Never log personal identifiable information or raw proprietary trading alpha signals.
* **Traceability:** Agents using RAG must return source URLs or Document IDs in their output schemas to prevent the injection of obsolete data.
