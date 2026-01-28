from database import DatabaseManager
import os

# 定義測試資料庫名稱
db_name = "manual_test.db"

# 確保乾淨的開始
if os.path.exists(db_name):
    os.remove(db_name)

print("--- 開始手動驗收測試 ---")

# 1. 初始化資料庫
db = DatabaseManager(db_name)
print("1. 資料庫初始化成功")

# 2. 建立場次
sid = db.create_session("手動測試場次", ["AI 助理", "測試員"])
print(f"2. 建立場次成功，ID: {sid}")

# 3. 新增訊息
msg_id = db.add_message(sid, "AI 助理", "assistant", "這是一則手動測試訊息", model_name="test-model", parameters={"temp": 0.7})
print(f"3. 新增訊息成功，ID: {msg_id}")

# 4. 讀取並顯示資料
sessions = db.get_all_sessions()
messages = db.get_session_messages(sid)

print("\n--- 驗收結果 ---")
print(f"場次列表 (預期 1 筆): {len(sessions)} 筆")
print(f"場次標題: {sessions[0]['title']}")
print(f"訊息列表 (預期 1 筆): {len(messages)} 筆")
print(f"訊息內容: {messages[0]['content']}")
print(f"模型參數: {messages[0]['parameters']}")

# 清理
if os.path.exists(db_name):
    os.remove(db_name)
    print("\n測試資料庫已清理")
print("--- 測試結束 ---")
