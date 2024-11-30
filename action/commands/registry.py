"""Command registry for mini_autogpt."""
from typing import Dict, Type, Optional, List, Any
from . import Command
from utils.log import log
import think.prompt as prompt

class CommandRegistry:
    """Registry for all available commands."""
    
    _commands: Dict[str, Type[Command]] = {}
    
    @classmethod
    def register(cls, name: str, command_class: Type[Command]):
        """Register a new command.
        
        Args:
            name: Name of the command
            command_class: Command class to register
        """
        cls._commands[name] = command_class
        log(f"Registered command: {name}")
    
    @classmethod
    def get_command(cls, name: str) -> Optional[Type[Command]]:
        """Get a command by name.
        
        Args:
            name: Name of the command
            
        Returns:
            Command class if found, None otherwise
        """
        return cls._commands.get(name)
    
    @classmethod
    def get_available_commands(cls) -> List[Dict[str, Any]]:
        """Get list of available commands with their descriptions."""
        commands = []
        for name, command_class in cls._commands.items():
            command_instance = command_class()
            doc = command_class.__doc__ or "No description available"
            # Clean up docstring
            doc = doc.strip().split('\n')[0]
            commands.append({
                "name": name,
                "description": doc,
                "args": command_instance.get_args() if hasattr(command_instance, 'get_args') else None
            })
        return commands
    
    @classmethod
    def get_command_prompt(cls) -> str:
        """Get a formatted string of all available commands for the LLM prompt.
        
        Returns:
            Formatted string listing all commands and their descriptions
        """
        commands = cls.get_available_commands()
        prompt = "Available commands:\n\n"
        for cmd in commands:
            prompt += f"- {cmd['name']}: {cmd['description']}\n"
        return prompt
    
    @classmethod
    def execute(cls, name: str, args: dict) -> dict:
        """Execute a command by name.
        
        Args:
            name: Name of the command
            args: Command arguments
            
        Returns:
            Command execution results
            
        Raises:
            ValueError: If command not found or arguments invalid
        """
        command_class = cls.get_command(name)
        if not command_class:
            raise ValueError(f"Command not found: {name}")
            
        command = command_class()
        if not command.validate_args(args):
            raise ValueError(f"Invalid arguments for command {name}: {args}")
            
        return command.execute(args)
