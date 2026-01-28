import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="history.db"):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    agents TEXT, -- JSON string of agent names
                    status TEXT DEFAULT 'active'
                )
            """)
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    sender_name TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_name TEXT,
                    parameters TEXT, -- JSON string of model parameters
                    tokens INTEGER,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            conn.commit()

    def create_session(self, title, agents=None):
        agents_json = json.dumps(agents) if agents else "[]"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (title, agents) VALUES (?, ?)",
                (title, agents_json)
            )
            conn.commit()
            return cursor.lastrowid

    def add_message(self, session_id, sender_name, role, content, model_name=None, parameters=None, tokens=None):
        params_json = json.dumps(parameters) if parameters else "{}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages 
                (session_id, sender_name, role, content, model_name, parameters, tokens) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, sender_name, role, content, model_name, params_json, tokens))
            conn.commit()
            return cursor.lastrowid

    def get_all_sessions(self):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions ORDER BY start_time DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_session_messages(self, session_id):
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM messages WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def delete_session(self, session_id):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            conn.commit()
