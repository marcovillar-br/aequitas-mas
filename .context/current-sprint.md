# 🎯 Project Status: Aequitas-MAS

## 📌 Current Sprint: 3.2 - Agente Macro e RAG HyDE (OpenSearch)
**Foco Imediato:** Integrar a busca vetorial real e validar a injeção do contexto macroeconômico holístico no Grafo.

### 🛠️ Objetivos da Próxima Sessão (SOD)
1.  **Integração OpenSearch (Prioridade 1):** Substituir a estrutura de *mock* em `src/agents/macro.py` por uma chamada ao adaptador vetorizado (ex: `OpenSearchVectorSearch`), utilizando o documento hipotético gerado pelo HyDE para buscar contexto real do FED/COPOM.
2.  **Rastreabilidade Ética:** Garantir que o campo `source_urls` no *schema* Pydantic `MacroAnalysis` seja preenchido dinamicamente com as URLs ou IDs recuperados do OpenSearch.
3.  **Confinamento de Infraestrutura (DIP):** Impedir que SDKs de nuvem (`boto3`, `opensearch-py`) vazem diretamente para o arquivo do agente. Eles devem vir encapsulados através da infraestrutura.

### ✅ Definition of Done (DoD)
- [ ] `macro_agent` realizando *retrieval* dinâmico com base no vetor de similaridade.
- [ ] Histórico de execução validado sem alucinações (uso restrito de `Optional[float] = None` caso os vetores não contenham dados quantitativos precisos).
- [ ] Grafo executado de ponta a ponta (`pytest tests/test_graph.py`) confirmando a robustez sem degradação do estado.clea