import os
import json
from datetime import datetime
from typing import Dict, Optional, List

# Task directories
TASKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks")
ACTIVE_TASKS_DIR = os.path.join(TASKS_DIR, "active")
COMPLETED_TASKS_DIR = os.path.join(TASKS_DIR, "completed")

class TaskManager:
    """Simplified task management system with file-based persistence"""
    _instance = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize task directories"""
        os.makedirs(ACTIVE_TASKS_DIR, exist_ok=True)
        os.makedirs(COMPLETED_TASKS_DIR, exist_ok=True)

    def create_task(self, task_details: Dict) -> str:
        """
        Create a new task with minimal details.
        
        Args:
            task_details (dict): Details of the task to be created
        
        Returns:
            str: Task ID
        """
        task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        default_task_data = {
            "id": task_id,
            "title": task_details.get('title', 'Untitled Task'),
            "description": task_details.get('description', ''),
            "priority": task_details.get('priority', 3),
            "status": task_details.get('status', 'pending'),
            "created_at": datetime.now().isoformat()
        }

        task_file = os.path.join(ACTIVE_TASKS_DIR, f"{task_id}.json")
        with open(task_file, "w") as f:
            json.dump(default_task_data, f, indent=2)

        return task_id

    def get_active_tasks(self) -> List[Dict]:
        """
        Retrieve all active tasks.
        
        Returns:
            list: List of active tasks
        """
        tasks = []
        for filename in os.listdir(ACTIVE_TASKS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(ACTIVE_TASKS_DIR, filename), 'r') as f:
                    tasks.append(json.load(f))
        return tasks

    def complete_task(self, task_id: str):
        """
        Move a task from active to completed folder.
        
        Args:
            task_id (str): ID of the task to complete
        """
        active_task_path = os.path.join(ACTIVE_TASKS_DIR, f"{task_id}.json")
        completed_task_path = os.path.join(COMPLETED_TASKS_DIR, f"{task_id}.json")
        
        if os.path.exists(active_task_path):
            # Read the task
            with open(active_task_path, 'r') as f:
                task_data = json.load(f)
            
            # Update status and completion time
            task_data['status'] = 'completed'
            task_data['completed_at'] = datetime.now().isoformat()
            
            # Move to completed folder
            with open(completed_task_path, 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Remove from active folder
            os.remove(active_task_path)

# Module-level singleton
task_manager = TaskManager.get_instance()

def get_first_task() -> Optional[Dict]:
    """
    Get the highest priority pending task.

    Returns:
        dict or None: The task with the highest priority, or None if no tasks exist
    """
    tasks = task_manager.get_active_tasks()
    
    # Sort tasks by priority
    tasks.sort(key=lambda x: x.get("priority", 999))
    
    return tasks[0] if tasks else None

def create_task(title: str, description: str, priority: int = 3, status: str = "pending") -> str:
    """
    Create a new task with minimal parameters.
    
    Args:
        title (str): Title of the task
        description (str): Detailed description of the task
        priority (int): Priority level (lower is higher priority)
        status (str): Current status of task
        
    Returns:
        str: ID of the created task
    """
    task_details = {
        "title": title,
        "description": description,
        "priority": priority,
        "status": status
    }
    return task_manager.create_task(task_details)
