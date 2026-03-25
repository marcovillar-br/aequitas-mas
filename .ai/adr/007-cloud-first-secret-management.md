---
id: adr-007
title: "Cloud-First Secret Management via SecretStorePort"
status: accepted
sprint: "Sprint 5"
date: "2026-03-13"
tags: [adr, secrets, zero-trust, secret-store-port]
---

# ADR 007: Cloud-First Secret Management via Port/Adapter

## Status
Accepted and Implemented (Sprint 6, 2026-03-15).

## Context

The repository historically resolved Gemini credentials through direct
environment access patterns such as `os.getenv("GEMINI_API_KEY")` in runtime
helpers. While simple, this approach created two architectural problems:

1. **Zero Trust violation:** domain-facing code became implicitly coupled to one
   specific secret provider mechanism.
2. **Cloud portability friction:** moving from local execution to managed secret
   providers would require touching the same application and agent code that
   should remain infrastructure-agnostic.

This conflicted with the Aequitas-MAS Dependency Inversion dogma: the domain
must depend on contracts, not on environment-provider details.

## Decision

We introduced a dedicated secret-management boundary based on Port/Adapter
principles.

- `src/core/interfaces/secret_store.py` defines `SecretStorePort`
- `src/infra/adapters/env_secret_adapter.py` implements `EnvSecretAdapter`
- `src/core/llm.py` now resolves `GEMINI_API_KEY` through the configured
  `SecretStorePort`

The current local and CI implementation uses `EnvSecretAdapter`, which reads
process environment variables. This preserves local simplicity while keeping the
domain layer independent from the secret backend.

## Consequences

**Positive**
- Domain code is now infrastructure-agnostic.
- Zero Trust posture is stronger because secret resolution is behind an explicit
  contract.
- A future AWS Secrets Manager adapter can be introduced without refactoring
  `src/agents/` or `src/core/`.
- Testability improves because secret lookup can be injected and stubbed.

**Negative**
- The system gains one more abstraction layer to maintain.
- The current local adapter still depends on environment variables at the
  infrastructure edge, which requires clear operational documentation.

**Follow-up**
- A future ADR may supersede `EnvSecretAdapter` in cloud runtimes with an
  `AWSSecretsManagerAdapter` that satisfies the same `SecretStorePort`.
