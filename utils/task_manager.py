import os
import json
from utils.log import log

def get_first_task(folder_path="tasks"):
    """
    Checks the JSON files in the given folder, sorts them by a 'priority' key, 
    and returns the first task.

    Args:
        folder_path (str): The path to the folder containing JSON files.

    Returns:
        dict or None: The task with the highest priority (lowest value of 'priority'), 
                      or None if no valid tasks are found.
    """
    tasks = []
    
    # Ensure the folder path is absolute
    if not os.path.isabs(folder_path):
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), folder_path)

    # Check if directory exists
    if not os.path.exists(folder_path):
        log(f"Task directory not found: {folder_path}")
        return None

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            try:
                # Read and parse the JSON file
                with open(file_path, 'r') as file:
                    task = json.load(file)

                # Ensure the task has a 'priority' key
                if 'priority' in task and isinstance(task['priority'], (int, float)):
                    tasks.append(task)
            except (json.JSONDecodeError, OSError) as e:
                log(f"Error reading {file_path}: {e}")

    # Sort tasks by 'priority' key
    tasks.sort(key=lambda x: x['priority'])

    # Return the task with the highest priority, or None if no tasks found
    return tasks[0] if tasks else None

def create_task(task_name, priority, description, status="pending"):
    """
    Creates a new task file in the tasks directory.
    
    Args:
        task_name (str): Name of the task (will be used in filename)
        priority (int): Priority level of the task (lower number = higher priority)
        description (str): Detailed description of the task
        status (str): Current status of the task (default: "pending")
    
    Returns:
        bool: True if task was created successfully, False otherwise
    """
    folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tasks")
    
    # Ensure tasks directory exists
    os.makedirs(folder_path, exist_ok=True)
    
    # Create safe filename from task name
    safe_name = "".join(c for c in task_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.lower().replace(' ', '_')
    filename = f"{safe_name}.json"
    
    task_data = {
        "priority": priority,
        "task": task_name,
        "description": description,
        "status": status
    }
    
    try:
        with open(os.path.join(folder_path, filename), 'w') as f:
            json.dump(task_data, f, indent=4)
        return True
    except Exception as e:
        log(f"Error creating task file: {e}")
        return False
