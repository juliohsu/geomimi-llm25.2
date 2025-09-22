import streamlit as st
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from .ragas_evaluator import RAGASEvaluator, RAGASResult
from .giskard_evaluator import GiskardEvaluator, GiskardResult
from .bhc_dataset import BHCDataset, get_evaluation_subset, get_all_questions
from .evaluation_ui import (
    render_evaluation_metrics_dashboard,
    render_evaluation_runner,
    display_evaluation_progress,
    show_evaluation_results_summary
)

class EvaluationCoordinator:
    
    def __init__(self):
        self.ragas_evaluator = RAGASEvaluator()
        self.giskard_evaluator = GiskardEvaluator()
        self.bhc_dataset = BHCDataset()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state for evaluation results"""
        if 'evaluation_results' not in st.session_state:
            st.session_state.evaluation_results = {
                'ragas_results': None,
                'giskard_results': None,
                'last_evaluation_time': None,
                'evaluation_settings': {}
            }
    
    def run_ragas_evaluation(self, rag_system_func, settings: Dict[str, Any]) -> List[RAGASResult]:
        
        max_questions = settings.get('max_questions', 5)
        questions = get_evaluation_subset(max_questions)
        
        ragas_results = []
        total_questions = len(questions)
        
        progress_placeholder = st.empty()
        
        for i, bhc_question in enumerate(questions):
            with progress_placeholder.container():
                display_evaluation_progress(
                    f"Avaliando pergunta {i+1}: {bhc_question.question[:50]}...",
                    total_questions,
                    i + 1
                )
            
            try:
                rag_response = rag_system_func(bhc_question.question)
                
                if not rag_response or 'solution' not in rag_response:
                    st.warning(f"Não foi possível obter resposta para a pergunta {i+1}")
                    continue
                
                answer = rag_response['solution']
                context = rag_response.get('documents', [''])[0] if rag_response.get('documents') else ""
                
                ragas_result = self.ragas_evaluator.evaluate_single_qa(
                    question=bhc_question.question,
                    answer=answer,
                    context=context,
                    ground_truth=bhc_question.ground_truth
                )
                
                ragas_results.append(ragas_result)
                
            except Exception as e:
                st.error(f"Erro na avaliação RAGAS da pergunta {i+1}: {str(e)}")
                st.text(traceback.format_exc())
        
        progress_placeholder.empty()
        return ragas_results
    
    def run_giskard_evaluation(self, rag_system_func, settings: Dict[str, Any]) -> GiskardResult:
        
        max_questions = settings.get('max_questions', 5)
        questions = get_evaluation_subset(max_questions)
        
        qa_pairs = []
        response_times = []
        
        progress_placeholder = st.empty()
        
        for i, bhc_question in enumerate(questions):
            with progress_placeholder.container():
                display_evaluation_progress(
                    f"Coletando dados para GISKARD: {bhc_question.question[:50]}...",
                    len(questions),
                    i + 1
                )
            
            try:
                start_time = time.time()
                rag_response = rag_system_func(bhc_question.question)
                response_time = (time.time() - start_time) * 1000
                
                if rag_response and 'solution' in rag_response:
                    qa_pair = {
                        "question": bhc_question.question,
                        "answer": rag_response['solution'],
                        "ground_truth": bhc_question.ground_truth,
                        "context": rag_response.get('documents', [''])[0] if rag_response.get('documents') else ""
                    }
                    qa_pairs.append(qa_pair)
                    response_times.append(response_time)
                
            except Exception as e:
                st.warning(f"Erro ao coletar dados para pergunta {i+1}: {str(e)}")
        
        progress_placeholder.empty()
        
        if not qa_pairs:
            st.error("Nenhum dado válido coletado para avaliação GISKARD")
            return None
        
        with st.spinner("Executando avaliação GISKARD..."):
            giskard_result = self.giskard_evaluator.evaluate_comprehensive(
                qa_pairs, rag_system_func, response_times
            )
        
        return giskard_result
    
    def run_comprehensive_evaluation(self, rag_system_func, settings: Dict[str, Any]) -> Tuple[List[RAGASResult], GiskardResult]:
        
        start_time = time.time()
        
        st.info("🚀 Iniciando avaliação abrangente do sistema RAG...")
        
        st.markdown("### 🎯 Executando RAGAS...")
        ragas_results = self.run_ragas_evaluation(rag_system_func, settings)
        
        st.markdown("### 🛡️ Executando GISKARD...")
        giskard_results = self.run_giskard_evaluation(rag_system_func, settings)
        
        execution_time = time.time() - start_time
        
        st.session_state.evaluation_results.update({
            'ragas_results': ragas_results,
            'giskard_results': giskard_results,
            'last_evaluation_time': time.time(),
            'evaluation_settings': settings
        })
        
        show_evaluation_results_summary(ragas_results, giskard_results, execution_time)
        
        return ragas_results, giskard_results
    
    def render_evaluation_interface(self, rag_system_func):
        
        st.markdown("## 📊 Avaliação Automática do Sistema RAG")
        st.markdown("Avalie a qualidade do sistema usando métricas RAGAS e GISKARD")
        
        runner_config = render_evaluation_runner()
        
        if runner_config['run_ragas']:
            st.markdown("---")
            with st.spinner("Executando avaliação RAGAS..."):
                ragas_results = self.run_ragas_evaluation(rag_system_func, runner_config['settings'])
                st.session_state.evaluation_results['ragas_results'] = ragas_results
                st.success(f"✅ RAGAS concluído! {len(ragas_results)} perguntas avaliadas")
        
        elif runner_config['run_giskard']:
            st.markdown("---")
            with st.spinner("Executando avaliação GISKARD..."):
                giskard_results = self.run_giskard_evaluation(rag_system_func, runner_config['settings'])
                st.session_state.evaluation_results['giskard_results'] = giskard_results
                st.success("✅ GISKARD concluído!")
        
        elif runner_config['run_both']:
            st.markdown("---")
            ragas_results, giskard_results = self.run_comprehensive_evaluation(
                rag_system_func, runner_config['settings']
            )
            st.success("✅ Avaliação abrangente concluída!")
        
        ragas_results = st.session_state.evaluation_results.get('ragas_results')
        giskard_results = st.session_state.evaluation_results.get('giskard_results')
        
        if ragas_results or giskard_results:
            st.markdown("---")
            try:
                render_evaluation_metrics_dashboard(ragas_results, giskard_results)
            except Exception as e:
                st.error(f"Erro ao renderizar dashboard: {str(e)}")
                st.text("Mostrando resultados em formato simplificado:")
                
                if ragas_results:
                    st.markdown("### RAGAS Results")
                    for i, result in enumerate(ragas_results):
                        st.markdown(f"**Pergunta {i+1}:**")
                        st.markdown(f"- Faithfulness: {result.faithfulness:.3f}")
                        st.markdown(f"- Answer Relevancy: {result.answer_relevancy:.3f}")
                        st.markdown(f"- Context Precision: {result.context_precision:.3f}")
                        st.markdown(f"- Context Recall: {result.context_recall:.3f}")
                        st.markdown(f"- Overall Score: {result.overall_score:.3f}")
                
                if giskard_results:
                    st.markdown("### GISKARD Results")
                    st.markdown(f"- Robustness: {giskard_results.robustness_score:.3f}")
                    st.markdown(f"- Bias Score: {giskard_results.bias_score:.3f}")
                    st.markdown(f"- Performance: {giskard_results.performance_score:.3f}")
                    st.markdown(f"- Consistency: {giskard_results.consistency_score:.3f}")
                    st.markdown(f"- Overall Risk: {giskard_results.overall_risk_score:.3f}")
        
        self._render_dataset_info()
    
    def _render_dataset_info(self):
        
        with st.expander("📋 Informações do Dataset de Avaliação"):
            stats = self.bhc_dataset.get_statistics()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Perguntas", stats['total_questions'])
                st.metric("Palavras-chave", stats['total_keywords'])
            
            with col2:
                st.markdown("**Categorias:**")
                for category, count in stats['categories'].items():
                    st.markdown(f"• {category}: {count}")
            
            with col3:
                st.markdown("**Níveis de Dificuldade:**")
                for difficulty, count in stats['difficulty_levels'].items():
                    st.markdown(f"• {difficulty}: {count}")
            
            st.markdown("#### 📝 Exemplos de Perguntas")
            sample_questions = get_evaluation_subset(3)
            
            for i, question in enumerate(sample_questions):
                with st.expander(f"Pergunta {i+1}: {question.question[:80]}..."):
                    st.markdown(f"**Categoria:** {question.category.value}")
                    st.markdown(f"**Dificuldade:** {question.difficulty.value}")
                    st.markdown(f"**Pergunta:** {question.question}")
                    st.markdown(f"**Resposta Esperada:** {question.ground_truth}")
                    st.markdown(f"**Palavras-chave:** {', '.join(question.keywords)}")
    
    def get_cached_results(self) -> Tuple[Optional[List[RAGASResult]], Optional[GiskardResult]]:
        return (
            st.session_state.evaluation_results.get('ragas_results'),
            st.session_state.evaluation_results.get('giskard_results')
        )
    
    def clear_cached_results(self):
        st.session_state.evaluation_results.update({
            'ragas_results': None,
            'giskard_results': None,
            'last_evaluation_time': None,
            'evaluation_settings': {}
        })

evaluation_coordinator = EvaluationCoordinator()

def render_evaluation_section(rag_system_func):
    return evaluation_coordinator.render_evaluation_interface(rag_system_func)