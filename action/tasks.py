import os
import json
from datetime import datetime
from utils.log import log

# Use absolute path for tasks directory
TASKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks")
ACTIVE_TASKS_DIR = os.path.join(TASKS_DIR, "active")
COMPLETED_TASKS_DIR = os.path.join(TASKS_DIR, "completed")

def ensure_task_directories():
    """Ensure all required task directories exist"""
    for dir_path in [TASKS_DIR, ACTIVE_TASKS_DIR, COMPLETED_TASKS_DIR]:
        os.makedirs(dir_path, exist_ok=True)

def get_first_task():
    """
    Checks the JSON files in the given folder, sorts them by a 'priority' key, 
    and returns the first task.

    Returns:
        dict or None: The task with the highest priority (lowest value of 'priority'), 
                      or None if no valid tasks are found.
    """
    tasks = []
    ensure_task_directories()
    
    # Create state file if it doesn't exist
    state_file = os.path.join(TASKS_DIR, "task_state.json")
    if not os.path.exists(state_file):
        with open(state_file, "w") as f:
            json.dump({"last_task": None, "in_progress": []}, f)
            
    # Load task state
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except:
        state = {"last_task": None, "in_progress": []}
    
    # Iterate over all files in the active tasks folder
    for task_id in os.listdir(ACTIVE_TASKS_DIR):
        task_file = os.path.join(ACTIVE_TASKS_DIR, task_id, "task.json")
        if os.path.exists(task_file):
            try:
                # Read and parse the JSON file
                with open(task_file, 'r') as file:
                    task = json.load(file)
                    
                # Skip tasks that are already in progress
                if task.get("id") in state["in_progress"]:
                    continue

                # Ensure the task has required fields
                if all(key in task for key in ["priority", "task", "status"]):
                    if task["status"] != "completed":
                        tasks.append(task)
            except (json.JSONDecodeError, OSError) as e:
                log(f"Error reading {task_file}: {e}")

    # Sort tasks by priority and creation time
    tasks.sort(key=lambda x: (x.get("priority", 999), x.get("created_at", "")))
    
    # Get next task
    next_task = tasks[0] if tasks else None
    
    # Update state
    if next_task:
        state["last_task"] = next_task.get("id")
        if next_task.get("id") not in state["in_progress"]:
            state["in_progress"].append(next_task.get("id"))
        
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
            
    return next_task

def create_task(task_name: str, description: str, priority: int = 3, status: str = "pending"):
    """
    Creates a new task file in the tasks directory.
    
    Args:
        task_name (str): Name/title of the task
        description (str): Detailed description of the task
        priority (int): Priority level (1-5, lower is higher priority)
        status (str): Current status of task (default: pending)
        
    Returns:
        str: ID of the created task
    """
    ensure_task_directories()
    
    task_id = str(int(datetime.utcnow().timestamp()))
    task_dir = os.path.join(ACTIVE_TASKS_DIR, task_id)
    os.makedirs(task_dir)
    os.makedirs(os.path.join(task_dir, "thoughts"))
    os.makedirs(os.path.join(task_dir, "subtasks"))
    
    task_data = {
        "id": task_id,
        "task": task_name,
        "priority": priority,
        "description": description,
        "status": status,
        "created_at": datetime.utcnow().isoformat(),
        "source": "user_message",
        "dependencies": [],
        "results": {}
    }
    
    task_file = os.path.join(task_dir, "task.json")
    log(f"Creating task: {task_name} with priority {priority} in {task_file}")
    
    with open(task_file, 'w') as f:
        json.dump(task_data, f, indent=4)
    
    return task_id
