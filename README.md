# Aequitas-MAS (Multi-Agent System) v5.0

**Aequitas-MAS** is an intelligent agent ecosystem designed for fundamental analysis and high-level financial decision-making. The system transcends static calculations by combining the mathematical rigor of **Value Investing** with qualitative market analysis and risk auditing, utilizing **LangGraph** for orchestration and **Gemini Flash** as the inference engine.

## 🧠 Agent Architecture

The project uses a Directed Acyclic Graph (DAG) to process financial assets through a supervised multi-agent flow, ensuring that intrinsic value is confronted with market reality and only reaches deterministic allocation after structured consensus:

1. **GRAHAM Node (Quantitative):** 
* Performs real-time fundamental data collection via `yfinance`.
* Executes the **Fair Value** calculation based on the Benjamin Graham formula.
* Establishes the nominal Margin of Safety of the asset.

2. **FISHER Node (Qualitative):** 
* Evaluates the "Yield Gap" and market sentiment through macroeconomic data.
* Identifies competitive advantages and dividend sustainability.
* Processed via **Gemini Flash** (Alias `gemini-flash-latest`).

3. **MARKS Node (Risk Audit):** 
* Applies "Second-Level Thinking" (Howard Marks) to challenge the previous nodes.
* Analyzes institutional, political, and governance risks (especially in state-owned enterprises).
* Defines the final verdict on the viability of the margin of safety.

4. **AEQUITAS CORE Node (Supervisor):**
* Acts as the orchestration authority for the LangGraph workflow.
* Coordinates specialist consensus across Graham, Fisher, Macro, and Marks.
* Triggers deterministic portfolio weighting only after the consensus checkpoint is complete.

## 🚀 Technical Stack

* **Language:** Python 3.10+
* **Orchestration:** [LangGraph](https://www.langchain.com/langgraph) (State-based agents)
* **LLM Engine:** Google Gemini Flash (Alias `gemini-flash-latest`)
* **Dependency Management:** [Poetry](https://python-poetry.org/)
* **Data:** yfinance, Pandas, Beautifulsoup4

## 🛠️ Installation and Setup

```bash
# Clone the repository
git clone https://github.com/marcovillar-br/aequitas-mas.git
cd aequitas-mas

# Link the interpreter and install dependencies via Poetry
poetry env use python3
poetry install
```

### Environment Variables

Create a `.env` file in the root of the project:

```text
GEMINI_API_KEY=your_google_ai_studio_key
```

## 📈 Real Use Case: PETR4

The system was validated with an analysis of **PETR4** in February 2026:

* **Graham Calculation:** Fair Value of **R$ 64.64** (Margin of 41.26%).
* **Fisher Context:** Attractive dividends (~10%) vs. Geopolitical volatility.
* **Marks Verdict:** Warning about a "moving target" in state-owned assets, adjusting the perception of the nominal margin.

---

## 🗺️ Implementation Roadmap (2026-2027)

This project follows a technical evolution schedule focused on transitioning from a functional prototype to a distributed and resilient analysis infrastructure:

* **Q1/2026 - Stabilization and Core:**
* Completed: dependency environment sanitation (Poetry) and migration to stable `v1` endpoints.
* Completed: Core Integration and deterministic Portfolio Optimization via the **AEQUITAS CORE Node** and `portfolio_optimizer.py`.

* **Q2/2026 - Observability and Testing:**
* Implementation of structured logs for auditing decisions of the Fisher and Marks agents.
* Unit and integration test coverage for the state graph (LangGraph).

* **Q3/2026 - Cloud Native & Containerization:**
* Application dockerization and CI/CD implementation (GitHub Actions).
* Experimental deployment on **AWS Fargate** and **AWS Secrets Manager** configuration.

* **Q4/2026 - Persistence and Big Data:**
* Data Lake implementation on **AWS S3** via Boto3.
* Historical storage of analyses for performance tracking of "Fair Value" vs. Market.

* **Q1/2027 - Intelligent Delivery and API:**
* Development of an API (FastAPI) for external consumption of analyses.
* Configuration of an alert system via **AWS SNS** for notification of critical Margins of Safety.

---

## AI-Driven Development Workflow
This repository operates under a strict **Cognitive Hybridization** topology and **Risk Confinement** dogmas. It is designed to be built by a team of Human Tech Leads and AI Assistants.

**For AI Assistants reading this file:**
1. **STOP** and immediately read `.ai/context.md`. It is your Single Source of Truth (SSOT).
2. Understand the "Zero Numerical Hallucination" dogma: Financial values in Graph State MUST use `Optional[float] = None`. `decimal.Decimal` is FORBIDDEN in state schemas.
3. This project utilizes the RPI (Research, Plan, Implement) workflow. Check `.context/protocol/` for the operational entry points.
4. **Topology Context:**
   - **NotebookLM:** Generates Macro/Micro briefings (`.notebooklm/`).
   - **Google AI Studio:** Semantic validation and prompt testing (`.ai-studio/`).
   - **GEM (Web):** The System Architect mapping the Sprints (`.gemini/`).
   - **VS Code (Claude/Copilot):** The Developer executing defensive coding.

---

## 📝 License

This project is strictly for academic purposes and software engineering study. **It does not constitute a recommendation to buy or sell assets.**
