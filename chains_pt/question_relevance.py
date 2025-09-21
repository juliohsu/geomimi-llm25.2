from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

class QuestionRelevance(BaseModel):
    
    binary_score: bool = Field(
        description="Whether the answer adequately addresses the question - true if relevant, false if not relevant"
    )
    
    relevance_score: float = Field(
        default=0.5,
        description="Relevance score between 0.0 and 1.0 indicating how well the answer addresses the question",
        ge=0.0,
        le=1.0
    )
    
    completeness: str = Field(
        default="partial",
        description="Assessment of answer completeness: 'complete', 'partial', or 'minimal'"
    )
    
    reasoning: str = Field(
        default="",
        description="Brief explanation of the relevance assessment and what makes the answer relevant or irrelevant"
    )
    
    missing_aspects: str = Field(
        default="",
        description="Key aspects of the question that are not addressed in the answer (if any)"
    )


llm = ChatOpenAI(temperature=0)
structured_output = llm.with_structured_output(QuestionRelevance)

system = """Você é um avaliador da relevância entre PERGUNTA e RESPOSTA.

CRITÉRIOS DE AVALIAÇÃO:

1. RELEVÂNCIA DIRETA:
    - A resposta aborda diretamente o núcleo da pergunta feita?
    - Os principais pontos da pergunta são especificamente tratados?
    - A resposta está focada no que o usuário realmente deseja saber?

2. AVALIAÇÃO DE COMPLETUDE:
    - A resposta cobre todos os aspectos importantes da pergunta?
    - Existem partes significativas da pergunta que ficaram sem resposta?
    - O nível de detalhe é apropriado para o tipo de pergunta?

3. PRECISÃO E ADEQUAÇÃO:
    - A resposta é consistente com o que foi perguntado?
    - A resposta permanece dentro do escopo da pergunta?
    - Existem contradições ou elementos fora do tema?

4. UTILIDADE PARA O USUÁRIO:
    - Esta resposta satisfaria a necessidade de informação do usuário?
    - A resposta é útil ou informativa conforme solicitado?
    - Ela fornece o tipo de resposta que a pergunta implica?

ORIENTAÇÕES DE PONTUAÇÃO:
- Marque 'true' se a resposta aborda adequadamente a pergunta e satisfaria o usuário
- Marque 'false' se a resposta está fora do tema, incompleta ou não aborda o núcleo da pergunta

AVALIAÇÕES ADICIONAIS:
- Forneça uma pontuação de relevância (0.0-1.0) indicando a qualidade da resposta
- Avalie o nível de completude: completa, parcial ou mínima
- Explique seu raciocínio para a avaliação
- Identifique quaisquer aspectos importantes da pergunta que não foram abordados, se a resposta estiver incompleta

Foque na utilidade prática: esta resposta ajudaria o usuário a atingir seu objetivo?"""
relevance_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", """Avalie se a resposta gerada aborda adequadamente a pergunta do usuário.

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA GERADA:
{solution}

AVALIAÇÃO REQUERIDA:
1. Pontuação Binária: true se a resposta aborda adequadamente a pergunta, false se não
2. Pontuação de Relevância: nota de 0.0 a 1.0 sobre o quanto a resposta aborda a pergunta
3. Completude: 'completa', 'parcial' ou 'mínima' cobertura dos aspectos da pergunta
4. Raciocínio: breve explicação da sua avaliação
5. Aspectos Ausentes: partes importantes da pergunta não abordadas (se houver)

Forneça sua avaliação detalhada com base nos critérios acima."""),
    ]
)

question_relevance: RunnableSequence = relevance_prompt | structured_output