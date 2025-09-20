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