import os
import json

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
                print(f"Error reading {file_path}: {e}")

    # Sort tasks by 'priority' key
    tasks.sort(key=lambda x: x['priority'])

    # Return the task with the highest priority, or None if no tasks found
    return tasks[0] if tasks else None

# Example usage:
# folder_path = '/path/to/json/folder'
# print(get_first_task(folder_path))
