from autogen import OpenAIWrapper
import llm_configs as config

def call_llm_for_enhancement(simple_desc):
    """
    Internal function to call LLM for persona expansion.
    Separated for easier mocking in tests.
    """
    if not simple_desc:
        return ""
        
    # 使用預設的 GLM 配置
    client = OpenAIWrapper(config_list=config.config_list_glm)
    
    prompt = f"""
    用戶想設定一個角色：『{simple_desc}』。
    請幫我把這個簡單描述擴寫成一段詳細的 System Prompt。
    
    要求：
    1. 包含具體的性格特徵（優點與缺點）。
    2. 定義說話方式與口癖（例如：喜歡冷嘲熱諷、講話帶點古風、或是喜歡用全大寫）。
    3. 增加一些背景設定，讓角色更有深度。
    4. 請直接輸出擴寫後的設定文字，不要有任何前言或結語（如「好的，這是您的設定」）。
    5. 繁體中文輸出。
    """
    
    response = client.create(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    
    return client.extract_text_or_completion_object(response)[0]

def enhance_persona(simple_desc):
    """
    Public API to enhance a simple character description.
    """
    if not simple_desc.strip():
        return ""
        
    try:
        enhanced_text = call_llm_for_enhancement(simple_desc)
        return enhanced_text.strip()
    except Exception as e:
        print(f"Error enhancing persona: {e}")
        return simple_desc # 回退到原始描述
