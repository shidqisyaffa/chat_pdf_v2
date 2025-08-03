import streamlit as st
from PyPDF2 import PdfReader
import os
import pickle
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from typing import List, Dict, Optional, Tuple

class PDFProcessor:
    def __init__(self, vector_store_path="vectorstore"):
        self.vector_store_path = vector_store_path
        os.makedirs(vector_store_path, exist_ok=True)
        
    def get_document_hash(self, pdf_docs) -> str:
        """Create a hash of the PDF files to use as identifier for vectorstore"""
        hasher = hashlib.md5()
        for pdf in pdf_docs:
            pdf_bytes = pdf.read()
            hasher.update(pdf_bytes)
            pdf.seek(0)  # Reset file pointer after reading
        return hasher.hexdigest()
        
    def get_vector_store(self, text_chunks: List[Dict], embeddings) -> Optional[object]:
        """Create vector store from text chunks using local embeddings"""
        try:
            texts = [chunk["content"] for chunk in text_chunks]
            metadatas = [chunk["metadata"] for chunk in text_chunks]
            
            vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
            
            return vectorstore
        except Exception as e:
            st.error(f"Issue with reading the PDF/s or creating embeddings: {e}")
            st.error("Your file might be scanned or the embedding model might have issues.")
            return None
            
    def save_vectorstore(self, vectorstore, file_hash: str):
        """Save vectorstore to disk"""
        with open(f"{self.vector_store_path}/{file_hash}.pkl", "wb") as f:
            pickle.dump(vectorstore, f)
            
    def load_vectorstore(self, file_hash: str) -> Optional[object]:
        """Load vectorstore from disk"""
        try:
            path = f"{self.vector_store_path}/{file_hash}.pkl"
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return pickle.load(f)
        except Exception as e:
            st.warning(f"Error loading vectorstore: {e}")
        return None
        
    def process_pdfs(self, pdf_docs, app_state, user_id: int, db_manager):
        """Process uploaded PDFs and create vectorstore"""
        app_state.is_processing = True
        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()
        
        try:
            # Check if we have a cached vectorstore for these exact PDFs
            pdf_hash = self.get_document_hash(pdf_docs)
            cached_vectorstore = self.load_vectorstore(pdf_hash)
            
            if cached_vectorstore:
                app_state.vectorstore = cached_vectorstore
                app_state.processed_pdfs = [pdf.name for pdf in pdf_docs]
                status_text.success("Loaded vector store from cache!")
                progress_bar.progress(1.0)
                app_state.is_processing = False
                
                # Save document info to database
                for pdf in pdf_docs:
                    db_manager.save_document(user_id, pdf.name, pdf_hash)
                return
                
            # Process the PDFs
            app_state.all_chunks = []
            total_pdfs = len(pdf_docs)
            
            for i, pdf in enumerate(pdf_docs):
                status_text.text(f"Processing {pdf.name} ({i+1}/{total_pdfs})")
                
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=app_state.chunk_size,
                    chunk_overlap=app_state.chunk_overlap
                )
                
                pdf_reader = PdfReader(pdf)
                pdf_chunks = []
                total_pages = len(pdf_reader.pages)
                
                for j, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        page_chunks = text_splitter.split_text(page_text)
                        for chunk in page_chunks:
                            pdf_chunks.append({
                                "content": chunk,
                                "metadata": {
                                    "source": pdf.name,
                                    "page": j + 1
                                }
                            })
                    
                    progress = (i + (j + 1) / total_pages) / total_pdfs
                    progress_bar.progress(min(progress * 0.8, 0.8))
                
                app_state.all_chunks.extend(pdf_chunks)
            
            # Create embeddings
            status_text.text("Creating vector embeddings...")
            progress_bar.progress(0.9)
            
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            
            vectorstore = self.get_vector_store(app_state.all_chunks, embeddings)
            
            if vectorstore:
                app_state.vectorstore = vectorstore
                app_state.processed_pdfs = [pdf.name for pdf in pdf_docs]
                
                # Save vectorstore and document info
                try:
                    self.save_vectorstore(vectorstore, pdf_hash)
                    for pdf in pdf_docs:
                        db_manager.save_document(user_id, pdf.name, pdf_hash)
                except Exception as e:
                    status_text.warning(f"Note: Could not cache vectorstore: {str(e)}")
                
                status_text.success("PDFs processed successfully!")
                progress_bar.progress(1.0)
            else:
                status_text.error("Failed to create vectorstore")
                progress_bar.progress(0)
                
        except Exception as e:
            status_text.error(f"Error: {str(e)}")
            progress_bar.progress(0)
        finally:
            app_state.is_processing = False