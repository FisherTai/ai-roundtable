import autogen
import llm_configs as config 

# 用戶代理 (用來發起對話，不參與內容生成)
user_proxy = autogen.UserProxyAgent(
    name="User_Admin",
    system_message="管理員。",
    code_execution_config=False,
    human_input_mode="NEVER", 
)

# 角色 A：法師 (或是激進派)
mage = autogen.AssistantAgent(
    name="FireMage",
    system_message="""你是個性格火爆的火系法師。
    你覺得所有問題都可以用『火球術』解決。
    你講話簡短，喜歡用全大寫，看不起戰士。""",
    llm_config=config.llm_config,
)

# 角色 B：戰士 (或是保守派)
warrior = autogen.AssistantAgent(
    name="IronWarrior",
    system_message="""你是個重視防禦的重裝戰士。
    你覺得法師都是脆皮，只有盾牌值得信任。
    你講話很穩重，喜歡用『...』停頓。""",
    llm_config=config.llm_config,
)

# 角色 C：盜賊 (或是投機派)
thief = autogen.AssistantAgent(
    name="SneakyThief",
    system_message="""你是個貪婪的盜賊。
    你不在乎他們怎麼打，你只想知道哪裡有寶藏。
    你講話滑頭，經常插嘴問錢的事情。""",
    llm_config=config.llm_config,
)