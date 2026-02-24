import structlog
from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.state import AequitasState

logger = structlog.get_logger(__name__)

def marks_agent(state: AequitasState) -> dict:
    """
    Marks Agent using Google Gemini Flash.
    Cross-references Graham and Fisher data to identify overconfidence or hidden risks.
    """
    metrics = state["quant_metrics"]
    analysis = state.get("qual_analysis")
    ticker = state["target_ticker"]

    # Build the audit prompt.
    # If the qualitative analysis failed, Marks still works with what it has.
    if analysis is None:
        qualitative_context = (
            "QUALITATIVE DATA (FISHER):\n"
            "- Data unavailable (news fetching may have failed)."
        )
        sentiment_score = "N/A"
        key_risks = ["N/A"]
    else:
        qualitative_context = (
            f"QUALITATIVE DATA (FISHER):\n"
            f"- Sentiment: {analysis.sentiment_score}\n"
            f"- Identified Risks: {', '.join(analysis.key_risks)}"
        )
        sentiment_score = analysis.sentiment_score
        key_risks = analysis.key_risks

    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )

    # Cross-Agent Audit Prompt
    prompt = (
        f"Act as the investor Howard Marks. Analyze the conclusions about {ticker}:\n\n"
        f"QUANTITATIVE DATA (GRAHAM):\n"
        f"- Fair Value: R${metrics.fair_value}\n"
        f"- Margin of Safety: {metrics.margin_of_safety}%\n\n"
        f"{qualitative_context}\n\n"
        "Your task: Identify if the margin of safety is robust or if the qualitative risks "
        "might nullify it. Generate a final verdict of max 3 sentences in Portuguese (PT-BR)."
    )

    response = llm.invoke(prompt)

    logger.info(
        "marks_agent_audit_complete",
        ticker=ticker,
        graham_fair_value=str(metrics.fair_value),
        graham_margin_of_safety=str(metrics.margin_of_safety),
        fisher_sentiment=sentiment_score,
        final_verdict=response.content,
    )

    return {
        "messages": [{"role": "assistant", "content": f"AUDITORIA MARKS: {response.content}"}]
    }