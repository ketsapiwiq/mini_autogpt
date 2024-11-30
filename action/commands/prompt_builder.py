"""Command prompt building system."""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class PromptTemplate(ABC):
    """Base class for command prompt templates."""
    
    @abstractmethod
    def build(self, args: Dict[str, Any]) -> str:
        """Build the prompt template with given arguments.
        
        Args:
            args: Dictionary of command arguments
            
        Returns:
            Formatted prompt string
        """
        pass

    @abstractmethod
    def get_template(self) -> str:
        """Get the raw template string.
        
        Returns:
            Template string
        """
        pass

class CommandPrompt:
    """Manages prompts for commands."""
    
    _prompts: Dict[str, PromptTemplate] = {}
    
    @classmethod
    def register_prompt(cls, command_name: str, prompt_template: PromptTemplate):
        """Register a prompt template for a command.
        
        Args:
            command_name: Name of the command
            prompt_template: PromptTemplate instance
        """
        cls._prompts[command_name] = prompt_template
    
    @classmethod
    def get_prompt(cls, command_name: str, args: Dict[str, Any]) -> Optional[str]:
        """Get the formatted prompt for a command.
        
        Args:
            command_name: Name of the command
            args: Command arguments
            
        Returns:
            Formatted prompt string if template exists, None otherwise
        """
        template = cls._prompts.get(command_name)
        if template:
            return template.build(args)
        return None

class BasicPromptTemplate(PromptTemplate):
    """Basic implementation of a prompt template."""
    
    def __init__(self, template: str):
        """Initialize with template string.
        
        Args:
            template: Template string with {arg_name} placeholders
        """
        self._template = template
    
    def build(self, args: Dict[str, Any]) -> str:
        """Build prompt from template and arguments.
        
        Args:
            args: Dictionary of arguments to format template with
            
        Returns:
            Formatted prompt string
        """
        return self._template.format(**args)
    
    def get_template(self) -> str:
        """Get the raw template string.
        
        Returns:
            Template string
        """
        return self._template
