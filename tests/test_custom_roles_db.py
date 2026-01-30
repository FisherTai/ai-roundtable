import pytest
import sqlite3
import os
from database import DatabaseManager

def test_custom_roles_table_creation(tmp_path):
    """Test if custom_roles table is created on initialization."""
    db_path = tmp_path / "test_roles.db"
    db_manager = DatabaseManager(str(db_path))
    
    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_roles';")
        assert cursor.fetchone() is not None

def test_add_custom_role(tmp_path):
    """Test adding a custom role."""
    db_path = tmp_path / "test_roles.db"
    db_manager = DatabaseManager(str(db_path))
    
    role_id = db_manager.add_custom_role(
        name="Angry Chef",
        description="A furious chef who shouts.",
        avatar="👨‍🍳",
        source_type="manual"
    )
    assert role_id is not None
    assert role_id > 0

def test_get_custom_roles(tmp_path):
    """Test retrieving custom roles."""
    db_path = tmp_path / "test_roles.db"
    db_manager = DatabaseManager(str(db_path))
    
    db_manager.add_custom_role("Chef", "Cooks food", "👨‍🍳", "manual")
    db_manager.add_custom_role("Cat", "Meows", "🐱", "import")
    
    roles = db_manager.get_custom_roles()
    assert len(roles) == 2
    assert roles[0]["name"] == "Chef"
    assert roles[1]["name"] == "Cat"

def test_delete_custom_role(tmp_path):
    """Test deleting a custom role."""
    db_path = tmp_path / "test_roles.db"
    db_manager = DatabaseManager(str(db_path))
    
    role_id = db_manager.add_custom_role("Chef", "Cooks food", "👨‍🍳", "manual")
    roles_before = db_manager.get_custom_roles()
    assert len(roles_before) == 1
    
    db_manager.delete_custom_role(role_id)
    roles_after = db_manager.get_custom_roles()
    assert len(roles_after) == 0
