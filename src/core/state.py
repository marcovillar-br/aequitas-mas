import operator
from typing import Annotated, List, Optional, TypedDict
from pydantic import BaseModel, Field, field_validator

# 1. ESQUEMAS PYDANTIC (VALIDAÇÃO DE FRONTEIRA)
# Estes esquemas garantem que os dados gerados pelas Tools ou LLMs 
# estejam matematicamente corretos antes de entrar no estado.

class GrahamMetrics(BaseModel):
    """Métricas determinísticas de Value Investing (Agente Graham)."""
    ticker: str = Field(..., description="Ticker da empresa na B3")
    price_to_earnings: float = Field(..., alias="p_l")
    margin_of_safety: float = Field(..., description="Margem de segurança em %")
    fair_value: float = Field(..., description="Preço justo calculado via fórmula")
    
@field_validator("ticker")
@classmethod
def validate_ticker(cls, v: str) -> str:
        if not v.endswith("3") and not v.endswith("4") and not v.endswith("11"):
            raise ValueError("Ticker inválido para o mercado brasileiro (B3).")
        return v.upper()

class FisherAnalysis(BaseModel):
    """Análise de contexto e sentimento (Agente Fisher)."""
    sentiment_score: float = Field(..., ge=-1, le=1)
    key_risks: List[str]
    # Rastreabilidade Ética: Obrigatório citar fontes 
    source_urls: List[str] = Field(default_factory=list)

# 2. DEFINIÇÃO DO ESTADO DO GRAFO (LANGGRAPH)
# O estado é o "objeto vivo" que circula entre os agentes.

class AequitasState(TypedDict):
    """
    Representação do Estado Cognitivo Híbrido do Aequitas-MAS.
    Utiliza Reducers para gerir a memória acumulativa.
    """
    
    # Histórico de conversação entre o Supervisor e Especialistas
    messages: Annotated[List[dict], operator.add]
    
    # Ticker alvo da análise atual
    target_ticker: str
    
    # Tensors de Decisão (Dados Estruturados)
    # São preenchidos conforme o fluxo avança [cite: 44]
    quant_metrics: Optional[GrahamMetrics]
    qual_analysis: Optional[FisherAnalysis]
    
    # Log de Auditoria do Agente Marks (O Advogado do Diabo)
    # Annotated + operator.add permite acumular críticas sem apagar as anteriores
    audit_log: Annotated[List[str], operator.add]
    
    # Controle de Roteamento do Supervisor
    next_agent: str