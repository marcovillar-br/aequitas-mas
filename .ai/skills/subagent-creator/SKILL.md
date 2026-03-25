---
name: subagent-creator
description: Skill for designing and implementing deterministic LLM-based agents and nodes in the Aequitas-MAS workflow.
metadata:
  title: Subagent Creator (LangGraph Nodes)
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

# Name: Subagent Creator (LangGraph Nodes)

## Description
Use this skill when designing or implementing a new LLM-based agent or node for the Aequitas-MAS workflow.

## Triggers
- create agent
- create node
- subagent
- langgraph node
- agent design
- system prompt

## Instructions

You are responsible for designing deterministic LLM-based agents and LangGraph nodes for Aequitas-MAS.

You MUST follow these directives:

1. **Language Constraints:** All system prompts, internal reasoning, Python code, variable names, and comments MUST be in English. Any string intended for the end-user MUST be strictly in Portuguese (PT-BR).
2. **Single Responsibility:** Each agent must have a distinct persona such as Howard Marks or Phil Fisher and a singular analytical goal.
3. **Deterministic Outputs:** LLMs are stochastic, so outputs MUST be forced into deterministic schemas that integrate safely with LangGraph state.
4. **Engine Selection:** Prefer the Gemini models already validated in the repository runtime, such as `gemini-2.5-flash`, unless the active specification states otherwise.
5. **Structured Output:** Bind the LLM to a Pydantic schema using `.with_structured_output(YourPydanticModel)` unless the current specification explicitly requires text-only output such as HyDE generation.
6. **Temperature Control:** Use `temperature=0.0` for extraction, mathematical classification, or strict auditing. Use at most `temperature=0.1` for sentiment analysis or qualitative summarization.
7. **Graph Integration:** The agent function must accept `AgentState` as its sole argument and return a dictionary representing state mutation, such as `{"new_key": data, "messages": [...]}`. Do not mutate state directly in the function body.

Terminal Output Obligation: After execution, you MUST output a terminal summary directly to the user detailing: 1. Status, 2. Modified Files, 3. Next Steps. This improves CLI observability without polluting the Blackboard.
