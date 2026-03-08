# 🎯 Project Status: Aequitas-MAS

## 📌 Current Sprint: 3.2 - Finalização do Agente Macro
**Foco Imediato:** Integrar a busca vetorial real e validar o fluxo completo do Grafo.

### 🛠️ Objetivos da Próxima Sessão (SOD)
1.  **Integração OpenSearch (Prioridade 1):** Substituir a lista estática de fontes em `src/agents/macro.py` por uma chamada ao `OpenSearchVectorSearch` usando o documento hipotético gerado pelo HyDE.
2.  **Validação de Rastreabilidade:** Garantir que o campo `source_urls` no estado seja preenchido com as URLs reais recuperadas do motor RAG.
3.  **Teste de Integração de Grafo:** Executar `pytest tests/test_graph.py` para garantir que o Agente Marks recebe as entradas macroeconômicas sem erros de esquema.

### ✅ Definition of Done (DoD)
- [ ] `macro_agent` retornando fontes dinâmicas de documentos oficiais (BCB/CVM).
- [ ] Logs estruturados demonstrando o fluxo: Pergunta -> HyDE -> OpenSearch -> Análise.
- [ ] Cobertura de testes unitários para a nova lógica de busca vetorial.