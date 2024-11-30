"""Command system for mini_autogpt."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Command(ABC):
    """Base class for all commands."""
    
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
