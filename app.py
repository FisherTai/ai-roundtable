import streamlit as st
import autogen
import llm_configs as config 
import role_config as role
from database import DatabaseManager
from utils.persona_enhancer import enhance_persona
from utils.png_parser import parse_tavern_card
from utils.agent_factory import create_agent

# ==========================================
# 初始化資料庫與常數
# ==========================================
db = DatabaseManager("history.db")

# 內建角色清單 (用於快速選取)
BUILTIN_ROLES = {
    "🔥 FireMage": {"name": "FireMage", "desc": role.mage.system_message},
    "🛡️ IronWarrior": {"name": "IronWarrior", "desc": role.warrior.system_message},
    "💰 SneakyThief": {"name": "SneakyThief", "desc": role.thief.system_message},
}

# ==========================================
# Streamlit 介面邏輯
# ==========================================
st.set_page_config(page_title="AI 圓桌會議 POC", page_icon="⚔️", layout="wide")
st.title("⚔️ AI 冒險者公會 (AutoGen 版)")
st.caption("Backend: Microsoft AutoGen | Frontend: Streamlit")

# --- 側邊欄：角色管理 ---
with st.sidebar:
    st.header("🎭 角色管理中心")
    
    with st.expander("➕ 新增自定義角色", expanded=False):
        tab1, tab2 = st.tabs(["📝 手動填寫", "🖼️ 上傳角色卡"])
        
        with tab1:
            with st.form("add_role_form"):
                new_name = st.text_input("角色名稱", placeholder="例如：憤怒的廚師")
                new_desc = st.text_area("性格描述 (System Prompt)", placeholder="簡單輸入或點擊增強")
                
                if st.form_submit_button("✨ AI 增強人設 (自動填入)"):
                    if new_name or new_desc:
                        with st.spinner("AI 正在編織人設..."):
                            input_text = new_name if not new_desc else new_desc
                            enhanced = enhance_persona(input_text)
                            st.info("人設已增強！請再次確認後提交。")
                            # 這裡由於 Streamlit form 的限制，無法直接更新 text_area
                            # 我們提示使用者這是一個預覽，或是改用非 form 結構
                            st.text_area("AI 建議人設 (請複製到上方)：", value=enhanced, height=150)
                    else:
                        st.warning("請先輸入名稱或簡單描述。")
                
                new_avatar = st.text_input("頭像 Emoji", value="🤖")
                
                if st.form_submit_button("💾 儲存角色"):
                    if new_name and new_desc:
                        db.add_custom_role(new_name, new_desc, new_avatar, "manual")
                        st.success(f"角色 {new_name} 已儲存！")
                        st.rerun()
                    else:
                        st.error("名稱與描述不能為空。")

        with tab2:
            uploaded_file = st.file_uploader("選擇 TavernAI V2 PNG 角色卡", type="png")
            if uploaded_file is not None:
                card_data = parse_tavern_card(uploaded_file)
                if card_data:
                    st.success(f"成功讀取角色：{card_data['name']}")
                    st.text_area("解析出的設定：", value=card_data['description'], height=100)
                    if st.button("📥 匯入此角色"):
                        db.add_custom_role(card_data['name'], card_data['description'], "🖼️", "import")
                        st.success("角色已匯入！")
                        st.rerun()
                else:
                    st.error("解析失敗，請確認檔案格式。")

    st.divider()
    st.subheader("👥 現有角色列表")
    custom_roles = db.get_custom_roles()
    if custom_roles:
        for r in custom_roles:
            col1, col2 = st.columns([4, 1])
            col1.write(f"{r['avatar']} **{r['name']}**")
            if col2.button("🗑️", key=f"del_{r['id']}"):
                db.delete_custom_role(r['id'])
                st.rerun()
    else:
        st.caption("尚無自定義角色")

# 初始化 Session State
if "selected_agents" not in st.session_state:
    st.session_state.selected_agents = list(BUILTIN_ROLES.keys())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 主畫面：圓桌會議配置 ---
st.divider()
st.subheader("⚙️ 會議配置")

# 快捷按鈕區
col1, col2, col3 = st.columns([1, 1, 4])
if col1.button("🛡️ 載入經典三人組"):
    st.session_state.selected_agents = list(BUILTIN_ROLES.keys())
    st.rerun()
if col2.button("🧹 清空選擇"):
    st.session_state.selected_agents = []
    st.rerun()

# 組合所有可選角色
custom_roles = db.get_custom_roles()
available_options = list(BUILTIN_ROLES.keys()) + [f"{r['avatar']} {r['name']}" for r in custom_roles]
selected_names = st.multiselect("參與成員 (從下方列表挑選，至少需 2 位)", options=available_options, default=st.session_state.selected_agents)
st.session_state.selected_agents = selected_names

# 輸入框
initial_msg = st.text_input("丟給他們一個任務/話題：", "前面有個上鎖的寶箱，我們該怎麼辦？")

if st.button("🚀 開始爭論 (Run Simulation)"):
    if len(selected_names) < 2:
        st.error("請至少選擇 2 位角色進行對話。")
    else:
        with st.spinner("AI 正在七嘴八舌討論中..."):
            
            # --- 動態建立 Agent 清單 ---
            active_agents = []
            # 加入 User Proxy
            active_agents.append(role.user_proxy)
            
            for sn in selected_names:
                # 判斷是內建還是自定義
                if sn in BUILTIN_ROLES:
                    r_data = BUILTIN_ROLES[sn]
                    active_agents.append(create_agent(r_data['name'], r_data['desc']))
                else:
                    # 從自定義角色中找
                    r_name = sn.split(" ", 1)[1] if " " in sn else sn
                    # 重新取得最新角色列表以確保資料同步
                    current_custom = db.get_custom_roles()
                    r_data = next(r for r in current_custom if r['name'] == r_name)
                    active_agents.append(create_agent(r_data['name'], r_data['description']))
            
            # 建立群組聊天
            groupchat = autogen.GroupChat(
                agents=active_agents, 
                messages=[], 
                max_round=len(active_agents) * 2
            )
            manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=config.llm_config)

            # --- 啟動 AutoGen ---
            role.user_proxy.initiate_chat(manager, message=initial_msg)

            # 把結果存入 session state
            st.session_state.chat_history = groupchat.messages
            
            # --- 自動存入資料庫 ---
            agent_names = [a.name for a in active_agents]
            session_id = db.create_session(title=initial_msg[:50], agents=agent_names)
            for msg in groupchat.messages:
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

