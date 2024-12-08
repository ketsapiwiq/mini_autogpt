import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.agent_selector import AgentSelector

class TestAgentSelector(unittest.TestCase):
    def setUp(self):
        """Initialize AgentSelector before each test."""
        self.selector = AgentSelector()

    def test_web_search_task(self):
        """Test agent selection for web search tasks."""
        tasks = [
            "Search Wikipedia for quantum computing",
            "Browse the internet for recent AI research",
            "Navigate to a specific website and summarize its content"
        ]
        
        for task in tasks:
            recommended_agent = self.selector.select_agent(task)
            self.assertIn('web_surfer', recommended_agent.lower(), 
                          f"Failed to select web agent for task: {task}")

    def test_math_task(self):
        """Test agent selection for mathematical tasks."""
        tasks = [
            "Calculate the trajectory of a satellite",
            "Solve a complex mathematical equation",
            "Compute statistical analysis of a dataset"
        ]
        
        for task in tasks:
            recommended_agent = self.selector.select_agent(task)
            self.assertIn('math_user_proxy_agent', recommended_agent.lower(), 
                          f"Failed to select math agent for task: {task}")

    def test_text_analysis_task(self):
        """Test agent selection for text analysis tasks."""
        tasks = [
            "Analyze sentiment of customer reviews",
            "Summarize a long research paper",
            "Extract key information from a document"
        ]
        
        for task in tasks:
            recommended_agent = self.selector.select_agent(task)
            self.assertIn('text_analyzer_agent', recommended_agent.lower(), 
                          f"Failed to select text analysis agent for task: {task}")

    def test_retrieval_task(self):
        """Test agent selection for information retrieval tasks."""
        tasks = [
            "Retrieve information about recent scientific publications",
            "Search a database for specific research papers",
            "Find and compile information from multiple sources"
        ]
        
        for task in tasks:
            recommended_agent = self.selector.select_agent(task)
            self.assertIn('retrieve_assistant_agent', recommended_agent.lower(), 
                          f"Failed to select retrieval agent for task: {task}")

    def test_multimodal_task(self):
        """Test agent selection for multimodal tasks."""
        tasks = [
            "Analyze an image and describe its contents",
            "Process a diagram and extract key information",
            "Understand a visual representation of data"
        ]
        
        for task in tasks:
            recommended_agent = self.selector.select_agent(task)
            self.assertIn('llava_agent', recommended_agent.lower(), 
                          f"Failed to select multimodal agent for task: {task}")

    def test_complex_reasoning_task(self):
        """Test agent selection for complex reasoning tasks."""
        tasks = [
            "Develop a strategic plan for a business problem",
            "Break down a complex multi-step problem",
            "Create a reasoning framework for decision making"
        ]
        
        for task in tasks:
            recommended_agent = self.selector.select_agent(task)
            self.assertIn('reasoning_agent', recommended_agent.lower(), 
                          f"Failed to select reasoning agent for task: {task}")

    def test_default_agent_selection(self):
        """Test default agent selection for generic tasks."""
        tasks = [
            "Have a general conversation",
            "Provide advice on a topic",
            "Engage in open-ended dialogue"
        ]
        
        for task in tasks:
            recommended_agent = self.selector.select_agent(task)
            self.assertEqual(recommended_agent, 'autogen.AssistantAgent', 
                             f"Failed to select default agent for task: {task}")

    def test_agent_description(self):
        """Test agent description retrieval."""
        agent_names = [
            'web_surfer_agent', 
            'math_user_proxy_agent', 
            'text_analyzer_agent', 
            'llava_agent', 
            'retrieve_assistant_agent',
            'non_existent_agent'
        ]
        
        for agent_name in agent_names:
            description = self.selector.get_agent_description(agent_name)
            self.assertIsInstance(description, str)
            self.assertTrue(len(description) > 0, f"Empty description for {agent_name}")

if __name__ == '__main__':
    unittest.main()
