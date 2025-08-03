import streamlit as st
from typing import Optional, Dict
from .database import DatabaseManager

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user account"""
        return self.db_manager.create_user(username, email, password)
        
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user credentials"""
        return self.db_manager.authenticate_user(username, password)
        
    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        if "app_state" in st.session_state:
            del st.session_state.app_state
        if "chat_history" in st.session_state:
            del st.session_state.chat_history