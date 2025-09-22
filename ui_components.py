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
    st.markdown("---")
    st.markdown("### 💬 Faça perguntas sobre seu documento")
    if user_file == "local_file":
        local_file_path = st.session_state.get('processed_file', 'local_data/geografo_proposta.pdf')
        file_display = f"📄 **Documento Atual:** {os.path.basename(local_file_path)} (arquivo local)"
    elif hasattr(user_file, 'name'):
        file_display = f"📄 **Documento Atual:** {user_file.name}"
        if hasattr(user_file, 'type') and user_file.type:
            file_display += f" ({user_file.type})"
    else:
        file_display = "📄 **Documento Atual:** Documento carregado"
    
    st.markdown(file_display)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input(
            'Digite sua pergunta:', 
            placeholder="como eh feito calculo de precipitacao? / quem eh o presidente do brasil?",
            disabled=not user_file,
            help="Pergunte qualquer coisa sobre o conteúdo do documento enviado"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ask_button = st.button("Perguntar", use_container_width=True)
    return question, ask_button


def render_answer_section(result):
    st.markdown("### 📝 Resposta")
    st.success(result['solution'])
    st.markdown("---")
