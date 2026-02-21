
# Aequitas-MAS (Multi-Agent System) v5.0

**Aequitas-MAS** é um ecossistema de agentes inteligentes projetado para análise fundamentalista e tomada de decisão financeira de alto nível. O sistema transcende cálculos estáticos ao combinar o rigor matemático do **Value Investing** com análises qualitativas de mercado e auditoria de risco, utilizando **LangGraph** para orquestração e **Gemini 1.5 Flash** como motor de inferência.

## 🧠 Arquitetura de Agentes

O projeto utiliza um grafo acíclico dirigido (DAG) para processar ativos financeiros através de três perspectivas críticas, garantindo que o valor intrínseco seja confrontado com a realidade do mercado:

1. **Nó GRAHAM (Quantitativo):** 
* Realiza a coleta de dados fundamentais em tempo real via `yfinance`.
* Executa o cálculo do **Valor Justo** baseado na fórmula de Benjamin Graham.
* Estabelece a Margem de Segurança nominal do ativo.


2. **Nó FISHER (Qualitativo):** 
* Avalia o "Yield Gap" e o sentimento do mercado através de dados macroeconômicos.
* Identifica vantagens competitivas e sustentabilidade de dividendos.
* Processado via **Gemini 1.5 Flash** (Endpoint estável `v1`).


3. **Nó MARKS (Auditoria de Risco):** 
* Aplica o "Pensamento de Segundo Nível" (Howard Marks) para contestar os nós anteriores.
* Analisa riscos institucionais, políticos e de governança (especialmente em estatais).
* Define o veredito final sobre a viabilidade da margem de segurança.



## 🚀 Stack Técnica

* **Linguagem:** Python 3.12+
* **Orquestração:** [LangGraph](https://www.langchain.com/langgraph) (Agentes baseados em estado)
* **LLM Engine:** Google Gemini 1.5 Flash (API v1 Stable)
* **Gestão de Dependências:** [Poetry](https://python-poetry.org/)
* **Dados:** yfinance, Pandas, Beautifulsoup4

## 🛠️ Instalação e Configuração

```bash
# Clone o repositório
git clone https://github.com/marcovillar-br/aequitas-mas.git
cd aequitas-mas

# Vincule o interpretador e instale as dependências via Poetry
poetry env use python3
poetry install

```

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```text
GOOGLE_API_KEY=sua_chave_do_google_ai_studio

```

## 📈 Caso de Uso Real: PETR4

O sistema foi validado com uma análise da **PETR4** em Fevereiro de 2026:

* **Cálculo Graham:** Valor Justo de **R$ 64,64** (Margem de 41.26%).
* **Contexto Fisher:** Dividendos atrativos (~10%) vs. Volatilidade geopolítica.
* **Veredito Marks:** Alerta sobre "alvo móvel" em ativos estatais, ajustando a percepção da margem nominal.

---

## 🗺️ Roadmap de Implementação (2026-2027)

Este projeto segue um cronograma de evolução técnica focado na transição de um protótipo funcional para uma infraestrutura de análise distribuída e resiliente:

* **Q1/2026 - Estabilização e Core:**
* Saneamento do ambiente de dependências (Poetry) e migração para endpoints estáveis `v1`.
* Refinamento dos algoritmos do **Nó GRAHAM** para suporte a múltiplos ativos simultâneos.

* **Q2/2026 - Observabilidade e Testes:**
* Implementação de logs estruturados para auditoria de decisões dos agentes Fisher e Marks.
* Cobertura de testes unitários e de integração para o grafo de estados (LangGraph).

* **Q3/2026 - Cloud Native & Containerização:**
* Dockerização da aplicação e implementação de CI/CD (GitHub Actions).
* Deploy experimental em **AWS Fargate** e configuração de **AWS Secrets Manager**.

* **Q4/2026 - Persistência e Big Data:**
* Implementação de um Data Lake em **AWS S3** via Boto3.
* Armazenamento histórico de análises para tracking de performance do "Valor Justo" vs. Mercado.

* **Q1/2027 - Entrega Inteligente e API:**
* Desenvolvimento de uma API (FastAPI) para consumo externo das análises.
* Configuração de sistema de alertas via **AWS SNS** para notificação de Margens de Segurança críticas.

---

## 📝 Licença

Este projeto é para fins estritamente acadêmicos e de estudo de engenharia de software. **Não constitui recomendação de compra ou venda de ativos.**
