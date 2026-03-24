---
plan_id: plan-spec-thesis-cot-boundaries-002
target_files:
  - ".context/SPEC.md"
enforced_dogmas: [risk-confinement, type-safety, temporal-invariance]
validation_scale: FACTS (Mean: 5.0)
---

## 1. Intent & Scope
Atualizar `.context/SPEC.md` para formalizar as novas fronteiras técnicas introduzidas pelo roadmap de longo prazo, evitando drift arquitetural nas próximas sprints. O foco é consolidar a expansão da boundary `HistoricalMarketData` e adicionar um contrato explícito para a camada de apresentação `Thesis-CoT`, alinhado ao padrão FinRobot sem permitir cálculo financeiro ou formatação visual pelo LLM.

## 2. File Implementation: .context/SPEC.md

### Step 2.1: Expandir o Contrato HistoricalMarketData
* **Action:** Atualizar a seção `5.2 Boundary de ingestão` para declarar explicitamente os campos `piotroski_f_score: Optional[int] = None` e `altman_z_score: Optional[float] = None` dentro do contrato `HistoricalMarketData`.
* **Constraints:** Must preserve `ConfigDict(frozen=True)`, must keep controlled degradation semantics, must not introduce `decimal.Decimal`, and must keep the boundary strictly point-in-time.
* **Signatures:** `class HistoricalMarketData(BaseModel): ... piotroski_f_score: Optional[int] = None; altman_z_score: Optional[float] = None`

### Step 2.2: Formalizar a Regra de Cálculo Exclusivamente Determinístico
* **Action:** Na subseção de regras invioláveis da boundary quantitativa, adicionar texto normativo afirmando que `piotroski_f_score` e `altman_z_score` são calculados exclusivamente por ferramentas em Python puro sob `src/tools/`.
* **Constraints:** Must explicitly ban any probabilistic LLM-side estimation, must reinforce Zero Math / Risk Confinement, and must require degradation to `None` when source evidence is missing or invalid.
* **Signatures:** `def calculate_piotroski_f_score(...) -> Optional[int]`; `def calculate_altman_z_score(...) -> Optional[float]`

### Step 2.3: Criar o Novo Contrato de Apresentação Thesis-CoT
* **Action:** Adicionar uma nova seção arquitetural para a camada de apresentação, definindo que o MAS produz um JSON estruturado via Pydantic contendo tese, evidências e dados, e que um Presentation Adapter isolado consome esse payload para renderizar gráficos e PDF.
* **Constraints:** Must explicitly prohibit ASCII charts, visually formatted markdown tables, and direct PDF formatting by the LLM. Must keep the adapter downstream and deterministic (e.g., Matplotlib/WeasyPrint), never inside the prompt layer.
* **Signatures:** `class ThesisReportPayload(BaseModel): ...`; `class PresentationAdapter(Protocol): def render_pdf(self, payload: ThesisReportPayload) -> bytes: ...`

### Step 2.4: Alinhar a Seção com o Padrão SOTA FinRobot
* **Action:** Inserir referência textual de que a camada de relatórios segue o padrão `Thesis-CoT` do framework FinRobot para reforçar rastreabilidade, profissionalismo e separação entre raciocínio, dados estruturados e rendering determinístico.
* **Constraints:** Must remain documentation-only, must not promise concrete implementation modules not yet present in the repo, and must avoid speculative architecture beyond the contract level.
* **Signatures:** `N/A (documentation contract update only)`

## 3. Definition of Done (DoD)
- [x] `.context/SPEC.md` declara `piotroski_f_score: Optional[int] = None` e `altman_z_score: Optional[float] = None` na boundary `HistoricalMarketData`.
- [x] O documento afirma explicitamente que esses indicadores são calculados apenas em `src/tools/` por Python puro.
- [x] O contrato proíbe qualquer estimativa probabilística desses indicadores pelo LLM.
- [x] Existe uma nova seção arquitetural para `Thesis-CoT Reporting` baseada em JSON Pydantic + Presentation Adapter desacoplado.
- [x] O texto proíbe explicitamente gráficos ASCII, markdown tables visuais e formatação direta de PDF pelo LLM.
- [x] A seção de apresentação referencia o padrão `Thesis-CoT` do FinRobot em nível contratual.
- [x] Code passes standard static analysis (`ruff check`).
- [x] Tests execute successfully with zero warnings.
- [x] Zero instances of `decimal.Decimal` and synchronous domain logic.
