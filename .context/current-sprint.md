# 🎯 Status Atual do Projeto: Aequitas-MAS

## 📌 Sprint Atual: 1.2 - O Motor Quantitativo Determinístico
**Foco Semanal:** Consolidação das ferramentas determinísticas e preparação para orquestração via LangGraph.

### 🛠️ Objetivos Imediatos da Sessão
1.  **Validação de Testes:** Alcançar 100% de cobertura no arquivo `tests/test_b3_fetcher.py`.
2.  **Integração Qualitativa:** Validar a extração de notícias no `news_fetcher.py` para garantir que o output seja mapeável para o schema `FisherAnalysis` (Pydantic).
3.  **Refinamento de Cálculo:** Ajustar o multiplicador dinâmico de Graham no `b3_fetcher.py` com base na taxa Selic atualizada via API do Banco Central.

### 🚫 Restrições Arquiteturais Atuais (Confinamento de Risco)
* **Isolamento de Redes:** A extração via `yfinance` e `requests` (BCB) são as únicas exceções de saída; o estado do grafo deve permanecer local.
* **Agnosticismo de LLM:** O Agente Graham não deve realizar cálculos; deve apenas instanciar a ferramenta `get_graham_data`.
* **Conformidade DDGS:** É estritamente proibido o uso da biblioteca `duckduckgo_search` legada; usar apenas `ddgs`.

### ✅ Definição de Pronto (DoD) para o Dia
- [ ] Execução bem-sucedida de `poetry run pytest` sem falhas nos mocks de rede.
- [ ] Tipagem estrita validada: Nenhum dado financeiro circula como `float`, apenas `decimal.Decimal`.
- [ ] Logs estruturados implementados em ambos os fetchers usando `structlog`.