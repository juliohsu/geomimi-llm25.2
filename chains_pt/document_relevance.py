from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableSequence
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(temperature=0)


class DocumentRelevance(BaseModel):
    
    binary_score: bool = Field(
        description="Whether the answer is grounded in the documents - true if supported, false if not supported"
    )
    
    confidence: float = Field(
        default=0.5,
        description="Confidence score between 0.0 and 1.0 indicating how certain the evaluation is",
        ge=0.0,
        le=1.0
    )
    
    reasoning: str = Field(
        default="",
        description="Brief explanation of why the answer is or isn't grounded in the documents"
    )


structured_output = llm.with_structured_output(DocumentRelevance)

system = """Você é um avaliador especialista em RELEVÂNCIA DE DOCUMENTOS para um sistema RAG.

CRITÉRIOS DE AVALIAÇÃO:
- A resposta deve ser diretamente suportada por informações encontradas nos documentos fonte
- Fatos, afirmações e detalhes importantes devem ser rastreáveis nos documentos fornecidos
- A resposta não deve conter informações que contradizem os documentos fonte
- Pequenas paráfrases ou inferências razoáveis dos documentos são aceitáveis
- A resposta não deve incluir informações fabricadas ou conhecimento externo não presente nos documentos

ORIENTAÇÕES DE PONTUAÇÃO:
- Marque 'sim' (true) se a resposta estiver bem fundamentada nos documentos
- Marque 'não' (false) se a resposta contiver afirmações sem suporte, contradições ou informações fabricadas

Seja rigoroso em sua avaliação para garantir a qualidade da resposta e evitar alucinações."""

relevance_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", """Avalie se a resposta gerada pela IA está fundamentada nos documentos fornecidos.

DOCUMENTOS FONTE:
{documents}

RESPOSTA GERADA PELA IA PARA AVALIAÇÃO:
{solution}

Forneça:
1. Uma pontuação binária (true/false) indicando se a resposta está fundamentada nos documentos
2. Uma pontuação de confiança (0.0-1.0) para sua avaliação
3. Um breve raciocínio explicando sua decisão

Com base nos critérios de avaliação, esta resposta está devidamente fundamentada nos documentos fonte?"""),
    ]
)

document_relevance: RunnableSequence = relevance_prompt | structured_output