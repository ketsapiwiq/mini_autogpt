import os
import logging
from typing import Optional, Dict, Any, List

import autogen
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('societyofminds.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create global user proxy and other agents for import compatibility
user_proxy = autogen.UserProxyAgent(
    "user_proxy",
    human_input_mode="NEVER",
    code_execution_config=False,
    default_auto_reply="",
    is_termination_msg=lambda x: True,
)

# Create a global model configuration and manager
model_config = {
    "model": os.getenv("LLM_MODEL", "llama3.1:8b-instruct-q8_0"),
    "api_key": os.getenv("LLM_API_KEY", ""),
    "base_url": os.getenv("LLM_BASE_URL", "http://192.168.1.50:11434/v1")
}

# Create a global group chat and manager
group_chat = autogen.GroupChat(
    agents=[user_proxy],
    messages=[],
    speaker_selection_method="round_robin",
    allow_repeat_speaker=False,
)

manager = autogen.GroupChatManager(
    groupchat=group_chat,
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config={"config_list": [model_config]},
)

def get_model_config() -> Dict[str, str]:
    """
    Retrieve model configuration from environment variables or default settings.
    """
    try:
        from autogen import config_list_from_json
        config_list = config_list_from_json("OAI_CONFIG_LIST")
        if config_list:
            return config_list[0]
    except Exception:
        pass
    
    return model_config

def create_assistant(model_config: Dict[str, Any]) -> autogen.AssistantAgent:
    """Create the main assistant agent."""
    return autogen.AssistantAgent(
        "inner-assistant",
        llm_config={"config_list": [model_config]},
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    )

def create_code_interpreter(work_dir: str = "coding") -> autogen.UserProxyAgent:
    """Create a code interpreter agent."""
    return autogen.UserProxyAgent(
        "inner-code-interpreter",
        human_input_mode="NEVER",
        code_execution_config={
            "work_dir": work_dir,
            "use_docker": False,
        },
        max_consecutive_auto_reply=5,
        default_auto_reply="",
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    )

def create_society_agent(
    assistant: autogen.AssistantAgent, 
    code_interpreter: autogen.UserProxyAgent, 
    model_config: Dict[str, Any], 
    max_rounds: int = 8
) -> SocietyOfMindAgent:
    """Create a Society of Mind Agent."""
    # Create group chat
    group_chat = autogen.GroupChat(
        agents=[assistant, code_interpreter],
        messages=[],
        speaker_selection_method="round_robin",
        allow_repeat_speaker=False,
        max_round=max_rounds,
    )
    
    # Create chat manager
    chat_manager = autogen.GroupChatManager(
        groupchat=group_chat,
        is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        llm_config={"config_list": [model_config]},
    )
    
    return SocietyOfMindAgent(
        "society_of_mind",
        chat_manager=chat_manager,
        llm_config={"config_list": [model_config]},
    )

def save_result(result: Any, problem: str):
    """
    Save the result of problem-solving to a file.
    """
    try:
        filename = f"societyofminds_result_{problem.replace(' ', '_')}.txt"
        with open(filename, 'w') as f:
            f.write(str(result))
        logger.info(f"Result saved to {filename}")
    except Exception as e:
        logger.error(f"Could not save result: {e}")

def solve_problems(
    problems: List[str], 
    work_dir: str = "coding", 
    max_rounds: int = 8
) -> List[Any]:
    """
    Solve complex reasoning problems using the Society of Minds approach.
    
    Args:
        problems (List[str]): The problems to solve.
        work_dir (str, optional): Working directory for code execution.
        max_rounds (int, optional): Maximum conversation rounds.
    
    Returns:
        List of results for each problem.
    """
    # Get model configuration
    current_model_config = get_model_config()
    
    # Create core agents
    assistant = create_assistant(current_model_config)
    code_interpreter = create_code_interpreter(work_dir)
    
    # Create Society of Mind agent
    society_agent = create_society_agent(
        assistant, 
        code_interpreter, 
        current_model_config, 
        max_rounds
    )
    
    # Solve problems
    results = []
    
    for problem in problems:
        try:
            logger.info(f"Initiating problem-solving for: {problem}")
            
            # Create a temporary user proxy for each problem
            problem_user_proxy = autogen.UserProxyAgent(
                "user_proxy",
                human_input_mode="NEVER",
                code_execution_config=False,
                default_auto_reply="",
                is_termination_msg=lambda x: True,
            )
            
            # Initiate chat and solve the problem
            result = society_agent.initiate_chat(problem_user_proxy, message=problem)
            
            # Save and collect results
            save_result(result, problem)
            results.append(result)
            
        except Exception as e:
            logger.error(f"Error solving problem: {problem}. Error: {e}")
            results.append(None)
    
    return results

def main():
    """
    Main function to demonstrate Society of Minds problem-solving.
    """
    # Example problems
    problems = [
        "On which days in 2024 was Microsoft Stock higher than $370?",
        "What is the expected maximum dice value if you can roll a 6-sided dice three times?"
    ]
    
    results = solve_problems(problems)
    
    for problem, result in zip(problems, results):
        print(f"Problem: {problem}")
        print(f"Result: {result}\n")

if __name__ == "__main__":
    main()
