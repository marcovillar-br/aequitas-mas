# ADR 006: OpenSearch Shared Collection Strategy (Option B)

## Status
Accepted (Sprint 3.3 preparation, 2026-03-10).

## 1. Context

The current Terraform baseline in `infra/terraform/opensearch.tf` was originally scoped to
Fisher-only resources (`aqm-fisher-*`). In parallel, the Macro Agent retrieval path (Sprint 3.2)
already depends on `VectorStorePort` plus environment-driven index selection
(`OPENSEARCH_INDEX`).

This creates an infrastructure mismatch:
- Terraform naming and collection scope imply single-agent provisioning.
- Runtime retrieval architecture already supports multi-agent index routing.

Without a formal decision, Sprint 3.3 remains blocked by uncertainty in resource topology,
policy scope, and cost model.

## 2. Decision

We adopt **Option B**:
- Provision one shared OpenSearch Serverless collection:
  `aequitas-vector-store-${terraform.workspace}`.
- Enforce logical isolation through dedicated indices per bounded context:
  - Fisher bounded context: `fisher-index`
  - Macro bounded context: `macro-index`

This preserves DDD boundaries at the storage contract level while avoiding duplicated collection
infrastructure. Agents remain isolated by index ownership and environment configuration, not by
separate collections.

## 3. Rationale

Option A (separate collections per agent) gives stronger physical isolation but duplicates OCU
cost and increases policy sprawl. Option C (fully generic Terraform module) improves long-term
maintainability but adds design overhead that is unnecessary to unblock the current sprint.

Option B is the fastest safe path because it:
- Resolves Sprint 3.3 provisioning blockers immediately.
- Reduces AWS footprint to a single collection billing unit.
- Reuses existing adapter behavior (`OPENSEARCH_INDEX`) with no changes in agent code.

## 4. Consequences

**Positive**
- Cost optimization: single shared collection during MVP/dev.
- Lower operational complexity: one set of encryption/network/access policies.
- DDD alignment: Fisher and Macro remain logically segmented by index namespace.

**Negative**
- Throughput is shared across indices inside the same collection.
- Misconfigured index env vars may route a workload to the wrong index.
- Future move to per-agent collections requires reindexing and migration planning.

## 5. Implementation Notes

- `infra/terraform/opensearch.tf`
  - rename resource prefixes from `AQM_FISHER_*` to `AQM_VECTOR_STORE_*`
  - set collection name to `aequitas-vector-store-${terraform.workspace}`
- `infra/terraform/variables.tf`
  - add `opensearch_index` variable for logical per-agent routing
- Runtime configuration
  - Fisher uses `OPENSEARCH_INDEX=fisher-index`
  - Macro uses `OPENSEARCH_INDEX=macro-index`

## 6. Guardrails

- No cloud SDK imports in `src/agents/` or `src/core/` (DIP remains enforced).
- No `terraform apply` in CI; applies are manual and Tech Lead supervised.
