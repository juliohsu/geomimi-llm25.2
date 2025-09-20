from typing import List, TypedDict, Optional, Dict, Any

class GraphState(TypedDict):
    question: str
    solution: str
    online_search: bool
    documents: List[str]
    search_method: Optional[str]
    document_evaluations: Optional[List[Dict[str, Any]]]
    document_relevance_score: Optional[Dict[str, Any]]
    question_relevance_score: Optional[Dict[str, Any]]
    retry_count: Optional[int]
    no_documents_available: Optional[bool]
    retry_limit_reached: Optional[bool]