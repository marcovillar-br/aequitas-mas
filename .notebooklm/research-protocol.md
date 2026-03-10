# NotebookLM: The Researcher (RAG Offline Protocol)

## 1. Actor Identity and Function
- **Role:** The Researcher / Macro & Micro Context Gatherer.
- **Function:** Ingest CVM/SEC filings, earnings call transcripts, and daily macroeconomic news to arm the Fisher Agent and Macro Agent.
- **Constraint:** This agent operates completely offline from the codebase. It parses human-uploaded PDFs/links and outputs structured text.

## 2. Tech Lead Actions (Human-in-the-Loop)
Before starting the development session, the Tech Lead MUST:
1. Open the designated NotebookLM workspace.
2. Upload the latest macroeconomic reports (focusing on Selic rate, IPCA, and Equity Risk Premium - ERP).
3. Upload the latest 10-K, 10-Q, or DFP/ITR filings for the target asset.
4. Execute the "Internal Prompt" below.

## 3. Internal Prompt (Copy and paste into NotebookLM)
```markdown
Synthesize the current macroeconomic context and major CVM/SEC updates based strictly on the uploaded documents.

Your tasks:
1. Highlight variables that directly affect the Equity Risk Premium (ERP) and the risk-free rate (Selic).
2. Extract any qualitative risks or forward-looking statements from the filings that the Fisher Agent must evaluate.
3. OUTPUT REQUIREMENT: Generate a concise, bulleted briefing for the System Architect (GEM).
4. TRACEABILITY REQUIREMENT: You MUST cite the specific document name and page/section for every bullet point. If a metric is not in the documents, output "Null/Not Found". Do not hallucinate external data.
```
