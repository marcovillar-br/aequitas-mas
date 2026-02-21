from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS 
from src.core.state import AequitasState, FisherAnalysis

def fisher_agent(state: AequitasState):
    ticker = state.get("target_ticker")
    # Flash é mais resiliente a erros de endpoint 404
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0)
    
    results = []
    # Uso do novo módulo 'ddgs'
    with DDGS() as ddgs:
        search_query = f"notícias recentes {ticker} B3 mercado financeiro"
        for r in ddgs.text(search_query, max_results=3):
            results.append(f"Título: {r['title']}\nResumo: {r['body']}")
    
    context = "\n\n".join(results)
    prompt = (
        f"Analise estas notícias recentes sobre {ticker}:\n\n{context}\n\n"
        "Gere um resumo executivo de 2 frases sobre o sentimento do mercado."
    )
    
    response = llm.invoke(prompt)
    
    return {
        "qual_analysis": FisherAnalysis(
            sentiment_score=0.6, 
            key_risks=["Análise Web Ativa"], 
            source_urls=["ddgs"]
        ),
        "messages": [{"role": "assistant", "content": f"Agente Fisher: {response.content}"}]
    }