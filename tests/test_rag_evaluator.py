"""Unit tests for the deterministic RAG confidence evaluator."""

import math

import pytest

from src.tools.rag_evaluator import calculate_c_rag_score


def test_calculate_c_rag_score_applies_aequitas_calibration() -> None:
    """The evaluator must apply the 0.60 / 0.30 / 0.10 weighting deterministically."""
    score = calculate_c_rag_score(0.9, 0.8, 0.7)

    assert score == pytest.approx(0.85)


def test_calculate_c_rag_score_respects_closed_interval_bounds() -> None:
    """Boundary inputs in the unit interval must remain valid."""
    assert calculate_c_rag_score(0.0, 0.0, 0.0) == pytest.approx(0.0)
    assert calculate_c_rag_score(1.0, 1.0, 1.0) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("faithfulness", "relevance", "support"),
    [
        (None, 0.8, 0.7),
        (0.8, None, 0.7),
        (0.8, 0.7, None),
        (math.nan, 0.8, 0.7),
        (0.8, math.inf, 0.7),
        (0.8, 0.7, -0.1),
        (1.1, 0.7, 0.6),
        ("invalid", 0.7, 0.6),
    ],
)
def test_calculate_c_rag_score_degrades_to_none_for_invalid_inputs(
    faithfulness: object,
    relevance: object,
    support: object,
) -> None:
    """Invalid inputs must degrade safely to None."""
    assert calculate_c_rag_score(faithfulness, relevance, support) is None
