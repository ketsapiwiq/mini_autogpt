import os
import json
from datetime import datetime
from utils.task_tree import get_highest_priority_task, get_active_task
from action.tasks import create_task
from utils.log import log

def get_first_task(folder_path="tasks"):
    """
    Wrapper for backward compatibility. 
    Delegates to task_tree's get_highest_priority_task.
    """
    log("Getting first task (delegating to get_highest_priority_task)")
    task = get_highest_priority_task()
    if task:
        log(f"Found task: {task.get('title', 'Unknown')}")
        active_task = get_active_task()
        if active_task:
            log(f"Current active task: {active_task.get('title', 'Unknown')}")
    else:
        log("No tasks found")
    return task

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
