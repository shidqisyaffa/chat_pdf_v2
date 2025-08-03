import sqlite3
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    def __init__(self, db_path="pdf_chat.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
            
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2]
            }
        return None
        
    def save_chat_message(self, user_id: int, message_type: str, content: str, sources: str = None):
        """Save chat message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO chat_history (user_id, message_type, content, sources) VALUES (?, ?, ?, ?)",
            (user_id, message_type, content, sources)
        )
        
        conn.commit()
        conn.close()
        
    def get_user_chat_history(self, user_id: int, limit: int = 50) -> List[Dict]: 
        """Get user's chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT message_type, content, sources FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        chat_history = []
        for message_type, content, sources_json in reversed(results):
            message = {
                "type": message_type,
                "content": content,
                "sources": json.loads(sources_json) if sources_json else None
            }
            chat_history.append(message)
                
        return chat_history
        
    def save_document(self, user_id: int, filename: str, file_hash: str):
        """Save document information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if document already exists for this user
        cursor.execute(
            "SELECT id FROM documents WHERE user_id = ? AND file_hash = ?",
            (user_id, file_hash)
        )
        
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO documents (user_id, filename, file_hash) VALUES (?, ?, ?)",
                (user_id, filename, file_hash)
            )
            
        conn.commit()
        conn.close()
        
    def get_user_documents(self, user_id: int) -> List[Dict]:
        """Get user's uploaded documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT filename, file_hash, uploaded_at FROM documents WHERE user_id = ? ORDER BY uploaded_at DESC",
            (user_id,)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'filename': row[0],
                'file_hash': row[1],
                'uploaded_at': row[2]
            }
            for row in results
        ]
        
    def clear_user_chat_history(self, user_id: int):
        """Clear user's chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()