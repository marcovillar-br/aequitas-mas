# -*- coding: utf-8 -*-
"""
Tests for the Macro Agent — HyDE + RAG pipeline (Sprint 3.2).

Validates the two-stage pipeline (HyDE generation → vector retrieval →
MacroAnalysis synthesis) using mocks for all external dependencies (LLM,
VectorStorePort). No real LLM or AWS calls are made.

Coverage:
    - Success path: HyDE generated, docs retrieved, MacroAnalysis populated.
    - Dynamic source_urls: injected from retrieval metadata, not from LLM.
    - Controlled Degradation: empty retrieval produces analysis with None metrics.
    - audit_log: reasoning trace present in all execution paths.
    - Full fallback: LLM failure returns degraded MacroAnalysis + audit entry.
    - NullVectorStore: module-level macro_agent runs without infrastructure.
"""
from datetime import date

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage

from src.agents.macro import (
    _build_audit_trace,
    _extract_source_urls,
    _format_retrieved_context,
    create_macro_agent,
    macro_agent,
)
from src.core.interfaces.vector_store import (
    NullVectorStore,
    VectorSearchResult,
    VectorStorePort,
)
from src.core.state import AgentState, MacroAnalysis

# ---------------------------------------------------------------------------
# 1. FIXTURES AND MOCK DATA
# ---------------------------------------------------------------------------

MOCK_HYDE_TEXT = (
    "O Comitê de Política Monetária (COPOM) deliberou pela manutenção da taxa Selic "
    "em 10,75% a.a., sinalizando ciclo contracionista diante da persistência inflacionária "
    "do IPCA acima da meta de 3,0%. O FED, por sua vez, manteve o intervalo alvo de "
    "5,25-5,50% para os Fed Funds, com postura hawkish para 2026."
)

MOCK_RETRIEVED_DOCS = [
    VectorSearchResult(
        document_id="bcb-copom-2025-12",
        source_url="https://www.bcb.gov.br/publicacoes/atascopom/cronologico",
        content="A taxa Selic permanece em 10,75% ao ano conforme deliberação do COPOM.",
        score=0.9231,
    ),
    VectorSearchResult(
        document_id="fed-minutes-2025-11",
        source_url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
        content="The Federal Open Market Committee maintained the target range at 5.25-5.50%.",
        score=0.8874,
    ),
]

MOCK_MACRO_ANALYSIS = MacroAnalysis(
    trend_summary="Ciclo contracionista global com Selic em 10,75% e Fed Funds em 5,25-5,50%.",
    interest_rate_impact=0.42,
    inflation_outlook="IPCA projetado acima da meta em 2025, com ancoragem prevista para 2026.",
    source_urls=[],  # LLM always returns [] — agent injects real URLs from retrieval.
)


@pytest.fixture
def initial_state() -> AgentState:
    """Baseline AgentState for macro agent tests."""
    return AgentState(
        messages=[],
        target_ticker="PETR4",
        as_of_date=date(2024, 1, 2),
        audit_log=[],
    )


@pytest.fixture
def mock_vector_store() -> MagicMock:
    """Mock VectorStorePort returning two realistic documents."""
    store = MagicMock(spec=VectorStorePort)
    store.search_macro_context.return_value = MOCK_RETRIEVED_DOCS
    return store


# ---------------------------------------------------------------------------
# 2. TEST CASES
# ---------------------------------------------------------------------------


@patch("src.agents.macro.time.sleep")
@patch("src.agents.macro.ChatGoogleGenerativeAI")
def test_macro_agent_success_path(
    mock_llm_cls, mock_sleep, initial_state: AgentState, mock_vector_store: MagicMock
) -> None:
    """
    Validates the full success path:
    1. HyDE chain is invoked to generate the hypothesis.
    2. VectorStore is called with the hypothesis text.
    3. Synthesis chain produces a MacroAnalysis.
    4. source_urls are injected from retrieval metadata (not from the LLM).
    5. audit_log contains a reasoning trace entry.
    """
    # Arrange: mock HyDE chain (returns AIMessage)
    mock_hyde_response = MagicMock()
    mock_hyde_response.content = MOCK_HYDE_TEXT

    # Arrange: mock synthesis chain (returns MacroAnalysis with empty source_urls)
    mock_synthesis_structured = MagicMock()
    mock_synthesis_structured.invoke.return_value = MOCK_MACRO_ANALYSIS

    mock_llm_instance = MagicMock()
    mock_llm_instance.__or__ = MagicMock(return_value=MagicMock(
        invoke=MagicMock(return_value=mock_hyde_response)
    ))
    mock_llm_instance.with_structured_output.return_value = MagicMock(
        __ror__=MagicMock()
    )
    mock_llm_cls.return_value = mock_llm_instance

    # Use a simpler approach: patch the internal chain invocations directly
    agent = create_macro_agent(mock_vector_store)

    with patch("src.agents.macro._invoke_hyde_chain", return_value=MOCK_HYDE_TEXT), \
         patch("src.agents.macro._invoke_synthesis_chain", return_value=MOCK_MACRO_ANALYSIS):

        result = agent(initial_state)

    # Assert: VectorStore was called with the HyDE text
    mock_vector_store.search_macro_context.assert_called_once_with(
        MOCK_HYDE_TEXT,
        as_of_date=initial_state.as_of_date,
        top_k=5,
    )

    # Assert: MacroAnalysis is present and valid
    assert "macro_analysis" in result
    analysis: MacroAnalysis = result["macro_analysis"]
    assert isinstance(analysis, MacroAnalysis)
    assert analysis.trend_summary == MOCK_MACRO_ANALYSIS.trend_summary
    assert analysis.interest_rate_impact == MOCK_MACRO_ANALYSIS.interest_rate_impact

    # Assert: source_urls come from retrieval metadata, NOT from LLM output
    expected_urls = [doc.source_url for doc in MOCK_RETRIEVED_DOCS]
    assert analysis.source_urls == expected_urls

    # Assert: audit_log has exactly one traceability entry
    assert "audit_log" in result
    assert len(result["audit_log"]) == 1
    audit_entry: str = result["audit_log"][0]
    assert "HyDE" in audit_entry
    assert "PETR4" in audit_entry


@patch("src.agents.macro.time.sleep")
@patch("src.agents.macro.ChatGoogleGenerativeAI")
def test_macro_agent_empty_retrieval_controlled_degradation(
    mock_llm_cls, mock_sleep, initial_state: AgentState
) -> None:
    """
    When the vector store returns no documents (NullVectorStore or empty index),
    the agent must still produce a valid MacroAnalysis with:
    - source_urls == []
    - Optional[float] fields set to None if the LLM can't confirm values.
    - audit_log explaining the absence of retrieval results.
    """
    null_store = NullVectorStore()
    agent = create_macro_agent(null_store)

    degraded_analysis = MacroAnalysis(
        trend_summary="Ciclo incerto: sem contexto vetorial disponível.",
        interest_rate_impact=None,
        inflation_outlook=None,
        source_urls=[],
    )

    with patch("src.agents.macro._invoke_hyde_chain", return_value=MOCK_HYDE_TEXT), \
         patch("src.agents.macro._invoke_synthesis_chain", return_value=degraded_analysis):

        result = agent(initial_state)

    analysis = result["macro_analysis"]
    assert analysis.source_urls == []
    assert analysis.interest_rate_impact is None
    assert analysis.inflation_outlook is None

    # Audit log must explain that no docs were retrieved
    assert "audit_log" in result
    assert "nenhum documento" in result["audit_log"][0].lower()


@patch("src.agents.macro.time.sleep")
@patch("src.agents.macro.ChatGoogleGenerativeAI")
def test_macro_agent_source_urls_deduplication(
    mock_llm_cls, mock_sleep, initial_state: AgentState
) -> None:
    """
    When retrieved docs contain duplicate source_urls, the agent must
    deduplicate them preserving retrieval order.
    """
    duplicate_docs = [
        VectorSearchResult(
            document_id="d1",
            source_url="https://bcb.gov.br/ata1",
            content="...",
            score=0.95,
        ),
        VectorSearchResult(
            document_id="d2",
            source_url="https://bcb.gov.br/ata1",
            content="...",
            score=0.91,
        ),
        VectorSearchResult(
            document_id="d3",
            source_url="https://fed.gov/minutes",
            content="...",
            score=0.88,
        ),
    ]
    store = MagicMock(spec=VectorStorePort)
    store.search_macro_context.return_value = duplicate_docs
    agent = create_macro_agent(store)

    with patch("src.agents.macro._invoke_hyde_chain", return_value=MOCK_HYDE_TEXT), \
         patch("src.agents.macro._invoke_synthesis_chain", return_value=MOCK_MACRO_ANALYSIS):

        result = agent(initial_state)

    urls = result["macro_analysis"].source_urls
    assert len(urls) == 2  # duplicate removed
    assert urls[0] == "https://bcb.gov.br/ata1"
    assert urls[1] == "https://fed.gov/minutes"


@patch("src.agents.macro.time.sleep")
@patch("src.agents.macro.ChatGoogleGenerativeAI")
def test_macro_agent_llm_failure_controlled_degradation(
    mock_llm_cls, mock_sleep, initial_state: AgentState, mock_vector_store: MagicMock
) -> None:
    """
    When the LLM raises an unexpected exception, the agent must:
    - Return a populated fallback MacroAnalysis (not raise).
    - Include an ALERTA entry in audit_log.
    - Include a failure AIMessage in messages.
    """
    agent = create_macro_agent(mock_vector_store)

    with patch("src.agents.macro._invoke_hyde_chain", side_effect=RuntimeError("LLM unavailable")):
        result = agent(initial_state)

    assert "macro_analysis" in result
    fallback: MacroAnalysis = result["macro_analysis"]
    assert isinstance(fallback, MacroAnalysis)
    assert fallback.interest_rate_impact is None
    assert fallback.source_urls == []

    assert "audit_log" in result
    assert "ALERTA" in result["audit_log"][0]

    assert "messages" in result
    assert any(isinstance(m, AIMessage) for m in result["messages"])


# ---------------------------------------------------------------------------
# 3. UNIT TESTS: Private helpers
# ---------------------------------------------------------------------------


def test_extract_source_urls_deduplication() -> None:
    docs = [
        VectorSearchResult(document_id="1", source_url="https://bcb.gov.br/a", content="", score=0.9),
        VectorSearchResult(document_id="2", source_url="https://bcb.gov.br/a", content="", score=0.8),
        VectorSearchResult(document_id="3", source_url="https://fed.gov/b", content="", score=0.7),
        VectorSearchResult(document_id="4", source_url="", content="", score=0.6),
        VectorSearchResult(document_id="5", source_url="https://bcb.gov.br/c", content="", score=0.5),
    ]
    result = _extract_source_urls(docs)
    assert result == ["https://bcb.gov.br/a", "https://fed.gov/b", "https://bcb.gov.br/c"]


def test_format_retrieved_context_empty() -> None:
    result = _format_retrieved_context([])
    assert "Nenhum documento recuperado" in result


def test_format_retrieved_context_with_docs() -> None:
    result = _format_retrieved_context(MOCK_RETRIEVED_DOCS)
    assert "bcb.gov.br" in result
    assert "federalreserve.gov" in result
    assert "0.9231" in result


def test_build_audit_trace_with_docs() -> None:
    trace = _build_audit_trace("PETR4", MOCK_HYDE_TEXT, MOCK_RETRIEVED_DOCS)
    assert "PETR4" in trace
    assert "HyDE" in trace
    assert "2" in trace  # 2 documents
    assert "bcb.gov.br" in trace


def test_build_audit_trace_no_docs() -> None:
    trace = _build_audit_trace("WEGE3", MOCK_HYDE_TEXT, [])
    assert "WEGE3" in trace
    assert "nenhum documento" in trace.lower()


# ---------------------------------------------------------------------------
# 4. PROTOCOL COMPLIANCE
# ---------------------------------------------------------------------------


def test_null_vector_store_satisfies_protocol() -> None:
    """NullVectorStore must satisfy VectorStorePort structurally."""
    store = NullVectorStore()
    assert isinstance(store, VectorStorePort)
    assert store.search_macro_context(
        "any query",
        as_of_date=date(2024, 1, 2),
        top_k=3,
    ) == []


def test_module_level_macro_agent_requires_explicit_wiring(
    initial_state: AgentState,
) -> None:
    """
    Direct imports of src.agents.macro.macro_agent must fail fast instead of
    silently degrading to an unwired NullVectorStore execution path.
    """
    assert callable(macro_agent)
    with pytest.raises(RuntimeError, match="explicit vector store wiring"):
        macro_agent(initial_state)


# ---------------------------------------------------------------------------
# 5. OPENSEARCH CONNECTION FAILURE — Controlled Degradation
# ---------------------------------------------------------------------------


@patch("src.agents.macro.time.sleep")
@patch("src.agents.macro.ChatGoogleGenerativeAI")
def test_macro_agent_opensearch_connection_failure_degrades_gracefully(
    mock_llm_cls, mock_sleep, initial_state: AgentState
) -> None:
    """
    Validates Controlled Degradation when OpenSearch raises ConnectionError during retrieval.

    Scenario: HyDE generation succeeds, but VectorStorePort raises ConnectionError
    (e.g., network timeout or cluster unavailable).

    Expected Controlled Degradation behaviour:
    1. Agent must NOT propagate the exception — LangGraph graph must not stall.
    2. macro_analysis must be returned with numeric metrics set to None
       (interest_rate_impact=None) — Zero Numerical Hallucination enforced.
    3. source_urls must be [] — no URLs hallucinated by the LLM.
    4. audit_log must contain an entry prefixed with "ALERTA" signalling the failure.
    5. messages must contain a degradation AIMessage for the graph conversation history.
    """
    # Arrange: VectorStore that raises a network error during retrieval.
    failing_store = MagicMock(spec=VectorStorePort)
    failing_store.search_macro_context.side_effect = ConnectionError(
        "OpenSearch cluster unavailable: connection timed out after 30s"
    )

    agent = create_macro_agent(failing_store)

    with patch("src.agents.macro._invoke_hyde_chain", return_value=MOCK_HYDE_TEXT):
        result = agent(initial_state)

    # --- Assert 1: valid return dict, no exception propagated ---
    assert isinstance(result, dict), "Agent must return a dict even on failure."

    # --- Assert 2: MacroAnalysis present with numeric metrics set to None ---
    assert "macro_analysis" in result
    fallback: MacroAnalysis = result["macro_analysis"]
    assert isinstance(fallback, MacroAnalysis)
    assert fallback.interest_rate_impact is None, (
        "interest_rate_impact must be None — Zero Numerical Hallucination."
    )
    assert fallback.inflation_outlook is None, (
        "inflation_outlook must be None after retrieval failure."
    )

    # --- Assert 3: source_urls empty — no URL hallucination ---
    assert fallback.source_urls == [], (
        "source_urls must be [] after OpenSearch connection failure."
    )

    # --- Assert 4: audit_log contains failure signal ---
    assert "audit_log" in result
    assert len(result["audit_log"]) >= 1
    assert "ALERTA" in result["audit_log"][0], (
        "audit_log must contain 'ALERTA' to signal degradation to the Marks Agent."
    )

    # --- Assert 5: degradation AIMessage present in graph history ---
    assert "messages" in result
    assert any(
        isinstance(m, AIMessage) for m in result["messages"]
    ), "messages must contain a degradation AIMessage for graph traceability."

    # --- Extra assert: VectorStore was called (HyDE reached the retrieval stage) ---
    failing_store.search_macro_context.assert_called_once_with(
        MOCK_HYDE_TEXT,
        as_of_date=initial_state.as_of_date,
        top_k=5,
    )


@patch("src.agents.macro.time.sleep")
@patch("src.agents.macro.ChatGoogleGenerativeAI")
def test_macro_agent_opensearch_timeout_does_not_stall_langgraph(
    mock_llm_cls, mock_sleep, initial_state: AgentState, mock_vector_store: MagicMock
) -> None:
    """
    Validates that macro_agent always returns a dict on failure, preventing LangGraph Death Loops.

    The LangGraph node contract requires the node to return a dict on every execution path.
    If macro_analysis is absent from the return value, the router cannot determine the next
    node and will loop indefinitely (Death Loop).

    Scenario: TimeoutError raised by the VectorStore after HyDE generation succeeds.
    """
    timeout_store = MagicMock(spec=VectorStorePort)
    timeout_store.search_macro_context.side_effect = TimeoutError(
        "OpenSearch request timed out after 30s"
    )

    agent = create_macro_agent(timeout_store)

    with patch("src.agents.macro._invoke_hyde_chain", return_value=MOCK_HYDE_TEXT):
        result = agent(initial_state)

    # LangGraph node contract: must return dict, never raise.
    assert isinstance(result, dict), "LangGraph node must return dict, never propagate exceptions."

    # macro_analysis must be present so the router can advance to the Marks node.
    assert "macro_analysis" in result, (
        "macro_analysis absent: router would loop indefinitely (Death Loop)."
    )

    # Confirm the fallback is a valid Pydantic instance (no ValidationError raised).
    assert isinstance(result["macro_analysis"], MacroAnalysis)
