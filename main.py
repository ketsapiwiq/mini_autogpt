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
    
    log("*** I am thinking... ***")
    while True:
        # Process tasks
        tasks = process_tasks()
        
        # If no tasks, wait for Telegram messages
        if not tasks:
            from utils.simple_telegram import TelegramUtils, get_telegram_config
            
            # Debug: Check Telegram configuration
            api_key, chat_id = get_telegram_config()
            log(f"Telegram Config - API Key: {bool(api_key)}, Chat ID: {bool(chat_id)}")
            
            # Ensure we have a valid configuration
            if api_key and chat_id:
                try:
                    telegram_utils = TelegramUtils.get_instance(api_key, chat_id)
                    
                    if telegram_utils:
                        log("Retrieving Telegram messages...")
                        messages = telegram_utils.get_last_few_messages()
                        
                        # Process Telegram messages if any
                        for message in messages:
                            task_id = handle_telegram_message({"text": message})
                    else:
                        log("Failed to initialize TelegramUtils.")
                except Exception as e:
                    log(f"Error retrieving Telegram messages: {e}")
                    log(traceback.format_exc())
            else:
                log("Telegram configuration is incomplete.")
        
        time.sleep(1)  # Prevent tight loop

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
   █▒▒▓▒░▒▒▒▒▓█▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▓█▒▒▒▒▒░▒▓▓▒▓     
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

def handle_telegram_message(message):
    # This function is not implemented in the provided code
    pass

if __name__ == "__main__":
    main()
