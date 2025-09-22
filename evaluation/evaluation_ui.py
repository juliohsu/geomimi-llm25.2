import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Any
import time
import json

def render_evaluation_metrics_dashboard(ragas_results, giskard_results):
    
    st.markdown("### 📊 Avaliação Detalhada do Sistema RAG")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 RAGAS Metrics", "🛡️ GISKARD Analysis", "📋 Comparação", "🔍 Insights"])
    
    with tab1:
        render_ragas_dashboard(ragas_results)
    
    with tab2:
        render_giskard_dashboard(giskard_results)
    
    with tab3:
        render_comparison_dashboard(ragas_results, giskard_results)
    
    with tab4:
        render_insights_dashboard(ragas_results, giskard_results)

def render_ragas_dashboard(ragas_results):
    if not ragas_results:
        st.warning("Nenhum resultado RAGAS disponível")
        return
    
    st.markdown("#### 🎯 RAGAS - Retrieval Augmented Generation Assessment")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_faithfulness = sum(r.faithfulness for r in ragas_results) / len(ragas_results)
        st.metric(
            "Faithfulness", 
            f"{avg_faithfulness:.3f}",
            help="Consistência factual entre resposta e contexto"
        )
    
    with col2:
        avg_relevancy = sum(r.answer_relevancy for r in ragas_results) / len(ragas_results)
        st.metric(
            "Answer Relevancy", 
            f"{avg_relevancy:.3f}",
            help="Relevância da resposta à pergunta"
        )
    
    with col3:
        avg_precision = sum(r.context_precision for r in ragas_results) / len(ragas_results)
        st.metric(
            "Context Precision", 
            f"{avg_precision:.3f}",
            help="Precisão do contexto recuperado"
        )
    
    with col4:
        avg_recall = sum(r.context_recall for r in ragas_results) / len(ragas_results)
        st.metric(
            "Context Recall", 
            f"{avg_recall:.3f}",
            help="Cobertura do contexto recuperado"
        )
    
    st.markdown("##### 📈 Distribuição das Métricas")
    
    metrics_data = []
    for i, result in enumerate(ragas_results):
        metrics_data.append({
            "Pergunta": f"Q{i+1}",
            "Faithfulness": result.faithfulness,
            "Answer Relevancy": result.answer_relevancy,
            "Context Precision": result.context_precision,
            "Context Recall": result.context_recall,
            "Overall Score": result.overall_score
        })
    
    df_metrics = pd.DataFrame(metrics_data)
    
    fig_radar = go.Figure()
    
    avg_metrics = {
        "Faithfulness": avg_faithfulness,
        "Answer Relevancy": avg_relevancy,
        "Context Precision": avg_precision,
        "Context Recall": avg_recall
    }
    
    fig_radar.add_trace(go.Scatterpolar(
        r=list(avg_metrics.values()),
        theta=list(avg_metrics.keys()),
        fill='toself',
        name='Métricas RAGAS'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Radar Chart - Métricas RAGAS Médias"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(
            df_metrics.melt(id_vars=['Pergunta'], 
                          value_vars=['Faithfulness', 'Answer Relevancy', 'Context Precision', 'Context Recall']),
            x='Pergunta',
            y='value',
            color='variable',
            title="Métricas por Pergunta",
            labels={'value': 'Score', 'variable': 'Métrica'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("##### 📋 Resultados Detalhados")
    st.dataframe(df_metrics, use_container_width=True)
    
    st.markdown("##### 💡 Insights RAGAS")
    
    insights = []
    if avg_faithfulness < 0.7:
        insights.append("⚠️ **Faithfulness baixo**: Respostas podem conter informações não suportadas pelo contexto")
    if avg_relevancy < 0.7:
        insights.append("⚠️ **Answer Relevancy baixo**: Respostas podem não estar abordando adequadamente as perguntas")
    if avg_precision < 0.7:
        insights.append("⚠️ **Context Precision baixo**: Sistema pode estar recuperando contexto irrelevante")
    if avg_recall < 0.7:
        insights.append("⚠️ **Context Recall baixo**: Sistema pode estar perdendo informações importantes")
    
    if not insights:
        insights.append("✅ **Desempenho satisfatório** em todas as métricas RAGAS")
    
    for insight in insights:
        st.markdown(insight)

def render_giskard_dashboard(giskard_results):
    if not giskard_results:
        st.warning("Nenhum resultado GISKARD disponível")
        return
    
    st.markdown("#### 🛡️ GISKARD - Análise de Robustez e Viés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Robustness", 
            f"{giskard_results.robustness_score:.3f}",
            help="Resistência a variações de entrada"
        )
    
    with col2:
        st.metric(
            "Bias Score", 
            f"{giskard_results.bias_score:.3f}",
            help="Ausência de vieses (maior = melhor)"
        )
    
    with col3:
        st.metric(
            "Performance", 
            f"{giskard_results.performance_score:.3f}",
            help="Desempenho geral do sistema"
        )
    
    with col4:
        st.metric(
            "Consistency", 
            f"{giskard_results.consistency_score:.3f}",
            help="Consistência entre respostas"
        )
    
    st.markdown("##### ⚠️ Avaliação de Risco")
    
    risk_level = "Baixo" if giskard_results.overall_risk_score < 0.3 else \
                 "Médio" if giskard_results.overall_risk_score < 0.6 else "Alto"
    
    risk_color = "green" if risk_level == "Baixo" else \
                 "orange" if risk_level == "Médio" else "red"
    
    st.markdown(f"**Nível de Risco Geral**: :{risk_color}[{risk_level}] ({giskard_results.overall_risk_score:.3f})")
    
    fig_risk = go.Figure(go.Bar(
        x=["Robustness", "Bias", "Performance", "Consistency"],
        y=[1-giskard_results.robustness_score, 1-giskard_results.bias_score, 
           1-giskard_results.performance_score, 1-giskard_results.consistency_score],
        marker_color=['red' if (1-score) > 0.5 else 'orange' if (1-score) > 0.3 else 'green' 
                     for score in [giskard_results.robustness_score, giskard_results.bias_score,
                                  giskard_results.performance_score, giskard_results.consistency_score]]
    ))
    
    fig_risk.update_layout(
        title="Pontuação de Risco por Categoria",
        yaxis_title="Risco (0 = Baixo, 1 = Alto)",
        xaxis_title="Categoria"
    )
    
    st.plotly_chart(fig_risk, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🔍 Áreas de Vulnerabilidade")
        if 'robustness_details' in giskard_results.details:
            vulnerability_areas = giskard_results.details['robustness_details'].get('vulnerability_areas', [])
            if vulnerability_areas:
                for area in vulnerability_areas[:5]:  # Show top 5
                    st.markdown(f"• {area}")
            else:
                st.markdown("✅ Nenhuma vulnerabilidade significativa detectada")
    
    with col2:
        st.markdown("##### ⚖️ Vieses Detectados")
        if 'bias_details' in giskard_results.details:
            detected_biases = giskard_results.details['bias_details'].get('detected_biases', [])
            if detected_biases:
                for bias in detected_biases[:5]:  # Show top 5
                    st.markdown(f"• {bias}")
            else:
                st.markdown("✅ Nenhum viés significativo detectado")
    
    st.markdown("##### 💡 Recomendações GISKARD")
    if giskard_results.recommendations:
        for rec in giskard_results.recommendations:
            st.markdown(f"• {rec}")
    else:
        st.markdown("✅ Sistema apresenta boa qualidade geral")

def render_comparison_dashboard(ragas_results, giskard_results):
    st.markdown("#### ⚖️ Comparação RAGAS vs GISKARD")
    
    if not ragas_results or not giskard_results:
        st.warning("Dados insuficientes para comparação")
        return
    
    ragas_avg = sum(r.overall_score for r in ragas_results) / len(ragas_results)
    giskard_avg = (giskard_results.robustness_score + giskard_results.performance_score + 
                   giskard_results.consistency_score + giskard_results.bias_score) / 4
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("RAGAS Overall", f"{ragas_avg:.3f}")
    
    with col2:
        st.metric("GISKARD Overall", f"{giskard_avg:.3f}")
    
    with col3:
        diff = ragas_avg - giskard_avg
        st.metric("Diferença", f"{diff:.3f}", delta=f"{diff:.3f}")
    
    comparison_data = {
        "Framework": ["RAGAS", "GISKARD"],
        "Score": [ragas_avg, giskard_avg]
    }
    
    fig_comparison = px.bar(
        comparison_data,
        x="Framework",
        y="Score",
        title="Comparação de Scores Gerais",
        color="Framework"
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    st.markdown("##### 📊 Comparação Detalhada")
    
    if ragas_results:
        ragas_avg_faithfulness = sum(r.faithfulness for r in ragas_results) / len(ragas_results)
        ragas_avg_relevancy = sum(r.answer_relevancy for r in ragas_results) / len(ragas_results)
        ragas_avg_precision = sum(r.context_precision for r in ragas_results) / len(ragas_results)
        ragas_avg_recall = sum(r.context_recall for r in ragas_results) / len(ragas_results)
    else:
        ragas_avg_faithfulness = ragas_avg_relevancy = ragas_avg_precision = ragas_avg_recall = 0
    
    comparison_df = pd.DataFrame({
        "Métrica": [
            "Qualidade da Resposta",
            "Robustez do Sistema",
            "Precisão do Contexto",
            "Consistência",
            "Ausência de Viés"
        ],
        "RAGAS": [
            ragas_avg_relevancy,
            "-",
            ragas_avg_precision,
            "-",
            "-"
        ],
        "GISKARD": [
            giskard_results.performance_score,
            giskard_results.robustness_score,
            "-",
            giskard_results.consistency_score,
            giskard_results.bias_score
        ],
        "Interpretação": [
            "Relevância das respostas às perguntas",
            "Resistência a variações de entrada",
            "Qualidade do contexto recuperado",
            "Estabilidade entre respostas similares",
            "Equidade e imparcialidade"
        ]
    })
    
    st.dataframe(comparison_df, use_container_width=True)

def render_insights_dashboard(ragas_results, giskard_results):
    st.markdown("#### 🔍 Insights e Recomendações Gerais")
    
    if ragas_results and giskard_results:
        ragas_score = sum(r.overall_score for r in ragas_results) / len(ragas_results)
        giskard_score = (giskard_results.robustness_score + giskard_results.performance_score + 
                        giskard_results.consistency_score + giskard_results.bias_score) / 4
        
        overall_health = (ragas_score + giskard_score) / 2
        
        health_level = "Excelente" if overall_health > 0.8 else \
                      "Bom" if overall_health > 0.6 else \
                      "Moderado" if overall_health > 0.4 else "Necessita Melhoria"
        
        health_color = "green" if health_level in ["Excelente", "Bom"] else \
                      "orange" if health_level == "Moderado" else "red"
        
        st.markdown(f"### 🏥 Saúde Geral do Sistema: :{health_color}[{health_level}] ({overall_health:.3f})")
    
    st.markdown("### 🎯 Recomendações Prioritárias")
    
    priority_recommendations = []
    
    if ragas_results:
        avg_faithfulness = sum(r.faithfulness for r in ragas_results) / len(ragas_results)
        avg_relevancy = sum(r.answer_relevancy for r in ragas_results) / len(ragas_results)
        
        if avg_faithfulness < 0.6:
            priority_recommendations.append({
                "priority": "Alta",
                "area": "Faithfulness",
                "issue": "Respostas contêm informações não suportadas pelo contexto",
                "action": "Revisar prompts de geração e implementar verificação de fatos mais rigorosa"
            })
        
        if avg_relevancy < 0.6:
            priority_recommendations.append({
                "priority": "Alta",
                "area": "Relevância",
                "issue": "Respostas não abordam adequadamente as perguntas",
                "action": "Melhorar compreensão da pergunta e foco da resposta"
            })
    
    if giskard_results:
        if giskard_results.robustness_score < 0.6:
            priority_recommendations.append({
                "priority": "Média",
                "area": "Robustez",
                "issue": "Sistema sensível a variações de entrada",
                "action": "Implementar normalização de entrada e testes de stress"
            })
        
        if giskard_results.bias_score < 0.6:
            priority_recommendations.append({
                "priority": "Alta",
                "area": "Viés",
                "issue": "Vieses detectados nas respostas",
                "action": "Revisar dados de treinamento e implementar checks de equidade"
            })
    
    if priority_recommendations:
        for i, rec in enumerate(priority_recommendations, 1):
            priority_color = "red" if rec["priority"] == "Alta" else \
                           "orange" if rec["priority"] == "Média" else "green"
            
            with st.expander(f"🎯 Recomendação {i}: {rec['area']} (Prioridade {rec['priority']})"):
                st.markdown(f"**Problema**: {rec['issue']}")
                st.markdown(f"**Ação Recomendada**: {rec['action']}")
    else:
        st.success("✅ Sistema apresenta boa qualidade geral. Mantenha monitoramento contínuo.")


def render_evaluation_runner():
    st.markdown("### 🧪 Executar Avaliações")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        run_ragas = st.button("🎯 Executar RAGAS", use_container_width=True)
    
    with col2:
        run_giskard = st.button("🛡️ Executar GISKARD", use_container_width=True)
    
    with col3:
        run_both = st.button("🚀 Executar Ambos", use_container_width=True)
    
    with st.expander("⚙️ Configurações de Avaliação"):
        col1, col2 = st.columns(2)
        
        with col1:
            max_questions = st.selectbox("Número de perguntas", [3, 5, 10], index=1)
            include_stress_tests = st.checkbox("Incluir testes de stress", value=True)
        
        with col2:
            evaluation_timeout = st.number_input("Timeout (segundos)", min_value=30, max_value=300, value=120)
            detailed_analysis = st.checkbox("Análise detalhada", value=True)
    
    return {
        "run_ragas": run_ragas,
        "run_giskard": run_giskard,
        "run_both": run_both,
        "settings": {
            "max_questions": max_questions,
            "include_stress_tests": include_stress_tests,
            "evaluation_timeout": evaluation_timeout,
            "detailed_analysis": detailed_analysis
        }
    }

def display_evaluation_progress(current_step: str, total_steps: int, current_step_num: int):
    progress = current_step_num / total_steps
    st.progress(progress)
    st.text(f"Passo {current_step_num}/{total_steps}: {current_step}")

def show_evaluation_results_summary(ragas_results, giskard_results, execution_time: float):
    st.markdown("### 📈 Resumo dos Resultados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if ragas_results:
            ragas_avg = sum(r.overall_score for r in ragas_results) / len(ragas_results)
            st.metric("RAGAS Score", f"{ragas_avg:.3f}")
        else:
            st.metric("RAGAS Score", "N/A")
    
    with col2:
        if giskard_results:
            giskard_avg = (giskard_results.robustness_score + giskard_results.performance_score + 
                          giskard_results.consistency_score + giskard_results.bias_score) / 4
            st.metric("GISKARD Score", f"{giskard_avg:.3f}")
        else:
            st.metric("GISKARD Score", "N/A")
    
    with col3:
        st.metric("Tempo de Execução", f"{execution_time:.1f}s")
    
    if ragas_results and giskard_results:
        st.markdown("#### 💡 Insights Rápidos")
        
        issues = []
        if ragas_avg < 0.7:
            issues.append("RAGAS indica problemas de qualidade de resposta")
        if giskard_results.overall_risk_score > 0.5:
            issues.append("GISKARD indica riscos elevados de robustez/viés")
        
        if issues:
            for issue in issues:
                st.warning(f"⚠️ {issue}")
        else:
            st.success("✅ Sistema apresenta boa qualidade geral")