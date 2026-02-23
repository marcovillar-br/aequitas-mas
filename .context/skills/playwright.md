# Playwright Data Extraction Automation

Use this skill when designing web scrapers for financial data that lack official APIs (Anti-Corruption Layer).

## 1. Resilient Locators
- **Prohibited:** Fragile XPath and deep CSS hierarchies.
- **Mandatory:** Use ARIA locators, data-testid, or semantic text-based selectors to ensure resilience against frontend framework updates.

## 2. Execution & Network
- Implement explicit waits for specific network states or element visibility.
- Build retry mechanisms with exponential backoff for network timeouts.

## 3. Data Confinement
- Unstructured scraped data must be immediately parsed, sanitized, and confined within a Pydantic V2 `BaseModel` before interacting with any core system logic. Do not leak raw HTML or loose dictionaries into the LangGraph state.