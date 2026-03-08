# 🎯 Sprint Atual: Restabelecimento do Confinamento de Risco e Auditoria Arquitetural

## 📌 Foco do Dia (Objetivos Atómicos)
1. **Refatoração da Máquina de Estados (LangGraph):** Substituir implementações não-conformes de tipagem monetária pelo esquema Pydantic oficial (`Optional[float] = None`), assegurando a Degradação Controlada na ausência de dados.
2. **Shift-Left Testing do Motor Quantitativo:** Desenvolver cobertura de testes estrita para o Agente Graham e suas ferramentas associadas, comprovando a execução determinística da Álgebra sem alucinação do LLM.
3. **Auditoria de DIP (Dependency Inversion Principle):** Aplicar varredura de código para garantir que nenhuma dependência de infraestrutura (ex: `import boto3`) exista dentro de `/src/agents/`.

## 📂 Arquivos-Alvo
* `/src/core/state.py` (Refatoração de tipagem Pydantic V2).
* `/tests/test_graham_agent.py` (Criação de testes unitários com `pytest`).
* `/src/agents/` (Auditoria e limpeza de importações).

## ⚖️ Dogmas a Aplicar
* **Zero Numerical Hallucination:** O LLM atua apenas como "Cérebro" probabilístico. O cálculo do Valor Justo ($Valor Justo = \sqrt{22.5 \times VPA \times LPA}$) deve ser feito em Python puro.
* **Degradação Controlada:** Na ausência de resolução de um Ticker ou métrica, o sistema não adivinha; ele retorna `None`.
* **Separação de Preocupações (SRP):** SDKs de Cloud devem ficar restritos aos Adapters (ex: `BaseCheckpointSaver`).

## ✅ Critérios de Aceite (Definition of Done)
- [ ] O ficheiro `state.py` não contém `Decimal` para dados de mercado, utilizando apenas tipos base e `Optional[float] = None`.
- [ ] O comando `poetry run pytest tests/test_graham_agent.py` retorna ✅ SUCESSO.
- [ ] Uma busca literal por `import boto3` no diretório `src/agents/` retorna zero resultados.

## 🚀 Passo 1 (Atómico) para Início de Sessão
**Instrução para GCA:** "Inicie a sessão abrindo o ficheiro `src/core/state.py`. Verifique a classe de estado do LangGraph (modelada em Pydantic V2) e altere qualquer campo financeiro que viole a diretriz de Degradação Controlada para `Optional[float] = None`."