import pytest
import os
import sqlite3
from database import DatabaseManager

def test_database_initialization(tmp_path):
    db_path = tmp_path / "test_history.db"
    db_manager = DatabaseManager(str(db_path))
    
    # Check if database file is created
    assert os.path.exists(db_path)
    
    # Check if tables exist
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions';")
    assert cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
    assert cursor.fetchone() is not None
    
    conn.close()

def test_crud_operations(tmp_path):
    db_path = tmp_path / "test_history.db"
    db_manager = DatabaseManager(str(db_path))
    
    # Create session
    agents = ["Agent A", "Agent B"]
    session_id = db_manager.create_session("Test Session", agents)
    assert session_id == 1
    
    # Add message
    msg_id = db_manager.add_message(
        session_id, "Agent A", "user", "Hello world", 
        model_name="glm-4", parameters={"temp": 0.7}, tokens=10
    )
    assert msg_id == 1
    
    # Get all sessions
    sessions = db_manager.get_all_sessions()
    assert len(sessions) == 1
    assert sessions[0]["title"] == "Test Session"
    assert sessions[0]["agents"] == '["Agent A", "Agent B"]'
    
    # Get messages
    messages = db_manager.get_session_messages(session_id)
    assert len(messages) == 1
    assert messages[0]["content"] == "Hello world"
    assert messages[0]["sender_name"] == "Agent A"
    assert messages[0]["model_name"] == "glm-4"
    
    # Delete session
    db_manager.delete_session(session_id)
    sessions_after_delete = db_manager.get_all_sessions()
    assert len(sessions_after_delete) == 0
    
    # Check if messages are cascaded deleted
    messages_after_delete = db_manager.get_session_messages(session_id)
    assert len(messages_after_delete) == 0
