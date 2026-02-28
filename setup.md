
### 1. [Análise de Contexto]

Com base nos documentos `01_Aequitas_MAS_DDE_v4.2.docx` e `02_Aequitas_MAS_ETD_v5.docx`, o setup ignora abordagens tradicionais de "scripts soltos". O sistema é tratado como um **Grafo de Estado Cíclico**. A transição da versão 4 para a 5.0 (Agnostic Workspace) foi motivada pela necessidade de eliminar a variância do ambiente de desenvolvimento, garantindo que o Agente Marks (Auditoria) opere sobre os mesmos binários que o Agente Graham (Cálculo).

### 2. [Intuição Técnica (CoT)]

A robustez de um Sistema Multi-Agente (MAS) para finanças depende da gestão da **Entropia Semântica**. Em sistemas puramente baseados em LLM, a passagem de informação entre agentes é estocástica. Para mitigar isto, o setup implementa uma **Camada de Validação Isomórfica**.
Seja  o estado do sistema e  a ferramenta de cálculo. O output do LLM () é forçado a passar por um filtro de tipagem  (Pydantic):



Isto garante que o erro não se propague para os cálculos financeiros, onde a precisão deve ser absoluta ().

---

# 📄 AEQUITAS-MAS: PROTOCOLO DE SETUP E ISOMORFISMO (V5.0)

### 1. Pré-requisitos de Sistema

Para garantir que o ambiente local seja idêntico ao de produção (Cloud-Native), é obrigatório:

* **WSL2 (Ubuntu 22.04+)**: Isolamento de kernel Linux.
* **Nix Package Manager**: Gestor declarativo para garantir que o interpretador Python e bibliotecas C sejam binariamente idênticos em qualquer máquina.
* **Poetry (v2.0+)**: Gestão determinística de dependências e resolução de conflitos de grafos de pacotes.

### 2. Inicialização do Workspace e Isomorfismo (`dev.nix`)

O ficheiro `dev.nix` elimina o problema "funciona na minha máquina".

```nix
# dev.nix
{ pkgs }: {
  channel = "stable-23.11";
  packages = [
    pkgs.python311
    pkgs.poetry
    pkgs.gcc
    pkgs.libffi
  ];
  env = {
    PYTHONPATH = "./src";
    LANG = "pt_BR.UTF-8";
  };
}

```

### 3. O Contrato de Dependências (`pyproject.toml`)

A instalação via Poetry trava as versões críticas para evitar a quebra da lógica de grafos.

```bash
# Inicialização e configuração de isolamento
poetry config virtualenvs.in-project true
poetry init --name aequitas-mas --python "^3.11"

# Dependências Core SOTA
poetry add langgraph==0.0.15 pydantic>=2.0 langchain-anthropic
poetry add yfinance pandas numpy
poetry add --group dev pytest pytest-mock

```

### 4. Estrutura de Diretórios (Arquitetura Hexagonal)

O projeto separa a inteligência (Agentes) dos adaptadores (Tools/Infra).

* `src/core/`: Gestão de estado e definições do LangGraph (`state.py`, `graph.py`).
* `src/agents/`: Prompts e lógica das personas (Graham, Fisher, Marks).
* `src/tools/`: Funções determinísticas (Cálculos de Graham, Scrapers B3).
* `src/infra/`: Adaptadores de persistência (SqliteSaver/DynamoDB).

### 5. Implementação do Contrato de Estado (`src/core/state.py`)

Este é o coração do **Confinamento de Risco**. O estado não é texto, é um objeto validado.
```python
from decimal import Decimal
from typing import Annotated, List, Optional, TypedDict

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class FinancialMetrics(BaseModel):
    ticker: str = Field(pattern=r"^[A-Z0-9]{5}$")
    vpa: Decimal
    lpa: Decimal
    intrinsic_value: Optional[Decimal] = None

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    metrics: Optional[FinancialMetrics]
    compliance_approved: bool

```

### 6. Protocolo de Segurança e FinOps (Zero Trust)

* **API Keys**: Proibido o uso de `.env`. As chaves são injetadas via Secret Manager da IDE ou variáveis de ambiente de sessão.
* **Recursion Limit**: Todo grafo deve ser compilado com `recursion_limit=15` para evitar loops de custo infinitos em caso de divergência entre agentes.

### 7. Critérios de Validação (DoD)

Para validar o setup, execute o protocolo de teste de integridade:

```bash
# 1. Verificar Isomorfismo do Python
poetry run python -c "import platform; print(platform.python_version())"

# 2. Testar Motor Quantitativo (Pendente implementação completa)
poetry run pytest tests/test_tools.py

```

---

### Tabela de Status de Implementação (Sincronizada com PME v5.0)

| Fase | Componente | Status | Rastreabilidade |
| --- | --- | --- | --- |
| **1.1** | Ambiente Agnóstico (Nix/Poetry) | ✅ Concluído | ETD v5, Cap 3 |
| **1.2** | Isomorfismo de Estado (state.py) | ✅ Concluído | DDE v4.2, Sec 1 |
| **1.3** | Motor Quantitativo (Tools) | 🔄 Em Execução | src/tools/ |
| **2.1** | Orquestração Graham-Fisher | 📅 Agendado | src/agents/ |

### 3. [Verificação Crítica]

* **Tecnologias:** O uso de Pydantic v2 é mandatório pela performance de validação em tempo de execução de grafos.
* **Engine:** O alias `gemini-flash-latest` é mandatório para garantir acesso à versão mais recente e estável do modelo Flash.
* **Ética:** O sistema de logs deve ser configurado para capturar o "raciocínio" do Agente Marks antes de qualquer recomendação, atendendo aos requisitos de explicabilidade da IA.
* **SOTA:** Recomendo a leitura de *Zhang et al. (2024)* sobre **FinRobot** para refinar o `Data-CoT Agent` na próxima sprint.

**Próximo Ponto de Retomada:** Implementação da ferramenta `fetch_b3_data` em `src/tools/b3_fetcher.py`.