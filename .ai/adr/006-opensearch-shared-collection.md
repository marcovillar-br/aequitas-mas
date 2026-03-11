# ADR 006: OpenSearch Serverless Provisioning Strategy — Shared Collection with Separate Indices

## 1. Context

The initial Terraform configuration (`infra/terraform/opensearch.tf`) provisions an AWS
OpenSearch Serverless collection scoped exclusively to the Fisher Agent:
- Collection name: `aqm-fisher-${terraform.workspace}`
- All policies (encryption, network, access) are named under the `aqm-fisher-*` namespace.

The Macro Agent (Sprint 3.2) was implemented with a `VectorStorePort` that targets the index
`aequitas-macro-docs` (configurable via `OPENSEARCH_INDEX` env var). This creates a divergence:
the infrastructure provisions Fisher's collection, but the Macro Agent's adapter expects a
separate endpoint with a different index name.

This misalignment is a **Sprint 3.3 blocker**: without a clear architectural decision, the
Terraform implementor risks duplicating policies, creating conflicting collection names, or
provisioning resources in the wrong scope.

Three options were evaluated:

| Option | Description | Trade-off |
|---|---|---|
| A | Separate collection per agent (`aqm-fisher-*` + `aqm-macro-*`) | Max isolation, ~2x OCU cost |
| **B** | **Shared collection (`aequitas-vector-store`) + separate indices per agent** | **Balanced cost/isolation** |
| C | Parameterized Terraform module reusable per agent | Best maintainability, higher initial complexity |

## 2. Decision

We adopt **Option B: Shared Collection with Separate Indices**.

A single AWS OpenSearch Serverless collection named `aequitas-vector-store-${terraform.workspace}`
is provisioned. Logical domain isolation between agents is implemented at the **index level**:

- Fisher Agent → index `fisher-index`
- Macro Agent → index `macro-index`

Policies (encryption, network, data access) are attached to the shared collection and cover
all indices within it. The `OPENSEARCH_INDEX` environment variable in each agent's runtime
configuration selects the appropriate index.

This decision balances:
- **Cost efficiency:** One collection = one OCU billing unit instead of two.
- **Domain isolation (DDD):** Each agent owns its index namespace; no cross-agent queries.
- **Clean Architecture:** `OpenSearchAdapter.from_env()` reads `OPENSEARCH_INDEX`, so the
  adapter is already parameterized — no code changes required, only environment configuration.

## 3. Consequences

**Positive:**
- Single OCU billing unit reduces AWS costs during MVP and dev phases.
- Existing `OpenSearchAdapter` is already index-configurable via `OPENSEARCH_INDEX` env var.
- Policies and network rules are maintained in one place — lower operational overhead.

**Negative:**
- Indices within the same collection share the same throughput (OCU) — a surge in Fisher
  retrieval could theoretically affect Macro retrieval latency (acceptable for MVP).
- Future migration to separate collections (Option A) requires a data migration step.
- Looser isolation than Option A: a misconfigured `OPENSEARCH_INDEX` could cause an agent
  to query the wrong index (mitigated by strict env-var management in each environment).

## 4. Implementation Reference

- `infra/terraform/opensearch.tf` — To be refactored: `AQM_FISHER_*` → `AQM_VECTOR_STORE_*`,
  collection name updated to `aequitas-vector-store-${terraform.workspace}`.
- `infra/terraform/variables.tf` — To add: `opensearch_index` variable for per-agent index routing.
- `src/infra/adapters/opensearch_client.py` — No changes required; already reads `OPENSEARCH_INDEX`.
- **Constraint:** No `terraform apply` in CI. All `apply` operations require manual Tech Lead
  supervision in the `dev` workspace before any `hom`/`prod` promotion.
