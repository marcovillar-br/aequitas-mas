### 🇧🇷 Versão Oficial em Português do Brasil (pt-BR)

**Base de Conhecimento Técnico: Integração de Agentes Inteligentes em Finanças Quantitativas**
**Versão:** 2.0
**Status:** Documento Oficial de Referência Teórica (Aequitas-MAS)

**1. Considerações Iniciais**
O desenvolvimento de Agentes de Inteligência Artificial voltados ao *Value Investing* exige a superação da assimetria informacional e das limitações matemáticas intrínsecas aos Modelos de Linguagem de Grande Escala (LLMs). No domínio financeiro, o mercado caracteriza-se por alta sensibilidade temporal, constante dinamismo e uma baixa relação sinal-ruído (SNR). Para o escopo do framework Aequitas-MAS, estabelece-se a premissa do **Confinamento de Risco**, onde a IA atua como orquestradora de lógica semântica, mas delega os cálculos financeiros determinísticos (como Margem de Segurança e otimização de portfólio) para ferramentas isoladas e tipadas. Este documento sintetiza o estado da arte das arquiteturas multiagentes baseadas em FinGPT (Yang et al., 2023), FinRobot (Zhang et al., 2024) e MarketSenseAI (Zhang et al., 2025), conectando-as aos pilares de engenharia de software e econometria adotados no projeto aplicado.

**2. Fundamentação Teórica: O Estado da Arte (SOTA)**

**2.1. Democratização de Dados e Adaptação Leve (FinGPT)**
Segundo Yang et al. (2023), modelos proprietários como o BloombergGPT possuem acesso privilegiado a dados, o que exige uma alternativa de código aberto para a comunidade financeira. O framework FinGPT adota uma abordagem centrada em dados (*Data-centric*), enfatizando a importância de um *pipeline* automatizado de curadoria de dados em tempo real provenientes de notícias e demonstrações financeiras. Em vez de treinar modelos massivos do zero, o framework recomenda o uso de técnicas de adaptação de baixo custo (*Low-Rank Adaptation* - LoRA) acopladas ao Aprendizado por Reforço com Preços de Ações (RLSP), permitindo que o modelo se alinhe rapidamente às flutuações do mercado.

**2.2. Arquitetura de Pesquisa de Ações (FinRobot)**
Para a automação da análise de *Equity Research*, Zhang et al. (2024) propõem o FinRobot, um sistema que divide o raciocínio complexo em uma arquitetura de camadas utilizando a técnica *Chain-of-Thought* (CoT). O sistema opera em três vertentes estruturais:

* **Data-CoT (Percepção):** Focado na coleta e estruturação de dados de fontes oficiais (ex: relatórios SEC, balanços patrimoniais).
* **Concept-CoT (Cérebro):** Realiza a análise quantitativa e a geração de gráficos, transformando dados processados em avaliações corporativas e projeções.
* **Thesis-CoT (Ação):** Sintetiza os achados qualitativos e quantitativos em um relatório final estruturado que atende aos padrões profissionais.

**2.3. Contexto Macroeconômico e Sinais Holísticos (MarketSenseAI)**
A avaliação isolada de balanços é insuficiente sem o contexto econômico. Zhang et al. (2025) expandem o conceito com o MarketSenseAI. No Aequitas-MAS, isso é formalizado pelo **Agente Macro**, que implementa um módulo de Geração Aumentada por Recuperação (RAG) impulsionado por *Hypothetical Dense Embeddings* (HyDE). Este agente isolado ingere transcrições de *Earnings Calls* e relatórios macroeconômicos (FED, Banco Central), aplicando o fracionamento semântico (*Semantic Chunking*) para contornar os limites da janela de contexto dos LLMs. A combinação da análise fundamentalista microeconômica com os sinais macroeconômicos demonstrou superar os índices de referência com retornos consistentes e controle de risco.

**3. Implementação de Algoritmo(s) de Machine Learning e Integração Arquitetural**

A integração dos conceitos de Yang e Zhang ao projeto Aequitas-MAS demanda rigor arquitetural e metodológico, estruturado nos seguintes pilares da bibliografia complementar:

**3.1. Arquitetura Limpa e Princípio da Responsabilidade Única (SRP)**
As camadas de raciocínio do FinRobot devem ser implementadas obedecendo estritamente ao Princípio da Responsabilidade Única, fundamentado no **Código Limpo** de Robert C. Martin. Para mitigar as alucinações numéricas, a **Arquitetura Limpa** isola a inteligência do LLM dos *frameworks* externos de cálculo. O Agente Graham atua unicamente na leitura quantitativa estruturada; o Agente Fisher foca estritamente na microeconomia; o Agente Macro atua sobre as taxas de juros globais. As operações financeiras são delegadas ao código Python puro, atuando como o núcleo inabalável da entidade financeira.

**3.2. Validação Econométrica (Gujarati)**
A extração de sinais de sentimento e projeções atua de forma probabilística. Para que esses sinais não sejam caracterizados como "ruído estocástico", exige-se a validação estatística baseada em **Damodar N. Gujarati**. Todo coeficiente sintético derivado das camadas de Análise de Dados deve passar por diagnóstico de pressupostos clássicos (ausência de heterocedasticidade e multicolinearidade), garantindo que a IA não atue sob inferências causais falsas.

**3.3. Sistemas de Apoio à Decisão (SAD) e Otimização de Portfólio**
Os relatórios qualitativos finais gerados pelos agentes alimentam um Sistema de Apoio à Decisão (SAD) multicritério. O **Aequitas Core (Supervisor)** coleta os ranqueamentos multicritério (Valor, Qualidade Micro, Macro e Sentimento). Para a maximização do retorno e mitigação do risco, a inteligência é repassada para uma *Tool* Python determinística que processa os fundamentos da **Álgebra Linear** (Anton/Rorres). Esta ferramenta resolve estritamente as equações de alocação ótima e a Fronteira Eficiente de Markowitz, garantindo que o LLM não realize predições matriciais estocásticas.

**4. Considerações Finais**
Conclui-se que o estado da arte na engenharia de *prompts* e agentes financeiros estabelece um paradigma de operação híbrida. A eficácia da orquestração multiagente não reside na delegação irrestrita da autonomia ao LLM, mas no confinamento do modelo ao seu domínio de excelência (inferência semântica de narrativas e relatórios macroeconômicos). O rigor de processamento é garantido através do acoplamento com infraestruturas de dados validadas (*Feature Stores* e RAG avançado), arquiteturas de software desacopladas e validação matemática estrita via Álgebra Linear.

**Referências**

Yang, H.; Liu, X.-Y.; Wang, C.D. 2023. FinGPT: Open-Source Financial Large Language Models. FinLLM Symposium at IJCAI 2023.

Zhang, W.; Zhao, L.; Xia, H.; Sun, S.; Sun, J.; Qin, M.; Li, X.; Zhao, Y.; Zhao, Y.; Cai, X.; et al. 2024. FinRobot: AI Agent for Equity Research and Valuation with Large Language Models. In: Proceedings of ACM International Conference on AI in Finance (ICAIF). ACM, New York, NY, USA.

Zhang, B.; Yang, H.; Zhou, T.; Babar, M.A.; Liu, X.-Y. 2025. MarketSenseAI: Enhancing financial sentiment analysis via retrieval augmented large language models. In: Proceedings of the ACM International Conference on AI in Finance. ACM, New York, NY, USA.

*(Conhecimento Externo: As orientações de formatação espacial, como recuos, tamanho da fonte Arial 11, e espaçamentos 1,5 exigidos pelas normas da USP ESALQ, embora não renderizáveis na presente interface textual contínua, devem ser rigorosamente aplicados pelo autor na formatação do arquivo final do projeto).*
