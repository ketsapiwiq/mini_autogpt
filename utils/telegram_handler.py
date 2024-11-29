from typing import Dict
from utils.task_tree import create_task

def handle_telegram_message(message: Dict) -> str:
    """
    Create a new task from an incoming Telegram message
    Returns the created task ID
    """
    # Extract message content
    text = message.get("text", "")
    
    # Create high priority task for telegram messages
    task_id = create_task(
        title=f"Process Telegram message: {text[:50]}...",
        description=f"Analyze and respond to Telegram message:\n\n{text}",
        priority=1,  # High priority for user messages
        source="telegram"
    )
    
    return task_id
