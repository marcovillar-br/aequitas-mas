# SKILL: PLAYWRIGHT AUTOMATION & DATA EXTRACTION

## 1. Trigger / Intent
Activate this skill when the user needs to collect financial data, textual reports (e.g., Earnings Calls, Investor Relations pages), or metrics that are **not available via standardized APIs** (like yfinance).

## 2. Core Directives

### 2.1. Architectural Role
* Playwright scripts must be implemented strictly as **Deterministic Tools** within the `src/tools/` directory.
* They are invoked by the Agents (primarily Fisher for qualitative data) but act independently of the LLM logic.

### 2.2. Execution & Concurrency
* **Async First:** Always use `async_playwright` to prevent blocking the LangGraph event loop during I/O bound network operations.
* **Headless & Stealth:** Always execute with `headless=True`. Implement custom headers and user-agents to avoid basic anti-bot triggers.
* **Resilience:** Wrap extraction logic in robust retry mechanisms (e.g., using the `tenacity` library with exponential backoff).

### 2.3. DOM Interaction Rules
* Avoid brittle selectors (XPath or deep CSS chains). Prefer robust attributes like `data-testid`, `aria-labels`, or semantic text selectors.
* Account for Shadow DOMs and dynamic JavaScript rendering (wait for specific network idle states or elements to attach).

## 3. Constraints & Security
* **Rate Limiting:** Respect `robots.txt` and implement artificial delays (`asyncio.sleep`) between pagination to prevent IP bans from B3 or corporate sites.
* **Input Sanitization:** Treat all extracted text as untrusted. Strip HTML tags and normalize encodings before passing the text to the LLM.

## 4. Implementation Standard (Pydantic Output)
Extracted data MUST never be returned as raw HTML or unstructured strings. Always parse the result into a strict Pydantic v2 model.

```python
from pydantic import BaseModel, Field

class ScrapedEarningsData(BaseModel):
    ticker: str = Field(..., pattern=r"^[A-Z0-9]{5}$")
    report_url: str
    executive_summary: str = Field(..., min_length=50)
    # The output must be validated before merging into the LangGraph state