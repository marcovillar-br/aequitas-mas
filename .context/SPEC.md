# 📐 SPEC: Adaptador Hexagonal DynamoDB e Correção Topológica
**Sprint:** 3.1
**Objetivo:** Implementar persistência Serverless (AWS DynamoDB) via Inversão de Dependência e preparar o grafo para o Agente Macro.

## 1. Contratos de Interface (DIP)
* **Arquivo-Alvo:** `src/infra/adapters/dynamo_saver.py`
* **Herança Obrigatória:** `langgraph.checkpoint.base.BaseCheckpointSaver`
* **Isolamento:** A biblioteca `boto3` DEVE estar confinada a este ficheiro. Nenhuma exceção. O módulo `src/core/graph.py` continuará a interagir apenas com a abstração do LangGraph.

## 2. Requisitos de Segurança (Zero Trust)
* A classe `DynamoDBSaver` deve inicializar o recurso `boto3.resource('dynamodb')` utilizando estritamente variáveis de ambiente (`os.getenv('AWS_REGION')`).
* É proibida a leitura de ficheiros `.env` diretamente no código do adaptador. A IDE ou a pipeline CI/CD injetarão as credenciais.

## 3. Topologia e Degradação Controlada (Grafo)
* **Arquivo-Alvo:** `src/core/graph.py` e `.context/domain/personas.md`
* **Novo Agente:** Agente Macro (responsável por RAG HyDE de dados FED/COPOM).
* O estado persistido no DynamoDB utilizará o esquema Pydantic já validado em `src/core/state.py`. Se dados macro estiverem ausentes, o sistema deve assumir `Optional[float] = None`.