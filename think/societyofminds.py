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
# Create a temporary user proxy for each problem
user_proxy = autogen.UserProxyAgent(
"user_proxy",
human_input_mode="NEVER",
code_execution_config=False,
default_auto_reply="",
is_termination_msg=lambda x: True,
)
group_chat = autogen.GroupChat(
agents=[self.assistant, self.code_interpreter],
messages=[],
speaker_selection_method="round_robin",
allow_repeat_speaker=False,
max_round=self.max_rounds,
)

manager = autogen.GroupChatManager(
            groupchat=group_chat,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
            llm_config={"config_list": [self.model_config]},
)

class SocietyOfMindsAgent:
    """
    A simplified Society of Minds agent system for complex problem-solving.
    """
    
    def __init__(
        self, 
        model_config: Optional[Dict[str, Any]] = None, 
        work_dir: str = "coding",
        max_rounds: int = 8
    ):
        """
        Initialize the Society of Minds Agent.
        
        Args:
            model_config (dict, optional): Configuration for the language model.
            work_dir (str, optional): Working directory for code execution.
            max_rounds (int, optional): Maximum conversation rounds.
        """
        self.logger = logger
        self.model_config = model_config or self._get_model_config()
        self.work_dir = work_dir
        self.max_rounds = max_rounds
        
        # Create core agents
        self.assistant = self._create_assistant()
        self.code_interpreter = self._create_code_interpreter()
        
        # Create Society of Mind specific components
        self.society_agent = self._create_society_agent()
    
    @classmethod
    def _get_model_config(cls) -> Dict[str, str]:
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
        
        return {
            "model": os.getenv("LLM_MODEL", "llama3.1:8b-instruct-q8_0"),
            "api_key": os.getenv("LLM_API_KEY", ""),
            "base_url": os.getenv("LLM_BASE_URL", "http://192.168.1.50:11434/v1")
        }
    
    def _create_assistant(self) -> autogen.AssistantAgent:
        """Create the main assistant agent."""
        return autogen.AssistantAgent(
            "inner-assistant",
            llm_config={"config_list": [self.model_config]},
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        )
    
    def _create_code_interpreter(self) -> autogen.UserProxyAgent:
        """Create a code interpreter agent."""
        return autogen.UserProxyAgent(
            "inner-code-interpreter",
            human_input_mode="NEVER",
            code_execution_config={
                "work_dir": self.work_dir,
                "use_docker": False,
            },
            max_consecutive_auto_reply=5,
            default_auto_reply="",
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        )
    
    def _create_society_agent(self) -> SocietyOfMindAgent:
        """Create a Society of Mind Agent."""
        # Create group chat
        group_chat = autogen.GroupChat(
            agents=[self.assistant, self.code_interpreter],
            messages=[],
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False,
            max_round=self.max_rounds,
        )
        
        # Create chat manager
        chat_manager = autogen.GroupChatManager(
            groupchat=group_chat,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
            llm_config={"config_list": [self.model_config]},
        )
        
        return SocietyOfMindAgent(
            "society_of_mind",
            chat_manager=chat_manager,
            llm_config={"config_list": [self.model_config]},
        )
    
    def solve_problem(self, problems: List[str]) -> List[Any]:
        """
        Solve complex reasoning problems using the Society of Minds approach.
        
        Args:
            problems (List[str]): The problems to solve.
        
        Returns:
            List of results for each problem.
        """
        results = []
        
        for problem in problems:
            try:
                self.logger.info(f"Initiating problem-solving for: {problem}")
                
                # Create a temporary user proxy for each problem
                user_proxy = autogen.UserProxyAgent(
                    "user_proxy",
                    human_input_mode="NEVER",
                    code_execution_config=False,
                    default_auto_reply="",
                    is_termination_msg=lambda x: True,
                )
                
                # Initiate chat and solve the problem
                result = self.society_agent.initiate_chat(user_proxy, message=problem)
                
                # Save and collect results
                self._save_result(result, problem)
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error solving problem: {problem}. Error: {e}")
                results.append(None)
        
        return results
    
    def _save_result(self, result: Any, problem: str):
        """
        Save the result of problem-solving to a file.
        """
        try:
            filename = f"societyofminds_result_{problem.replace(' ', '_')}.txt"
            with open(filename, 'w') as f:
                f.write(str(result))
            self.logger.info(f"Result saved to {filename}")
        except Exception as e:
            self.logger.error(f"Could not save result: {e}")

def main():
    """
    Main function to demonstrate Society of Minds problem-solving.
    """
    agent = SocietyOfMindsAgent()
    
    # Example problems
    problems = [
        "On which days in 2024 was Microsoft Stock higher than $370?",
        "What is the expected maximum dice value if you can roll a 6-sided dice three times?"
    ]
    
    results = agent.solve_problem(problems)
    
    for problem, result in zip(problems, results):
        print(f"Problem: {problem}")
        print(f"Result: {result}\n")

if __name__ == "__main__":
    main()
