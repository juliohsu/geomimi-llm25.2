from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv 

load_dotenv()

llm = ChatOpenAI(temperature=0)

class EvaluateDocs(BaseModel):
       
    score: str = Field(
        description="Whether documents are relevant to the question - 'yes' if sufficient, 'no' if insufficient"
    )
    
    relevance_score: float = Field(
        default=0.5,
        description="Relevance score between 0.0 and 1.0 indicating how well documents match the query",
        ge=0.0,
        le=1.0
    )
    
    coverage_assessment: str = Field(
        default="",
        description="Assessment of how well the documents cover the query requirements"
    )
    
    missing_information: str = Field(
        default="",
        description="Description of key information missing from documents (if any)"
    )


structured_output = llm.with_structured_output(EvaluateDocs)

system = """Você é um avaliador de documentos para um sistema RAG.

CRITÉRIOS DE AVALIAÇÃO:

1. RELEVÂNCIA TEMÁTICA:
    - Os documentos abordam diretamente o tema principal da pergunta?
    - Os conceitos e tópicos-chave estão alinhados com o que o usuário está perguntando?

2. SUFICIÊNCIA DE INFORMAÇÃO:
    - Há detalhes suficientes para fornecer uma resposta completa?
    - Existem fatos, dados ou exemplos específicos quando necessário?
    - A pergunta pode ser respondida sem necessidade de conhecimento externo?

3. QUALIDADE DA INFORMAÇÃO:
    - As informações são precisas e confiáveis?
    - Existem afirmações conflitantes nos documentos?
    - As informações são atuais e relevantes para o contexto da pergunta?

4. AVALIAÇÃO DE COMPLETUDE:
    - O conjunto de documentos cobre todos os aspectos da pergunta?
    - Existem lacunas óbvias que impedem uma resposta completa?

CRITÉRIOS DE PONTUAÇÃO:
- Marque 'sim' se os documentos fornecem informações suficientes e relevantes para responder satisfatoriamente à pergunta
- Marque 'não' se os documentos não têm informações-chave, são fora do tema ou insuficientes para uma resposta completa

REQUISITOS ADICIONAIS:
- Forneça uma pontuação de relevância (0.0-1.0) indicando a qualidade da correspondência
- Avalie a cobertura dos requisitos da pergunta
- Identifique qualquer informação crítica ausente

Seja detalhista, mas eficiente em sua avaliação. Foque na utilidade prática para geração da resposta."""

evaluate_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", """Avalie se os documentos recuperados são suficientes para responder à pergunta do usuário.

PERGUNTA DO USUÁRIO:
{question}

DOCUMENTOS RECUPERADOS:
{document}

AVALIAÇÃO REQUERIDA:
1. Pontuação Principal: 'sim' se os documentos são suficientes, 'não' se insuficientes
2. Pontuação de Relevância: nota de 0.0 a 1.0 sobre o quanto os documentos correspondem à pergunta
3. Avaliação de Cobertura: como os documentos atendem aos requisitos da pergunta?
4. Informação Ausente: qual informação chave (se houver) está faltando para uma resposta completa?

Forneça sua avaliação detalhada com base nos critérios acima."""),
    ]
)

evaluate_docs = evaluate_prompt | structured_output