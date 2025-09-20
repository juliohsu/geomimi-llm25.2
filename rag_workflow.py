import streamlit as st

from langgraph.graph import END, StateGraph
from state import GraphState

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
    
    
    
