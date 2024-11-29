import os
import json
from datetime import datetime

def get_first_task():
    """
    Checks the JSON files in the given folder, sorts them by a 'priority' key, 
    and returns the first task.

    Returns:
        dict or None: The task with the highest priority (lowest value of 'priority'), 
                      or None if no valid tasks are found.
    """
    tasks = []
    folder_path = "tasks"
    
    # Ensure tasks directory exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Create state file if it doesn't exist
    state_file = os.path.join(folder_path, "task_state.json")
    if not os.path.exists(state_file):
        with open(state_file, "w") as f:
            json.dump({"last_task": None, "in_progress": []}, f)
            
    # Load task state
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except:
        state = {"last_task": None, "in_progress": []}
    
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json') and filename != "task_state.json":
            file_path = os.path.join(folder_path, filename)
            try:
                # Read and parse the JSON file
                with open(file_path, 'r') as file:
                    task = json.load(file)
                    
                # Skip tasks that are already in progress
                if task.get("id") in state["in_progress"]:
                    continue

                # Ensure the task has required fields
                if all(key in task for key in ["priority", "task", "status"]):
                    if task["status"] != "completed":
                        tasks.append(task)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error reading {file_path}: {e}")

    # Sort tasks by priority
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

def create_task(task_name, priority, description, status="pending"):
    """
    Creates a new task file in the tasks directory.
    
    Args:
        task_name (str): Name/title of the task
        priority (int): Priority level (1-5, lower is higher priority)
        description (str): Detailed description of the task
        status (str): Current status of task (default: pending)
        
    Returns:
        str: Path to created task file
    """
    folder_path = "tasks"
    os.makedirs(folder_path, exist_ok=True)
    
    task_data = {
        "id": int(datetime.utcnow().timestamp()),
        "task": task_name,
        "priority": priority,
        "description": description,
        "status": status,
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Create unique filename using timestamp
    filename = f"{task_data['id']}_{task_name.lower().replace(' ', '_')}.json"
    file_path = os.path.join(folder_path, filename)
    
    with open(file_path, 'w') as f:
        json.dump(task_data, f, indent=4)
    
    return file_path

# Example usage:
# folder_path = '/path/to/json/folder'
# print(get_first_task(folder_path))
