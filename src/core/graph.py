from src.agents.graham import graham_agent
from src.agents.fisher import fisher_agent
from src.agents.marks import marks_agent
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.state import AequitasState

# 1. DEFINIÇÃO DO ROTEADOR (CONDITIONAL EDGES)
def router(state: AequitasState) -> Literal["graham", "fisher", "marks", "__end__"]:
    """
    Lógica de roteamento do Supervisor (Aequitas Core).
    Decide o próximo passo com base no estado atual.
    """
    # Se o Agente Graham (Quant) ainda não atuou, ele é a prioridade
    if not state.get("quant_metrics"):
        return "graham"
    
    # Se já temos os dados quantitativos mas falta a análise qualitativa
    if not state.get("qual_analysis"):
        return "fisher"
    
    # Se Graham e Fisher concluíram, Marks (Auditor) faz o veredito final
    if len(state.get("audit_log", [])) == 0:
        return "marks"
    
    return "__end__"

# 2. CONSTRUÇÃO DO GRAFO
def create_graph():
    # Inicializa o Grafo com o esquema de estado normativo
    workflow = StateGraph(AequitasState)

    # Definição dos Nós (Nesta fase, usaremos placeholders para os agentes)
    # Em breve, conectaremos os LLMs reais nestes pontos
    workflow.add_node("graham", graham_agent)
    workflow.add_node("fisher", fisher_agent)
    workflow.add_node("marks", marks_agent)

    # Definição das Bordas
    workflow.set_entry_point("graham") # Entrada padrão
    
    # Roteamento Inteligente
    workflow.add_conditional_edges(
        "graham",
        router,
        {
            "graham": "graham",
            "fisher": "fisher",
            "marks": "marks",
            "__end__": END
        }
    )
    
    workflow.add_edge("fisher", "marks")
    workflow.add_edge("marks", END)

    # 3. PERSISTÊNCIA (CHECKPOINTER)
    # SqliteSaver local para manter o Isomorfismo e Custo Zero
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)

# Instância Global do Grafo
app = create_graph()