import streamlit as st

from langgraph.graph import END, StateGraph
from state import GraphState
from chains.evaluate import evaluate_docs
from chains.generate_answer import generate_chain

class RAGWorkflow:
    
    def __init__(self):
        self.graph = None
        self.retriever = None
        self._current_session_retriever_key = None

    def _create_graph(self):
        workflow = StateGraph(GraphState)
        
        workflow.add_node("Retrieve Documents", self._retrieve)
        workflow.add_node("Grade Documents", self._evaluate)
        workflow.add_node("Generate Answer", self._generate_answer)

        workflow.set_entry_point("Retrieve Documents")
        workflow.add_edge("Retrieve Documents", "Grade Documents")
        workflow.add_conditional_edges(
            "Grade Documents",
            self._any_doc_irrelevant,
            {
                "Generate Answer": "Generate Answer",
            },
        )

        workflow.add_conditional_edges(
            "Generate Answer",
            self._check_hallucinations,
            {
                "Hallucinations detected": "Generate Answer",
                "Answers Question": END,
                "Question not addressed": END,
            },
        )

        workflow.add_edge("Generate Answer", END)

        return workflow.compile()
    
    def _evaluate(self, state: GraphState):
        print("GRAPH STATE: Grade Documents")
        question = state["question"]
        documents = state["documents"]

        online_search = state.get("online_search", False)
        print(f"Evaluating {len(documents)} documents, online_search: {online_search}")
        
        filtered_docs = []
        document_evaluations = []
        
        for document in documents:
            response = evaluate_docs.invoke({"question": question, "document": document.page_content})
            document_evaluations.append(response)
            
            result = response.score
            if result.lower() == "yes":
                filtered_docs.append(document)
            else:
                online_search = True
        
        print(f"Filtered to {len(filtered_docs)} relevant documents, online_search: {online_search}")
        
        search_method = "online" if online_search else "documents" 
        
        return {
            "documents": filtered_docs, 
            "question": question, 
            "online_search": online_search,
            "search_method": search_method,
            "document_evaluations": document_evaluations
        }
    
    def set_retriever(self, retriever):
        self.retriever = retriever
        
        if retriever is not None:
            current_file_key = st.session_state.get('processed_file')
            self._current_session_retriever_key = current_file_key
            print(f"Retriever set for file: {current_file_key}")
        else:
            self._current_session_retriever_key = None
            print("Retriever cleared")

    def get_current_retriever(self):
        if self.retriever is not None:
            return self.retriever
            
        session_retriever = st.session_state.get('retriever')
        if session_retriever is not None:
            print("Using retriever from session state")
            self.retriever = session_retriever
            return session_retriever
            
        return None
    
    def _any_doc_irrelevant(self, state):
        next_state = "Generate Answer"
        return next_state
    
    def _generate_answer(self, state: GraphState):
        print("GRAPH STATE: Generate Answer")
        question = state["question"]
        documents = state["documents"]
        
        retry_count = state.get("retry_count", 0)
        
        print(f"Generating answer using {len(documents)} documents (attempt {retry_count + 1})")
        
        if len(documents) == 0:
            print("No relevant documents found - providing fallback response")
            solution = self._generate_fallback_response(question)
            return {
                "documents": documents, 
                "question": question, 
                "solution": solution,
                "retry_count": retry_count + 1,
                "no_documents_available": True
            }
        
        solution = generate_chain.invoke({"context": documents, "question": question})
        print(f"Answer generated: {len(solution)} characters")
        return {
            "documents": documents, 
            "question": question, 
            "solution": solution,
            "retry_count": retry_count + 1
        }
    
    def _generate_fallback_response(self, question):
        fallback_message = f"""Desculpe, mas não consegui encontrar informações relevantes nos documentos carregados para responder à sua pergunta: "{question}".

Os documentos disponíveis parecem não conter informações relacionadas ao que você está perguntando. Para obter uma resposta adequada, seria necessário:

1. Carregar documentos que contenham informações relacionadas à sua pergunta
2. Fazer uma pergunta mais específica sobre o conteúdo dos documentos carregados
3. Verificar se sua pergunta está relacionada ao contexto dos documentos disponíveis

Você poderia reformular sua pergunta de forma mais específica sobre o conteúdo dos documentos, ou carregar documentos relevantes para sua consulta?"""
        
        return fallback_message
    
