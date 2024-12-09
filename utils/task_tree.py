import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from utils.log import log
from action.tasks import (
    TASKS_DIR,
    ACTIVE_TASKS_DIR,
    COMPLETED_TASKS_DIR,
    TaskManager,
)

# Global variable to store the currently active task ID
_active_task_id = None

def get_active_task() -> Optional[Dict]:
    """Get the currently active task"""
    global _active_task_id
    if _active_task_id:
        try:
            return get_task(_active_task_id)
        except:
            _active_task_id = None
    return None

def get_task(task_id: str) -> Dict:
    """Get task data by ID"""
    task_manager = TaskManager.get_instance()
    return task_manager.get_task_by_id(task_id)

def get_highest_priority_task() -> Optional[Dict]:
    """Get the highest priority pending task"""
    task_manager = TaskManager.get_instance()
    return task_manager.get_highest_priority_task()

def create_subtask(parent_id: str, title: str, description: str, priority: Optional[int] = None) -> str:
    """Create a subtask under a parent task"""
    task_manager = TaskManager.get_instance()
    parent_task = get_task(parent_id)
    
    if not priority:
        priority = parent_task.get("priority", 3)
    
    subtask_id = task_manager.create_task({
        "title": title,
        "description": description,
        "priority": priority,
        "parent_id": parent_id
    })
    
    return subtask_id

def add_thought(task_id: str, thought: str):
    """Add a thought to the task's thought process"""
    task_manager = TaskManager.get_instance()
    task_manager.add_thought_to_task(task_id, thought)

def update_task_results(task_data: dict, results, folder_path="tasks"):
    """
    Updates a task file with the results/insights from thinking about it.
    
    Args:
        task_data (dict): The original task data
        results (Union[str, dict, list]): The thinking results to add
        folder_path (str, optional): The path to the tasks folder
    
    Returns:
        dict: Updated task information with processing metadata
    """
    task_manager = TaskManager.get_instance()
    return task_manager.update_task_results(task_data, results, folder_path)

def update_task_status(task_id: str, status: str, results: Optional[Dict] = None):
    """Update task status and optionally add results"""
    task_manager = TaskManager.get_instance()
    task_manager.update_task_status(task_id, status, results)

def create_task_from_json(task_data: Dict) -> str:
    """Create a new task from JSON data"""
    task_manager = TaskManager.get_instance()
    return task_manager.create_task(task_data)
