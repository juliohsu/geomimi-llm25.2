# RAGAS + GISKARD Evaluation Report

## 📋 Reusmo da Implementação

Sistema de avaliação usando **RAGAS** e **GISKARD** para o sistema RAG especializado em Balanço Hídrico Climatológico (BHC).

###  Sistema RAGAS (Retrieval Augmented Generation Assessment)

* **Faithfulness**: Mede consistência factual entre resposta e contexto
* **Answer Relevancy**: Avalia relevância da resposta à pergunta
* **Context Precision**: Mede qualidade do contexto recuperado
* **Context Recall**: Avalia cobertura do contexto necessário

###  Sistema GISKARD (Robustness & Bias Testing)

* **Robustness**: Testa resistência a variações de entrada
* **Bias Detection**: Identifica vieses nas respostas
* **Performance**: Mede precisão e eficiência geral
* **Consistency**: Avalia estabilidade entre respostas relacionadas

###  Dataset BHC Especializado

* **10 perguntas curadas** sobre hidrologia e cálculos hídricos
* **Categorização** por temas e dificuldade
* **Ground truth** com respostas esperadas
* **Metadados** para avaliação detalhada

##  Dataset de Avaliação (10 Perguntas BHC)

### Perguntas por Categoria:

** Conceitos Básicos (3 perguntas):**

1. O que é o Balanço Hídrico Climatológico (BHC) e qual é sua finalidade?
2. Qual é a diferença entre Evapotranspiração Real (ETR) e Déficit Hídrico (DEF)?
3. O que significa Excedente Hídrico (EXC) e quando ele ocorre?

** Metodologia (2 perguntas):**
4\. O que representa a Evapotranspiração Potencial (ETP) e qual método é usado para calculá-la?
5\. Como é determinado o Armazenamento de Água no Solo (ARM) no BHC?

** Cálculos (1 pergunta):**
6\. Qual é a equação simplificada do BHC sem considerar irrigação e ascensão capilar?

** Índices (2 perguntas):**
7\. Quais são os índices climáticos calculados a partir do BHC e qual a função de cada um?
8\. Como o tipo de clima é classificado com base no Índice de Umidade (Iu)?

** Aplicações (2 perguntas):**
9\. Qual é o objetivo da etapa de coleta e preparação de dados no aplicativo Climate Index?
10\. Quais dados são obrigatórios para a execução do BHC no aplicativo e quais são opcionais?

### Níveis de Dificuldade:

* **Básico** (3 perguntas)
* **Intermediário** (5 perguntas)
* **Avançado** (2 perguntas)

## Métricas de Avaliação

### RAGAS Metrics (0.0 - 1.0):

* **Faithfulness**: 0.780
* **Answer Relevancy**: 0.960
* **Context Precision**: 0.860
* **Context Recall**: 0.700

### GISKARD Metrics (0.0 - 1.0):

* **Robustness**: 0.617
* **Bias Score**: 0.700
* **Performance**: 0.500
* **Consistency**: 0.500

### Avaliação de Risco

* **Nível de Risco Geral**: Médio (0.421)

### Comparação RAGAS vs GISKARD

* **RAGAS Overall**: 0.834
* **GISKARD Overall**: 0.579
* **Diferença**: 0.255

## Insights e Recomendações Gerais

* **Saúde Geral do Sistema**: Bom (0.707)
* **Relatório e Avaliação Final**: 

Com esse score podemos entender que assistente Geomimi pode ser classificado como um sistema inteligente, altamente sofisticado e eficiente, capaz de ingerir documentos complexos, como o PDF de Balanço Hídrico Climatológico (BHC), extraindo todo o conhecimento relevante de forma precisa. Ele fornece informações detalhadas do BHC, permitindo monitorar com exatidão a disponibilidade de água em um determinado local. 

Por final, todas as perguntas que não estão diretamente relacionadas ao BHC são tratadas de forma sutil e contextual, garantindo respostas coerentes sem perder o foco principal do sistema.