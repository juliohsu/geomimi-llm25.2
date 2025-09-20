import os
from typing import List, Dict, Any, Union
from pathlib import Path
import logging

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredExcelLoader,
    TextLoader
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiFormatDocumentLoader:
    
    def __init__(self):
        self.loaders = {
            "pdf": PyPDFLoader,
            "docx": Docx2txtLoader,
            "doc": Docx2txtLoader,
            "csv": CSVLoader,
            "xlsx": UnstructuredExcelLoader,
            "xls": UnstructuredExcelLoader,
            "txt": TextLoader,
            "md": TextLoader,
            "py": TextLoader,
            "js": TextLoader,
            "html": TextLoader,
            "xml": TextLoader,
        }
        
        self.text_formats = {"txt", "md", "py", "js", "html", "xml", "json", "yaml", "yml"}
    
    def get_file_extension(self, file_path: Union[str, Path]) -> str:
        return Path(file_path).suffix[1:].lower()
    
    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        extension = self.get_file_extension(file_path)
        return extension in self.loaders
    
    def load_document(self, file_path: Union[str, Path]) -> List[Document]:
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = self.get_file_extension(file_path)
        
        if not self.is_supported_format(file_path):
            raise ValueError(f"Unsupported file type: {extension}")
        
        logger.info(f"Loading document: {file_path} (format: {extension})")
        
        try:
            loader_class = self.loaders[extension]
            
            if extension in ["csv"]:
                loader = loader_class(str(file_path), encoding="utf-8")
            else:
                loader = loader_class(str(file_path))
            
            documents = loader.load()
            
            for doc in documents:
                doc.metadata.update({
                    "source": str(file_path),
                    "file_type": extension,
                    "file_name": file_path.name,
                    "file_size": file_path.stat().st_size if file_path.exists() else 0,
                })
            
            logger.info(f"Successfully loaded {len(documents)} document chunks from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise Exception(f"Failed to load document {file_path}: {str(e)}")
    
    def load_multiple_documents(self, file_paths: List[Union[str, Path]]) -> List[Document]:
        all_documents = []
        failed_files = []
        
        for file_path in file_paths:
            try:
                documents = self.load_document(file_path)
                all_documents.extend(documents)
            except Exception as e:
                logger.warning(f"Failed to load {file_path}: {str(e)}")
                failed_files.append(str(file_path))
        
        if failed_files:
            logger.warning(f"Failed to load {len(failed_files)} files: {failed_files}")
        
        logger.info(f"Successfully loaded {len(all_documents)} total document chunks from {len(file_paths) - len(failed_files)} files")
        return all_documents
    
    def load_directory(self, directory_path: Union[str, Path], recursive: bool = True) -> List[Document]:
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Invalid directory path: {directory_path}")
        
        pattern = "**/*" if recursive else "*"
        all_files = []
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and self.is_supported_format(file_path):
                all_files.append(file_path)
        
        logger.info(f"Found {len(all_files)} supported files in {directory_path}")
        
        return self.load_multiple_documents(all_files)
    
    def get_supported_extensions(self) -> List[str]:
        return list(self.loaders.keys())
    
    def get_document_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {"error": "File not found"}
        
        extension = self.get_file_extension(file_path)
        
        return {
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_extension": extension,
            "file_size": file_path.stat().st_size,
            "is_supported": self.is_supported_format(file_path),
            "loader_type": self.loaders.get(extension, "Unsupported").__name__ if extension in self.loaders else "Unsupported"
        }

def load_document(file_path: Union[str, Path]) -> List[Document]:
    loader = MultiFormatDocumentLoader()
    return loader.load_document(file_path)

MultiModalDocumentLoader = MultiFormatDocumentLoader

if __name__ == "__main__":
    loader = MultiFormatDocumentLoader()
    
    print("Supported file extensions:")
    print(loader.get_supported_extensions())
    
    # Example usage (uncomment to test with actual files)
    # documents = loader.load_document("sample.pdf")
    # print(f"Loaded {len(documents)} documents")
