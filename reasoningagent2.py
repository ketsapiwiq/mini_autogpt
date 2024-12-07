import os
from autogen import AssistantAgent, UserProxyAgent
from autogen.agentchat.contrib.reasoning_agent import ReasoningAgent, visualize_tree

# Configure the model
config_list = [{"model": "llama3.1:8b-instruct-q8_0", "api_key":"sdfsdf", "base_url": "http://192.168.1.50:11434/v1"}]

# Create a reasoning agent with beam search
reasoning_agent = ReasoningAgent(
    name="reason_agent",
    llm_config={"config_list": config_list},
    verbose=False,
    beam_size=1,  # Using beam size 1 for O1-style reasoning
    max_depth=3,
)

# Create a user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": False},
    max_consecutive_auto_reply=10,
)

question = "What is the expected maximum dice value if you can roll a 6-sided dice three times?"



user_proxy.initiate_chat(reasoning_agent, message=question)
import json
data = reasoning_agent._root.to_dict()
with open("reasoning_tree.json", "w") as f:
    json.dump(data, f)

# recover the node
new_node = ThinkNode.from_dict(json.load(open("reasoning_tree.json", "r")))
visualize_tree(reason_agent._root)


