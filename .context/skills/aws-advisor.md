# AWS Cloud Infrastructure Advisor

Use this skill to design, review, and implement the Q3/Q4 AWS architecture for the Aequitas-MAS ecosystem.

## 1. Core Architecture Principles
- **Compute (Fargate):** All LangGraph agents must run in stateless AWS Fargate containers. State is strictly managed externally.
- **Storage (S3 Data Lake):** Analytical outputs and structured JSON logs (`structlog`) must be routed to AWS S3. Use `boto3` strictly.
- **Secrets Management:** Credentials (e.g., `GOOGLE_API_KEY`) must be dynamically fetched from **AWS Secrets Manager**. Never use environment variables in the production container image.

## 2. Infrastructure as Code (IaC)
- Proposals must utilize AWS CDK (Python) or Terraform. Manual console configurations are prohibited.
- **IAM Policies:** Enforce the Principle of Least Privilege (PoLP). Explicitly define IAM roles for the Fargate task execution and S3 bucket policies.

## 3. Observability & Costs
- Architecture designs must integrate with AWS CloudWatch for ingesting JSON streams.
- Always provide a conservative cost estimate for any new AWS service proposed.