import streamlit as st
from src.auth import AuthManager
from src.database import DatabaseManager
from src.pdf_processor import PDFProcessor
from src.lm_studio import LMStudioManager
from src.ui_components import UIComponents
from src.models import AppState
import os
from dotenv import load_dotenv

class PDFChatApp:
    def __init__(self):
        load_dotenv()
        self.setup_page_config()
        self.initialize_managers()
        
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Enhanced PDF Chat with Local model",
            page_icon="📚",
            layout="wide"
        )
        
    def initialize_managers(self):
        """Initialize all manager classes"""
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)
        self.pdf_processor = PDFProcessor()
        self.lm_studio_manager = LMStudioManager()
        self.lm_studio_manager.setup_client() 
        self.ui_components = UIComponents()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if "app_state" not in st.session_state:
            st.session_state.app_state = AppState()
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
        if "username" not in st.session_state:
            st.session_state.username = None

    def run_auth_flow(self):
        """Handle authentication flow"""
        st.header("🔐 PDF Chat Login System")

        tab1, tab2 = st.tabs(["Login", "Register"])

        # ======== TAB LOGIN ========
        with tab1:
            with st.form("login_form"):
                st.subheader("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")

                if submitted:
                    if username and password:
                        user = self.auth_manager.authenticate_user(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user['id']
                            st.session_state.username = user['username']

                            # ===============================
                            # Tambahkan: muat chat history
                            chat_history = self.db_manager.get_user_chat_history(user['id'])
                            if chat_history:
                                st.session_state.chat_history = chat_history
                            else:
                                st.session_state.chat_history = [
                                    {
                                        "type": "ai",
                                        "content": "Hello! I'm a PDF Assistant. Ask me anything about your PDFs or Documents.",
                                        "sources": None
                                    }
                                ]
                            # ===============================

                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.error("Please fill in all fields")

        # ======== TAB REGISTER ========
        with tab2:
            with st.form("register_form"):
                st.subheader("Register New Account")
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Choose Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register")

                if submitted:
                    if new_username and new_email and new_password and confirm_password:
                        if new_password == confirm_password:
                            if self.auth_manager.create_user(new_username, new_email, new_password):
                                st.success("Registration successful! Please login.")
                            else:
                                st.error("Username or email already exists")
                        else:
                            st.error("Passwords do not match")
                    else:
                        st.error("Please fill in all fields")
                        
    def run_main_app(self):
        """Run the main PDF chat application"""
        app_state = st.session_state.app_state
        
        # Header with logout button
        col1, col2 = st.columns([4, 1])
        with col1:
            st.header("🔍 Chat with PDF Documents using local Model")
        with col2:
            if st.button("Logout", type="secondary"):
                self.auth_manager.logout()
                st.rerun()
        
        st.markdown(f"**Welcome, {st.session_state.username}!**")
        
        # Load user's chat history
        if not hasattr(app_state, 'chat_history_loaded'):
            chat_history = self.db_manager.get_user_chat_history(st.session_state.user_id)
            if chat_history:
                st.session_state.chat_history = chat_history
            app_state.chat_history_loaded = True
        
        # Render sidebar
        self.ui_components.render_sidebar(
            app_state, 
            self.pdf_processor, 
            self.lm_studio_manager,
            st.session_state.user_id,
            self.db_manager
        )
        
        # Main chat interface
        if app_state.vectorstore and app_state.openai_client and app_state.selected_model:
            self.ui_components.render_chat_interface(
                app_state, 
                self.lm_studio_manager,
                st.session_state.user_id,
                self.db_manager
            )
        else:
            self.ui_components.display_welcome_message()
            
    def run(self):
        """Main application entry point"""
        self.initialize_session_state()
        
        if not st.session_state.authenticated:
            self.run_auth_flow()
        else:
            self.run_main_app()

if __name__ == "__main__":
    app = PDFChatApp()
    app.run()
    