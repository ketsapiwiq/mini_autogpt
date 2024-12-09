import os
import logging
from typing import Optional, Dict, Any

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

class SocietyOfMindsOrchestrator:
    """
    A comprehensive orchestrator for the Society of Minds agent system.
    Provides flexible configuration and task management.
    """
    
    def __init__(
        self, 
        model_config: Optional[Dict[str, Any]] = None, 
        work_dir: str = "coding",
        max_rounds: int = 8
    ):
        """
        Initialize the Society of Minds Orchestrator.
        
        Args:
            model_config (dict, optional): Configuration for the language model.
            work_dir (str, optional): Working directory for code execution.
            max_rounds (int, optional): Maximum conversation rounds.
        """
        self.logger = logger
        self.model_config = model_config or self._get_model_config()
        self.work_dir = work_dir
        self.max_rounds = max_rounds
        
        self.agents = self._setup_agents()
        self.groupchat = self._create_groupchat()
        self.manager = self._create_chat_manager()
        self.society_agent = self._create_society_agent()
        self.user_proxy = self._create_user_proxy()
    
    @classmethod
    def _get_model_config(cls) -> Dict[str, str]:
        """
        Retrieve model configuration from environment variables or default settings.
        
        Returns:
            dict: Model configuration dictionary.
        """
        # Try to load from Autogen's config list if available
        try:
            from autogen import config_list_from_json
            config_list = config_list_from_json("OAI_CONFIG_LIST")
            if config_list:
                return config_list[0]
        except Exception:
            pass
        
        # Fallback to environment variables
        return {
            "model": os.getenv("LLM_MODEL", "llama3.1:8b-instruct-q8_0"),
            "api_key": os.getenv("LLM_API_KEY", ""),
            "base_url": os.getenv("LLM_BASE_URL", "http://192.168.1.50:11434/v1")
        }
    
    def _setup_agents(self) -> Dict[str, Any]:
        """
        Set up base agents for the Society of Minds system.
        
        Returns:
            dict: Dictionary of configured agents.
        """
        assistant = autogen.AssistantAgent(
            "inner-assistant",
            llm_config={"config_list": [self.model_config]},
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
        )
        
        code_interpreter = autogen.UserProxyAgent(
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
        
        return {
            "assistant": assistant,
            "code_interpreter": code_interpreter
        }
    
    def _create_groupchat(self) -> autogen.GroupChat:
        """
        Create a GroupChat with configured agents.
        
        Returns:
            autogen.GroupChat: Configured group chat.
        """
        return autogen.GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            speaker_selection_method="round_robin",
            allow_repeat_speaker=False,
            max_round=self.max_rounds,
        )
    
    def _create_chat_manager(self) -> autogen.GroupChatManager:
        """
        Create a GroupChatManager.
        
        Returns:
            autogen.GroupChatManager: Configured chat manager.
        """
        return autogen.GroupChatManager(
            groupchat=self.groupchat,
            is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
            llm_config={"config_list": [self.model_config]},
        )
    
    def _create_society_agent(self) -> SocietyOfMindAgent:
        """
        Create a Society of Mind Agent.
        
        Returns:
            SocietyOfMindAgent: Configured Society of Mind Agent.
        """
        return SocietyOfMindAgent(
            "society_of_mind",
            chat_manager=self.manager,
            llm_config={"config_list": [self.model_config]},
        )
    
    def _create_user_proxy(self) -> autogen.UserProxyAgent:
        """
        Create a UserProxyAgent for interaction.
        
        Returns:
            autogen.UserProxyAgent: Configured user proxy agent.
        """
        return autogen.UserProxyAgent(
            "user_proxy",
            human_input_mode="NEVER",
            code_execution_config=False,
            default_auto_reply="",
            is_termination_msg=lambda x: True,
        )
    
    def solve_problem(self, problem: str) -> Any:
        """
        Solve a complex reasoning problem using the Society of Minds approach.
        
        Args:
            problem (str): The problem to solve.
        
        Returns:
            The result of the problem-solving process.
        """
        try:
            self.logger.info(f"Initiating problem-solving for: {problem}")
            result = self.society_agent.initiate_chat(self.user_proxy, message=problem)
            
            self._save_result(result, problem)
            return result
        except Exception as e:
            self.logger.error(f"Error solving problem: {e}")
            raise
    
    def _save_result(self, result: Any, problem: str):
        """
        Save the result of problem-solving to a file.
        
        Args:
            result (Any): The result to save.
            problem (str): The original problem.
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
    orchestrator = SocietyOfMindsOrchestrator()
    
    # Example problems
    problems = [
        "On which days in 2024 was Microsoft Stock higher than $370?",
        "What is the expected maximum dice value if you can roll a 6-sided dice three times?"
    ]
    
    for problem in problems:
        try:
            result = orchestrator.solve_problem(problem)
            print(f"Problem: {problem}")
            print(f"Result: {result}\n")
        except Exception as e:
            print(f"Failed to solve problem: {problem}")
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()

orchestrator = SocietyOfMindsOrchestrator()
user_proxy = orchestrator.user_proxy
manager = orchestrator.manager
