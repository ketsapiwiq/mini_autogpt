import os
import autogen
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.reasoning_agent import ReasoningAgent, visualize_tree

# Configure the model
llm_config = {"model": "llama3.1:8b-instruct-q8_0", "api_key":"sdfsdf", "base_url": "http://192.168.1.50:11434/v1"}




assistant = autogen.AssistantAgent(
    "inner-assistant",
    llm_config=llm_config,
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

code_interpreter = autogen.UserProxyAgent(
    "inner-code-interpreter",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
    max_consecutive_auto_reply=5,
    default_auto_reply="",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
)

groupchat = autogen.GroupChat(
    agents=[assistant, code_interpreter],
    messages=[],
    speaker_selection_method="round_robin",  # With two agents, this is equivalent to a 1:1 conversation.
    allow_repeat_speaker=False,
    max_round=8,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
)


from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent  # noqa: E402

 # task = "On which days in 2024 was Microsoft Stock higher than $370?"
# task = "What is the expected maximum dice value if you can roll a 6-sided dice three times?"
society_of_mind_agent = SocietyOfMindAgent(
    "society_of_mind",
    chat_manager=manager,
    llm_config=llm_config,
)

user_proxy = autogen.UserProxyAgent(
    "user_proxy",
    human_input_mode="NEVER",
    code_execution_config=False,
    default_auto_reply="",
    is_termination_msg=lambda x: True,
)

# Invoke Society of Mind Agent
result = society_of_mind_agent.initiate_chat(user_proxy, message="Solve a complex reasoning problem")

# Add post-processing or logging after invoking societyofminds()
print("Society of Mind Agent Result:")
print(result)

# Optional: Save the result to a file
with open('societyofminds_result.txt', 'w') as f:
    f.write(str(result))

# Optional: Perform additional analysis or actions based on the result
if result:
    print("Society of Mind Agent completed its task successfully.")
else:
    print("Society of Mind Agent did not complete the task.")
