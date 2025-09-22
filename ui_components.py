import streamlit as st
from config import (
    PAGE_TITLE, PAGE_ICON, LAYOUT, SIDEBAR_STATE, 
    FILE_CATEGORIES, UPLOAD_PLACEHOLDER_TITLE, UPLOAD_PLACEHOLDER_TEXT
)
from utils import format_file_size
import os

def setup_page_config():
    st.set_page_config(
        page_title=PAGE_TITLE, 
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state=SIDEBAR_STATE
    )


def render_header():
    st.title(f"{PAGE_ICON} Geomimi - IA Geografo")
    st.subheader("Assistente Inteligente Especializada em Geografia")
    
    st.markdown("### **Arquitetura dos Agentes**")
    image_path = "screenshots/graph.png"
    if os.path.exists(image_path):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image_path, caption="Diagrama da Arquitetura Multi-Agente", use_container_width=True)
    else:
        st.info(" **Visualização da Arquitetura**: Diagrama do fluxo de agentes especializados e suas interações no sistema RAG")
    
    st.markdown("---")
    st.markdown("### **Funcionalidade Principais do Sistema**")
    
    # Destaques de funcionalidades
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🧠 **Sistema Multi-Agente**\n\nSupervisor orchestral com agentes especializados: Retriever (busca densa + rerank), Answerer (citações obrigatórias), Self-check (validação de evidências)")
    with col2:
        st.info("📄 **Processamento Inteligente**\n\nChunking avançado, embedding semântico e suporte multi-formato (PDF, Word, Excel, código)")
    with col3:
        st.info("🛡️ **IA Responsável**\n\nSelf-RAG com auto-verificação, Safety Agent para disclaimers médicos/legais e prevenção de aconselhamento perigoso")
    st.divider()

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="background: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h4>🔍 Sistema RAG Avançado</h4>
            <p>Envie documentos e faça perguntas inteligentes usando recuperação por IA.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 📋 Tipos de Arquivos Suportados")

        for category, formats in FILE_CATEGORIES.items():
            with st.expander(category, expanded=False):
                for fmt in formats:
                    st.markdown(f"• {fmt}")


def render_upload_section(document_loader):
    st.markdown("## 📤 Envio de Documento")
    st.info("📁 **Arraste e solte seu documento**\n\nSuportado: PDF, Word, Excel, Texto, Código")
    with st.expander("ℹ️ Ver Todos os Formatos Suportados", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Extensões suportadas:** {document_loader.get_supported_extensions_display()}")
        with col2:
            st.write(f"**Total de formatos:** {len(document_loader.get_supported_extensions())}")
    user_file = st.file_uploader(
        "Escolha um arquivo", 
        type=document_loader.get_supported_extensions(),
        help="Envie qualquer tipo de documento suportado.",
        label_visibility="collapsed"
    )
    return user_file


def render_file_analysis(file_info):
    st.markdown("### 📊 Análise do Arquivo")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**📄 Nome do Arquivo**")
        st.write(file_info['filename'])
    with col2:
        st.markdown("**📏 Tamanho**")
        size_display = format_file_size(file_info['size'])
        st.write(size_display)
    with col3:
        st.markdown("**🏷️ Tipo**")
        st.write(f".{file_info['extension'].upper()}")
    with col4:
        st.markdown("**📋 Status**")
        status_icon = "✅" if file_info['is_supported'] else "❌"
        status_text = "Suportado" if file_info['is_supported'] else "Não suportado"
        st.write(f"{status_icon} {status_text}")


def render_upload_placeholder():
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 10px; margin: 2rem 0;">
        <h3>{UPLOAD_PLACEHOLDER_TITLE}</h3>
        <p>{UPLOAD_PLACEHOLDER_TEXT}</p>
    </div>
    """, unsafe_allow_html=True)


def render_question_section(user_file):
    """Shows the question input section with integrated RAGAS and GISKARD evaluation"""
    st.markdown("---")
    st.markdown("### 💬 Faça perguntas sobre seu documento")
    
    # Handle both uploaded files and local files
    if user_file == "local_file":
        # For local files, get the path from session state
        local_file_path = st.session_state.get('processed_file', 'local_data/geografo_proposta.pdf')
        file_display = f"📄 **Documento Atual:** {os.path.basename(local_file_path)} (arquivo local)"
    elif hasattr(user_file, 'name'):
        # For uploaded files
        file_display = f"📄 **Documento Atual:** {user_file.name}"
        if hasattr(user_file, 'type') and user_file.type:
            file_display += f" ({user_file.type})"
    else:
        # Fallback for any other case
        file_display = "📄 **Documento Atual:** Documento carregado"
    
    st.markdown(file_display)
    
    # Create tabs for regular questions and evaluation
    tab1, tab2 = st.tabs(["🔍 Perguntas Livres", "📊 Avaliação Automática (RAGAS + GISKARD)"])
    
    with tab1:
        # Regular question input
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input(
                'Digite sua pergunta:', 
                placeholder="como eh feito calculo de precipitacao? / quem eh o presidente do brasil?",
                disabled=not user_file,
                help="Pergunte qualquer coisa sobre o conteúdo do documento enviado"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento
            ask_button = st.button("Perguntar", use_container_width=True)
    
    with tab2:
        # Evaluation section
        render_evaluation_section_content(user_file)
        question = ""
        ask_button = False
    
    return question, ask_button


def render_evaluation_section_content(user_file):
    """Render the evaluation section with RAGAS and GISKARD"""
    if not user_file:
        st.warning("📤 Envie um documento primeiro para executar a avaliação automática")
        return
    
    # Import evaluation components (conditional import to avoid errors if packages not installed)
    try:
        from evaluation import render_evaluation_section
        from rag_workflow import RAGWorkflow
        
        # Get RAG workflow instance
        if 'rag_workflow' not in st.session_state:
            st.session_state.rag_workflow = RAGWorkflow()
        
        rag_workflow = st.session_state.rag_workflow
        
        # Create a wrapper function for the RAG system
        def rag_system_func(question):
            """Wrapper function for RAG system to use in evaluation"""
            try:
                return rag_workflow.process_question(question)
            except Exception as e:
                st.error(f"Erro no sistema RAG: {str(e)}")
                return {"solution": "Erro na geração da resposta", "documents": []}
        
        # Render evaluation interface
        render_evaluation_section(rag_system_func)
        
    except ImportError as e:
        st.error(f"Erro ao importar módulos de avaliação: {str(e)}")
        render_fallback_evaluation_section()
    except Exception as e:
        st.error(f"Erro na seção de avaliação: {str(e)}")
        render_fallback_evaluation_section()


def render_fallback_evaluation_section():
    """Render a fallback evaluation section when full evaluation isn't available"""
    st.markdown("### 📊 Avaliação de Sistema RAG")
    st.info("""
    **Sistema de Avaliação RAGAS + GISKARD**
    
    Esta seção implementa avaliação automática do sistema RAG usando:
    
    **🎯 RAGAS (Retrieval Augmented Generation Assessment):**
    - **Faithfulness**: Mede consistência factual entre resposta e contexto
    - **Answer Relevancy**: Avalia relevância da resposta à pergunta  
    - **Context Precision**: Mede qualidade do contexto recuperado
    - **Context Recall**: Avalia cobertura do contexto necessário
    
    **🛡️ GISKARD (Robustness & Bias Testing):**
    - **Robustness**: Testa resistência a variações de entrada
    - **Bias Detection**: Identifica vieses nas respostas
    - **Performance**: Mede precisão e eficiência
    - **Consistency**: Avalia estabilidade entre respostas
    
    **📋 Dataset BHC (10 Perguntas Especializadas):**
    1. O que é o Balanço Hídrico Climatológico (BHC) e qual é sua finalidade?
    2. Qual é a equação simplificada do BHC sem considerar irrigação e ascensão capilar?
    3. O que representa a Evapotranspiração Potencial (ETP) e qual método é usado para calculá-la?
    4. Como é determinado o Armazenamento de Água no Solo (ARM) no BHC?
    5. Qual é a diferença entre Evapotranspiração Real (ETR) e Déficit Hídrico (DEF)?
    6. O que significa Excedente Hídrico (EXC) e quando ele ocorre?
    7. Quais são os índices climáticos calculados a partir do BHC e qual a função de cada um?
    8. Como o tipo de clima é classificado com base no Índice de Umidade (Iu)?
    9. Qual é o objetivo da etapa de coleta e preparação de dados no aplicativo Climate Index?
    10. Quais dados são obrigatórios para a execução do BHC no aplicativo e quais são opcionais?
    """)

def render_answer_section(result):
    st.markdown("### 📝 Resposta")
    st.success(result['solution'])
    st.markdown("---")
