"""Command system for mini_autogpt."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from .prompt_builder import CommandPrompt, BasicPromptTemplate

class Command(ABC):
    """Base class for all commands."""
    
    def __init__(self):
        """Initialize command and register its prompt if provided."""
        prompt_template = self.get_prompt_template()
        if prompt_template:
            CommandPrompt.register_prompt(self.__class__.__name__, prompt_template)
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the command with given arguments.
        
        Args:
            args: Dictionary of command arguments
            
        Returns:
            Dictionary containing command results
        """
        pass
    
    @abstractmethod
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate command arguments.
        
        Args:
            args: Dictionary of command arguments
            
        Returns:
            True if arguments are valid, False otherwise
        """
        pass

    @abstractmethod
    def get_args(self) -> Optional[Dict[str, str]]:
        """Get command argument descriptions.
        
        Returns:
            Dictionary mapping argument names to their descriptions,
            or None if command takes no arguments
        """
        pass

    def get_prompt_template(self) -> Optional[BasicPromptTemplate]:
        """Get the prompt template for this command.
        
        Returns:
            Prompt template for this command, or None if not needed
        """
        return None

    def get_formatted_prompt(self, args: Dict[str, Any]) -> Optional[str]:
        """Get the formatted prompt for this command.
        
        Args:
            args: Command arguments
            
        Returns:
            Formatted prompt string if template exists,
            None otherwise
        """
        return CommandPrompt.get_prompt(self.__class__.__name__, args)

    def get_agent_requirements(self) -> Dict[str, Any]:
        """Get the agent requirements for this command.
        This is a placeholder for future agent integration.
        
        Returns:
            Dictionary containing:
                - capabilities: List of required agent capabilities
                - permissions: List of required permissions
                - resources: List of required resources
                - metadata: Additional metadata for agent handling
        """
        return {
            "capabilities": [],
            "permissions": [],
            "resources": [],
            "metadata": {}
        }
    
    def prepare_for_agent(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare command arguments for agent execution.
        This is a placeholder for future agent integration.
        
        Args:
            args: Original command arguments
            
        Returns:
            Modified arguments suitable for agent execution
        """
        return args
    
    def handle_agent_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process the response from an agent execution.
        This is a placeholder for future agent integration.
        
        Args:
            response: Raw response from agent execution
            
        Returns:
            Processed response in standard command format
        """
        return response
