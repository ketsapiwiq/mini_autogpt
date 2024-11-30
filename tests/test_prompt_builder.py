"""Tests for the prompt building system."""
import unittest
from action.commands.prompt_builder import CommandPrompt, BasicPromptTemplate
from action.commands import Command
from typing import Dict, Any, Optional

class TestCommand(Command):
    """Test command implementation."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success"}
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        return True
    
    def get_args(self) -> Optional[Dict[str, str]]:
        return None
    
    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        return BasicPromptTemplate("Test command with {arg1} and {arg2}")

class PromptBuilderTest(unittest.TestCase):
    """Test cases for prompt building system."""
    
    def setUp(self):
        """Set up test cases."""
        self.command = TestCommand()
    
    def test_prompt_registration(self):
        """Test that prompts are properly registered."""
        prompt = CommandPrompt.get_prompt("TestCommand", {"arg1": "value1", "arg2": "value2"})
        self.assertEqual(prompt, "Test command with value1 and value2")
    
    def test_missing_prompt(self):
        """Test behavior when prompt template doesn't exist."""
        prompt = CommandPrompt.get_prompt("NonexistentCommand", {})
        self.assertIsNone(prompt)
    
    def test_missing_args(self):
        """Test behavior when required args are missing."""
        with self.assertRaises(KeyError):
            CommandPrompt.get_prompt("TestCommand", {"arg1": "value1"})
    
    def test_extra_args(self):
        """Test that extra args are ignored."""
        prompt = CommandPrompt.get_prompt(
            "TestCommand", 
            {"arg1": "value1", "arg2": "value2", "extra": "ignored"}
        )
        self.assertEqual(prompt, "Test command with value1 and value2")

if __name__ == '__main__':
    unittest.main()
