# -*- coding: utf-8 -*-
"""
Macro Agent Implementation (Aequitas-MAS) — Sprint 3.2.

Implements a two-stage RAG pipeline powered by Hypothetical Document
Embeddings (HyDE) to retrieve macroeconomic context from OpenSearch and
synthesize a structured MacroAnalysis.

Pipeline:
    Stage 1 — HyDE Generation:
        The LLM produces a dense, hypothetical COPOM/FED announcement text
        anchored to the target ticker. This synthetic document serves as the
        semantic query vector, bypassing the vocabulary mismatch problem of
        sparse retrieval.

    Stage 2 — Retrieval + Synthesis:
        The hypothetical text is passed to the injected VectorStorePort, which
        performs k-NN similarity search against the OpenSearch index. Retrieved
        chunks are injected into the synthesis prompt and the LLM produces a
        validated MacroAnalysis. source_urls are populated deterministically
        from the retrieval metadata — never hallucinated by the LLM.

DIP Enforcement:
    This module depends exclusively on VectorStorePort (core/interfaces).
    No infrastructure SDK (boto3, opensearch-py) is imported here.
"""

import time
from collections.abc import Callable
from datetime import date
from typing import Any

import structlog
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

try:
    from google.api_core.exceptions import ResourceExhausted
except ImportError:  # pragma: no cover - defensive import guard
    class _ResourceExhaustedFallback(Exception):
        """Fallback exception used when google.api_core is unavailable."""

    ResourceExhausted = _ResourceExhaustedFallback

from src.core.llm import require_gemini_api_key
from src.core.interfaces.vector_store import (
    VectorSearchResult,
    VectorStorePort,
)
from src.core.state import AgentState, MacroAnalysis

logger = structlog.get_logger(__name__)


def _resolve_as_of_date(state: AgentState) -> date:
    """Resolve the point-in-time date from state when available."""
    as_of_date = getattr(state, "as_of_date", None)
    if not isinstance(as_of_date, date):
        raise ValueError("AgentState.as_of_date must be a valid date.")
    return as_of_date

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

# Stage 1: HyDE — Generates a hypothetical COPOM/FED announcement.
# Output is plain text; structured extraction is NOT used here to preserve
# the maximum semantic density of the hypothetical document.
_HYDE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Macro Agent of Aequitas-MAS. Your sole task is to generate a "
            "technically dense hypothetical document that simulates an excerpt from "
            "official COPOM and/or FED meeting minutes relevant to the target asset.\n\n"
            "The document MUST:\n"
            "- Explicitly mention the Selic rate and/or Fed Funds Rate.\n"
            "- Describe the current liquidity cycle (expansionary or contractionary).\n"
            "- Include an inflation outlook (IPCA/CPI) with plausible data.\n"
            "- Use formal monetary-policy language at academic level (UFG/USP ESALQ).\n\n"
            "Generate ONLY the body of the hypothetical document, with no preamble or "
            "explanations.\n\n"
            "CRITICAL: You must write the entire hypothetical document strictly in "
            "Portuguese (pt-BR), as the indexed corpus is in pt-BR and semantic "
            "similarity depends on language alignment.",
        ),
        (
            "human",
            "Generate the hypothetical macroeconomic context document for asset: {ticker}.",
        ),
    ]
)

# Stage 2: Synthesis — Produces MacroAnalysis grounded in retrieved context.
# source_urls MUST be returned as [] — they are injected deterministically
# from retrieval metadata after this call to enforce Zero Hallucination.
_SYNTHESIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are the Macro Agent of Aequitas-MAS. Based on the macroeconomic context "
            "below — retrieved via vector search from official sources (BCB, FED) — "
            "produce a structured analysis of the macroeconomic environment for the "
            "target asset.\n\n"
            "Non-negotiable rules (Risk Confinement):\n"
            "- If a numeric value is NOT explicitly present in the retrieved context, "
            "return null for that field (Controlled Degradation). NEVER invent numbers.\n"
            "- Return `source_urls` as an empty list [] — it will be populated "
            "deterministically from retrieval metadata after this call.\n\n"
            "Retrieved context:\n"
            "---\n"
            "{context}\n"
            "---\n\n"
            "CRITICAL: You must generate the `trend_summary` and `inflation_outlook` "
            "fields strictly in Portuguese (pt-BR), using formal academic language "
            "(UFG/USP ESALQ standard).",
        ),
        (
            "human",
            "Synthesize the macroeconomic scenario for asset: {ticker}.",
        ),
    ]
)


# ---------------------------------------------------------------------------
# Retry-wrapped LLM invocations
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _invoke_hyde_chain(chain: Any, ticker: str, reflection: str = "") -> str:
    """Invoke HyDE chain with exponential backoff. Returns the raw hypothesis text."""
    ticker_with_reflection = f"{reflection}{ticker}" if reflection else ticker
    response = chain.invoke({"ticker": ticker_with_reflection})
    return response.content if hasattr(response, "content") else str(response)


@retry(
    retry=retry_if_exception_type(ResourceExhausted),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    reraise=True,
)
def _invoke_synthesis_chain(chain: Any, ticker: str, context: str) -> MacroAnalysis:
    """Invoke synthesis chain with exponential backoff. Returns a validated MacroAnalysis."""
    return chain.invoke({"ticker": ticker, "context": context})


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _format_retrieved_context(docs: list[VectorSearchResult]) -> str:
    """
    Format retrieved OpenSearch hits into a readable block for the synthesis prompt.

    Args:
        docs: List of typed results conforming to the VectorStorePort contract.

    Returns:
        A formatted string with numbered excerpts and source attribution.
        Returns a fallback message when the list is empty.
    """
    if not docs:
        return (
            "[Nenhum documento recuperado do índice vetorial. "
            "Utilize seu conhecimento interno, mas aplique Controlled Degradation "
            "para campos numéricos ausentes.]"
        )

    lines: list[str] = []
    for i, doc in enumerate(docs, start=1):
        source = doc.source_url or doc.document_id or "fonte desconhecida"
        content = doc.content.strip()
        lines.append(f"[{i}] Fonte: {source} (score={doc.score:.4f})\n{content}")

    return "\n\n".join(lines)


def _extract_source_urls(docs: list[VectorSearchResult]) -> list[str]:
    """
    Extract non-empty source_url values from retrieved documents.

    Returns a deduplicated, ordered list preserving retrieval rank.
    """
    seen: set[str] = set()
    urls: list[str] = []
    for doc in docs:
        url = doc.source_url.strip()
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def _build_audit_trace(
    ticker: str,
    hyde_text: str,
    docs: list[VectorSearchResult],
) -> str:
    """
    Build a structured reasoning trace for the audit_log.

    Explains which documents were selected by the HyDE retrieval and why,
    satisfying the Ethical Traceability requirement of the system.

    Args:
        ticker:    Target asset ticker.
        hyde_text: The hypothetical document used as the semantic query.
        docs:      Retrieved documents from the vector store.

    Returns:
        A formatted pt-BR audit string for append to AgentState.audit_log.
    """
    hyde_preview = hyde_text[:200].replace("\n", " ") + ("..." if len(hyde_text) > 200 else "")

    if not docs:
        return (
            f"[Macro/HyDE] Análise sem RAG para '{ticker}': nenhum documento recuperado "
            f"do índice vetorial. O agente utilizou conhecimento interno do LLM com "
            f"Controlled Degradation aplicada a todos os campos numéricos.\n"
            f"Consulta HyDE (prévia): \"{hyde_preview}\""
        )

    doc_lines: list[str] = []
    for i, doc in enumerate(docs, start=1):
        source = doc.source_url or doc.document_id or "desconhecido"
        doc_lines.append(f"  [{i}] score={doc.score:.4f} | fonte={source}")

    docs_block = "\n".join(doc_lines)
    return (
        f"[Macro/HyDE] Recuperação vetorial concluída para '{ticker}': "
        f"{len(docs)} documento(s) selecionado(s) por similaridade de cosseno.\n"
        f"Critério de seleção: distância vetorial entre o documento hipotético (HyDE) "
        f"e os chunks indexados do BCB/FED.\n"
        f"Documentos selecionados:\n{docs_block}\n"
        f"Consulta HyDE (prévia): \"{hyde_preview}\""
    )


# ---------------------------------------------------------------------------
# Factory: create_macro_agent (DIP entry point)
# ---------------------------------------------------------------------------

def create_macro_agent(
    vector_store: VectorStorePort,
) -> Callable[[AgentState], dict]:
    """
    Factory that returns a LangGraph-compatible macro agent node.

    Injects the VectorStorePort at construction time, decoupling the agent
    logic from any concrete infrastructure SDK.

    Args:
        vector_store: Any object satisfying the VectorStorePort protocol.
                      Use OpenSearchAdapter for production, NullVectorStore
                      for local/offline execution.

    Returns:
        A callable ``(AgentState) -> dict`` ready to be registered as a
        LangGraph node via ``workflow.add_node("macro", ...)``.
    """

    def macro_agent(state: AgentState) -> dict:
        """
        Execute the two-stage HyDE RAG pipeline for macroeconomic analysis.

        Stage 1: Generate a hypothetical COPOM/FED document (HyDE).
        Stage 2: Retrieve similar chunks from OpenSearch.
        Stage 3: Synthesize a validated MacroAnalysis with real source_urls.
        """
        ticker = state.target_ticker
        as_of_date = _resolve_as_of_date(state)
        logger.info(
            "macro_agent_started",
            ticker=ticker,
            as_of_date=as_of_date.isoformat(),
            pipeline="HyDE+RAG",
        )

        # Free-Tier rate limiting before first LLM call.
        logger.debug("macro_agent_rate_limit_applied", sleep_seconds=15)
        time.sleep(15)

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.0,
            max_retries=1,  # Tenacity handles robust retry logic.
            google_api_key=require_gemini_api_key(),
        )

        try:
            # ------------------------------------------------------------------
            # Stage 1: HyDE — Generate hypothetical COPOM/FED announcement
            # ------------------------------------------------------------------
            hyde_chain = _HYDE_PROMPT | llm
            logger.info("macro_hyde_generation_started", ticker=ticker)
            reflection_block = ""
            if state.iteration_count > 0 and state.reflection_feedback:
                reflection_block = (
                    f"\n\n[REFLECTION — Iteration {state.iteration_count}]\n"
                    f"The consensus supervisor requested re-evaluation: "
                    f"{state.reflection_feedback}\n"
                    "Adjust your analysis considering this feedback.\n\n"
                )
            hyde_text = _invoke_hyde_chain(hyde_chain, ticker, reflection=reflection_block)
            logger.info(
                "macro_hyde_generation_completed",
                ticker=ticker,
                hypothesis_length=len(hyde_text),
            )

            # ------------------------------------------------------------------
            # Stage 2: Retrieval — k-NN search using the hypothesis as query
            # ------------------------------------------------------------------
            logger.info("macro_retrieval_started", ticker=ticker)
            retrieved_docs = vector_store.search_macro_context(
                hyde_text,
                as_of_date=as_of_date,
                top_k=5,
            )
            logger.info(
                "macro_retrieval_completed",
                ticker=ticker,
                documents_retrieved=len(retrieved_docs),
            )

            # ------------------------------------------------------------------
            # Stage 3: Synthesis — Ground the LLM in the retrieved context
            # ------------------------------------------------------------------
            context_block = _format_retrieved_context(retrieved_docs)

            # Free-Tier throttle before second LLM call.
            time.sleep(10)

            synthesis_chain = _SYNTHESIS_PROMPT | llm.with_structured_output(MacroAnalysis)
            raw_result: MacroAnalysis = _invoke_synthesis_chain(
                synthesis_chain, ticker, context_block
            )

            # Inject source_urls deterministically from retrieval metadata.
            # MacroAnalysis is frozen; model_copy creates a new immutable instance.
            dynamic_urls = _extract_source_urls(retrieved_docs)
            result = raw_result.model_copy(update={"source_urls": dynamic_urls})

            # Build reasoning trace for ethical traceability.
            audit_entry = _build_audit_trace(ticker, hyde_text, retrieved_docs)

            logger.info(
                "macro_agent_completed",
                ticker=ticker,
                status="success",
                sources_count=len(dynamic_urls),
            )

            success_message = AIMessage(
                content=f"Análise macroeconômica (Macro) para {ticker} concluída.",
                name="macro",
            )

            return {
                "macro_analysis": result,
                "messages": [success_message],
                "audit_log": [audit_entry],
                "executed_nodes": ["macro"],
            }

        except ResourceExhausted as error:
            logger.error(
                "macro_agent_quota_exhausted",
                error=str(error),
                ticker=ticker,
                exc_info=True,
            )
        except Exception as error:
            logger.error(
                "macro_agent_failed",
                error=str(error),
                ticker=ticker,
                exc_info=True,
            )

        # ------------------------------------------------------------------
        # Controlled Degradation fallback — graph execution never stalls.
        # ------------------------------------------------------------------
        fallback_analysis = MacroAnalysis(
            trend_summary=(
                "Dados macroeconômicos insuficientes: falha no pipeline HyDE/RAG "
                "devido a limites de API ou erro transitório."
            ),
            interest_rate_impact=None,
            inflation_outlook=None,
            source_urls=[],
        )
        failure_msg = AIMessage(
            content=(
                "[Degradação] Agente Macro retornou análise de fallback após falha "
                "no pipeline HyDE+RAG (cota de API ou erro de rede)."
            ),
            name="macro",
        )
        audit_failure = (
            f"ALERTA: Agente Macro degradou para fallback em '{ticker}'. "
            "Pipeline HyDE+RAG não concluído. Análise macroeconômica indisponível."
        )
        return {
            "macro_analysis": fallback_analysis,
            "messages": [failure_msg],
            "audit_log": [audit_failure],
            "executed_nodes": ["macro"],
        }

    return macro_agent


def macro_agent(state: AgentState) -> dict:
    """
    Guard against accidental direct imports without dependency wiring.

    Production/runtime code must use ``create_macro_agent(...)`` with an
    injected ``VectorStorePort`` or consume the fully wired node exported by
    ``src.core.graph``.
    """
    raise RuntimeError(
        "macro_agent requires explicit vector store wiring. "
        "Use create_macro_agent(vector_store) or import src.core.graph.macro_agent."
    )
