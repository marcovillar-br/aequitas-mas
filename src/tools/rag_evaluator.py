# -*- coding: utf-8 -*-
"""
Deterministic RAG confidence evaluator for Aequitas-MAS.

This module applies the Aequitas calibration for RAG confidence scoring:

    C_rag = 0.60 * Faithfulness + 0.30 * Relevance + 0.10 * Support

The function is intentionally deterministic and defensive. Invalid or missing
inputs degrade safely to ``None`` rather than propagating unreliable numeric
values into the graph state.
"""

from __future__ import annotations

import math
from typing import Any, Optional

FAITHFULNESS_WEIGHT = 0.60
RELEVANCE_WEIGHT = 0.30
SUPPORT_WEIGHT = 0.10


def _coerce_unit_interval(value: Any) -> Optional[float]:
    """Coerce a value to a finite float in the closed interval [0.0, 1.0]."""
    if value is None:
        return None

    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(coerced):
        return None

    if coerced < 0.0 or coerced > 1.0:
        return None

    return coerced


def calculate_c_rag_score(
    faithfulness: Any,
    relevance: Any,
    support: Any,
) -> Optional[float]:
    """
    Compute the deterministic RAG confidence score using Aequitas calibration.

    Args:
        faithfulness: Grounding score in the interval [0.0, 1.0].
        relevance: Answer relevance score in the interval [0.0, 1.0].
        support: Retrieval support score in the interval [0.0, 1.0].

    Returns:
        The calibrated confidence score as a finite float, or ``None`` when
        any input is missing or invalid.
    """
    validated_faithfulness = _coerce_unit_interval(faithfulness)
    validated_relevance = _coerce_unit_interval(relevance)
    validated_support = _coerce_unit_interval(support)

    if (
        validated_faithfulness is None
        or validated_relevance is None
        or validated_support is None
    ):
        return None

    score = (
        FAITHFULNESS_WEIGHT * validated_faithfulness
        + RELEVANCE_WEIGHT * validated_relevance
        + SUPPORT_WEIGHT * validated_support
    )

    if not math.isfinite(score):
        return None

    return score
