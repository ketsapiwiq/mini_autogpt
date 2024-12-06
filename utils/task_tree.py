import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from utils.log import log
from action.tasks import (
    TASKS_DIR,
    ACTIVE_TASKS_DIR,
    COMPLETED_TASKS_DIR,
    ensure_task_directories,
    create_task as create_base_task,
    get_first_task,
    create_task,
)

# Global variable to store the currently active task ID
_active_task_id = None

def create_task_from_json(task_data: Dict) -> str:
    """Create a new task from JSON data"""
    log(f"Creating task from JSON: {task_data}")
    
    # Extract required fields with defaults
    title = task_data.get("title", "Untitled Task")
    description = task_data.get("description", "No description provided")
    priority = task_data.get("priority", 3)
    source = task_data.get("source", "unknown")
    
    return create_base_task(
        title=title,
        description=description,
        priority=priority,
        source=source
    )

def get_task(task_id: str) -> Dict:
    """Get task data by ID"""
    log(f"Retrieving task data for ID: {task_id}")
    task_file = os.path.join(ACTIVE_TASKS_DIR, f"{task_id}.json")
    if not os.path.exists(task_file):
        task_file = os.path.join(COMPLETED_TASKS_DIR, f"{task_id}.json")
    
    with open(task_file) as f:
        return json.load(f)

def update_task_status(task_id: str, status: str, results: Optional[Dict] = None):
    """Update task status and optionally add results"""
    log(f"Updating task status for ID: {task_id} to {status}")
    task_file = os.path.join(ACTIVE_TASKS_DIR, f"{task_id}.json")
    
    with open(task_file) as f:
        task_data = json.load(f)
    
    task_data["status"] = status
    if results:
        task_data["results"] = results
    
    if status == "completed":
        # Move to completed directory
        log(f"Moving task to completed directory: {task_id}")
        target_file = os.path.join(COMPLETED_TASKS_DIR, f"{task_id}.json")
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w") as f:
            json.dump(task_data, f, indent=2)
        os.remove(task_file)
    else:
        with open(task_file, "w") as f:
            json.dump(task_data, f, indent=2)

def add_thought(task_id: str, thought: str):
    """Add a thought to the task's thought process"""
    log(f"Adding thought to task ID: {task_id}")
    task_file = os.path.join(ACTIVE_TASKS_DIR, f"{task_id}.json")
    
    with open(task_file) as f:
        task_data = json.load(f)
    
    if "thoughts" not in task_data:
        task_data["thoughts"] = []
    task_data["thoughts"].append(thought)
    
    with open(task_file, "w") as f:
        json.dump(task_data, f, indent=2)

def get_active_task() -> Optional[Dict]:
    """Get the currently active task"""
    global _active_task_id
    if _active_task_id:
        try:
            return get_task(_active_task_id)
        except:
            _active_task_id = None
    return None

def create_subtask(parent_id: str, title: str, description: str, priority: Optional[int] = None) -> str:
    """Create a subtask under a parent task"""
    parent_task = get_task(parent_id)
    if not priority:
        priority = parent_task.get("priority", 3)
    
    subtask_id = create_task(
        title=title,
        description=description,
        priority=priority
    )
    
    # Link subtask to parent
    task_file = os.path.join(ACTIVE_TASKS_DIR, f"{subtask_id}.json")
    with open(task_file) as f:
        task_data = json.load(f)
    
    task_data["parent_id"] = parent_id
    
    with open(task_file, "w") as f:
        json.dump(task_data, f, indent=2)
    
    return subtask_id

def get_highest_priority_task() -> Optional[Dict]:
    """Get the highest priority pending task"""
    log("Retrieving highest priority pending task")
    
    # Ensure task directories exist
    ensure_task_directories()
    
    # List all active tasks
    active_tasks = []
    for filename in os.listdir(ACTIVE_TASKS_DIR):
        if filename.endswith(".json"):
            task_file = os.path.join(ACTIVE_TASKS_DIR, filename)
            with open(task_file) as f:
                task_data = json.load(f)
                if task_data.get("status", "pending") == "pending":
                    active_tasks.append(task_data)
    
    if not active_tasks:
        return None
    
    # Sort by priority (lower number = higher priority)
    return sorted(active_tasks, key=lambda x: x.get("priority", 3))[0]

def update_task_results(task_data, results, folder_path="tasks"):
    """
    Updates a task file with the results/insights from thinking about it.
    
    Args:
        task_data (dict): The original task data
        results (str): The thinking results to add
        folder_path (str): The path to the tasks folder
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    log(f"Updating task results in folder: {folder_path}")
    log(f"Task data: {task_data}")
    
    if not os.path.isabs(folder_path):
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), folder_path)
        log(f"Using absolute folder path: {folder_path}")
    
    # Find the task file that matches this task
    log("Searching for matching task file...")
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            log(f"Checking file: {file_path}")
            try:
                with open(file_path, 'r') as f:
                    current_task = json.load(f)
                
                # Check if this is the matching task
                if (current_task.get('task') == task_data.get('task') and 
                    current_task.get('priority') == task_data.get('priority')):
                    
                    log("Found matching task, updating with results...")
                    # Update the task with results
                    current_task['last_thoughts'] = results
                    current_task['last_updated'] = datetime.now().isoformat()
                    
                    # Write back to file
                    with open(file_path, 'w') as f:
                        json.dump(current_task, f, indent=4)
                    log("Task updated successfully")
                    return True
            except (json.JSONDecodeError, OSError) as e:
                log(f"Error updating task file {file_path}: {e}")
    
    log("No matching task file found")
    return False
