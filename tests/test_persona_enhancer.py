import pytest
from unittest.mock import MagicMock, patch
from utils.persona_enhancer import enhance_persona

def test_enhance_persona_success():
    """Test persona enhancement with mocked LLM response."""
    # Mock return value of OpenAIWrapper or custom LLM caller
    mock_response = "這是一個擴寫後的豐富人設：性格火爆的法師..."
    
    # We patch the internal caller in persona_enhancer
    with patch("utils.persona_enhancer.call_llm_for_enhancement", return_value=mock_response):
        result = enhance_persona("憤怒的法師")
        
    assert result == mock_response
    assert "擴寫" in result

def test_enhance_persona_empty_input():
    """Test behavior with empty input."""
    result = enhance_persona("")
    assert result == ""
