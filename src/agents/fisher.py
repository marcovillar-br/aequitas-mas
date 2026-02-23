from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS 
from src.core.state import AequitasState, FisherAnalysis

def fisher_agent(state: AequitasState):
    """
    Agente Fisher Refatorado.
    Utiliza LLM with_structured_output para amarrar inferência estocástica 
    à validação estrita do schema Pydantic.
    """
    ticker = state.get("target_ticker")
    
    # 1. Instância do LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest", # Nome padronizado e estável
        temperature=0.1 # Leve estocasticidade para inferência de sentimento
    )
    
    # 2. Binding do Modelo Pydantic à Saída do LLM
    structured_llm = llm.with_structured_output(FisherAnalysis)
    
    results = []
    urls = []
    
    # Busca de Contexto via DDGS
    with DDGS() as ddgs:
        search_query = f"notícias recentes {ticker} B3 mercado financeiro"
        for r in ddgs.text(search_query, max_results=3):
            results.append(f"Título: {r.get('title', '')}\nResumo: {r.get('body', '')}")
            if 'href' in r:
                urls.append(r['href'])
    
    context = "\n\n".join(results)
    
    # 3. Prompt de Engenharia (Instruction-Tuned)
    prompt = (
        f"Analise estas notícias recentes sobre a empresa {ticker}:\n\n{context}\n\n"
        "Com base APENAS nestas informações, preencha o schema de análise:\n"
        "- sentiment_score: Extraia o sentimento de mercado (-1.0 para extremo pessimismo, 1.0 para extremo otimismo).\n"
        "- key_risks: Liste os principais riscos, incertezas macroeconômicas ou políticas mencionadas.\n"
        f"- source_urls: Utilize estritamente estas URLs de referência: {urls}"
    )
    
    # 4. Inferência Estruturada
    # O retorno não é mais uma string (AIMessage), mas a própria instância do FisherAnalysis validada
    analysis_data: FisherAnalysis = structured_llm.invoke(prompt)
    
    # 5. Formatação do Histórico de Conversação
    # Como o router precisa manter a memória do grafo, convertemos a decisão em linguagem natural
    content_summary = (
        f"Resumo Fisher Qualitativo - Sentimento: {analysis_data.sentiment_score} | "
        f"Riscos mapeados: {', '.join(analysis_data.key_risks)}"
    )
    
    return {
        "qual_analysis": analysis_data,
        "messages": [{"role": "assistant", "content": f"Agente Fisher: {content_summary}"}]
    }