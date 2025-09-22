import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
import json
import time
import re
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
import numpy as np
from collections import defaultdict, Counter

def get_llm():
    return ChatOpenAI(temperature=0, model="gpt-4")

@dataclass
class GiskardResult:
    robustness_score: float
    bias_score: float
    performance_score: float
    consistency_score: float
    overall_risk_score: float
    evaluation_time: float
    details: Dict[str, Any]
    recommendations: List[str]

class RobustnessEval(BaseModel):
    score: float = Field(description="Robustness score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of robustness assessment")
    vulnerability_areas: List[str] = Field(description="Areas where system shows vulnerability")
    stress_test_results: Dict[str, float] = Field(description="Results of various stress tests")

class BiasEval(BaseModel):
    score: float = Field(description="Bias score between 0 and 1 (higher = less biased)", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of bias assessment")
    detected_biases: List[str] = Field(description="Types of biases detected")
    fairness_issues: List[str] = Field(description="Fairness concerns identified")

class PerformanceEval(BaseModel):
    score: float = Field(description="Performance score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of performance assessment")
    accuracy_metrics: Dict[str, float] = Field(description="Various accuracy measurements")
    efficiency_metrics: Dict[str, float] = Field(description="Efficiency measurements")

class ConsistencyEval(BaseModel):
    score: float = Field(description="Consistency score between 0 and 1", ge=0.0, le=1.0)
    reasoning: str = Field(description="Explanation of consistency assessment")
    variation_analysis: Dict[str, float] = Field(description="Analysis of response variations")
    stability_issues: List[str] = Field(description="Identified stability concerns")

class GiskardEvaluator:
    
    def __init__(self):
        self.llm = None
        self._setup_prompts()
        self._setup_test_cases()
    
    def _get_llm(self):
        if self.llm is None:
            self.llm = get_llm()
        return self.llm
    
    def _setup_prompts(self):
        self.robustness_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert ML system evaluator. Evaluate the robustness of this RAG system response.

Robustness measures how well the system handles:
1. Variations in input formatting and style
2. Edge cases and unusual queries
3. Noisy or incomplete input data
4. Different phrasings of the same question
5. Out-of-domain or adversarial inputs

Consider if the response maintains quality despite input variations.
Score from 0.0 (very fragile) to 1.0 (very robust).
Answer in Portuguese."""),
            ("human", """Original Question: {original_question}

Modified Question: {modified_question}

Original Answer: {original_answer}

Modified Answer: {modified_answer}

Context: {context}

Evaluate the robustness of the system's responses to input variations.""")
        ])
        
        self.bias_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in ML fairness and bias detection. Evaluate potential biases in this RAG system.

Look for biases such as:
1. Geographic or regional bias
2. Temporal bias (favoring recent vs. historical data)
3. Language or terminology bias
4. Methodology bias (favoring certain calculation methods)
5. Confirmation bias in information selection
6. Cultural or institutional bias

Score from 0.0 (highly biased) to 1.0 (unbiased).
Answer in Portuguese."""),
            ("human", """Question: {question}

Answer: {answer}

Context: {context}

Alternative Phrasings and Their Answers: {alternative_responses}

Evaluate potential biases in the system's responses.""")
        ])
        
        self.performance_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in ML system performance evaluation. Assess the performance of this RAG system.

Evaluate:
1. Accuracy of information provided
2. Completeness of answers
3. Precision and specificity
4. Response quality and clarity
5. Technical correctness
6. Appropriate level of detail

Score from 0.0 (poor performance) to 1.0 (excellent performance).
Answer in Portuguese."""),
            ("human", """Question: {question}

Generated Answer: {answer}

Ground Truth: {ground_truth}

Context Used: {context}

Response Time: {response_time}ms

Evaluate the overall performance of this response.""")
        ])
        
        self.consistency_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in ML system consistency evaluation. Assess the consistency of this RAG system.

Evaluate:
1. Consistency across similar questions
2. Stability of responses over time
3. Coherence within individual responses
4. Consistent use of terminology and concepts
5. Reproducibility of results
6. Logical consistency across related topics

Score from 0.0 (very inconsistent) to 1.0 (perfectly consistent).
Answer in Portuguese."""),
            ("human", """Related Questions and Answers:
{related_qa_pairs}

Context Information: {context}

System Responses Over Time: {temporal_responses}

Evaluate the consistency of the system's responses.""")
        ])
    
    def _setup_test_cases(self):
        self.robustness_tests = {
            "typos": self._generate_typo_variants,
            "formatting": self._generate_format_variants,
            "synonyms": self._generate_synonym_variants,
            "length": self._generate_length_variants,
            "complexity": self._generate_complexity_variants,
            "edge_cases": self._generate_edge_cases
        }
    
    def _generate_typo_variants(self, question: str) -> List[str]:
        variants = []
        
        typo_map = {
            "precipitação": ["precipitacao", "preciptação", "precipitçao"],
            "evapotranspiração": ["evapotranspiracao", "evapotranspiraçao"],
            "balanço": ["balanco", "balansso"],
            "hídrico": ["hidrico", "hidríco"],
            "climatológico": ["climatologico", "climatologíco"],
            "armazenamento": ["armazenameto", "armezamento"],
            "umidade": ["humidade", "umidede"]
        }
        
        modified_question = question.lower()
        for correct, typos in typo_map.items():
            if correct in modified_question:
                for typo in typos:
                    variant = modified_question.replace(correct, typo)
                    variants.append(variant.capitalize())
        
        return variants[:3]
    
    def _generate_format_variants(self, question: str) -> List[str]:
        return [
            question.upper(),
            question.lower(),
            question.replace("?", ""),
            f"Me explique: {question.lower()}",
            f"Gostaria de saber {question.lower()}"
        ]
    
    def _generate_synonym_variants(self, question: str) -> List[str]:
        synonym_map = {
            "precipitação": "chuva",
            "evapotranspiração": "perda de água",
            "balanço hídrico": "cálculo de água",
            "armazenamento": "reserva",
            "déficit": "falta",
            "excedente": "sobra"
        }
        
        variants = []
        for original, synonym in synonym_map.items():
            if original in question.lower():
                variant = question.lower().replace(original, synonym)
                variants.append(variant.capitalize())
        
        return variants
    
    def _generate_length_variants(self, question: str) -> List[str]:
        short = re.sub(r'\(.*?\)', '', question)
        short = re.sub(r'\s+', ' ', short).strip()
        
        verbose = f"Você poderia me explicar detalhadamente {question.lower()} Preciso de uma resposta completa e técnica."
        
        return [short, verbose]
    
    def _generate_complexity_variants(self, question: str) -> List[str]:
        return [
            f"De forma simples: {question.lower()}",
            f"Tecnicamente falando: {question.lower()}",
            f"Para um especialista: {question.lower()}"
        ]
    
    def _generate_edge_cases(self, question: str) -> List[str]:
        return [
            "",
            "?", 
            question * 3,
            f"{question} {question}",
            question.replace(" ", "")
        ]
    
    def evaluate_robustness(self, original_qa: Dict[str, str], rag_system_func) -> RobustnessEval:
        original_question = original_qa["question"]
        original_answer = original_qa["answer"]
        
        test_results = {}
        vulnerability_areas = []
        
        for test_name, test_generator in self.robustness_tests.items():
            variants = test_generator(original_question)
            scores = []
            
            for variant in variants:
                if not variant.strip():
                    continue
                    
                try:
                    variant_response = rag_system_func(variant)
                    
                    similarity = self._calculate_response_similarity(original_answer, variant_response.get("solution", ""))
                    scores.append(similarity)
                    
                    if similarity < 0.5:
                        vulnerability_areas.append(f"{test_name}: {variant[:50]}...")
                        
                except Exception as e:
                    scores.append(0.0)
                    vulnerability_areas.append(f"{test_name}: Error - {str(e)[:50]}")
            
            test_results[test_name] = np.mean(scores) if scores else 0.0
        
        overall_robustness = np.mean(list(test_results.values()))
        
        try:
            structured_llm = self._get_llm().with_structured_output(RobustnessEval)
            chain = self.robustness_prompt | structured_llm
            
            representative_variant = self._generate_format_variants(original_question)[0]
            variant_response = rag_system_func(representative_variant)
            
            llm_eval = chain.invoke({
                "original_question": original_question,
                "modified_question": representative_variant,
                "original_answer": original_answer,
                "modified_answer": variant_response.get("solution", ""),
                "context": original_qa.get("context", "")
            })
            
            final_score = (overall_robustness + llm_eval.score) / 2
            
            return RobustnessEval(
                score=final_score,
                reasoning=llm_eval.reasoning,
                vulnerability_areas=vulnerability_areas,
                stress_test_results=test_results
            )
            
        except Exception as e:
            return RobustnessEval(
                score=overall_robustness,
                reasoning=f"Automated evaluation only. Error in LLM eval: {str(e)}",
                vulnerability_areas=vulnerability_areas,
                stress_test_results=test_results
            )
    
    def _calculate_response_similarity(self, response1: str, response2: str) -> float:
        if not response1 or not response2:
            return 0.0
        
        tokens1 = set(response1.lower().split())
        tokens2 = set(response2.lower().split())
        
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0
        
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))
        
        return intersection / union if union > 0 else 0.0
    
    def evaluate_bias(self, qa_pairs: List[Dict[str, str]]) -> BiasEval:
        try:
            detected_biases = []
            fairness_issues = []
            
            geographic_terms = ["brasil", "brazil", "nordeste", "sudeste", "norte", "sul"]
            geo_mentions = defaultdict(int)
            
            for qa in qa_pairs:
                answer = qa["answer"].lower()
                for term in geographic_terms:
                    if term in answer:
                        geo_mentions[term] += 1
            
            if len(geo_mentions) > 0 and max(geo_mentions.values()) > 3 * np.mean(list(geo_mentions.values())):
                detected_biases.append("Possível viés geográfico detectado")
            
            temporal_terms = ["atual", "moderno", "antigo", "recente", "histórico"]
            temporal_balance = sum(1 for qa in qa_pairs for term in temporal_terms if term in qa["answer"].lower())
            
            if temporal_balance > len(qa_pairs) * 0.7:
                detected_biases.append("Possível viés temporal detectado")
            
            methods = ["thornthwaite", "penman", "blaney-criddle", "hargreaves"]
            method_mentions = defaultdict(int)
            
            for qa in qa_pairs:
                answer = qa["answer"].lower()
                for method in methods:
                    if method in answer:
                        method_mentions[method] += 1
            
            if len(method_mentions) > 0 and max(method_mentions.values()) > 2 * np.mean(list(method_mentions.values())):
                detected_biases.append("Possível viés metodológico detectado")
            
            structured_llm = self._get_llm().with_structured_output(BiasEval)
            chain = self.bias_prompt | structured_llm
            
            alternative_responses = {}
            for i, qa in enumerate(qa_pairs[:3]):
                alternative_responses[f"qa_{i}"] = qa["answer"]
            
            llm_eval = chain.invoke({
                "question": qa_pairs[0]["question"] if qa_pairs else "",
                "answer": qa_pairs[0]["answer"] if qa_pairs else "",
                "context": qa_pairs[0].get("context", ""),
                "alternative_responses": json.dumps(alternative_responses, ensure_ascii=False)
            })
            
            all_detected_biases = detected_biases + llm_eval.detected_biases
            all_fairness_issues = fairness_issues + llm_eval.fairness_issues
            
            bias_score = max(0.0, llm_eval.score - len(all_detected_biases) * 0.1)
            
            return BiasEval(
                score=bias_score,
                reasoning=llm_eval.reasoning,
                detected_biases=all_detected_biases,
                fairness_issues=all_fairness_issues
            )
            
        except Exception as e:
            return BiasEval(
                score=0.5,
                reasoning=f"Error in bias evaluation: {str(e)}",
                detected_biases=["Erro na avaliação de viés"],
                fairness_issues=[]
            )
    
    def evaluate_performance(self, qa_pair: Dict[str, str], response_time: float) -> PerformanceEval:
        try:
            structured_llm = self._get_llm().with_structured_output(PerformanceEval)
            chain = self.performance_prompt | structured_llm
            
            result = chain.invoke({
                "question": qa_pair["question"],
                "answer": qa_pair["answer"],
                "ground_truth": qa_pair.get("ground_truth", ""),
                "context": qa_pair.get("context", ""),
                "response_time": response_time
            })
            
            return result
            
        except Exception as e:
            return PerformanceEval(
                score=0.5,
                reasoning=f"Error in performance evaluation: {str(e)}",
                accuracy_metrics={},
                efficiency_metrics={"response_time": response_time}
            )
    
    def evaluate_consistency(self, qa_pairs: List[Dict[str, str]]) -> ConsistencyEval:
        try:
            variation_analysis = {}
            stability_issues = []
            
            key_terms = ["precipitação", "evapotranspiração", "balanço hídrico", "armazenamento"]
            term_usage = defaultdict(list)
            
            for qa in qa_pairs:
                answer = qa["answer"].lower()
                for term in key_terms:
                    if term in answer:
                        term_usage[term].append(qa["question"])
            
            for term, questions in term_usage.items():
                if len(questions) > 1:
                    variation_analysis[f"term_{term}"] = len(set(questions)) / len(questions)
            
            response_lengths = [len(qa["answer"]) for qa in qa_pairs]
            if response_lengths:
                length_cv = np.std(response_lengths) / np.mean(response_lengths)
                variation_analysis["response_length_cv"] = length_cv
                
                if length_cv > 0.5:
                    stability_issues.append("Alta variabilidade no comprimento das respostas")
            
            structured_llm = self._get_llm().with_structured_output(ConsistencyEval)
            chain = self.consistency_prompt | structured_llm
            
            related_qa_text = "\n\n".join([
                f"Q: {qa['question']}\nA: {qa['answer']}"
                for qa in qa_pairs[:5]
            ])
            
            llm_eval = chain.invoke({
                "related_qa_pairs": related_qa_text,
                "context": qa_pairs[0].get("context", "") if qa_pairs else "",
                "temporal_responses": "Dados de uma única sessão"
            })
            
            return llm_eval
            
        except Exception as e:
            return ConsistencyEval(
                score=0.5,
                reasoning=f"Error in consistency evaluation: {str(e)}",
                variation_analysis={},
                stability_issues=["Erro na avaliação de consistência"]
            )
    
    def evaluate_comprehensive(self, qa_pairs: List[Dict[str, str]], rag_system_func, response_times: List[float] = None) -> GiskardResult:
        start_time = time.time()
        
        if not qa_pairs:
            return GiskardResult(
                robustness_score=0.0,
                bias_score=0.0,
                performance_score=0.0,
                consistency_score=0.0,
                overall_risk_score=1.0,
                evaluation_time=0.0,
                details={},
                recommendations=["Nenhum dado para avaliação"]
            )
        
        robustness_eval = self.evaluate_robustness(qa_pairs[0], rag_system_func)
        bias_eval = self.evaluate_bias(qa_pairs)
        performance_eval = self.evaluate_performance(qa_pairs[0], response_times[0] if response_times else 1000.0)
        consistency_eval = self.evaluate_consistency(qa_pairs)
        
        risk_score = 1.0 - (
            robustness_eval.score * 0.25 +
            bias_eval.score * 0.25 +
            performance_eval.score * 0.25 +
            consistency_eval.score * 0.25
        )
        
        recommendations = []
        if robustness_eval.score < 0.7:
            recommendations.append("Melhorar robustez contra variações de entrada")
        if bias_eval.score < 0.7:
            recommendations.append("Revisar potenciais vieses nas respostas")
        if performance_eval.score < 0.7:
            recommendations.append("Otimizar precisão e qualidade das respostas")
        if consistency_eval.score < 0.7:
            recommendations.append("Melhorar consistência entre respostas relacionadas")
        
        evaluation_time = time.time() - start_time
        
        details = {
            "robustness_details": {
                "vulnerability_areas": robustness_eval.vulnerability_areas,
                "stress_test_results": robustness_eval.stress_test_results
            },
            "bias_details": {
                "detected_biases": bias_eval.detected_biases,
                "fairness_issues": bias_eval.fairness_issues
            },
            "performance_details": {
                "accuracy_metrics": performance_eval.accuracy_metrics,
                "efficiency_metrics": performance_eval.efficiency_metrics
            },
            "consistency_details": {
                "variation_analysis": consistency_eval.variation_analysis,
                "stability_issues": consistency_eval.stability_issues
            }
        }
        
        return GiskardResult(
            robustness_score=robustness_eval.score,
            bias_score=bias_eval.score,
            performance_score=performance_eval.score,
            consistency_score=consistency_eval.score,
            overall_risk_score=risk_score,
            evaluation_time=evaluation_time,
            details=details,
            recommendations=recommendations
        )