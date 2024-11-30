"""Prompt-related commands."""
from typing import Dict, Any, Optional
from . import Command
from think.prompt import commands as static_commands

class GetPromptCommand(Command):
    """Command to get the current prompt."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get the current prompt commands.
        
        Args:
            args: Empty dictionary, no arguments needed
            
        Returns:
            Dictionary containing the list of available commands
        """
        return {"commands": static_commands}
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate command arguments.
        
        Args:
            args: Dictionary of command arguments
            
        Returns:
            True if arguments are valid, False otherwise
        """
        return True

    def get_args(self) -> Optional[Dict[str, str]]:
        """Get command argument descriptions.
        
        Returns:
            None since this command takes no arguments
        """
        return None

class SetPromptCommand(Command):
    """Command to set/update prompt commands."""
    
    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Set or update prompt commands.
        
        Args:
            args: Dictionary containing:
                - name: Name of the command to update
                - enabled: Boolean indicating if command should be enabled
                
        Returns:
            Dictionary containing success status
        """
        command_name = args.get("name")
        enabled = args.get("enabled", True)
        
        # Find and update the command
        for cmd in static_commands:
            if cmd["name"] == command_name:
                cmd["enabled"] = enabled
                return {"success": True, "message": f"Command '{command_name}' {'enabled' if enabled else 'disabled'}"}
        
        return {"success": False, "message": f"Command '{command_name}' not found"}
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate command arguments.
        
        Args:
            args: Dictionary of command arguments
            
        Returns:
            True if arguments are valid, False otherwise
        """
        return "name" in args and isinstance(args.get("enabled", True), bool)

    def get_args(self) -> Optional[Dict[str, str]]:
        """Get command argument descriptions.
        
        Returns:
            Dictionary describing the required arguments
        """
        return {
            "name": "Name of the command to enable/disable",
            "enabled": "Boolean flag to enable (True) or disable (False) the command"
        }
