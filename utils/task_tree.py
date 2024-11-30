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
    get_first_task
)

# Global variable to store the currently active task ID
_active_task_id = None

def create_task_from_json(task_data: Dict) -> str:
    """Create a new task from JSON data"""
    log(f"Creating task from JSON: {task_data}")
    
    # Extract required fields with defaults
    title = task_data.get("title", task_data.get("task", "Untitled Task"))
    description = task_data.get("description", "No description provided")
    priority = task_data.get("priority", 3)
    status = task_data.get("status", "pending")
    
    return create_base_task(
        task_name=title,
        description=description,
        priority=priority,
        status=status
    )

def get_task(task_id: str) -> Dict:
    """Get task data by ID"""
    log(f"Retrieving task data for ID: {task_id}")
    task_file = os.path.join(ACTIVE_TASKS_DIR, task_id, "task.json")
    if not os.path.exists(task_file):
        task_file = os.path.join(COMPLETED_TASKS_DIR, task_id, "task.json")
    
    with open(task_file) as f:
        return json.load(f)

def update_task_status(task_id: str, status: str, results: Optional[Dict] = None):
    """Update task status and optionally add results"""
    log(f"Updating task status for ID: {task_id} to {status}")
    task_dir = os.path.join(ACTIVE_TASKS_DIR, task_id)
    task_file = os.path.join(task_dir, "task.json")
    
    with open(task_file) as f:
        task_data = json.load(f)
    
    task_data["status"] = status
    if results:
        task_data["results"] = results
    
    with open(task_file, "w") as f:
        json.dump(task_data, f, indent=2)
    
    if status == "completed":
        # Move to completed directory
        log(f"Moving task to completed directory: {task_id}")
        target_dir = os.path.join(COMPLETED_TASKS_DIR, task_id)
        os.makedirs(os.path.dirname(target_dir), exist_ok=True)
        os.rename(task_dir, target_dir)

def add_thought(task_id: str, thought: str):
    """Add a thought to the task's thought process"""
    log(f"Adding thought to task ID: {task_id}")
    thought_dir = os.path.join(ACTIVE_TASKS_DIR, task_id, "thoughts")
    timestamp = datetime.utcnow().isoformat()
    thought_file = os.path.join(thought_dir, f"{timestamp}.txt")
    
    with open(thought_file, "w") as f:
        f.write(thought)

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
    
    subtask_id = create_base_task(
        task_name=title,
        description=description,
        priority=priority
    )
    
    # Add subtask reference to parent
    subtasks_dir = os.path.join(ACTIVE_TASKS_DIR, parent_id, "subtasks")
    with open(os.path.join(subtasks_dir, f"{subtask_id}.json"), "w") as f:
        json.dump({"id": subtask_id, "title": title}, f)
    
    return subtask_id

def get_highest_priority_task() -> Optional[Dict]:
    """Get the highest priority pending task"""
    global _active_task_id
    log("Retrieving highest priority pending task")
    
    highest_priority = float('inf')
    selected_task = None
    
    for task_id in os.listdir(ACTIVE_TASKS_DIR):
        task_file = os.path.join(ACTIVE_TASKS_DIR, task_id, "task.json")
        if os.path.exists(task_file):
            try:
                with open(task_file) as f:
                    task_data = json.load(f)
                    if (task_data["status"] == "pending" and 
                        task_data["priority"] < highest_priority):
                        highest_priority = task_data["priority"]
                        selected_task = task_data
                        _active_task_id = task_id  # Set the active task ID
            except (json.JSONDecodeError, OSError) as e:
                # TODO: Implement proper error logging here
                pass
    
    if not selected_task:
        _active_task_id = None  # Clear active task if no task found
        
    return selected_task
