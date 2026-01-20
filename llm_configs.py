import os
from dotenv import load_dotenv

# ==========================================
# 1. 基礎模型來源 (The Providers)
# ==========================================

# 1. 載入環境變數
#這行程式碼會去找你專案裡的 .env 檔，把裡面的設定載入到系統環境中
load_dotenv() 

# 2. 讀取 Key
# 使用 os.getenv，如果以後你把程式部署到雲端 (如 Heroku/Vercel/Docker)，
# 就算沒有 .env 檔，直接在雲端後台設環境變數，這行程式也能跑
nano_key = os.getenv("NANO_API_KEY")

#注意點：config_list的陣列是備援機制，
#如果第一個模型失敗，會自動切換到第二個模型
#因此如果要讓每個人用不同的模型，
#需要為每個模型建立一個config_list

# GLM-4
config_list_glm = [
    {
        "model": "zai-org/glm-4.7",
        "api_key": nano_key,
        "base_url": "https://nano-gpt.com/api/v1"
    }
]

# Amoral
config_list_amoral = [
    {
        "model": "soob3123/amoral-gemma3-27B-v2",
        "api_key": nano_key,
        "base_url": "https://nano-gpt.com/api/v1"
    }
]

# ==========================================
# 2. 角色專屬設定 (The Personas)
# ==========================================


llm_config = {
    "config_list": config_list_glm,
    "temperature": 0.7,
    "seed": 42,
}

# 給法師用的 (高智商，創造力中等)
mage_config = {
    "config_list": config_list_glm,
    "temperature": 0.5,
    "seed": 42,
}

# 給盜賊用的 (瘋狂，創造力高)
thief_config = {
    "config_list": config_list_amoral,
    "temperature": 0.9, # 讓它說話更不可預測
    "seed": 42,
}

# 給管理者用的 (需要邏輯清晰，選人準確)
manager_config = {
    "config_list": config_list_glm, # 用聰明的模型來當管理者
    "temperature": 0.1, # 越低越冷靜，選人邏輯越穩定
}
