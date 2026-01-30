import pytest
from unittest.mock import MagicMock, patch
import json
from utils.png_parser import parse_tavern_card

def test_parse_tavern_card_success():
    """Test parsing a valid TavernAI V2 card."""
    
    # Mock character data
    char_data = {
        "name": "Seraphina",
        "description": "A mystical elf.",
        "personality": "Wise and calm.",
        "scenario": "In a forest.",
        "first_mes": "Greetings, traveler.",
        "mes_example": "",
        "creator_notes": "",
        "system_prompt": "",
        "post_history_instructions": "",
        "alternate_greetings": [],
        "character_book": None,
        "tags": [],
        "creator": "Anon",
        "character_version": "",
        "extensions": {}
    }
    
    # TavernAI V2 format wraps the data in a "data" field inside "chara" key within the tEXt chunk
    # The key in tEXt chunk is usually "chara" and value is base64 encoded, 
    # BUT wait, TavernAI V2 spec says:
    # It uses a "chara" tEXt chunk containing base64 encoded JSON.
    # OR sometimes "ccv3" etc.
    # Let's verify standard TavernAI V2 implementation.
    # Actually, often the raw JSON text is just stored under 'chara' key in tEXt info.
    # Let's start with simple unencoded JSON string simulation which is common in some variants,
    # or implement the base64 decoding if that's the standard.
    
    # Standard V2 spec: 'chara' chunk contains base64 encoded string of the JSON.
    import base64
    json_str = json.dumps({"spec": "chara_card_v2", "spec_version": "2.0", "data": char_data})
    base64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    mock_image = MagicMock()
    # Simulate tEXt info dictionary
    mock_image.info = {"chara": base64_str}
    
    with patch("PIL.Image.open", return_value=mock_image):
        result = parse_tavern_card("dummy_path.png")
        
    assert result is not None
    assert result["name"] == "Seraphina"
    assert "mystical elf" in result["description"]
    assert "Wise and calm" in result["description"] # Description often combines personality

def test_parse_tavern_card_no_metadata():
    """Test parsing an image without relevant metadata."""
    mock_image = MagicMock()
    mock_image.info = {}
    
    with patch("PIL.Image.open", return_value=mock_image):
        result = parse_tavern_card("dummy_path.png")
        
    assert result is None

def test_parse_tavern_card_invalid_json():
    """Test parsing invalid metadata."""
    mock_image = MagicMock()
    import base64
    # Invalid JSON base64
    base64_str = base64.b64encode(b"invalid json").decode('utf-8')
    mock_image.info = {"chara": base64_str}
    
    with patch("PIL.Image.open", return_value=mock_image):
        result = parse_tavern_card("dummy_path.png")
        
    assert result is None
