# Playwright Automation Skill (Web Scraping)

Use this skill to collect financial data that is **not available via APIs** (like yfinance).

## 1. Architecture & Integration
- **Role**: Playwright scripts must be implemented as **Tools** (`src/tools/`) invoked by Agents.
- **Output**: Must return structured data (Pydantic Models) or raise typed exceptions. Never return raw HTML.
- **Async**: Prefer `async_playwright` to avoid blocking the LangGraph event loop.

## 2. Implementation Guidelines
- **Headless**: Always use `headless=True`.
- **Stealth**: Use custom `User-Agent` headers to mimic real browsers.
- **Resilience**: Implement `tenacity` for retries with exponential backoff on network errors.
- **Selectors**: Prefer `data-testid` or robust text selectors over brittle XPath/CSS paths.

## 3. Infrastructure (AWS Fargate/Docker)
- **Browsers**: In Docker/Fargate, ensure the container image includes necessary browser binaries (e.g., `playwright install --with-deps chromium`).
- **Memory**: Browser automation is memory intensive. Ensure the container has enough RAM.

## 4. Debugging & Observability
- **Snapshots**: On failure, save HTML/PNG snapshots to `/tmp` (if local) or S3 (if prod) for debugging.
- **Logging**: Log key events (navigation, extraction) using structured logging.

## 5. Security
- **Sanitization**: Treat all scraped text as untrusted input. Sanitize before processing.
- **Rate Limiting**: Respect `robots.txt` and avoid aggressive scraping loops.
