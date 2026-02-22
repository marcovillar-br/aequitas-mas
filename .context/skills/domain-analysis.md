# Domain-Driven Design (DDD) & Architecture

Use this skill to model financial complexity, ensuring that investment logic (Graham, Fisher, Marks) is isolated from infrastructure and orchestrated precisely.

## 1. Context Map (Bounded Contexts)

The system is divided into strict bounded contexts. Each LangGraph Agent/Node acts as a guardian of a context.

| Context | Guardian (Agent) | Responsibility | Entities & Value Objects |
| :--- | :--- | :--- | :--- |
| **Fundamentals (Quant)** | `GrahamNode` | Accounting, Static Valuation, Numerical Margin of Safety. | `BalanceSheet`, `IntrinsicValue`, `EPS`, `BVPS`. |
| **Quality & Growth** | `FisherNode` | Business Analysis, Moat, Management, Future Outlook. | `Scuttlebutt`, `YieldGap`, `MarketSentiment`. |
| **Risk Audit** | `MarksNode` | Second-Level Thinking, Market Cycles, Psychology. | `MarketCycle`, `InstitutionalRisk`, `Verdict`. |
| **Data Infrastructure** | `Tools` | External data adaptation (ACL - Anti-Corruption Layer). | `YFinanceDTO`, `B3Scraper`. |

## 2. Ubiquitous Language

Use the correct terms to avoid ambiguity in prompts and code.

- **Asset:** The root entity (e.g., PETR4). Has unique identity.
- **Margin of Safety (Graham):** Mathematical difference between Price and Fair Value.
- **Economic Moat (Fisher):** Durable competitive advantage (not to be confused with momentary profit).
- **Mr. Market:** The personification of irrational volatility (Marks Context).

## 3. Tactical Patterns (Python Implementation)

### Entities vs. Value Objects
- **Value Objects (Immutable):** Use `Frozen Pydantic Models` or `dataclasses(frozen=True)`.
    - *Example:* A `Price(value=10.0, currency='BRL')` does not change. If the price rises, a new object is created.
- **Entities (Identity):** The `Ticker` is the identity. The Ticker state evolves in the Graph.

### Adaptation Layer (ACL)
- Never use raw `yfinance` dictionaries inside domain logic.
- Convert external data to **Domain Events** or **Typed DTOs** immediately upon entry (Tools).

## 4. Golden Rules of Design

1.  **Logic Isolation:** Graham's calculation should not know that Fisher exists. Coupling occurs only in the LangGraph `State`.
2.  **Rich Models:** Avoid "Anemic Models" (classes with only data). Classes must have business methods (e.g., `asset.calculate_margin()`).
3.  **Invariants:** Rules that can never be broken (e.g., "Price cannot be negative", "Asset must have minimum liquidity"). Must be validated in the class constructor.

> **Reference:** Based on "Domain-Driven Design" (Eric Evans) and adapted for Financial Agent Architecture.
