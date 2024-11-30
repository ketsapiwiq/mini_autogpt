"""Command setup and registration."""
from . import user_interaction, web_search, file_operations
from .registry import CommandRegistry

def register_commands():
    """Import and register all available commands."""
    # The import statements above will trigger the command registration
    # as each module registers its commands when imported
    # Register file operation commands
    CommandRegistry.register("read_file", file_operations.ReadFileCommand)
    CommandRegistry.register("lookup_files", file_operations.LookupFilesCommand)
    CommandRegistry.register("lookup_term", file_operations.LookupTermCommand)
    CommandRegistry.register("exec_docker_command", file_operations.ExecDockerCommand)
    CommandRegistry.register("git_stash", file_operations.GitStashCommand)
    CommandRegistry.register("git_switch_branch", file_operations.GitSwitchBranchCommand)
    
    # Register user interaction commands
    CommandRegistry.register("ask_user", user_interaction.AskUserCommand)
    CommandRegistry.register("tell_user", user_interaction.TellUserCommand)
    
    # Register web search commands
    CommandRegistry.register("web_search", web_search.WebSearchCommand)
    