import os
import json
from datetime import datetime
from utils.log import log
import time

# Use absolute path for tasks directory
TASKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks")
ACTIVE_TASKS_DIR = os.path.join(TASKS_DIR, "active")
COMPLETED_TASKS_DIR = os.path.join(TASKS_DIR, "completed")
CANCELLED_TASKS_DIR = os.path.join(TASKS_DIR, "cancelled")

class TaskManager:
    """
    A comprehensive task management system with file-based persistence and status tracking.
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize task directories and state"""
        self.ensure_task_directories()
        self.state_file = os.path.join(TASKS_DIR, "task_state.json")
        self.load_state()

    def ensure_task_directories(self):
        """Ensure all required task directories exist"""
        for dir_path in [TASKS_DIR, ACTIVE_TASKS_DIR, COMPLETED_TASKS_DIR, CANCELLED_TASKS_DIR]:
            os.makedirs(dir_path, exist_ok=True)

    def load_state(self):
        """Load or initialize task state"""
        if not os.path.exists(self.state_file):
            with open(self.state_file, "w") as f:
                json.dump({"last_task": None, "in_progress": [], "task_history": []}, f)

        try:
            with open(self.state_file, "r") as f:
                self.state = json.load(f)
        except:
            self.state = {"last_task": None, "in_progress": [], "task_history": []}

    def save_state(self):
        """Save current task state"""
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def create_task(self, task_details):
        """
        Create a new task with comprehensive details.
        
        Args:
            task_details (dict): Details of the task to be created
        
        Returns:
            str: Task ID
        """
        # Generate unique task ID
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare task data with default and provided values
        default_task_data = {
            "id": task_id,
            "title": task_details.get('description', 'Untitled Task'),
            "description": task_details.get('description', ''),
            "priority": task_details.get('priority', 3),
            "status": task_details.get('status', 'created'),
            "source": task_details.get('source', 'unknown'),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": task_details.get('metadata', {})
        }

        # Create task directory
        task_dir = os.path.join(ACTIVE_TASKS_DIR, task_id)
        os.makedirs(task_dir, exist_ok=True)

        # Write task file
        task_file = os.path.join(task_dir, "task.json")
        with open(task_file, "w") as f:
            json.dump(default_task_data, f, indent=2)

        # Update state
        if task_id not in self.state["in_progress"]:
            self.state["in_progress"].append(task_id)
        self.state["last_task"] = task_id
        
        # Add to task history
        if "task_history" not in self.state:
            self.state["task_history"] = []
        self.state["task_history"].append(default_task_data)
        
        self.save_state()

        return task_id

    def update_task_status(self, task_id, status):
        """
        Update the status of a task and move it if necessary.
        
        Args:
            task_id (str): ID of the task
            status (str): New status of the task
        """
        task_file = os.path.join(ACTIVE_TASKS_DIR, task_id, "task.json")
        
        if not os.path.exists(task_file):
            log(f"Task {task_id} not found.")
            return

        # Read current task data
        with open(task_file, 'r') as f:
            task_data = json.load(f)

        # Update status and timestamp
        task_data['status'] = status
        task_data['updated_at'] = datetime.now().isoformat()

        # Write updated task data
        with open(task_file, 'w') as f:
            json.dump(task_data, f, indent=2)

        # Handle task movement based on status
        if status == 'completed':
            os.makedirs(COMPLETED_TASKS_DIR, exist_ok=True)
            new_task_path = os.path.join(COMPLETED_TASKS_DIR, task_id)
            os.rename(os.path.dirname(task_file), new_task_path)
        elif status == 'cancelled':
            os.makedirs(CANCELLED_TASKS_DIR, exist_ok=True)
            new_task_path = os.path.join(CANCELLED_TASKS_DIR, task_id)
            os.rename(os.path.dirname(task_file), new_task_path)

        # Update state
        if task_id in self.state.get("in_progress", []):
            self.state["in_progress"].remove(task_id)
        self.save_state()

    def get_active_tasks(self):
        """
        Retrieve all active tasks.
        
        Returns:
            list: List of active tasks
        """
        active_tasks = []
        for task_id in os.listdir(ACTIVE_TASKS_DIR):
            task_file = os.path.join(ACTIVE_TASKS_DIR, task_id, "task.json")
            if os.path.exists(task_file):
                with open(task_file, 'r') as f:
                    task = json.load(f)
                    active_tasks.append(task)
        return active_tasks

    def get_task_history(self):
        """
        Retrieve task history.
        
        Returns:
            list: List of all tasks from history
        """
        return self.state.get("task_history", [])

    def cancel_task(self, task_id):
        """
        Cancel a specific task.
        
        Args:
            task_id (str): ID of the task to cancel
        """
        self.update_task_status(task_id, 'cancelled')

    def pause_task(self, task_id):
        """
        Pause a specific task.
        
        Args:
            task_id (str): ID of the task to pause
        """
        self.update_task_status(task_id, 'paused')

# Expose the TaskManager as a module-level singleton
task_manager = TaskManager.get_instance()

# Preserve existing functions for backward compatibility
def get_first_task():
    """
    Checks the JSON files in the given folder, sorts them by a 'priority' key, 
    and returns the first task.

    Returns:
        dict or None: The task with the highest priority (lowest value of 'priority'), 
                      or None if no valid tasks are found.
    """
    tasks = task_manager.get_active_tasks()
    
    # Sort tasks by priority and creation time
    tasks.sort(key=lambda x: (x.get("priority", 999), x.get("created_at", "")))
    
    return tasks[0] if tasks else None

def create_task(title: str, description: str, priority: int = 3, source: str = "unknown", status: str = "pending") -> str:
    """
    Creates a new task file in the tasks directory.
    
    Args:
        title (str): Title of the task
        description (str): Detailed description of the task
        priority (int): Priority level (1-5, lower is higher priority)
        source (str): Source of the task creation
        status (str): Current status of task
        
    Returns:
        str: ID of the created task
    """
    task_details = {
        "title": title,
        "description": description,
        "priority": priority,
        "source": source,
        "status": status
    }
    return task_manager.create_task(task_details)
