import autogen
import llm_configs as config

def create_agent(name, system_message, agent_type="assistant", llm_override=None):
    """
    Factory function to create an AutoGen agent.
    
    Args:
        name (str): Agent name.
        system_message (str): System prompt for the agent.
        agent_type (str): 'assistant' or 'user_proxy'.
        llm_override (dict): Optional LLM configuration override.
        
    Returns:
        autogen.Agent: The created agent instance.
    """
    llm_cfg = llm_override if llm_override else config.llm_config
    
    if agent_type == "assistant":
        return autogen.AssistantAgent(
            name=name,
            system_message=system_message,
            llm_config=llm_cfg
        )
    elif agent_type == "user_proxy":
        return autogen.UserProxyAgent(
            name=name,
            system_message=system_message,
            code_execution_config=False,
            human_input_mode="NEVER"
        )
    else:
        raise ValueError(f"Unsupported agent type: {agent_type}")
