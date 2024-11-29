json_schema = """RESPOND WITH ONLY VALID JSON CONFORMING TO THE FOLLOWING SCHEMA:
{
    "command": {
            "name": {"type": "string"},
            "args": {"type": "object"}
    }
}"""

commands = [
    {
        "name": "ask_user",
        "description": "Ask the user for input or tell them something and wait for their response. Do not greet the user, if you already talked.",
        "args": {"message": "<message that awaits user input>"},
        "enabled": True,
    },
    {
        "name": "conversation_history",
        "description": "gets the full conversation history",
        "args": None,
        "enabled": True,
    },
    {
        "name": "web_search",
        "description": "search the web for keyword",
        "args": {"query": "<query to research>"},
        "enabled": True,
    },
]


def get_commands():
    output = ""
    for command in commands:
        if command["enabled"] != True:
            continue
        # enabled_status = "Enabled" if command["enabled"] else "Disabled"
        output += f"Command: {command['name']}\n"
        output += f"Description: {command['description']}\n"
        if command["args"] is not None:
            output += "Arguments:\n"
            for arg, description in command["args"].items():
                output += f"  {arg}: {description}\n"
        else:
            output += "Arguments: None\n"
        output += "\n"  # For spacing between commands
    return output.strip()  # Remove the trailing newline for cleaner output


summarize_conversation = """Create a concise summary of the conversation, focusing on key information and latest developments. Use first person past tense. Older information should be condensed or omitted."""

summarize = """Create a concise summary of the text, focusing on key information. Use first person perspective as the AI talking to the human."""


thought_prompt = """You are a helpful AI assistant focused on independent decision making and problem solving.

Core principles:
1. Make decisions independently without user assistance
2. Use simple, practical strategies
3. Save important information to files
4. Break down complex thoughts using a tree-of-thought approach

Suggest what to do next with:
- Action: The action to perform
- Content: What the action should contain"""

action_prompt = (
    """Analyze the AI's thoughts and decide on actions to take.
Core requirements:
1. Use only the commands listed below
2. Save important information to files
3. No user assistance needed
4. Use ask_user for new command requests
5. Use Null for None in JSON responses

Available commands:
"""
    + get_commands()
    + "\n"
    + json_schema
)

evaluation_prompt = (
    """Evaluate the AI's thoughts and decisions in the JSON response.
Core requirements:
1. Use only listed commands
2. No user assistance needed
3. Fill empty Thoughts with empty strings
4. Use ask_user command to communicate thoughts
5. Use Null for None in JSON responses

Available commands:
"""
    + get_commands()
    + "\n"
    + json_schema
)
