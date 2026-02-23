import operator
from typing import Annotated, List, Optional, TypedDict
from pydantic import BaseModel, Field, field_validator, ConfigDict

# 1. PYDANTIC SCHEMAS (BOUNDARY VALIDATION & VALUE OBJECTS)
# Enforces immutability and encapsulates business logic (Rich Models).

class GrahamMetrics(BaseModel):
    """Deterministic metrics for Value Investing (Graham Agent)."""
    
    # SOTA: Enforces Immutability for LangGraph State safety
    model_config = ConfigDict(frozen=True)

    ticker: str = Field(..., description="Company ticker on the Brazilian Exchange (B3)")
    price_to_earnings: float = Field(..., alias="p_l")
    margin_of_safety: float = Field(..., description="Margin of safety in percentage")
    fair_value: float = Field(..., description="Fair price calculated via Benjamin Graham's formula")
    
    # CORRECTED: Validator is now properly inside the class scope
    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not v.endswith(("3", "4", "11")):
            raise ValueError(f"Invalid B3 ticker: {v}. Must end with 3, 4, or 11.")
        return v.upper()

    # RICH MODEL: Business Logic Encapsulation (DDD)
    @property
    def is_deep_value(self) -> bool:
        """Evaluates if the margin of safety constitutes a deep value opportunity."""
        return self.margin_of_safety >= 30.0


class FisherAnalysis(BaseModel):
    """Context and sentiment analysis (Fisher Agent)."""
    
    # SOTA: Enforces Immutability
    model_config = ConfigDict(frozen=True)

    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Score from -1.0 (bearish) to 1.0 (bullish)")
    key_risks: List[str] = Field(..., description="List of mapped qualitative risks")
    source_urls: List[str] = Field(default_factory=list, description="Mandatory references for ethical tracing")

    # RICH MODEL: Business Logic Encapsulation (DDD)
    @property
    def is_bearish(self) -> bool:
        """Determines if the overall market sentiment is negative."""
        return self.sentiment_score < 0.0


# 2. LANGGRAPH STATE DEFINITION
# The living cognitive object that mutates safely as it flows through the DAG.

class AequitasState(TypedDict):
    """
    Hybrid Cognitive State Representation of Aequitas-MAS.
    Uses Reducers to manage cumulative memory.
    """
    
    # Conversation history between Supervisor and Experts
    messages: Annotated[List[dict], operator.add]
    
    # Target asset for the current analysis pipeline
    target_ticker: str
    
    # Decision Tensors (Structured Data)
    quant_metrics: Optional[GrahamMetrics]
    qual_analysis: Optional[FisherAnalysis]
    
    # Audit Log from Marks Agent (The Devil's Advocate)
    audit_log: Annotated[List[str], operator.add]
    
    # Supervisor Routing Control
    next_agent: str