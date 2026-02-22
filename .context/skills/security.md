# Security & Compliance (Aequitas-MAS)

## 1. LLM & AI Security (GenAI)
- **Prompt Injection**: Sanitize external inputs before injecting into Gemini context.
- **Output Validation**: Never trust LLM output. Use **Pydantic** to enforce strict schemas.
- **Data Leakage**: Never include API keys or credentials in prompt text.

## 2. Financial Integrity
- **Numerical Precision**: Strictly use `decimal.Decimal` for monetary calculations. `float` is forbidden for financial values.
- **Data Source**: Validate `yfinance` data integrity (e.g., gaps in time series) before processing.

## 3. Infrastructure & Cloud (AWS)
- **Secrets Management**:
    - **Local**: Environment variables (not committed).
    - **Prod**: AWS Secrets Manager. **Never** hardcode keys in code.
- **IAM**: Apply Least Privilege Principle to Fargate Roles.
- **Network**: Agents must run in private subnets, without direct public IP.

## 4. Supply Chain & Dependencies
- **Poetry**: Keep `poetry.lock` committed and audited.
- **Images**: Scan Docker images in ECR (Amazon Inspector) for vulnerabilities (CVEs).

## 5. LangGraph Safety
- **Recursion Limit**: Configure recursion limits in the graph (e.g., `recursion_limit=15`) to avoid infinite loops and excessive LLM costs.
- **State Isolation**: Ensure that the state of one ticker does not leak to another (isolation by `thread_id`).

## 6. Secure Observability
- **Logs**: Use structured JSON. Never log PII (CPF, Email) or proprietary strategy details (Alpha).
