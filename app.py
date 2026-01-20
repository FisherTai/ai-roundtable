import streamlit as st
import autogen
import llm_configs as config 
import role_config as role

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
        groupchat = autogen.GroupChat(
            agents=[role.user_proxy, role.mage, role.warrior, role.thief], 
            messages=[], 
            max_round=6  # 限制講 6 句話就好，省錢
        )
        
        # 建立管理員 (這是 AutoGen 的大腦，它決定誰下一個講話)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=config.llm_config)

        # --- 啟動 AutoGen ---
        # 這裡會卡住一下，直到對話跑完 (POC 階段先這樣做最簡單)
        role.user_proxy.initiate_chat(
            manager,
            message=initial_msg
        )

        # 把結果存入 session state
        st.session_state.chat_history = groupchat.messages

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

