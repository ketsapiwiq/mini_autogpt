"""Agent-based command handling system."""
from typing import Dict, Any, List, Optional
from . import Command
from .registry import CommandRegistry
from think.swarm import BaseAgent, CommandAgent, Swarm, AgentContext


class AgentCommandExecutor(Command):
    """Command to execute commands through the agent system."""
    
    def __init__(self):
        self.swarm = Swarm()
        self._setup_agents()
        
    def _setup_agents(self):
        """Set up the initial set of agents."""
        # Create specialized agents for different command types
        self._create_system_agent()
        self._create_file_agent()
        self._create_prompt_agent()
        
    def _create_system_agent(self):
        """Create agent for handling system commands."""
        system_commands = ["ask_user", "conversation_history"]
        agent = CommandAgent(
            name="SystemAgent",
            instructions="Handle core system interactions and user communication.",
            commands=system_commands
        )
        self.swarm.add_agent(agent)
        
    def _create_file_agent(self):
        """Create agent for handling file operations."""
        file_commands = ["read_file", "write_file", "list_directory"]
        agent = CommandAgent(
            name="FileAgent",
            instructions="Handle all file system operations safely and efficiently.",
            commands=file_commands
        )
        self.swarm.add_agent(agent)
        
    def _create_prompt_agent(self):
        """Create agent for handling prompt-related commands."""
        prompt_commands = ["get_prompt", "set_prompt"]
        agent = CommandAgent(
            name="PromptAgent",
            instructions="Manage and modify system prompts and templates.",
            commands=prompt_commands
        )
        self.swarm.add_agent(agent)

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command through the agent system.
        
        Args:
            args: Dictionary containing:
                - command: The command to execute
                - context: Optional context information
                
        Returns:
            Dictionary containing the command execution results
        """
        command = args.get("command")
        if not command:
            return {"error": "No command specified"}
            
        context = AgentContext(
            variables=args.get("context", {}),
            history=args.get("history", []),
            metadata={"command": command}
        )
        
        # Find the appropriate agent to handle the command
        for agent in self.swarm.agents:
            if agent.can_handle(context):
                return self.swarm.run(agent, [], context)
                
        return {"error": f"No agent available to handle command: {command}"}
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate command arguments.
        
        Args:
            args: Dictionary of command arguments
            
        Returns:
            True if arguments are valid, False otherwise
        """
        return "command" in args
    
    def get_args(self) -> Optional[Dict[str, str]]:
        """Get command argument descriptions.
        
        Returns:
            Dictionary of argument descriptions
        """
        return {
            "command": "The command to execute",
            "context": "Optional context information for the command"
        }


# Register the agent command executor
CommandRegistry.register("agent_execute", AgentCommandExecutor)
