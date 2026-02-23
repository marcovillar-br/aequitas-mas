from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.state import AequitasState

def marks_agent(state: AequitasState):
    """
    Marks Agent using Google Gemini Flash.
    Cross-references Graham and Fisher data to identify overconfidence or hidden risks.
    """
    metrics = state.get("quant_metrics")
    analysis = state.get("qual_analysis")
    ticker = state.get("target_ticker")
    
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
        f"QUALITATIVE DATA (FISHER):\n"
        f"- Sentiment: {analysis.sentiment_score}\n"
        f"- Identified Risks: {', '.join(analysis.key_risks)}\n\n"
        "Your task: Identify if the margin of safety is robust or if the qualitative risks "
        "might nullify it. Generate a final verdict of max 3 sentences in Portuguese (PT-BR)."
    )
    
    response = llm.invoke(prompt)
    
    return {
        "audit_log": [response.content],
        "messages": [{"role": "assistant", "content": f"AUDITORIA MARKS: {response.content}"}]
    }