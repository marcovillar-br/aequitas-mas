---
name: playwright
description: Skill for deterministic browser automation and robust data extraction when APIs are unavailable.
metadata:
  title: Playwright Automation & Data Extraction
  triggers:
    - scraping
    - playwright
    - browser automation
    - earnings calls
    - investor relations
    - dynamic dom
    - data extraction
  tags:
    - playwright
    - scraping
    - automation
    - extraction
    - tools
  applies_to:
    - implementation
    - data-collection
    - review
  language: en
  output_language: pt-BR
  priority: medium
  status: active
  version: 1
---

# Name: Playwright Automation & Data Extraction

## Description
Use this skill when the user needs deterministic browser automation or robust data extraction for financial pages and dynamic sites that are not accessible through standardized APIs.

## Triggers
- scraping
- playwright
- browser automation
- earnings calls
- investor relations
- dynamic dom
- data extraction

## Instructions

You are responsible for deterministic browser automation and extraction patterns in Aequitas-MAS.

You MUST follow these directives:

1. **Architectural Role:** Playwright scripts must be implemented strictly as deterministic tools under `src/tools/`. They are invoked by agents, primarily Fisher for qualitative data, but remain independent of LLM logic.
2. **Execution & Concurrency:** Always use `async_playwright` to avoid blocking the LangGraph event loop. Always execute with `headless=True` and apply custom headers or user-agents when necessary to reduce basic anti-bot triggers.
3. **Resilience:** Wrap extraction logic in robust retry mechanisms such as `tenacity` with exponential backoff.
4. **DOM Interaction Rules:** Avoid brittle selectors like XPath or deep CSS chains. Prefer robust selectors such as `data-testid`, `aria-label`, or semantic text selectors. Account for Shadow DOM and dynamic JavaScript rendering by waiting for network idle states or attached elements.
5. **Constraints & Security:** Respect `robots.txt` and implement artificial delays such as `asyncio.sleep` between pagination steps when needed. Treat all extracted text as untrusted and sanitize HTML plus encodings before passing content to the LLM.
6. **Implementation Standard (Pydantic Output):** Extracted data MUST never be returned as raw HTML or unstructured strings. Always parse the result into a strict Pydantic v2 model, for example:

```python
from pydantic import BaseModel, Field

class ScrapedEarningsData(BaseModel):
    ticker: str = Field(..., pattern=r"^[A-Z0-9]{5}$")
    report_url: str
    executive_summary: str = Field(..., min_length=50)
```

Terminal Output Obligation: After execution, you MUST output a terminal summary directly to the user detailing: 1. Status, 2. Modified Files, 3. Next Steps. This improves CLI observability without polluting the Blackboard.
