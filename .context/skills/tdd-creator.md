# Technical Design Doc Creator (TDD)

Act as a Senior Software Engineer. Use this skill to plan complex features before coding, following the **RPI (Research -> Plan -> Implement)** methodology.

## 1. Context & Objective
- **Goal**: What problem are we solving? (e.g., "Implement Fisher's Qualitative Analysis").
- **Bounded Context**: Which domain does this belong to? (Graham/Quant, Fisher/Qualitative, Marks/Risk).

## 2. Mathematical & Logical Model
- **Formulas**: LaTeX or Python-like pseudocode for financial calculations.
- **Logic**: Decision trees for qualitative analysis.

## 3. Architecture & Data Flow
- **LangGraph Integration**:
    - **Node**: Name of the new node.
    - **State**: What data is read from/written to `AequitasState`?
    - **Edges**: Where does it route to?
- **Schema (Pydantic)**: Define the input/output data structures strictly.
- **Diagram**: Mermaid sequence or flowchart.

## 4. Implementation Plan
- **Step 1**: Create Pydantic models in `src/core/schemas.py`.
- **Step 2**: Implement core logic/tools in `src/tools/`.
- **Step 3**: Create the Agent/Node in `src/agents/`.
- **Step 4**: Register in `src/core/graph.py`.

## 5. Risk Assessment & Mitigation
- **Data Gaps**: What if `yfinance` returns `None`?
- **Hallucination**: How to validate LLM outputs? (e.g., "Use strict Pydantic parsing").

## 6. Testing Strategy
- **Unit Tests**: What needs to be mocked? (e.g., `Mock yfinance API`).
- **Integration**: How to test the node within the graph?
