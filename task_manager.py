import telegram
from tasks.schema import Task

class TaskManager:
    def __init__(self, telegram_bot_token):
        self.bot = telegram.Bot(token=telegram_bot_token)

    def capture_last_message_as_task(self):
        """Fetch the last message from Telegram and create a task."""
        updates = self.bot.get_updates()
        if updates:
            last_message = updates[-1].message.text
            return Task(id="1", title="Telegram Task", description=last_message, priority=1, source="telegram", subtasks=[])
        return None

    def evaluate_and_filter_tasks(self, tasks):
        """Evaluate tasks and remove any that are nonsensical or empty."""
        valid_tasks = []
        for task in tasks:
            if task.description.strip() and not self.is_nonsensical(task.description):
                valid_tasks.append(task)
        return valid_tasks

    def is_nonsensical(self, description):
        """Determine if a task description is nonsensical."""
        # Placeholder for more sophisticated evaluation logic
        return len(description.split()) < 3
