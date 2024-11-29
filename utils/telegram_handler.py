from typing import Dict
from utils.task_tree import create_task_from_json
from utils.simple_telegram import TelegramUtils


def handle_telegram_message(message: Dict) -> str:
    """
    Create a new task from the last message in the conversation history using JSON structure.
    Returns the created task ID
    """
    # Initialize TelegramUtils to access conversation history
    telegram_utils = TelegramUtils()
    last_messages = telegram_utils.get_last_few_messages()
    if last_messages:
        text = last_messages[-1].get("text", "")
    else:
        text = ""

    # Create high priority task for telegram messages
    task_data = {
        "title": f"Process Telegram message: {text[:50]}...",
        "description": f"Analyze and respond to Telegram message:\n\n{text}",
        "priority": 1,  # High priority for user messages
        "source": "telegram",
        "subtasks": []
    }

    task_id = create_task_from_json(task_data)

    return task_id
