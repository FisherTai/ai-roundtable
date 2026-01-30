from PIL import Image
import json
import base64
import io

def parse_tavern_card(image_file):
    """
    Parses a TavernAI V2 PNG character card.
    
    Args:
        image_file: Path to the file or file-like object (BytesIO).
        
    Returns:
        dict: A dictionary with 'name' and 'description' keys, or None if parsing fails.
    """
    try:
        img = Image.open(image_file)
        img.load() # Ensure metadata is loaded
        
        # Check for 'chara' chunk (TavernAI V2)
        if "chara" not in img.info:
            return None
            
        encoded_data = img.info["chara"]
        decoded_data = base64.b64decode(encoded_data).decode("utf-8")
        json_data = json.loads(decoded_data)
        
        # Structure is usually: {"spec": "chara_card_v2", "spec_version": "2.0", "data": {...}}
        if "data" not in json_data:
            return None
            
        data = json_data["data"]
        
        name = data.get("name", "Unknown")
        
        # Construct a rich description from available fields
        description_parts = []
        if data.get("description"):
            description_parts.append(f"Description: {data.get('description')}")
        if data.get("personality"):
            description_parts.append(f"Personality: {data.get('personality')}")
        if data.get("scenario"):
            description_parts.append(f"Scenario: {data.get('scenario')}")
        if data.get("first_mes"):
            description_parts.append(f"First Message: {data.get('first_mes')}")
            
        full_description = "\n\n".join(description_parts)
        
        return {
            "name": name,
            "description": full_description,
            "avatar": image_file if isinstance(image_file, str) else "🖼️" # Keep path or generic icon
        }
        
    except Exception as e:
        print(f"Error parsing PNG card: {e}")
        return None
