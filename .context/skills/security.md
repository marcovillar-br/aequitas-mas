# Security & Observability Best Practices

Use this skill to review code for vulnerabilities, handle sensitive financial data, and manage cloud credentials safely.

## 1. Secrets Management
- **Local:** Use `.env` files loaded via `python-dotenv`. Never commit this file.
- **Production (AWS):** Prepare all code to eventually fetch credentials via `boto3` from **AWS Secrets Manager**. 
- **Rule:** API Keys (like `GOOGLE_API_KEY`) must never be hardcoded or passed as default arguments in function signatures.

## 2. Structured Logging & Sanitization (structlog)
- **Library:** Use `structlog` for JSON-formatted observability. `print()` and standard `logging` are forbidden.
- **PII & Secrets:** Never pass API keys, user identifiers, or raw authentication headers into the logger.
- **Context Binding:** Use `structlog.contextvars.bind_contextvars()` to attach safe metadata (like `target_ticker` or `thread_id`) to the log stream.

## 3. Code Execution Risks
- **Confinement:** Mathematical evaluation must use standard library math or AST parsing. Never use `eval()` or `exec()` for parsing dynamic financial formulas.
- **Dependency Integrity:** Pin versions strictly in `pyproject.toml` using Poetry to avoid supply-chain attacks.