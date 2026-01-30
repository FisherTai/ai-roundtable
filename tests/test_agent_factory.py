import pytest
import autogen
from utils.agent_factory import create_agent

def test_create_agent_assistant():
    """Test creating an AssistantAgent."""
    name = "CustomBot"
    system_message = "You are a helpful bot."
    
    agent = create_agent(name, system_message, "assistant")
    
    assert isinstance(agent, autogen.AssistantAgent)
    assert agent.name == name
    assert agent.system_message == system_message

def test_create_agent_user_proxy():
    """Test creating a UserProxyAgent."""
    name = "Admin"
    agent = create_agent(name, "Admin role", "user_proxy")
    
    assert isinstance(agent, autogen.UserProxyAgent)
    assert agent.name == name
