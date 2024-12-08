from typing import List, Dict, Optional
import importlib
import os

class AgentSelector:
    def __init__(self, contrib_path: str = "/home/hadrien/git/ag2/autogen/agentchat/contrib"):
        self.contrib_path = contrib_path
        self.agents = self._load_agents()

    def _load_agents(self) -> Dict[str, str]:
        """
        Dynamically load available agents from the contrib directory.
        
        Returns:
            Dict of agent names and their module paths
        """
        agents = {}
        for filename in os.listdir(self.contrib_path):
            if filename.endswith("_agent.py"):
                agent_name = filename[:-3]  # Remove .py
                agents[agent_name] = f"autogen.agentchat.contrib.{agent_name}"
        return agents

    def select_agent(self, task_description: str, task_type: Optional[str] = None) -> str:
        """
        Select the most appropriate agent based on task description and type.
        
        Args:
            task_description (str): Detailed description of the task
            task_type (str, optional): Predefined task type for more precise matching
        
        Returns:
            str: Recommended agent module path
        """
        task_description = task_description.lower()
        
        # Web and Research Tasks
        if any(keyword in task_description for keyword in ['search', 'browse', 'web', 'navigate', 'wikipedia']):
            return self.agents.get('web_surfer', 'autogen.UserProxyAgent')
        
        # Mathematical or Analytical Tasks
        if any(keyword in task_description for keyword in ['calculate', 'math', 'compute', 'solve equation']):
            return self.agents.get('math_user_proxy_agent', 'autogen.AssistantAgent')
        
        # Text Analysis Tasks
        if any(keyword in task_description for keyword in ['analyze', 'summarize', 'extract', 'understand text']):
            return self.agents.get('text_analyzer_agent', 'autogen.AssistantAgent')
        
        # Multimodal Tasks
        if any(keyword in task_description for keyword in ['image', 'visual', 'picture', 'diagram']):
            return self.agents.get('llava_agent', 'autogen.AssistantAgent')
        
        # Information Retrieval Tasks
        if any(keyword in task_description for keyword in ['retrieve', 'find information', 'search database']):
            return self.agents.get('retrieve_assistant_agent', 'autogen.UserProxyAgent')
        
        # Complex Reasoning Tasks
        if any(keyword in task_description for keyword in ['reason', 'complex problem', 'multi-step', 'strategy']):
            return self.agents.get('reasoning_agent', 'autogen.AssistantAgent')
        
        # Default to a standard AssistantAgent if no specific match is found
        return 'autogen.AssistantAgent'

    def get_agent_description(self, agent_name: str) -> str:
        """
        Get a brief description of an agent.
        
        Args:
            agent_name (str): Name of the agent
        
        Returns:
            str: Agent description or a default message
        """
        # This is a placeholder. In a real implementation, you'd parse docstrings or have predefined descriptions
        descriptions = {
            'web_surfer_agent': 'An agent capable of web browsing, searching, and content summarization.',
            'math_user_proxy_agent': 'An agent specialized in mathematical computations and problem-solving.',
            'text_analyzer_agent': 'An agent designed for text analysis, summarization, and information extraction.',
            'llava_agent': 'A multimodal agent capable of understanding and processing visual and textual information.',
            'retrieve_assistant_agent': 'An agent focused on information retrieval from various sources and databases.'
        }
        
        return descriptions.get(agent_name, 'A general-purpose conversational agent.')

def main():
    # Example usage
    selector = AgentSelector()
    
    # Example tasks
    tasks = [
        "Search Wikipedia for information about quantum computing",
        "Calculate the trajectory of a satellite",
        "Analyze the sentiment of customer reviews",
        "Retrieve information about recent scientific publications"
    ]
    
    for task in tasks:
        recommended_agent = selector.select_agent(task)
        print(f"Task: {task}")
        print(f"Recommended Agent: {recommended_agent}")
        print(f"Description: {selector.get_agent_description(recommended_agent.split('.')[-1])}\n")

if __name__ == "__main__":
    main()
