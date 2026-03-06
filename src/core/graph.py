from src.agents.graham import graham_agent
from src.agents.fisher import fisher_agent
from src.agents.marks import marks_agent
from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.core.state import AgentState

# 1. DEFINIÇÃO DO ROTEADOR (ARESTAS CONDICIONAIS)
def router(state: AgentState) -> Literal["graham", "fisher", "marks", "__end__"]:
    """
    Lógica de roteamento do Supervisor (Núcleo Aequitas).
    Decide o próximo passo com base no estado atual.
    """
    # Se o Agente Graham (Quant) ainda não atuou, ele é a prioridade
    if not state.get("metrics"):
        return "graham"

    # Se já temos dados quantitativos, mas falta a análise qualitativa
    if not state.get("qual_analysis"):
        return "fisher"

    # Se Graham e Fisher terminaram, Marks (Auditor) dá o veredito final
    if len(state.get("audit_log", [])) == 0:
        return "marks"

    return "__end__"

# 2. CONSTRUÇÃO DO GRAFO
def create_graph():
    """
    Constrói o grafo agêntico Aequitas-MAS usando LangGraph.

    Este grafo utiliza um padrão de roteamento centralizado onde cada agente especialista
    (Graham, Fisher, Marks) devolve o controle a uma função `router` central
    após a execução. O roteador então decide o próximo passo com base no estado
    atual, permitindo fluxos de trabalho dinâmicos, robustos e cíclicos.
    """
    # Inicializa o Grafo com o esquema de estado normativo
    workflow = StateGraph(AgentState)

    # Define os nós dos agentes especialistas
    workflow.add_node("graham", graham_agent)
    workflow.add_node("fisher", fisher_agent)
    workflow.add_node("marks", marks_agent)

    # Define o mapeamento da decisão do roteador para o próximo nó
    router_map = {
        "graham": "graham",
        "fisher": "fisher",
        "marks": "marks",
        "__end__": END,
    }

    # O ponto de entrada agora é condicional, decidido pela própria função do roteador,
    # permitindo que o grafo inicie em qualquer ponto do processo.
    workflow.set_conditional_entry_point(router, router_map)

    # Adiciona arestas condicionais de cada especialista de volta para o roteador.
    workflow.add_conditional_edges("graham", router, router_map)
    workflow.add_conditional_edges("fisher", router, router_map)
    workflow.add_conditional_edges("marks", router, router_map)

    # 3. PERSISTÊNCIA (CHECKPOINTER)
    # MemorySaver local para manter Isomorfismo e Custo Zero
    memory = MemorySaver()

    # Compila o grafo em um aplicativo executável
    return workflow.compile(checkpointer=memory)

# Instância Global do Grafo
app = create_graph()