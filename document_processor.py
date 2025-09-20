import streamlit as st
import time
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from config import CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR
from utils import get_file_key
from ui_components import render_file_analysis

class DocumentProcessor:
    
    def __init__(self, document_loader):
        self.document_loader = document_loader
        self.embedding_function = OpenAIEmbeddings()
    
    def process_local_file(self, file_path):
        if not file_path:
            return None
        
        current_file_key = f"local_{file_path}"
        if st.session_state.get('processed_file') == current_file_key:
            return st.session_state.get('retriever')
        
        try:
            return self._process_local_file_pipeline(file_path, current_file_key)
        except Exception as e:
            st.error(f"❌ Error processing local file: {str(e)}")
            st.info("💡 Please make sure the file exists and is in a supported format.")
            return None
    
    def _process_local_file_pipeline(self, file_path, current_file_key):
        st.markdown("### 🔄 Processing Status")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Carregando documento local...")
            progress_bar.progress(25)
            documents = self.document_loader.load_document(file_path)

            status_text.text("🔍 Extraindo conteúdo...")
            progress_bar.progress(50)
            st.success(f"✅ Conteúdo extraído com sucesso de {file_path}")

            progress_bar.progress(75)
            status_text.text("✂️ Dividindo em partes...")
            doc_splits = self._create_document_chunks(documents)

            progress_bar.progress(90)
            status_text.text("🧠 Criando embeddings...")
            chroma_db = self._create_vector_database(doc_splits)

            progress_bar.progress(100)
            status_text.text("✅ Processamento concluído!")
            
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            retriever = chroma_db.as_retriever()
            st.session_state.processed_file = current_file_key
            st.session_state.retriever = retriever
            
            print(f"Local file retriever created successfully: {retriever is not None}")
            print(f"Session state updated with file key: {current_file_key}")
            
            try:
                test_docs = retriever.invoke("test")
                print(f"Local file retriever test successful - {len(test_docs)} documents found")
            except Exception as test_error:
                print(f"Local file retriever test failed: {test_error}")
            
            return retriever
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            raise e
    
    def process_file(self, user_file):
        if user_file is None:
            return None
        
        current_file_key = get_file_key(user_file)
        if st.session_state.get('processed_file') == current_file_key:
            return st.session_state.get('retriever')
        
        try:
            return self._process_new_file(user_file, current_file_key)
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.info("💡 Please make sure your file is in a supported format and try again.")
            return None
    
    def _process_new_file(self, user_file, current_file_key):
        file_info = self.document_loader.get_upload_info(user_file)
        render_file_analysis(file_info)
        
        if not file_info['is_supported']:
            st.error(f"❌ Unsupported file type: .{file_info['extension']}")
            st.info(f"📋 Supported formats: {self.document_loader.get_supported_extensions_display()}")
            return None
        
        return self._execute_processing_pipeline(user_file, file_info, current_file_key)
    
    def _execute_processing_pipeline(self, user_file, file_info, current_file_key):
        st.markdown("### 🔄 Processing Status")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔄 Carregando documento...")
            progress_bar.progress(25)
            documents = self.document_loader.load_uploaded_file(user_file)

            status_text.text("🔍 Extraindo conteúdo...")
            progress_bar.progress(50)
            st.success(f"✅ Conteúdo extraído com sucesso de {file_info['filename']}")

            progress_bar.progress(75)
            status_text.text("✂️ Dividindo em partes...")
            doc_splits = self._create_document_chunks(documents)

            progress_bar.progress(90)
            status_text.text("🧠 Criando embeddings...")
            chroma_db = self._create_vector_database(doc_splits)

            progress_bar.progress(100)
            status_text.text("✅ Processamento concluído!")
            
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            retriever = chroma_db.as_retriever()
            st.session_state.processed_file = current_file_key
            st.session_state.retriever = retriever
            
            print(f"Retriever criado com sucesso: {retriever is not None}")
            print(f"Session state atualizado com a chave do arquivo: {current_file_key}")
            
            try:
                test_docs = retriever.invoke("test")
                print(f"Teste do retriever bem-sucedido - {len(test_docs)} documentos encontrados")
            except Exception as test_error:
                print(f"Teste do retriever falhou: {test_error}")
            
            return retriever
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            raise e
    
    def _create_document_chunks(self, documents):
        document_texts = [doc.page_content for doc in documents]
        
        splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE, 
            chunk_overlap=CHUNK_OVERLAP
        )
        doc_splits = splitter.create_documents(document_texts)
        
        for i, split in enumerate(doc_splits):
            original_doc_index = min(i, len(documents) - 1)
            split.metadata.update(documents[original_doc_index].metadata)
            split.metadata.update({
                "chunk_id": i,
                "total_chunks": len(doc_splits),
                "chunk_size": len(split.page_content)
            })
        
        return doc_splits
    
    def _create_vector_database(self, doc_splits):
        return Chroma.from_documents(
            documents=doc_splits, 
            collection_name=CHROMA_COLLECTION_NAME, 
            embedding=self.embedding_function,
            persist_directory=CHROMA_PERSIST_DIR
        )