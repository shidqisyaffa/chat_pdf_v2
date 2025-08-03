from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AppState:
    """Application state management"""
    vectorstore: Optional[object] = None
    openai_client: Optional[object] = None
    selected_model: Optional[str] = None
    available_models: List[str] = None
    processed_pdfs: List[str] = None
    connection_status: str = "Not connected"
    is_processing: bool = False
    processing_progress: float = 0.0
    temperature: float = 0.7
    max_tokens: int = 1000
    chunk_size: int = 2500
    chunk_overlap: int = 500
    similarity_k: int = 5
    all_chunks: List[dict] = None
    chat_history_loaded: bool = False
    
    def __post_init__(self):
        if self.available_models is None:
            self.available_models = []
        if self.processed_pdfs is None:
            self.processed_pdfs = []
        if self.all_chunks is None:
            self.all_chunks = []
            
    def reset_chat_history(self, user_id: int, db_manager):
        """Reset chat history for current user"""
        import streamlit as st
        
        
        db_manager.clear_user_chat_history(user_id)
        # UBAH: Gunakan format dictionary untuk pesan default
        st.session_state.chat_history = [
            {
                "type": "ai",
                "content": "Hello! I'm a PDF Assistant. Ask me anything about your PDFs or Documents",
                "sources": None
            }
        ]