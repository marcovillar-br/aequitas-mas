# -*- coding: utf-8 -*-
"""
Módulo de estado central para o Aequitas-MAS.

Este arquivo define a estrutura de dados que circula entre os agentes no grafo LangGraph.
Aderindo ao princípio "Zero Alucinação Numérica", todas as métricas financeiras
utilizam `decimal.Decimal` para garantir precisão matemática e evitar erros de ponto flutuante
do tipo `float`.

Classes:
    GrahamMetrics: Esquema Pydantic para as métricas do Agente Graham.
    FisherAnalysis: Esquema Pydantic para a análise qualitativa do Agente Fisher.
    AgentState: TypedDict representando o estado completo do grafo.
"""
import operator
from decimal import Decimal, InvalidOperation
from typing import Annotated, List, Optional, TypedDict, Any, NotRequired

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# 1. ESQUEMAS PYDANTIC (VALIDAÇÃO DE FRONTEIRA)
# Estes esquemas garantem que os dados gerados por Ferramentas ou LLMs
# estejam matematicamente corretos antes de entrar no estado.


class GrahamMetrics(BaseModel):
    """
    Métricas determinísticas de Value Investing (Agente Graham).

    Esta classe impõe o dogma "Zero Alucinação Numérica" usando
    `Decimal` para todos os cálculos financeiros e impedindo a entrada de
    tipos primitivos `float`.
    """

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    # Validação estrita do ticker para conformidade com o padrão de mercado.
    ticker: str = Field(
        ...,
        description="O código de negociação do ativo na bolsa B3.",
        pattern=r"^[A-Z0-9]{5,6}$",
    )

    # Campos financeiros obrigatórios para a fórmula de Graham.
    vpa: Decimal = Field(..., description="Valor Patrimonial por Ação (VPA).")
    lpa: Decimal = Field(..., description="Lucro por Ação (LPA).")

    # Campos opcionais que dependem de cálculos ou disponibilidade de dados.
    price_to_earnings: Optional[Decimal] = Field(
        None, description="Índice Preço/Lucro (P/L)."
    )
    fair_value: Optional[Decimal] = Field(
        None, description="Valor intrínseco calculado pela fórmula de Graham."
    )
    margin_of_safety: Optional[Decimal] = Field(
        None, description="Margem de segurança percentual."
    )

    @field_validator(
        "vpa",
        "lpa",
        "price_to_earnings",
        "fair_value",
        "margin_of_safety",
        mode="before",
    )
    @classmethod
    def coerce_to_decimal(cls, v: Any) -> Optional[Decimal]:
        """
        Coage com segurança entradas (str, int, float) para Decimal.

        Este validador de pré-processamento garante que quaisquer dados numéricos
        recebidos de fontes externas (APIs, scraping) sejam convertidos para
        `Decimal` antes da validação do Pydantic, evitando a perda de precisão
        do padrão IEEE 754.
        """
        if v is None:
            return None
        try:
            return Decimal(str(v))
        except (InvalidOperation, ValueError):
            raise ValueError(f"Não foi possível converter o valor '{v}' para Decimal.")


class FisherAnalysis(BaseModel):
    """Análise de contexto e sentimento (Agente Fisher)."""

    model_config = ConfigDict(frozen=True)

    sentiment_score: float = Field(
        ...,
        ge=-1,
        le=1,
        description="Pontuação de sentimento extraída das notícias (-1 a 1).",
    )
    key_risks: List[str] = Field(
        ..., description="Lista de principais riscos identificados."
    )
    # Rastreabilidade Ética: Citação de fonte obrigatória.
    source_urls: List[str] = Field(
        default_factory=list, description="URLs das fontes usadas para a análise."
    )


class MacroAnalysis(BaseModel):
    """Holistic evaluation of the macroeconomic environment (Macro Agent)."""

    model_config = ConfigDict(frozen=True)

    trend_summary: str = Field(
        ..., description="Summary of the current macroeconomic trend."
    )
    interest_rate_impact: Optional[Decimal] = Field(
        None, description="Estimated impact of the interest rate (e.g., Selic/Fed Funds)."
    )
    inflation_outlook: Optional[str] = Field(
        None, description="Inflation outlook extracted from official minutes."
    )
    # Rastreabilidade Ética: Citação de fonte obrigatória.
    source_urls: List[str] = Field(
        default_factory=list, description="URLs das fontes usadas para a análise."
    )

    @field_validator(
        "interest_rate_impact",
        mode="before",
    )
    @classmethod
    def coerce_to_decimal(cls, v: Any) -> Optional[Decimal]:
        """
        Coage com segurança entradas para Decimal.
        """
        if v is None:
            return None
        try:
            return Decimal(str(v))
        except (InvalidOperation, ValueError):
            raise ValueError(f"Não foi possível converter o valor '{v}' para Decimal.")


# 2. DEFINIÇÃO DO ESTADO DO GRAFO (LANGGRAPH)
# O estado é o "objeto vivo" que circula entre os agentes.


class AgentState(TypedDict):
    """
    Representa o Estado Cognitivo Híbrido da Aequitas-MAS.

    Utiliza Redutores (`operator.add`) para gerenciar a memória acumulativa
    em `messages` e `audit_log`, permitindo que o histórico seja construído
    de forma incremental a cada passo do grafo.
    """

    # Histórico da conversa entre o Supervisor e os Especialistas.
    messages: Annotated[List[dict], operator.add]

    # Ticker-alvo para a análise atual.
    target_ticker: str

    # Tensores de Decisão (Dados Estruturados).
    # Opcionais e Não-Obrigatórios porque são preenchidos progressivamente.
    # A ausência da chave indica 'não executado', enquanto None indica 'falha controlada'.
    metrics: NotRequired[Optional[GrahamMetrics]]
    qual_analysis: NotRequired[Optional[FisherAnalysis]]
    macro_analysis: NotRequired[Optional[MacroAnalysis]]

    # Log de Auditoria do Agente Marks (O Advogado do Diabo).
    # Annotated + operator.add permite acumular críticas sem sobrescrever.
    audit_log: Annotated[List[str], operator.add]

    # Controle de roteamento para o Supervisor.
    next_agent: str
