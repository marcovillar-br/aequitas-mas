### SOTA VALIDATION PROMPT: Aequitas-MAS Architectural Integrity Audit (V4.0 - Temporal Alignment)

**Context:** Act as the PhD Mentor of the Aequitas-MAS project. Validate
whether the architectural premises, code contracts, and SOTA topology are
correctly represented in your active knowledge base.

**Task:** Explain how the multi-agent ecosystem should process the analysis of
the fictional company `TECH3` under an **Extreme Panic** scenario, following
the repository contracts and current architectural documents.

Your answer must explicitly address the six fronts below:

1. **Risk Confinement (Quantitative Engine):** How does `state.py` prevent the
   Graham path from hallucinating arithmetic while computing fair value?
2. **Qualitative SOTA Integration (Fisher):** How does the Fisher agent enforce
   ethical traceability and grounded qualitative analysis?
3. **Holistic SOTA Integration (Macro):** How does the Macro agent use HyDE
   retrieval while preserving timestamp-bounded evidence?
4. **Audit Decision Logic (Marks):** Present the dynamic intrinsic-value
   formula in LaTeX and explain the contrarian intervention expected under
   panic.
5. **Flow Architecture (Core / LangGraph):** Explain the router's role in
   controlling state flow and avoiding cascading failures.
6. **Infrastructure Restriction (DIP):** State the hard rule regarding cloud
   SDK usage inside `/src/agents/`.

---

### Mandatory SOTA Audit Clauses

- **Temporal Alignment (MarketSenseAI, 2025):** Verify whether news and macro
  retrieval are timestamp-filtered so that only evidence valid at or before the
  active `as_of_date` can enter the analysis. Any retrieval path that ignores
  temporal filtering must be treated as a look-ahead bias defect.
- **Controlled Degradation:** Financial and benchmark metrics must degrade via
  `Optional[float] = None`, never by fabricated defaults.
- **Point-in-Time Synchronization:** Confirm that Graham valuation, historical
  data loading, and RAG/HyDE retrieval operate under the same temporal anchor
  defined by ADR 011.

---

### Expected Characteristics of a Correct Answer

To validate the model against the current architecture, the answer must contain:

- explicit mention of **Pydantic V2**, `math.isfinite()`, and
  `Optional[float] = None`
- confirmation that the system deliberately does **not** use
  `decimal.Decimal` in LangGraph-facing state
- confirmation that Fisher and Macro remain traceable through source-backed
  evidence
- explanation that HyDE retrieval is point-in-time aligned through
  `as_of_date`
- the dynamic valuation formulas rendered in LaTeX
- explicit mention that `import boto3` is forbidden in `/src/agents/`
- a final disclaimer stating that the system is an academic DSS framework and
  not investment advice

**CRITICAL OUTPUT RULE:** The full diagnostic report, explanations, and
reasoning must be written in Brazilian Portuguese (pt-BR). Any generated code
or technical nomenclature inside the text must remain in English.
