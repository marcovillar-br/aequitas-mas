---
name: domain-analysis
description: Skill for modeling financial domain complexity, bounded contexts, and strict design rules for investment logic.
metadata:
  title: Domain-Driven Design (DDD) & Architecture
  triggers:
    - financial analysis
    - domain modeling
    - ddd
    - graham
    - fisher
    - marks
    - bounded context
  tags:
    - domain
    - finance
    - ddd
    - architecture
    - pydantic
  applies_to:
    - architecture
    - modeling
    - review
  language: en
  output_language: pt-BR
  priority: high
  status: active
  version: 1
---

# Name: Domain-Driven Design (DDD) & Architecture

## Description
Use this skill to model financial complexity, ensuring that investment logic such as Graham, Fisher, and Marks is isolated from infrastructure and orchestrated precisely via LangGraph.

## Triggers
- financial analysis
- domain modeling
- ddd
- graham
- fisher
- marks
- bounded context

## Instructions

You are responsible for preserving domain isolation and bounded-context discipline in Aequitas-MAS.

You MUST follow these directives:

1. **Context Map (Bounded Contexts):**
   - Fundamentals (Quant): `GrahamNode`, responsible for accounting, static valuation, and numerical margin of safety, centered on `GrahamMetrics`.
   - Quality & Growth: `FisherNode`, responsible for business analysis, moat, management, and future outlook, centered on `FisherAnalysis`.
   - Risk Audit: `MarksNode`, responsible for second-level thinking, market cycles, and psychology, centered on entities such as `MarketCycle` and `Verdict`.
2. **Rich Models over Anemic Models:** Never create classes that only hold data. Use Python `@property` decorators inside Pydantic models to derive business logic such as `is_deep_value` or `is_bearish`.
3. **Immutability (Strict):** Value objects must be strictly immutable. Always use `model_config = ConfigDict(frozen=True)` in Pydantic V2 models. If an agent needs to change a value, it must return a completely new instance to the LangGraph state.
4. **Logic Isolation:** Graham's mathematical calculation must remain ignorant of Fisher's qualitative sentiment. They only cross paths at the `AgentState` level.
5. **Fail Fast at Boundaries:** Use `@field_validator` in Pydantic to block invalid data such as wrong ticker formats or negative EPS before it enters the LLM context window.

Terminal Output Obligation: After execution, you MUST output a terminal summary directly to the user detailing: 1. Status, 2. Modified Files, 3. Next Steps. This improves CLI observability without polluting the Blackboard.
