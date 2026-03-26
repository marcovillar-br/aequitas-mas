---
plan_id: plan-sprint12-graham-structured-streaming-001
target_files:
  - ".context/current-sprint.md"
  - "src/core/state.py"
  - "src/agents/graham.py"
  - "tests/test_graham_agent.py"
  - "src/api/routers/analyze.py"
  - "src/api/schemas.py"
  - "tests/test_api_analyze_router.py"
  - ".context/SPEC.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, temporal-invariance]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Sprint 12 delivers two high-impact features aligned with the
`PLAN.md` roadmap for **Abr-Mai/26 (Framework & API): Telemetry & Streaming**:

1. **Graham `with_structured_output`:** The Graham agent is the only specialist
   that still returns a plain-text `AIMessage`. Fisher, Marks, Macro, and
   Core Consensus all use `with_structured_output` to produce validated
   Pydantic schemas. This asymmetry forces `core_consensus_node` to parse
   Graham's output as raw text, losing type safety at the committee boundary.
   Fixing this is a prerequisite for the Thesis-CoT Presentation Adapter
   (which consumes structured JSON) and for the XAI Dashboard (which renders
   typed committee outputs).

2. **Streaming API (`/analyze/stream`):** The graph already supports
   `stream()` internally (via `InstrumentedGraphApp.stream()`), but no API
   endpoint exposes it. Adding an SSE endpoint enables real-time observation
   of the committee deliberation — a key requirement for the optional
   XAI Dashboard and for the PA defense demo.

**SCOPE GUARD:**
- `src/agents/graham.py` is the only agent file modified.
- `src/core/state.py` receives a new Pydantic schema (`GrahamInterpretation`).
- `src/api/routers/analyze.py` receives a new SSE endpoint.
- `src/api/schemas.py` receives streaming event schemas.
- Zero modifications to other agents, tools, or infrastructure files.
- `.context/SPEC.md` is updated (artifact-only) to reflect the new contracts.

---

## 2. File Implementation

### Step 2.1 — Define `GrahamInterpretation` schema (RED-GREEN-REFACTOR)

* **Target:** `src/core/state.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:** Add a new Pydantic V2 schema alongside the existing state
  definitions:

```python
class GrahamInterpretation(BaseModel):
    """Structured output boundary for the Graham interpreter agent."""

    model_config = ConfigDict(frozen=True)

    thesis: str
    fair_value_assessment: str
    margin_of_safety_assessment: str
    piotroski_assessment: Optional[str] = None
    altman_assessment: Optional[str] = None
    recommendation: str  # "buy", "hold", "avoid"
    confidence: Optional[float] = None  # 0.0–1.0, validated by isfinite
```

* **Tests to add in `tests/test_graham_agent.py`:**

**Test A — GrahamInterpretation is frozen (immutable)**
```python
def test_graham_interpretation_is_frozen() -> None:
    """The structured output boundary must be immutable."""
    interp = GrahamInterpretation(
        thesis="Strong margin of safety.",
        fair_value_assessment="Undervalued by 35%.",
        margin_of_safety_assessment="Adequate per Graham criteria.",
        recommendation="buy",
    )
    with pytest.raises(ValidationError):
        interp.thesis = "changed"
```

**Test B — GrahamInterpretation degrades confidence to None for non-finite**
```python
def test_graham_interpretation_degrades_non_finite_confidence() -> None:
    """Non-finite confidence must degrade to None at the boundary."""
    interp = GrahamInterpretation(
        thesis="Test thesis.",
        fair_value_assessment="Test.",
        margin_of_safety_assessment="Test.",
        recommendation="hold",
        confidence=float("nan"),
    )
    assert interp.confidence is None
```

* **Constraints:** The `confidence` field requires a `@field_validator` to
  coerce non-finite floats to `None` using `math.isfinite()`, consistent with
  the pattern in `PiotroskiInputs` and `AltmanInputs`.

---

### Step 2.2 — Wire `with_structured_output` in Graham agent (REFACTOR)

* **Target:** `src/agents/graham.py`
* **Execution mode:** code-bearing — modify the existing agent to use
  structured extraction.

* **Action:**
  1. Import `GrahamInterpretation` from `src.core.state`.
  2. Replace the current `llm.invoke(prompt)` call with
     `llm.with_structured_output(GrahamInterpretation).invoke(prompt)`.
  3. Map the structured output into the state patch returned by the node.
     The `metrics` field in `AgentState` already stores the quantitative
     data; the new `GrahamInterpretation` should be stored in a new
     state field or serialized into the existing `graham_interpretation`
     message. Read `src/core/state.py` to determine the exact field.
  4. Update the prompt to instruct the LLM to populate all schema fields,
     especially `recommendation` (constrained to "buy", "hold", "avoid")
     and `confidence` (0.0–1.0).

* **Tests to add in `tests/test_graham_agent.py`:**

**Test C — Graham node returns structured interpretation (mocked LLM)**
```python
def test_graham_node_returns_structured_interpretation() -> None:
    """The Graham node must return a GrahamInterpretation, not raw text."""
    # Mock the LLM to return a valid GrahamInterpretation
    # Invoke the graham node with a valid state
    # Assert the returned patch contains a GrahamInterpretation-compatible dict
```

* **Constraints:** The anti-math guardrails in the prompt must be preserved
  exactly. The prompt must explicitly instruct: "Populate all fields of the
  output schema. For `recommendation`, use exactly one of: buy, hold, avoid.
  For `confidence`, provide a value between 0.0 and 1.0."

---

### Step 2.3 — Add SSE streaming endpoint `/analyze/stream` (RED-GREEN-REFACTOR)

* **Target:** `src/api/routers/analyze.py` and `src/api/schemas.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action in `src/api/schemas.py`:** Add streaming event schema:

```python
class StreamEvent(BaseModel):
    """SSE event payload for real-time committee observation."""

    model_config = ConfigDict(frozen=True)

    node_name: str
    event_type: str  # "node_start", "node_end", "final"
    data: dict[str, Any]
```

* **Action in `src/api/routers/analyze.py`:** Add a new endpoint:

```python
@router.post("/analyze/stream")
async def analyze_stream(request: AnalyzeRequest, ...) -> EventSourceResponse:
    """Stream committee deliberation as Server-Sent Events."""
    async def event_generator():
        for chunk in graph_app.stream(input_data, config):
            for node_name, node_output in chunk.items():
                yield StreamEvent(
                    node_name=node_name,
                    event_type="node_end",
                    data=_serialize_node_output(node_output),
                ).model_dump_json()
    return EventSourceResponse(event_generator())
```

* **Dependency:** `sse-starlette` must be added to `pyproject.toml`.
  Verify Lambda compatibility with Mangum before adding.

* **Tests to add in `tests/test_api_analyze_router.py`:**

**Test D — Streaming endpoint returns SSE events**
```python
def test_analyze_stream_returns_sse_events() -> None:
    """The /analyze/stream endpoint must return Server-Sent Events."""
    # Mock the graph app to yield 5 chunks (one per specialist node)
    # POST to /analyze/stream with a valid AnalyzeRequest
    # Assert response content-type is text/event-stream
    # Assert 5 events are received with correct node_name ordering
```

**Test E — Streaming endpoint handles graph errors gracefully**
```python
def test_analyze_stream_handles_graph_error_gracefully() -> None:
    """Graph errors during streaming must not crash the SSE connection."""
    # Mock graph_app.stream() to raise after 2 events
    # Assert the stream closes cleanly with an error event
```

* **Constraints:** The endpoint must use the same DI pattern as `/analyze`
  (graph app + checkpointer via `Depends`). The SSE serialization must NOT
  include raw exception text in production — use sanitized error events.

---

### Step 2.4 — Update SPEC.md Section 7 (artifact-only)

* **Target:** `.context/SPEC.md`
* **Action:** Replace the current "Próxima Extensão Planejada" section (7)
  with Sprint 12 deliverables:

```markdown
## 7. Próxima Extensão Planejada

O baseline consolidado (Sprint 11) entrega CI/CD shift-left com dogma
enforcement automatizado e cobertura DAIA estatística.

Os próximos passos (Sprint 12: Abr/26 — Framework & API) focam em:
- Elevação do Graham agent para `with_structured_output` (`GrahamInterpretation`),
  eliminando a última assimetria de tipagem no comitê.
- Exposição de streaming SSE via `/analyze/stream` para observação em tempo
  real da deliberação do comitê iterativo.
- Preparação da superfície de API para o XAI Dashboard opcional.
```

---

## 3. Definition of Done (DoD)

- [ ] `src/core/state.py`: `GrahamInterpretation` schema with `frozen=True`,
  `confidence` field validated by `math.isfinite()`, and controlled degradation.
- [ ] `src/agents/graham.py`: Uses `with_structured_output(GrahamInterpretation)`
  instead of plain `invoke()`. Anti-math guardrails preserved.
- [ ] `tests/test_graham_agent.py`: Tests A–C passing (frozen, degradation,
  structured output integration).
- [ ] `src/api/routers/analyze.py`: `/analyze/stream` SSE endpoint implemented
  with sanitized error handling.
- [ ] `src/api/schemas.py`: `StreamEvent` schema added.
- [ ] `tests/test_api_analyze_router.py`: Tests D–E passing (SSE events,
  error handling).
- [ ] `.context/SPEC.md`: Section 7 updated to reflect Sprint 12 scope.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] **HARD CONSTRAINT:** Only `src/agents/graham.py` modified among agent
  files — no other agents touched.
- [ ] **HARD CONSTRAINT:** No modifications to `src/tools/`, `.tf`, or `.sh`.
