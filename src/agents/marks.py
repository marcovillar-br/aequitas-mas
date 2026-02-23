from langchain_google_genai import ChatGoogleGenerativeAI
from src.core.state import AequitasState

def marks_agent(state: AequitasState):
    """
    Agente Marks usando Google Gemini Flash.
    Cruza dados de Graham e Fisher para identificar excesso de confiança ou riscos ocultos.
    """
    metrics = state.get("quant_metrics")
    analysis = state.get("qual_analysis")
    ticker = state.get("target_ticker")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        temperature=0
    )
    
    # Prompt de Auditoria Cross-Agent
    prompt = (
        f"Aja como o investidor Howard Marks. Analise as conclusões sobre {ticker}:\n\n"
        f"DADOS QUANTITATIVOS (GRAHAM):\n"
        f"- Valor Justo: R${metrics.fair_value}\n"
        f"- Margem de Segurança: {metrics.margin_of_safety}%\n\n"
        f"DADOS QUALITATIVOS (FISHER):\n"
        f"- Sentimento: {analysis.sentiment_score}\n"
        f"- Riscos Identificados: {', '.join(analysis.key_risks)}\n\n"
        "Sua tarefa: Identifique se a margem de segurança é robusta ou se os riscos qualitativos "
        "podem anulá-la. Gere um veredito final de no máximo 3 frases."
    )
    
    response = llm.invoke(prompt)
    
    return {
        "audit_log": [response.content],
        "messages": [{"role": "assistant", "content": f"AUDITORIA MARKS: {response.content}"}]
    }