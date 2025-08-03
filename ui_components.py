import streamlit as st
import json

class UIComponents:
    def render_sidebar(self, app_state, pdf_processor, lm_studio_manager, user_id, db_manager):
        """Render sidebar UI components"""
        with st.sidebar:
            st.subheader("📄 Your Documents")
            pdf_docs = st.file_uploader("Upload your PDFs here", accept_multiple_files=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Process PDFs", disabled=app_state.is_processing):
                    if pdf_docs:
                        pdf_processor.process_pdfs(pdf_docs, app_state, user_id, db_manager)
                    else:
                        st.warning("Please upload PDF files first")
                        
            with col2:
                if st.button("Clear Chat", disabled=app_state.is_processing):
                    app_state.reset_chat_history(user_id, db_manager)
                    st.success("Chat history cleared!")
                    
            # Show processed PDFs
            if app_state.processed_pdfs:
                st.success(f"{len(app_state.processed_pdfs)} PDFs processed:")
                for pdf in app_state.processed_pdfs:
                    st.info(f"📄 {pdf}")
                
                if app_state.vectorstore and app_state.openai_client and app_state.selected_model:
                    if st.button("Summarize Documents"):
                        with st.spinner("Generating document summary..."):
                            success, summary = lm_studio_manager.summarize_document(
                                app_state.all_chunks, 
                                app_state.selected_model,
                                app_state.temperature
                            )
                            if success:
                                st.success("Summary generated!")
                                st.info(summary)
                                # Save summary to chat history
                                db_manager.save_chat_message(user_id, "ai", f"Document Summary: {summary}")
                            else:
                                st.error(summary)
            
            # Show user's document history
            with st.expander("📚 Your Document History"):
                user_docs = db_manager.get_user_documents(user_id)
                if user_docs:
                    for doc in user_docs[:10]:  # Show last 10 documents
                        st.text(f"📄 {doc['filename']}")
                        st.caption(f"Uploaded: {doc['uploaded_at']}")
                else:
                    st.info("No documents uploaded yet")
            
            # LM Studio connection
            st.subheader("🔌 LM Studio Connection")
            
            connection_color = "green" if app_state.connection_status == "Connected" else "red"
            st.markdown(f"Status: <span style='color:{connection_color};font-weight:bold'>{app_state.connection_status}</span>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Connect", disabled=app_state.connection_status == "Connecting..."):
                    self.connect_to_lm_studio(app_state, lm_studio_manager)
            
            with col2:
                if st.button("Refresh Models", disabled=app_state.connection_status != "Connected"):
                    self.refresh_models(app_state, lm_studio_manager)
                    
            # Available models dropdown
            if app_state.available_models:
                selected_model = st.selectbox(
                    "Select a model",
                    options=app_state.available_models,
                    index=0 if app_state.available_models else None
                )
                if selected_model:
                    app_state.selected_model = selected_model
                    st.success(f"Selected model: {selected_model}")
            elif app_state.connection_status == "Connected":
                st.warning("No models available. Please load a model in LM Studio and click 'Refresh Models'.")
                
            # Model parameters
            if app_state.connection_status == "Connected":
                st.subheader("⚙️ Model Parameters")
                app_state.temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=app_state.temperature, step=0.1)
                app_state.max_tokens = st.slider("Max Tokens", min_value=100, max_value=4000, value=app_state.max_tokens, step=100)
            
            # Document processing parameters
            with st.expander("Advanced Document Settings"):
                app_state.chunk_size = st.number_input("Chunk Size", min_value=500, max_value=5000, value=app_state.chunk_size, step=100)
                app_state.chunk_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=1000, value=app_state.chunk_overlap, step=50)
                app_state.similarity_k = st.number_input("Retrieved Chunks", min_value=1, max_value=10, value=app_state.similarity_k, step=1)
                
    def connect_to_lm_studio(self, app_state, lm_studio_manager):
        """Connect to LM Studio API"""
        app_state.connection_status = "Connecting..."
        
        status_message = st.sidebar.empty()
        status_message.info("Connecting to LM Studio...")
        
        try:
            success, message = lm_studio_manager.check_connection()
            
            if success:
                app_state.openai_client = lm_studio_manager.setup_client()
                app_state.connection_status = "Connected"
                status_message.success("Connected to LM Studio!")
                
                success, models = lm_studio_manager.get_available_models()
                if success and models:
                    app_state.available_models = models
                else:
                    if isinstance(models, str):
                        st.sidebar.warning(models)
                    st.sidebar.warning("Connected to LM Studio, but no models are loaded")
            else:
                app_state.connection_status = message
                status_message.error(message)
        except Exception as e:
            app_state.connection_status = f"Error: {str(e)}"
            status_message.error(f"Error: {str(e)}")
            
    def refresh_models(self, app_state, lm_studio_manager):
        """Refresh list of available models"""
        status_message = st.sidebar.empty()
        status_message.info("Fetching available models...")
        
        try:
            success, models_or_error = lm_studio_manager.get_available_models()
            if success:
                app_state.available_models = models_or_error
                if models_or_error:
                    status_message.success(f"Found {len(models_or_error)} model(s)!")
                else:
                    status_message.warning("No models found. Please load a model in LM Studio.")
            else:
                status_message.error(models_or_error)
        except Exception as e:
            status_message.error(f"Error: {str(e)}")
            
    def render_chat_interface(self, app_state, lm_studio_manager, user_id, db_manager):
        """Render chat interface for user interaction"""
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {
                    "type": "ai",
                    "content": "Hello! I'm a PDF Assistant. Ask me anything about your PDFs or Documents",
                    "sources": None
                }
            ]

        # Display chat history
        for message in st.session_state.chat_history:
            role = "assistant" if message["type"] == "ai" else "user"
            with st.chat_message(role):
                st.markdown(message["content"])
                # BARU: Logika untuk menampilkan sumber dari riwayat
                if message["type"] == "ai" and message.get("sources"):
                    with st.expander("View sources"):
                        for i, source in enumerate(message["sources"]):
                            st.markdown(f"**Source {i+1}:** {source.get('source', 'N/A')} (Page {source.get('page', 'N/A')})")
                            content_preview = source.get('content', '')
                            st.text(content_preview[:200] + "..." if len(content_preview) > 200 else content_preview)
                            if i < len(message["sources"]) - 1:
                                st.divider()

        # Chat input
        user_query = st.chat_input("Enter your query about the documents...", 
                                 disabled=not app_state.vectorstore or not app_state.selected_model or not app_state.openai_client)
        
        if user_query and user_query.strip():
            db_manager.save_chat_message(user_id, "human", user_query)
            # UBAH: Tambahkan pesan pengguna ke history dalam format dictionary
            st.session_state.chat_history.append({"type": "human", "content": user_query})

            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                if not app_state.vectorstore:
                    response = "Please upload and process PDF documents first."
                    st.warning(response)
                    db_manager.save_chat_message(user_id, "ai", response)
                    # UBAH: Tambahkan pesan AI ke history dalam format dictionary
                    st.session_state.chat_history.append({"type": "ai", "content": response, "sources": None})
                else:
                    with st.spinner("Searching documents and generating response..."):
                        try:
                            docs = app_state.vectorstore.similarity_search(user_query, k=app_state.similarity_k)
                            
                            context_pieces = []
                            sources_info = []
                            for i, doc in enumerate(docs):
                                source = doc.metadata.get("source", "Unknown")
                                page = doc.metadata.get("page", "Unknown")
                                context_pieces.append(f"[Document: {source}, Page: {page}]\n{doc.page_content}")
                                sources_info.append({"source": source, "page": page, "content": doc.page_content})
                            
                            context = "\n\n".join(context_pieces)
                            
                            success, result = lm_studio_manager.get_response(
                                context, user_query, app_state.selected_model,
                                app_state.temperature, app_state.max_tokens
                            )
                            
                            if success:
                                st.markdown(result)
                                
                                # Tampilkan sumber untuk pesan baru (logika ini tetap sama)
                                with st.expander("View sources"):
                                    for i, doc in enumerate(docs):
                                        source = doc.metadata.get("source", "Unknown")
                                        page = doc.metadata.get("page", "Unknown")
                                        st.markdown(f"**Source {i+1}:** {source} (Page {page})")
                                        st.text(doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content)
                                        st.divider()
                                
                                sources_json = json.dumps(sources_info)
                                db_manager.save_chat_message(user_id, "ai", result, sources_json)
                                # UBAH: Tambahkan pesan AI baru ke history dengan sumbernya
                                st.session_state.chat_history.append({"type": "ai", "content": result, "sources": sources_info})
                            else:
                                st.error(result)
                                db_manager.save_chat_message(user_id, "ai", f"Error: {result}")
                                # UBAH: Tambahkan pesan error ke history
                                st.session_state.chat_history.append({"type": "ai", "content": f"Error: {result}", "sources": None})
                        except Exception as e:
                            error_msg = f"Error during processing: {str(e)}"
                            st.error(error_msg)
                            db_manager.save_chat_message(user_id, "ai", error_msg)
                            # UBAH: Tambahkan pesan error ke history
                            st.session_state.chat_history.append({"type": "ai", "content": error_msg, "sources": None})
    
                            
    def display_welcome_message(self):
        """Display welcome message when application starts"""
        st.markdown("""
        ## 📚 Welcome to the Enhanced PDF Chat Application!
        
        This application allows you to chat with your PDF documents using a local model running in LM Studio.
        
        ### ✨ Features:
        
        - **User Authentication** - Secure login system with personal document storage
        - **Chat History** - Your conversations are saved and restored between sessions
        - **Chat with multiple PDFs** - Upload and process multiple documents at once
        - **Local LLM integration** - Uses your own models through LM Studio
        - **Document summarization** - Get quick summaries of your documents
        - **Source citations** - See exactly where information comes from
        - **Persistent vector store** - Process documents once, use them many times
        - **Customizable parameters** - Adjust settings for optimal results
        - **Document History** - Track all your uploaded documents
        
        ### 🚀 Getting Started:
        
        1. **Upload PDF Documents** in the sidebar
        2. Click **Process PDFs** to extract and analyze the text
        3. **Connect to LM Studio** and select your model
        4. Start asking questions about your documents!
        
        ### 🔧 Prerequisites:
        
        - Make sure **LM Studio** is running with a loaded model
        - The application connects to LM Studio at http://127.0.0.1:1234
        """)