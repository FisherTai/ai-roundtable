import streamlit as st
from database import DatabaseManager
import json

# 初始化資料庫
db = DatabaseManager("history.db")

st.set_page_config(page_title="歷史紀錄 - AI 圓桌會議", page_icon="📜")

st.title("📜 歷史對話紀錄")

# 讀取所有場次
sessions = db.get_all_sessions()

if not sessions:
    st.info("目前還沒有任何對話紀錄。")
else:
    # 側邊欄：場次選擇
    st.sidebar.header("場次列表")
    
    # 建立顯示用的標籤 (標題 + 時間)
    session_labels = {s['id']: f"{s['title']} ({s['start_time'][:16]})" for s in sessions}
    
    selected_session_id = st.sidebar.radio(
        "選擇場次",
        options=list(session_labels.keys()),
        format_func=lambda x: session_labels[x]
    )

    # 取得選定場次的資料
    selected_session = next(s for s in sessions if s['id'] == selected_session_id)
    messages = db.get_session_messages(selected_session_id)

    # 主畫面工具列
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"場次：{selected_session['title']}")
    with col2:
        # 刪除功能
        if st.button("🗑️ 刪除紀錄", use_container_width=True):
            db.delete_session(selected_session_id)
            st.rerun()
    with col3:
        st.write("") # 佔位

    # 匯出區塊
    st.write("---")
    export_col1, export_col2, export_col3 = st.columns(3)
    
    # 準備匯出內容
    export_data = {
        "session": selected_session,
        "messages": messages
    }
    
    # Markdown 轉換
    md_content = f"# 對話紀錄: {selected_session['title']}\n\n"
    md_content += f"- **時間**: {selected_session['start_time']}\n"
    md_content += f"- **參與者**: {selected_session['agents']}\n\n---\n\n"
    for m in messages:
        if m['sender_name'] != "User_Admin":
            md_content += f"### {m['sender_name']} ({m['role']})\n"
            if m['model_name']:
                md_content += f"> 模型: {m['model_name']}\n\n"
            md_content += f"{m['content']}\n\n"

    # 純文字轉換
    txt_content = f"對話紀錄: {selected_session['title']}\n"
    txt_content += f"時間: {selected_session['start_time']}\n"
    txt_content += "="*30 + "\n\n"
    for m in messages:
        if m['sender_name'] != "User_Admin":
            txt_content += f"[{m['sender_name']}]: {m['content']}\n\n"

    with export_col1:
        st.download_button("📥 匯出 Markdown", data=md_content, file_name=f"chat_{selected_session_id}.md")
    with export_col2:
        st.download_button("📥 匯出 JSON", data=json.dumps(export_data, indent=2, ensure_ascii=False), file_name=f"chat_{selected_session_id}.json")
    with export_col3:
        st.download_button("📥 匯出 TXT", data=txt_content, file_name=f"chat_{selected_session_id}.txt")

    st.write("---")

    # 顯示對話內容
    for msg in messages:
        if msg['sender_name'] != "User_Admin":
            # 簡單判斷頭像
            avatar = "🤖"
            name = msg['sender_name']
            if "FireMage" in name: avatar = "🔥"
            elif "IronWarrior" in name: avatar = "🛡️"
            elif "SneakyThief" in name: avatar = "💰"

            with st.chat_message(name, avatar=avatar):
                st.write(f"**{name}**: {msg['content']}")
                if msg['model_name']:
                    st.caption(f"Model: {msg['model_name']}")
