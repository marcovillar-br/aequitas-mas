---
name: subagent-creator
title: Subagent Creator (LangGraph Nodes)
description: Skill for designing and implementing deterministic LLM-based agents and nodes in the Aequitas-MAS workflow.
triggers:
  - create agent
  - create node
  - subagent
  - langgraph node
  - agent design
  - system prompt
tags:
  - agents
  - langgraph
  - llm
  - orchestration
  - pydantic
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

# Subagent Creator (LangGraph Nodes)

Use this skill when designing or implementing a new LLM-based agent or node for the Aequitas-MAS workflow.

# Constraints
- **Cognitive Language:** All system prompts, internal reasoning, python code, variable names, and comments MUST be in **English**.
- **User Interface Language:** The final output, analysis report, and any string intended for the end-user MUST be strictly in **Portuguese (PT-BR)**.

## 1. Agent Design Principles
- **Single Responsibility:** Each agent must have a distinct persona (e.g., "Howard Marks", "Phil Fisher") and a singular analytical goal.
- **Deterministic Outputs:** LLMs are stochastic. To integrate them into the LangGraph state machine, their outputs MUST be forced into a deterministic schema.

## 2. Implementation Rules (SOTA)
- **Engine:** Prefer the Gemini models already validated in the repository runtime, such as `gemini-2.5-flash`, unless the active specification states otherwise.
- **Structured Output:** Bind the LLM to a Pydantic schema using `.with_structured_output(YourPydanticModel)` unless the current specification explicitly requires text-only output (for example, HyDE generation).
- **Temperature Control:** - `temperature=0.0`: For extraction, mathematical classification, or strict auditing.
  - `temperature=0.1`: Maximum allowed for sentiment analysis or qualitative summarization to preserve logic stability.

## 3. Integration with Graph
- The agent function must accept `AgentState` as its sole argument.
- It must return a dictionary representing the state mutation (e.g., `{"new_key": data, "messages": [...]}`). Do not mutate the state directly in the function body.
