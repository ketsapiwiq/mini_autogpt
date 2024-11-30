"""Prompt templates and command definitions."""

json_schema = """RESPOND WITH ONLY VALID JSON CONFORMING TO THE FOLLOWING SCHEMA:
{
    "command": {
            "name": {"type": "string"},
            "args": {"type": "object"}
    }
}"""

def get_commands():
    """Get all available commands with their descriptions and arguments."""
    from action.commands.registry import CommandRegistry
    output = "=== Available Commands ===\n\n"
    
    # Get all registered commands
    for command in CommandRegistry.get_available_commands():
        output += f"Command: {command['name']}\n"
        output += f"Description: {command['description']}\n"
        if command["args"] is not None:
            output += "Arguments:\n"
            for arg, description in command["args"].items():
                output += f"  {arg}: {description}\n"
        else:
            output += "Arguments: None\n"
        output += "\n"
    
    return output

def get_command_prompt():
    """Get the command prompt template with available commands."""
    return """Response Format:
1. Use only the commands listed below
2. Provide all required arguments
3. Use Null for optional arguments
4. Return valid JSON matching the schema
5. Include only one command per response

Available Commands:
""" + get_commands() + "\n" + json_schema

def get_action_prompt():
    """Get the action prompt template."""
    return """Analyze the AI's thoughts and decide on the most appropriate action to take.

Core Decision Making Guidelines:
1. Prioritize autonomous actions over user interaction
2. Use specific command arguments for precise actions
3. Consider command context and dependencies
4. Save important information to files when needed
5. Only use ask_user when user input is absolutely necessary

Command Selection Process:
1. First consider task-specific commands (file operations, git, docker, etc.)
2. Use system commands for infrastructure tasks
3. Only use ask_user as a last resort when user input is required
4. Ensure all command arguments are properly specified
5. Consider command impact and side effects

Response Format:
1. Use only the commands listed below
2. Provide all required arguments
3. Use Null for optional arguments
4. Return valid JSON matching the schema
5. Include only one command per response

Available Commands:
""" + get_commands() + "\n" + json_schema

def get_evaluation_prompt():
    """Get the evaluation prompt template."""
    return """Evaluate the AI's thoughts and decisions in the JSON response.

Core Evaluation Guidelines:
1. Verify command selection is appropriate
2. Ensure all required arguments are provided
3. Check for potential command impact
4. Validate JSON schema compliance
5. Consider alternative command options

Evaluation Process:
1. Review thought process and context
2. Validate command selection
3. Check argument completeness
4. Assess potential outcomes
5. Suggest improvements if needed

Response Requirements:
1. Use only listed commands
2. Provide complete argument sets
3. Use Null for optional arguments
4. Return valid JSON response
5. Consider command alternatives

Available Commands:
""" + get_commands() + "\n" + json_schema

def get_thought_prompt():
    """Get the thought prompt template."""
    return """You are a helpful AI assistant focused on independent decision making and problem solving.

Core principles:
1. Make decisions independently without user assistance
2. Use simple, practical strategies
3. Save important information to files
4. Break down complex thoughts using a tree-of-thought approach

Suggest what to do next with:
- Action: The action to perform
- Content: What the action should contain"""

# Constants that don't require imports
summarize_conversation = """Create a concise summary of the conversation, focusing on key information and latest developments. Use first person past tense. Older information should be condensed or omitted."""

summarize = """Create a concise summary of the text, focusing on key information. Use first person perspective as the AI talking to the human."""
