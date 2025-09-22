import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional
import json
import time
from dataclasses import dataclass
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_llm():
    return ChatOpenAI(temperature=0, model="gpt-4")

def get_embeddings():
    return OpenAIEmbeddings()

@dataclass
class RAGASResult:
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float
    overall_score: float
    evaluation_time: float
    details: Dict[str, Any]

class FaithfulnessEval(BaseModel):
    score: float = Field(description="Faithfulness score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of the faithfulness assessment")
    contradictions: List[str] = Field(description="List of any contradictions found")

class AnswerRelevancyEval(BaseModel):
    score: float = Field(description="Relevancy score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of relevancy assessment")
    key_points_addressed: List[str] = Field(description="Key question points that were addressed")
    missing_points: List[str] = Field(description="Important question points that were missed")

class ContextPrecisionEval(BaseModel):
    score: float = Field(description="Precision score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of precision assessment")
    relevant_chunks: int = Field(description="Number of relevant context chunks")
    total_chunks: int = Field(description="Total number of context chunks")

class ContextRecallEval(BaseModel):
    score: float = Field(description="Recall score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of recall assessment")
    retrieved_info: List[str] = Field(description="Key information that was retrieved")
    missing_info: List[str] = Field(description="Important information that was missed")

class RAGASEvaluator:
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self._setup_prompts()
    
    def _get_llm(self):
        if self.llm is None:
            self.llm = get_llm()
        return self.llm
    
    def _get_embeddings(self):
        if self.embeddings is None:
            self.embeddings = get_embeddings()
        return self.embeddings
    
    def _setup_prompts(self):
        self.faithfulness_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator for RAG systems. Evaluate the faithfulness of the generated answer to the provided context.

Faithfulness measures how factually consistent the answer is with the given context. The answer should:
1. Not contradict any information in the context
2. Only make claims that can be supported by the context
3. Not hallucinate or add information not present in the context

Score from 0.0 (completely unfaithful) to 1.0 (perfectly faithful).
Answer in Portuguese."""),
            ("human", """Context: {context}

Generated Answer: {answer}

Evaluate the faithfulness of this answer to the context.""")
        ])
        
        self.relevancy_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator for RAG systems. Evaluate how relevant the generated answer is to the question asked.

Answer Relevancy measures how well the answer addresses the specific question. Consider:
1. Does the answer directly address what was asked?
2. Are the key aspects of the question covered?
3. Is the answer focused and on-topic?
4. Does it provide the type of information the question seeks?

Score from 0.0 (completely irrelevant) to 1.0 (perfectly relevant).
Answer in Portuguese."""),
            ("human", """Question: {question}

Generated Answer: {answer}

Evaluate the relevancy of this answer to the question.""")
        ])
        
        self.precision_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator for RAG systems. Evaluate the precision of the retrieved context for answering the question.

Context Precision measures how much of the retrieved context is actually relevant to answering the question. Consider:
1. How much of the context directly helps answer the question?
2. Is there irrelevant or off-topic information?
3. Are the retrieved chunks focused and useful?

Score from 0.0 (no relevant context) to 1.0 (all context is relevant).
Answer in Portuguese."""),
            ("human", """Question: {question}

Retrieved Context: {context}

Evaluate the precision of this context for answering the question.""")
        ])
        
        self.recall_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert evaluator for RAG systems. Evaluate the recall of the retrieved context against the ground truth.

Context Recall measures whether all necessary information to answer the question was retrieved. Consider:
1. Does the context contain all key information needed?
2. Are there important details missing that would improve the answer?
3. Is the retrieval comprehensive for this type of question?

Score from 0.0 (missing critical information) to 1.0 (all necessary information retrieved).
Answer in Portuguese."""),
            ("human", """Question: {question}

Retrieved Context: {context}

Ground Truth Answer: {ground_truth}

Evaluate if the retrieved context contains sufficient information to generate the ground truth answer.""")
        ])
    
    def evaluate_faithfulness(self, answer: str, context: str) -> FaithfulnessEval:
        structured_llm = self._get_llm().with_structured_output(FaithfulnessEval)
        chain = self.faithfulness_prompt | structured_llm
        return chain.invoke({"answer": answer, "context": context})
    
    def evaluate_answer_relevancy(self, question: str, answer: str) -> AnswerRelevancyEval:
        structured_llm = self._get_llm().with_structured_output(AnswerRelevancyEval)
        chain = self.relevancy_prompt | structured_llm
        return chain.invoke({"question": question, "answer": answer})
    
    def evaluate_context_precision(self, question: str, context: str) -> ContextPrecisionEval:
        structured_llm = self._get_llm().with_structured_output(ContextPrecisionEval)
        chain = self.precision_prompt | structured_llm
        return chain.invoke({"question": question, "context": context})
    
    def evaluate_context_recall(self, question: str, context: str, ground_truth: str) -> ContextRecallEval:
        structured_llm = self._get_llm().with_structured_output(ContextRecallEval)
        chain = self.recall_prompt | structured_llm
        return chain.invoke({
            "question": question,
            "context": context,
            "ground_truth": ground_truth
        })
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        try:
            embeddings = self._get_embeddings()
            emb1 = embeddings.embed_query(text1)
            emb2 = embeddings.embed_query(text2)
            similarity = cosine_similarity([emb1], [emb2])[0][0]
            return float(similarity)
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 0.0
    
    def evaluate_single_qa(self, question: str, answer: str, context: str, ground_truth: str) -> RAGASResult:
        start_time = time.time()
        
        try:
            faithfulness_eval = self.evaluate_faithfulness(answer, context)
            relevancy_eval = self.evaluate_answer_relevancy(question, answer)
            precision_eval = self.evaluate_context_precision(question, context)
            recall_eval = self.evaluate_context_recall(question, context, ground_truth)
            
            semantic_sim = self.calculate_semantic_similarity(answer, ground_truth)
            
            overall_score = (
                faithfulness_eval.score * 0.3 +
                relevancy_eval.score * 0.3 +
                precision_eval.score * 0.2 +
                recall_eval.score * 0.2
            )
            
            evaluation_time = time.time() - start_time
            
            details = {
                "faithfulness_details": {
                    "reasoning": faithfulness_eval.reasoning,
                    "contradictions": faithfulness_eval.contradictions
                },
                "relevancy_details": {
                    "reasoning": relevancy_eval.reasoning,
                    "key_points_addressed": relevancy_eval.key_points_addressed,
                    "missing_points": relevancy_eval.missing_points
                },
                "precision_details": {
                    "reasoning": precision_eval.reasoning,
                    "relevant_chunks": precision_eval.relevant_chunks,
                    "total_chunks": precision_eval.total_chunks
                },
                "recall_details": {
                    "reasoning": recall_eval.reasoning,
                    "retrieved_info": recall_eval.retrieved_info,
                    "missing_info": recall_eval.missing_info
                },
                "semantic_similarity": semantic_sim
            }
            
            return RAGASResult(
                faithfulness=faithfulness_eval.score,
                answer_relevancy=relevancy_eval.score,
                context_precision=precision_eval.score,
                context_recall=recall_eval.score,
                overall_score=overall_score,
                evaluation_time=evaluation_time,
                details=details
            )
            
        except Exception as e:
            print(f"Error in RAGAS evaluation: {e}")
            return RAGASResult(
                faithfulness=0.0,
                answer_relevancy=0.0,
                context_precision=0.0,
                context_recall=0.0,
                overall_score=0.0,
                evaluation_time=time.time() - start_time,
                details={"error": str(e)}
            )
    
    def evaluate_batch(self, test_cases: List[Dict[str, str]]) -> List[RAGASResult]:
        results = []
        for case in test_cases:
            result = self.evaluate_single_qa(
                question=case["question"],
                answer=case["answer"],
                context=case.get("context", ""),
                ground_truth=case["ground_truth"]
            )
            results.append(result)
        return results
    
    def get_aggregate_metrics(self, results: List[RAGASResult]) -> Dict[str, float]:
        if not results:
            return {}
        
        return {
            "avg_faithfulness": np.mean([r.faithfulness for r in results]),
            "avg_answer_relevancy": np.mean([r.answer_relevancy for r in results]),
            "avg_context_precision": np.mean([r.context_precision for r in results]),
            "avg_context_recall": np.mean([r.context_recall for r in results]),
            "avg_overall_score": np.mean([r.overall_score for r in results]),
            "total_evaluation_time": sum([r.evaluation_time for r in results]),
            "std_faithfulness": np.std([r.faithfulness for r in results]),
            "std_answer_relevancy": np.std([r.answer_relevancy for r in results]),
            "std_context_precision": np.std([r.context_precision for r in results]),
            "std_context_recall": np.std([r.context_recall for r in results])
        }