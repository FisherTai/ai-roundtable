# AI 圓桌會議 (Streamlit + AutoGen)

這是一個簡單的 POC：用 Streamlit 做前端，Microsoft AutoGen 負責角色對話，模擬冒險者公會的「圓桌辯論」。

## 功能簡介
- 多角色對話模擬的簡單 POC
- 一鍵啟動模擬對話，結果顯示在聊天視窗

## 環境需求
- Python 3.10+
- 有效的 API Key（NANO_API_KEY）

## 安裝
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 設定環境變數
建立 `.env`：
```
NANO_API_KEY=你的key
```

## 執行
```bash
streamlit run app.py
```

## 備註
- 模型與角色設定在 `llm_configs.py`、`role_config.py`
- 對話最大回合數可在 `app.py` 的 `max_round` 調整
