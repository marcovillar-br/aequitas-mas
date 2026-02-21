from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.b3_fetcher import get_graham_data
from src.core.state import AequitasState

def graham_agent(state: AequitasState):
    """
    Agente Graham usando Google Gemini 1.5 Pro.
    Efetua a análise quantitativa via ferramentas determinísticas.
    """
    ticker = state.get("target_ticker")
    
    # Inicializa o modelo da Google
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
        
    try:
        # Chamada limpa da ferramenta (Sem metadados de citação)
        metrics = get_graham_data(ticker)
        
        content = (
            f"Análise quantitativa de {ticker} finalizada. "
            f"Valor Justo: R${metrics.fair_value} | Margem: {metrics.margin_of_safety}%."
        )
        
        return {
            "quant_metrics": metrics,
            "messages": [{"role": "assistant", "content": content}]
        }
    except Exception as e:
        return {
            "messages": [{"role": "assistant", "content": f"Falha no Agente Graham: {str(e)}"}],
            "next_agent": "__end__"
        }