"""Main entry point for mini_autogpt."""
import sys
from pathlib import Path
import traceback
sys.path.append(str(Path(__file__).parent))
from utils.log import log, debug
import time

def main():
    """Run the main AI loop."""
    log("*** Starting up... ***")
    
    # Register all available commands
    # register_commands()
    
    # Log available commands for debugging
    # commands = CommandRegistry.get_available_commands()
    # debug("Registered Commands:")
    # for cmd in commands:
    #     debug(f"- {cmd['name']}: {cmd['description']}")
    
    log("*** I am thinking... ***")
    while True:
        try:
            process_tasks()
            time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
            break
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            print(f"Full traceback: {traceback.format_exc()}")
            time.sleep(5)

def write_start_message():
    """Display the startup ASCII art."""
    ascii_art = """                           
                                                 
                         ░▓█▓░░                          
         ▒▒▒      ██░ ░░░░░░░░░░ ░░██░      ▒░           
         ▒▒▒░ ░█░░▒░░░░░░░░░     ░░░▒ ░█   ░▒░░          
      ▒░    ░█ ▒▒░░░░░░░░░░░░░░░░░▒▒▒ █      ░▒       
     ░▒▒░  ▒░▒▒▒░███░░░░░░░░░░░░░░░███░▒▒░▓░  ▒▒▒░▒▒     
      ░   ▒░▒▒▒░░░░░░░░░░░░░░░░░░░░░░░░░▒▒▒░    ░▒       
          █▒▒░░██░░░▒░░░░░░░░░░░░░░░░░██░░▒▒█            
   ▒░░▒  █░▒▒░█░█▓░   █░░░░░░░░░█   █▒█░█░▒▒░░           
         █░▒▒█░████   ██░░░░░░░██  ░████░█▒▒░█  ▒░░▒     
         █░▒▒█ █▓░░█▒░▓█░█░░▓▓░█▓░██░█▓█ ▒▒▒░░    ░      
         ░█▒▒▒░ ▓░░░░░█░░░▒▒▒░░░█░░░░▓░ ░▒▒░█            
    ░█░█░ ░█▒▒▒▓▒░▒░░░░░░░░░░░░░░░░░▒▓▓▒▒▒░█  ▒░░█░      
   █░░░█    █░▒▒▒▒▒▒▒▒▒░░░░░░░░░░▒▒▒▒▒▒▒▒░█   ░█░░░█     
   █▓▒░░ ████▓██▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▒▒██▓████░░░▒▓█     
   █▒▒▓▒░▒▒▒▒▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓█▒▒▒▒▒░▒▓▓▒▓     
    ▓▒██░░   ░░░░░░▓▓▒░░░░▓▓▓░░░░▒▓▓░░░░░░    ░██▒░      
    █░░░░░░░░░░░░▒▓█░▒░░░░▒▓▒░░░░▒░█▓░░░░░░░░░░░░░█      
    █▓░░▓▓▒▒▒█░░░░░█░░░░░▒▓▓▓▒░░░░░░█░░░░░█▒▒▒▒▓░░▒█      
     ███░░▓▓█▒▓▒▒░░░░░░▒▒▓▒█▓▓▒░░░░░░▒▒▓▓▒▓▓▓░░▓██       
     ░░░█████▓▒░▒▒░▒▒▒▒▒▒▒█░█▓▒▒▒▒▒▒▒▒▓▒░██████░░░       
      ░░░░░░░░██░░█▓░▒▒░█░░░░░█░█░░█▒░▒█"""
    print(ascii_art)
    message = """Hello my friend!
I am Mini-Autogpt, a small version of Autogpt for smaller llms.
I am here to help you and will try to contact you as soon as possible!

Note: I am still in development, so please be patient with me! <3

"""
    for char in message:
        print(char, end="", flush=True)

def process_tasks():
    """
    Read and list active tasks from the tasks directory.
    
    This is a placeholder implementation that will be expanded 
    when processing logic is added from the think/ module.
    """
    from action.tasks import ACTIVE_TASKS_DIR
    import os
    import json
    
    print("Processing Active Tasks:")
    
    # Ensure the active tasks directory exists
    if not os.path.exists(ACTIVE_TASKS_DIR):
        print("No active tasks directory found.")
        return []
    
    active_tasks = []
    
    # Iterate through task directories in the active tasks folder
    for task_id in os.listdir(ACTIVE_TASKS_DIR):
        task_file_path = os.path.join(ACTIVE_TASKS_DIR, task_id, "task.json")
        
        # Check if task.json exists for this task
        if os.path.exists(task_file_path):
            try:
                with open(task_file_path, 'r') as file:
                    task = json.load(file)
                    
                # Print task details
                print(f"Task ID: {task.get('id', 'N/A')}")
                print(f"Title: {task.get('title', 'Untitled')}")
                print(f"Description: {task.get('description', 'No description')}")
                print(f"Priority: {task.get('priority', 'Unspecified')}")
                print(f"Status: {task.get('status', 'Unknown')}")
                print("---")
                
                active_tasks.append(task)
            
            except json.JSONDecodeError:
                print(f"Error reading task file: {task_file_path}")
    
    if not active_tasks:
        print("No active tasks found.")
    
    return active_tasks

if __name__ == "__main__":
    main()
