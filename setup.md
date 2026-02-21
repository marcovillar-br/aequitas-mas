### 1. Pré-requisitos de Sistema

Para garantir o **Isomorfismo**, o ambiente deve possuir:

* **WSL2 (Ubuntu 22.04+)**: Para simular o ambiente cloud-native.


* **Nix Package Manager**: Gestor de pacotes declarativo.


* *Poetry (v2.3.2+)**: Gestor determinístico de dependências Python.



### 2. Inicialização do Workspace

```bash
# Clone e entrada no diretório
git clone <url-do-repositorio>
cd aequitas-mas

# Configuração de isolamento do Poetry (Essencial para convívio de múltiplos projetos)
poetry config virtualenvs.in-project true

```

### 3. O Contrato de Dependências

A instalação deve ser feita via Poetry para garantir que as versões de `langgraph` e `pydantic` sejam idênticas às testadas.

```bash
# Instalação das dependências e criação do ambiente virtual (.venv)
poetry install

```

### 4. Estrutura de Diretórios (Arquitetura Hexagonal)

O projeto segue uma separação estrita de preocupações:

* `src/core/`: O motor de inferência e gestão de estado.


* `src/agents/`: Lógica das personas (Graham, Fisher, Marks).


* `src/tools/`: Ferramentas determinísticas de cálculo.


* `src/infra/`: Adaptadores para persistência (Sqlite/DynamoDB).



### 5. Protocolo de Segurança (Zero Trust)

* **Chaves de API**: Nunca crie arquivos `.env` commitados.


* **Local**: Utilize o Secret Manager da IDE (IDX) ou exporte variáveis de ambiente temporárias no shell do WSL2.



### 6. Critérios de Validação (DoD)

Para considerar o setup concluído, execute:

```bash
# Validação da versão do Python no ambiente isolado
poetry run python --version # Deve retornar Python >= 3.10

# Execução de testes unitários (Sprint 1.2 em diante)
poetry run pytest

```

---

### Tabela de Status de Implementação (PME v5.0)

| Fase | Descrição | Status | Referência |
| --- | --- | --- | --- |
| **1.1** | Ambiente Agnóstico (Nix/Poetry/Git) | ✅ Concluído
| **1.2** | Motor Quantitativo (Tools/Pydantic) | 🔄 Em Início
| **2.1** | Máquina de Estados (LangGraph) | 📅 Agendado

---
