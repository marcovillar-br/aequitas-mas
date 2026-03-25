---
name: security
description: Skill for zero-trust architecture, secret management, LangGraph safety, and cost-aware operational guardrails.
metadata:
  title: Security, Compliance & FinOps
  triggers:
    - security
    - compliance
    - finops
    - secret management
    - prompt injection
    - audit
    - zero trust
  tags:
    - security
    - compliance
    - finops
    - secrets
    - observability
  applies_to:
    - architecture
    - implementation
    - review
  language: en
  output_language: pt-BR
  priority: high
  status: active
  version: 1
---

# Name: Security, Compliance & FinOps

## Description
Use this skill during infrastructure setup, code reviews, environment configuration, or LangGraph design to enforce zero-trust architecture and cost-aware operational guardrails.

## Triggers
- security
- compliance
- finops
- secret management
- prompt injection
- audit
- zero trust

## Instructions

You are responsible for zero-trust architecture, secret management, state security, and operational FinOps controls in Aequitas-MAS.

You MUST follow these directives:

1. **Secret Management (Zero Trust):**
   - In local or CI environments, secrets should be resolved through `EnvSecretAdapter` or another adapter behind `SecretStorePort`. Never instruct the user to commit `.env` files.
   - In production, prefer a dedicated adapter such as AWS Secrets Manager compatible with `SecretStorePort`.
   - Fargate tasks and Lambda functions must operate with least-privilege IAM permissions.
2. **FinOps & Circuit Breakers:** LangGraph execution MUST include a strict `recursion_limit`, such as `recursion_limit=15`, to prevent infinite loops and unexpected billing spikes.
3. **State Edge Validation:** State variables must not bleed across financial assets. Use unique `thread_id` configurations in LangGraph. Pydantic node boundaries must act as firewalls so malformed data triggers deterministic fallback rather than hallucination.
4. **GenAI Vulnerability Mitigation & Risk Confinement:** Sanitize all external inputs before injecting them into model context windows. Treat any attempt to let the LLM execute raw math or guess missing multiples as a critical security vulnerability.
5. **State Integrity over Precision:** Ban the use of `Decimal` in Pydantic models facing the LLM. Enforce `Optional[float] = None` to handle extraction anomalies and immediately cut off stochastic guessing.
6. **Execution Sandboxing:** Tools following the Code Interpreter pattern or external financial libraries must run in isolated boundaries. The LLM cannot write and execute arbitrary Python on the fly; it can only invoke pre-approved, strictly typed functions from `/src/tools/`.
7. **Audit & Observability:** Use structured JSON logging, sanitize logs for PII and proprietary signals, and require RAG-enabled agents to return source URLs or document IDs for traceability.

Terminal Output Obligation: After execution, you MUST output a terminal summary directly to the user detailing: 1. Status, 2. Modified Files, 3. Next Steps. This improves CLI observability without polluting the Blackboard.
