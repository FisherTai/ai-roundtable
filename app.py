import streamlit as st
import autogen
import llm_configs as config 
import role_config as role
from database import DatabaseManager

# ==========================================
# 初始化資料庫
# ==========================================
db = DatabaseManager("history.db")

# ==========================================
# Streamlit 介面邏輯
# ==========================================
st.set_page_config(page_title="AI 圓桌會議 POC", page_icon="⚔️")
st.title("⚔️ AI 冒險者公會 (AutoGen 版)")
st.caption("Backend: Microsoft AutoGen | Frontend: Streamlit")

# 初始化 Session State 來存對話
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 輸入框
initial_msg = st.text_input("丟給他們一個任務/話題：", "前面有個上鎖的寶箱，我們該怎麼辦？")

if st.button("開始爭論 (Run Simulation)"):
    with st.spinner("AI 正在七嘴八舌討論中... (請稍等約 10-20 秒)"):
        
        # 建立群組聊天
        agents = [role.user_proxy, role.mage, role.warrior, role.thief]
        groupchat = autogen.GroupChat(
            agents=agents, 
            messages=[], 
            max_round=6  # 限制講 6 句話就好，省錢
        )
        
        # 建立管理員 (這是 AutoGen 的大腦，它決定誰下一個講話)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=config.llm_config)

        # --- 啟動 AutoGen ---
        role.user_proxy.initiate_chat(
            manager,
            message=initial_msg
        )

        # 把結果存入 session state
        st.session_state.chat_history = groupchat.messages
        
        # --- 自動存入資料庫 ---
        agent_names = [a.name for a in agents]
        session_id = db.create_session(title=initial_msg[:50], agents=agent_names)
        
        for msg in groupchat.messages:
            # 嘗試取得模型資訊 (從 config 中取得)
            model_name = config.llm_config["config_list"][0].get("model")
            
            db.add_message(
                session_id=session_id,
                sender_name=msg.get("name", "Unknown"),
                role=msg.get("role", "assistant"),
                content=msg.get("content", ""),
                model_name=model_name
            )

# ==========================================
# 顯示結果 (Rendering)
# ==========================================
st.divider()

if st.session_state.chat_history:
    for msg in st.session_state.chat_history:
        # 跳過系統管理員的發言，只看角色
        if msg['name'] != "User_Admin":
            
            # 設定一下頭像
            avatar = "🤖"
            if msg['name'] == "FireMage": avatar = "🔥"
            elif msg['name'] == "IronWarrior": avatar = "🛡️"
            elif msg['name'] == "SneakyThief": avatar = "💰"

            with st.chat_message(msg['name'], avatar=avatar):
                st.write(f"**{msg['name']}**: {msg['content']}")

else:
    st.info("尚未開始對話，請按上方按鈕。")

