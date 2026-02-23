# Domain-Driven Design (DDD) & Architecture

Use this skill to model financial complexity, ensuring that investment logic (Graham, Fisher, Marks) is isolated from infrastructure and orchestrated precisely via LangGraph.

## 1. Context Map (Bounded Contexts)
| Context | Guardian (Agent) | Responsibility | Entities & Value Objects |
| :--- | :--- | :--- | :--- |
| **Fundamentals (Quant)** | `GrahamNode` | Accounting, Static Valuation, Numerical Margin of Safety. | `GrahamMetrics` |
| **Quality & Growth** | `FisherNode` | Business Analysis, Moat, Management, Future Outlook. | `FisherAnalysis` |
| **Risk Audit** | `MarksNode` | Second-Level Thinking, Market Cycles, Psychology. | `MarketCycle`, `Verdict` |

## 2. Tactical Patterns (SOTA Implementation)

### Rich Models over Anemic Models
- **Rule:** Never create classes that only hold data.
- **Action:** Use Python `@property` decorators inside Pydantic models to derive business logic (e.g., `is_deep_value`, `is_bearish`). 

### Immutability (Strict)
- **Value Objects:** Must be strictly immutable.
- **Implementation:** Always use `model_config = ConfigDict(frozen=True)` in Pydantic V2 models. If an agent needs to change a value, it must return a completely new instance to the LangGraph state.

## 3. Golden Rules of Design
1. **Logic Isolation:** Graham's mathematical calculation must remain ignorant of Fisher's qualitative sentiment. They only cross paths at the `AequitasState` level.
2. **Fail Fast at Boundaries:** Use `@field_validator` in Pydantic to block invalid data (like wrong ticker formats or negative EPS) *before* it enters the LLM context window.