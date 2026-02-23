from langchain_google_genai import ChatGoogleGenerativeAI
from ddgs import DDGS 
from src.core.state import AequitasState, FisherAnalysis

def fisher_agent(state: AequitasState):
    """
    Fisher Agent using Google Gemini Flash.
    Uses LLM with_structured_output to bind stochastic inference 
    to strict Pydantic schema validation.
    """
    ticker = state.get("target_ticker")
    
    # 1. LLM Instance
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest", # Standardized and stable alias
        temperature=0.1 # Slight stochasticity for sentiment inference
    )
    
    # 2. Binding Pydantic Model to LLM Output
    structured_llm = llm.with_structured_output(FisherAnalysis)
    
    results = []
    urls = []
    
    # Context Retrieval via DDGS
    with DDGS() as ddgs:
        search_query = f"notícias recentes {ticker} B3 mercado financeiro"
        for r in ddgs.text(search_query, max_results=3):
            results.append(f"Título: {r.get('title', '')}\nResumo: {r.get('body', '')}")
            if 'href' in r:
                urls.append(r['href'])
    
    context = "\n\n".join(results)
    
    # 3. Prompt Engineering (Instruction-Tuned)
    prompt = (
        f"Analyze these recent news about the company {ticker}:\n\n{context}\n\n"
        "Based ONLY on this information, populate the analysis schema:\n"
        "- sentiment_score: Extract market sentiment (-1.0 for extreme pessimism, 1.0 for extreme optimism).\n"
        "- key_risks: List the main risks, macroeconomic or political uncertainties mentioned (in Portuguese).\n"
        f"- source_urls: Strictly use these reference URLs: {urls}"
    )
    
    # 4. Structured Inference
    # The return is no longer a string (AIMessage), but the validated FisherAnalysis instance itself
    analysis_data: FisherAnalysis = structured_llm.invoke(prompt)
    
    # 5. Conversation History Formatting
    # Since the router needs to maintain graph memory, we convert the decision to natural language (PT-BR for User)
    content_summary = (
        f"Resumo Fisher Qualitativo - Sentimento: {analysis_data.sentiment_score} | "
        f"Riscos mapeados: {', '.join(analysis_data.key_risks)}"
    )
    
    return {
        "qual_analysis": analysis_data,
        "messages": [{"role": "assistant", "content": f"Agente Fisher: {content_summary}"}]
    }