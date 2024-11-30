import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from utils.log import log

TASKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks")
ACTIVE_TASKS_DIR = os.path.join(TASKS_DIR, "active")
COMPLETED_TASKS_DIR = os.path.join(TASKS_DIR, "completed")

def ensure_task_directories():
    """Ensure all required task directories exist"""
    log("Creating task directories...")
    for dir_path in [TASKS_DIR, ACTIVE_TASKS_DIR, COMPLETED_TASKS_DIR]:
        log(f"Ensuring directory exists: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)

def create_task(title: str, description: str, priority: int = 3, 
                source: str = "system", parent_task: Optional[str] = None) -> str:
    """Create a new task and return its ID"""
    log(f"Creating new task: {title}")
    log(f"Task details - Priority: {priority}, Source: {source}, Parent: {parent_task}")
    
    task_id = str(uuid.uuid4())
    task_dir = os.path.join(ACTIVE_TASKS_DIR, task_id)
    log(f"Creating task directory: {task_dir}")
    
    os.makedirs(task_dir)
    os.makedirs(os.path.join(task_dir, "thoughts"))
    os.makedirs(os.path.join(task_dir, "subtasks"))
    
    task_data = {
        "id": task_id,
        "priority": priority,
        "created_at": datetime.utcnow().isoformat(),
        "source": source,
        "title": title,
        "description": description,
        "status": "pending",
        "parent_task": parent_task,
        "dependencies": [],
        "results": {}
    }
    
    task_file = os.path.join(task_dir, "task.json")
    log(f"Writing task data to: {task_file}")
    with open(task_file, "w") as f:
        json.dump(task_data, f, indent=2)
    
    log(f"Task created successfully with ID: {task_id}")
    return task_id

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

def get_highest_priority_task() -> Optional[Dict]:
    """Get the highest priority pending task"""
    log("Retrieving highest priority pending task")
    # TODO: Add support for custom folder paths instead of fixed ACTIVE_TASKS_DIR
    # TODO: Add validation for priority field type (int or float)
    # TODO: Add error logging for JSON parsing errors
    # TODO: Add sorting by creation date as secondary criteria
    
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
            except (json.JSONDecodeError, OSError) as e:
                # TODO: Implement proper error logging here
                pass
    
    return selected_task

def create_subtask(parent_id: str, title: str, description: str, 
                   priority: Optional[int] = None) -> str:
    """Create a subtask under a parent task"""
    log(f"Creating subtask under parent ID: {parent_id}")
    parent_task = get_task(parent_id)
    if priority is None:
        priority = parent_task["priority"]
    
    task_id = create_task(
        title=title,
        description=description,
        priority=priority,
        parent_task=parent_id
    )
    
    return task_id
